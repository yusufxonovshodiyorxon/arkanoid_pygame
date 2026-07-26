import random

import pygame

import settings as cfg
from game.entities import Paddle, Ball, Bonus
from game.level import load_level


def _bounce_off_rect(ball: Ball, rect: pygame.Rect) -> None:
    """ Bounces the Ball off the given rect (brick, paddle, wall). """
    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top

    min_overlap = min(overlap_bottom, overlap_left, overlap_right, overlap_top)

    if min_overlap == overlap_top and ball.vy > 0:
        ball.rect.bottom = rect.top
        ball.vy *= -1
    elif min_overlap == overlap_bottom and ball.vy < 0:
        ball.rect.top = rect.bottom
        ball.vy *= -1
    elif min_overlap == overlap_left and ball.vx > 0:
        ball.rect.right = rect.left
        ball.vx *= -1
    elif min_overlap == overlap_right and ball.vx < 0:
        ball.rect.left = rect.right
        ball.vx *= -1


def _handle_ball_vs_paddle(ball: Ball, paddle: Paddle) -> None:
    """ Handles a Ball bouncing off the Paddle, adding "spin" based on where it hit. """
    _bounce_off_rect(ball, paddle.rect)
    offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
    max_vx = cfg.MAX_BALL_SPEED_X
    ball.vx = max(-max_vx, min(max_vx, offset * max_vx))


def _maybe_spawn_bonus(brick_rect: pygame.Rect, bonuses: list[Bonus]) -> None:
    """ Rolls the dice on a just-destroyed Brick and may drop a random Bonus. """
    if random.random() < cfg.BONUS_PROBABILITY:
        kind = random.choice(cfg.BONUS_TYPES)
        bonuses.append(Bonus(brick_rect.centerx, brick_rect.centery, kind))


def _handle_balls_vs_bricks(balls: list[Ball], bricks: list, bonuses: list[Bonus]) -> int:
    """ Resolves collisions between every Ball and every Brick. Returns score gained. """
    scored = 0
    for ball in balls:
        for brick in bricks[:]:
            if not ball.rect.colliderect(brick.rect):
                continue
            _bounce_off_rect(ball, brick.rect)

            if brick.hp <= 0:
                continue  # Level boundary (-1) or indestructible brick (0)

            brick.hit()
            if brick.hp == 0:
                bricks.remove(brick)
                scored += 10
                _maybe_spawn_bonus(brick.rect, bonuses)
    return scored


def _scale_ball_speed(ball: Ball, factor: float) -> tuple[float, float]:
    """ Scales a Ball's velocity by `factor`, keeping its speed within configured limits. """
    vx, vy = ball.vx * factor, ball.vy * factor
    speed = (vx ** 2 + vy ** 2) ** 0.5
    if speed == 0:
        return vx, vy
    clamped = max(cfg.BALL_MIN_SPEED, min(cfg.BALL_MAX_SPEED, speed))
    scale = clamped / speed
    return vx * scale, vy * scale


def ApplyBonus(paddle: Paddle, balls: list[Ball], bonus: Bonus, state: dict) -> None:
    """
        Applies the effect of a collected Bonus to the game state.

        `state` carries loop-level values a bonus might need to change
        (currently just "lives") since Paddle/Ball don't track those themselves.
    """
    kind = bonus.kind

    if kind == "extend":
        new_width = min(cfg.PADDLE_MAX_WIDTH, paddle.rect.width + cfg.PADDLE_EXTEND_STEP)
        center = paddle.rect.centerx
        paddle.rect.width = new_width
        paddle.rect.centerx = center
        paddle.extended = new_width > cfg.PADDLE_WIDTH

    elif kind == "shrink":
        new_width = max(cfg.PADDLE_MIN_WIDTH, paddle.rect.width - cfg.PADDLE_SHRINK_STEP)
        center = paddle.rect.centerx
        paddle.rect.width = new_width
        paddle.rect.centerx = center
        paddle.extended = new_width > cfg.PADDLE_WIDTH

    elif kind == "speed_up":
        for ball in balls:
            ball.vx, ball.vy = _scale_ball_speed(ball, cfg.BALL_SPEED_MULTIPLIER)

    elif kind == "speed_down":
        for ball in balls:
            ball.vx, ball.vy = _scale_ball_speed(ball, 1 / cfg.BALL_SPEED_MULTIPLIER)

    elif kind == "multiball":
        if balls:
            source = balls[0]
            for dvx in (-2, 2):
                clone = Ball(source.rect.centerx, source.rect.centery)
                clone.vx = source.vx + dvx
                clone.vy = source.vy
                balls.append(clone)

    elif kind == "laser":
        paddle.laser = True

    elif kind == "extra_life":
        state["lives"] = state.get("lives", cfg.LIVES_START) + 1

    # Keep the paddle inside the playfield after any width change
    if paddle.rect.left < cfg.FIELD_LEFT:
        paddle.rect.left = cfg.FIELD_LEFT
    if paddle.rect.right > cfg.FIELD_RIGHT:
        paddle.rect.right = cfg.FIELD_RIGHT


def _reset_ball_and_paddle(paddle: Paddle) -> list[Ball]:
    """ Resets Paddle size/laser state and returns a fresh single-Ball list after a life is lost. """
    paddle.rect.width = cfg.PADDLE_WIDTH
    paddle.rect.midbottom = (cfg.WIDTH // 2, cfg.HEIGHT - 20)
    paddle.extended = False
    paddle.laser = False
    return [Ball(cfg.WIDTH // 2, cfg.HEIGHT - 40)]


def run(screen: pygame.Surface, clock: pygame.time.Clock, level: int) -> str:
    """
        Runs one full game level.

        Returns "won" (all breakable bricks cleared), "lost" (out of lives)
        or "quit" (player closed the window / pressed Escape).
    """
    paddle = Paddle()
    bricks, rows, cols = load_level(level)
    balls: list[Ball] = [Ball(cfg.WIDTH // 2, cfg.HEIGHT - 40)]
    bonuses: list[Bonus] = []
    lasers: list[pygame.Rect] = []
    laser_cooldown = 0

    state = {"lives": cfg.LIVES_START, "score": 0}
    font = pygame.font.SysFont("consolas", 20, bold=True)

    while True:
        clock.tick(cfg.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quit"

        keys = pygame.key.get_pressed()
        paddle.move(keys)

        # --- Laser firing ---
        if laser_cooldown > 0:
            laser_cooldown -= 1
        if paddle.laser and keys[pygame.K_SPACE] and laser_cooldown == 0:
            lasers.append(
                pygame.Rect(
                    paddle.rect.left + 6,
                    paddle.rect.top - cfg.LASER_HEIGHT,
                    cfg.LASER_WIDTH,
                    cfg.LASER_HEIGHT,
                )
            )
            lasers.append(
                pygame.Rect(
                    paddle.rect.right - 6 - cfg.LASER_WIDTH,
                    paddle.rect.top - cfg.LASER_HEIGHT,
                    cfg.LASER_WIDTH,
                    cfg.LASER_HEIGHT,
                )
            )
            laser_cooldown = cfg.LASER_COOLDOWN

        # --- Update lasers ---
        for bolt in lasers[:]:
            bolt.y -= cfg.LASER_SPEED
            hit_brick = None
            for brick in bricks:
                if brick.hp > 0 and bolt.colliderect(brick.rect):
                    hit_brick = brick
                    break
            if hit_brick is not None:
                hit_brick.hit()
                lasers.remove(bolt)
                if hit_brick.hp == 0:
                    bricks.remove(hit_brick)
                    state["score"] += 10
                    _maybe_spawn_bonus(hit_brick.rect, bonuses)
                continue
            if bolt.bottom < 0:
                lasers.remove(bolt)

        # --- Update balls & collisions ---
        for ball in balls:
            ball.update()

        state["score"] += _handle_balls_vs_bricks(balls, bricks, bonuses)

        for ball in balls[:]:
            if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
                _handle_ball_vs_paddle(ball, paddle)
            if ball.rect.top > cfg.HEIGHT:
                balls.remove(ball)

        if not balls:
            state["lives"] -= 1
            if state["lives"] <= 0:
                return "lost"
            balls = _reset_ball_and_paddle(paddle)
            bonuses.clear()
            lasers.clear()

        # --- Update bonuses & catch them with the paddle ---
        for bonus in bonuses[:]:
            bonus.update()
            if bonus.rect.colliderect(paddle.rect):
                ApplyBonus(paddle, balls, bonus, state)
                bonuses.remove(bonus)
            elif bonus.is_off_screen():
                bonuses.remove(bonus)

        if not any(brick.hp > 0 for brick in bricks):
            return "won"

        # --- Draw ---
        screen.fill(cfg.BLACK)

        for brick in bricks:
            brick.draw(screen)

        for bonus in bonuses:
            bonus.draw(screen)

        for bolt in lasers:
            pygame.draw.rect(screen, cfg.RED, bolt)

        paddle.draw(screen)

        for ball in balls:
            ball.draw(screen)

        hud = font.render(
            f"Score: {state['score']}   Lives: {state['lives']}",
            True,
            cfg.WHITE,
        )
        screen.blit(hud, (cfg.FIELD_LEFT, 20))

        pygame.display.flip()

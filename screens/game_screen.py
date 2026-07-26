import random

import pygame

import settings as cfg
from game.entities import Ball, Brick, Paddle, PowerUp


POWER_UP_DROP_CHANCE = 0.25

MINIMUM_BALL_SPEED = 2.0
MAXIMUM_BALL_SPEED = 12.0

SPEED_UP_MULTIPLIER = 1.25
SPEED_DOWN_MULTIPLIER = 0.75

PADDLE_SHRINK_MULTIPLIER = 0.60
PADDLE_EXTEND_MULTIPLIER = 1.50


def clamp_speed(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """Restricts velocity while preserving its direction."""
    if value > 0:
        return max(minimum, min(value, maximum))

    if value < 0:
        return min(-minimum, max(value, -maximum))

    return value


def change_ball_speed(
    ball: Ball,
    multiplier: float,
) -> None:
    """Changes the speed of one ball."""
    new_vx = ball.vx * multiplier
    new_vy = ball.vy * multiplier

    ball.vx = clamp_speed(
        new_vx,
        MINIMUM_BALL_SPEED,
        MAXIMUM_BALL_SPEED,
    )

    ball.vy = clamp_speed(
        new_vy,
        MINIMUM_BALL_SPEED,
        MAXIMUM_BALL_SPEED,
    )


def ApplyBonus(
    power_type: str,
    paddle: Paddle,
    balls: list[Ball],
) -> None:
    """
    Applies the collected power-up.

    Required homework power-ups:
    - paddle_shrink
    - ball_speed_up
    - ball_speed_down
    """

    if power_type == "paddle_shrink":
        new_width = int(
            paddle.original_width
            * PADDLE_SHRINK_MULTIPLIER
        )

        new_width = max(new_width, 40)

        paddle.resize(new_width)
        paddle.shrunk = True
        paddle.extended = False

    elif power_type == "ball_speed_up":
        for ball in balls:
            change_ball_speed(
                ball,
                SPEED_UP_MULTIPLIER,
            )

    elif power_type == "ball_speed_down":
        for ball in balls:
            change_ball_speed(
                ball,
                SPEED_DOWN_MULTIPLIER,
            )

    elif power_type == "paddle_extend":
        new_width = int(
            paddle.original_width
            * PADDLE_EXTEND_MULTIPLIER
        )

        maximum_width = (
            cfg.FIELD_RIGHT - cfg.FIELD_LEFT
        )

        new_width = min(
            new_width,
            maximum_width,
        )

        paddle.resize(new_width)
        paddle.extended = True
        paddle.shrunk = False

    elif power_type == "extra_ball":
        if not balls:
            return

        source_ball = balls[0]

        new_ball = Ball(
            source_ball.rect.centerx,
            source_ball.rect.centery,
        )

        new_ball.vx = -source_ball.vx
        new_ball.vy = source_ball.vy

        balls.append(new_ball)

    elif power_type == "laser":
        paddle.laser = True


def create_bricks() -> list[Brick]:
    """Creates a basic brick layout."""
    bricks: list[Brick] = []

    field_width = (
        cfg.FIELD_RIGHT - cfg.FIELD_LEFT
    )

    columns = max(
        1,
        field_width // cfg.BRICK_WIDTH,
    )

    rows = 6

    for row in range(rows):
        for col in range(columns):
            if row < 2:
                hp = 2
            else:
                hp = 1

            brick = Brick(
                col,
                row,
                hp,
            )

            bricks.append(brick)

    return bricks


def handle_wall_collision(ball: Ball) -> None:
    """Handles collisions between the ball and game boundaries."""
    if ball.rect.left <= cfg.FIELD_LEFT:
        ball.rect.left = cfg.FIELD_LEFT
        ball.vx = abs(ball.vx)

    elif ball.rect.right >= cfg.FIELD_RIGHT:
        ball.rect.right = cfg.FIELD_RIGHT
        ball.vx = -abs(ball.vx)

    if ball.rect.top <= 0:
        ball.rect.top = 0
        ball.vy = abs(ball.vy)


def handle_paddle_collision(
    ball: Ball,
    paddle: Paddle,
) -> None:
    """Handles collision between a ball and the paddle."""
    if ball.vy <= 0:
        return

    if not ball.rect.colliderect(paddle.rect):
        return

    ball.rect.bottom = paddle.rect.top
    ball.vy = -abs(ball.vy)

    paddle_center = paddle.rect.centerx
    ball_center = ball.rect.centerx

    horizontal_difference = (
        ball_center - paddle_center
    )

    half_paddle_width = max(
        paddle.rect.width / 2,
        1,
    )

    hit_position = (
        horizontal_difference
        / half_paddle_width
    )

    ball.vx += hit_position * 2

    ball.vx = clamp_speed(
        ball.vx,
        MINIMUM_BALL_SPEED,
        MAXIMUM_BALL_SPEED,
    )


def handle_brick_collision(
    ball: Ball,
    bricks: list[Brick],
    power_ups: list[PowerUp],
) -> None:
    """Handles collision between one ball and the bricks."""
    for brick in bricks[:]:
        if not ball.rect.colliderect(brick.rect):
            continue

        overlap_left = (
            ball.rect.right - brick.rect.left
        )

        overlap_right = (
            brick.rect.right - ball.rect.left
        )

        overlap_top = (
            ball.rect.bottom - brick.rect.top
        )

        overlap_bottom = (
            brick.rect.bottom - ball.rect.top
        )

        minimum_overlap = min(
            overlap_left,
            overlap_right,
            overlap_top,
            overlap_bottom,
        )

        if minimum_overlap in (
            overlap_left,
            overlap_right,
        ):
            ball.vx *= -1
        else:
            ball.vy *= -1

        brick.hit()

        if brick.hp == 0:
            bricks.remove(brick)

            if random.random() < POWER_UP_DROP_CHANCE:
                power_up = PowerUp.create_random(
                    brick.rect.centerx,
                    brick.rect.centery,
                )

                power_ups.append(power_up)

        break


def update_power_ups(
    power_ups: list[PowerUp],
    paddle: Paddle,
    balls: list[Ball],
) -> None:
    """Updates power-ups and applies collected bonuses."""
    for power_up in power_ups[:]:
        power_up.update()

        if power_up.rect.colliderect(paddle.rect):
            ApplyBonus(
                power_up.power_type,
                paddle,
                balls,
            )

            power_ups.remove(power_up)
            continue

        if power_up.rect.top > cfg.HEIGHT:
            power_ups.remove(power_up)


def draw_information(
    screen: pygame.Surface,
    balls: list[Ball],
    bricks: list[Brick],
) -> None:
    """Displays simple game information."""
    font = pygame.font.Font(None, 26)

    information = (
        f"Balls: {len(balls)}   "
        f"Bricks: {len(bricks)}"
    )

    text = font.render(
        information,
        True,
        (255, 255, 255),
    )

    screen.blit(
        text,
        (cfg.FIELD_LEFT, 10),
    )


def run(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    level: int,
) -> None:
    """Runs the Arkanoid game screen."""
    paddle = Paddle()

    ball = Ball(
        paddle.rect.centerx,
        paddle.rect.top - cfg.BALL_RADIUS - 2,
    )

    # Make the first ball move upward.
    ball.vy = -abs(ball.vy)

    balls: list[Ball] = [ball]
    bricks = create_bricks()
    power_ups: list[PowerUp] = []

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        paddle.move(keys)

        for current_ball in balls[:]:
            current_ball.update()

            handle_wall_collision(current_ball)

            handle_paddle_collision(
                current_ball,
                paddle,
            )

            handle_brick_collision(
                current_ball,
                bricks,
                power_ups,
            )

            if current_ball.rect.top > cfg.HEIGHT:
                balls.remove(current_ball)

        update_power_ups(
            power_ups,
            paddle,
            balls,
        )

        # Restart the ball when all balls are lost.
        if not balls:
            new_ball = Ball(
                paddle.rect.centerx,
                paddle.rect.top
                - cfg.BALL_RADIUS
                - 2,
            )

            new_ball.vy = -abs(new_ball.vy)
            balls.append(new_ball)

        # Recreate bricks after the player destroys all of them.
        if not bricks:
            bricks = create_bricks()

        screen.fill((20, 20, 25))

        for brick in bricks:
            brick.draw(screen)

        for power_up in power_ups:
            power_up.draw(screen)

        paddle.draw(screen)

        for current_ball in balls:
            current_ball.draw(screen)

        draw_information(
            screen,
            balls,
            bricks,
        )

        pygame.display.flip()
        clock.tick(60)

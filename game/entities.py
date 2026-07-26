import random

import pygame

import settings as cfg


class Paddle:
    """Main player. The paddle moves only horizontally."""

    def __init__(self) -> None:
        self.rect = pygame.Rect(
            0,
            0,
            cfg.PADDLE_WIDTH,
            cfg.PADDLE_HEIGHT,
        )
        self.rect.midbottom = (
            cfg.WIDTH // 2,
            cfg.HEIGHT - 20,
        )

        self.original_width = cfg.PADDLE_WIDTH
        self.speed = cfg.PADDLE_SPEED
        self.vx = 0

        self.extended = False
        self.shrunk = False
        self.laser = False

    def move(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Moves the paddle when the player presses an arrow key."""
        self.vx = 0

        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vx = self.speed

        self.rect.x += self.vx

        # Restrict the paddle's movement.
        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT

        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT

    def resize(self, new_width: int) -> None:
        """Changes paddle width while preserving its center position."""
        old_center_x = self.rect.centerx

        self.rect.width = new_width
        self.rect.centerx = old_center_x

        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT

        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT

    def draw(self, screen: pygame.Surface) -> None:
        """Renders the paddle."""
        pygame.draw.rect(
            screen,
            cfg.PADDLE_COLOR,
            self.rect,
            border_radius=5,
        )


class Brick:
    """
    Game brick.

    HP = -1: level boundary
    HP = 0: indestructible
    HP = 1: one hit
    HP = 2: two hits
    """

    def __init__(self, col: int, row: int, hp: int) -> None:
        self.hp = hp
        self.color = cfg.BRICK_COLORS[hp]

        self.rect = pygame.Rect(
            cfg.FIELD_LEFT + col * cfg.BRICK_WIDTH,
            cfg.TOP_OFFSET + row * cfg.BRICK_HEIGHT,
            cfg.BRICK_WIDTH,
            cfg.BRICK_HEIGHT,
        )

    def draw(self, screen: pygame.Surface) -> None:
        """Renders the brick."""
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, cfg.DARK_GRAY, self.rect, 2)

    def hit(self) -> None:
        """Handles the brick being hit."""
        if self.hp > 0:
            self.hp -= 1

            if self.hp > 0:
                self.color = cfg.BRICK_COLORS[self.hp]


class Ball:
    """Ball actor class."""

    def __init__(self, x: int, y: int) -> None:
        self.radius = cfg.BALL_RADIUS

        self.rect = pygame.Rect(
            x - self.radius,
            y - self.radius,
            2 * self.radius,
            2 * self.radius,
        )

        self.vx = cfg.BALL_SPEED_X
        self.vy = cfg.BALL_SPEED_Y

    def update(self) -> None:
        """Updates the ball's position for each frame."""
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def draw(self, screen: pygame.Surface) -> None:
        """Renders the ball."""
        pygame.draw.circle(
            screen,
            cfg.BALL_COLOR,
            self.rect.center,
            self.radius,
        )


class PowerUp:
    """A power-up that falls from a destroyed brick."""

    POWER_UPS = {
        "paddle_extend": {
            "icon": "E",
            "color": (0, 220, 0),
        },
        "extra_ball": {
            "icon": "B",
            "color": (0, 150, 255),
        },
        "laser": {
            "icon": "L",
            "color": (255, 50, 50),
        },

        # New homework power-ups.
        "paddle_shrink": {
            "icon": "S",
            "color": (255, 140, 0),
        },
        "ball_speed_up": {
            "icon": "U",
            "color": (255, 220, 0),
        },
        "ball_speed_down": {
            "icon": "D",
            "color": (160, 100, 255),
        },
    }

    POWER_UP_NAMES = list(POWER_UPS.keys())

    def __init__(self, x: int, y: int, power_type: str) -> None:
        if power_type not in self.POWER_UPS:
            raise ValueError(
                f"Unknown power-up type: {power_type}"
            )

        self.power_type = power_type
        self.icon = self.POWER_UPS[power_type]["icon"]
        self.color = self.POWER_UPS[power_type]["color"]

        self.rect = pygame.Rect(
            x - 15,
            y - 10,
            30,
            20,
        )

        self.speed = 3

    @classmethod
    def create_random(cls, x: int, y: int) -> "PowerUp":
        """Creates a random power-up."""
        power_type = random.choice(cls.POWER_UP_NAMES)
        return cls(x, y, power_type)

    def update(self) -> None:
        """Moves the power-up downward."""
        self.rect.y += self.speed

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the power-up and its icon."""
        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=5,
        )

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            self.rect,
            width=2,
            border_radius=5,
        )

        font = pygame.font.Font(None, 22)
        text = font.render(
            self.icon,
            True,
            (0, 0, 0),
        )

        text_rect = text.get_rect(
            center=self.rect.center
        )

        screen.blit(text, text_rect)

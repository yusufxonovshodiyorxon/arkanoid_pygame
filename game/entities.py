import pygame

import settings as cfg

class Paddle:
    """ Our main player, Paddle, moves only horizontally. """

    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, cfg.PADDLE_WIDTH, cfg.PADDLE_HEIGHT)
        self.rect.midbottom = (cfg.WIDTH // 2, cfg.HEIGHT - 20)
        self.speed = cfg.PADDLE_SPEED
        self.vx = 0
        self.extended = False
        self.laser = False

    def move(self, keys: pygame.key.ScancodeWrapper):
        """ Moves the Paddle if the key is pressed. """
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vx = self.speed
        
        self.rect.x += self.vx

        # Restrict the Paddle's movement
        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT
        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT

    def draw(self, screen: pygame.Surface) -> None:
        """ Renders the Paddle on the screen. """
        pygame.draw.rect(screen, cfg.PADDLE_COLOR, self.rect, border_radius=5)


class Brick:
    """
        Class for Game's brick.

        HP = -1: Level Boundary
        HP = 0: Indestructable
        HP = 1, 2: One / Two hit
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
        """ Renders a Brick in a certain row and col. """
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, cfg.DARK_GRAY, self.rect, 2)
    
    def hit(self) -> None:
        """ Handles the Brick Hit. """
        if self.hp > 0:
            self.hp -= 1
            if self.hp > 0:
                self.color = cfg.BRICK_COLORS[self.hp]
                return
        return


class Ball:
    """ Ball Actor class. """

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
        """ Updates the Ball's position for the each frame. """
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw(self, screen: pygame.surface) -> None:
        """ Renders the Ball. """
        colour = cfg.BALL_COLOR
        pygame.draw.circle(screen, colour, self.rect.center, self.radius)


class Bonus:
    """
        Falling power-up dropped by a destroyed Brick.

        Each bonus has a `kind` (one of cfg.BONUS_TYPES), a unique display
        letter and a color, both looked up from cfg.BONUS_ICONS / cfg.BONUS_COLORS.
        It falls straight down until it's caught by the Paddle (or leaves the
        screen), at which point `ApplyBonus` in the game screen applies its effect.
    """

    _font = None  # Lazily created; needs the pygame display/font module to be init'd

    def __init__(self, x: int, y: int, kind: str) -> None:
        self.kind = kind
        self.letter = cfg.BONUS_ICONS[kind]
        self.color = cfg.BONUS_COLORS[kind]
        self.vy = cfg.BONUS_FALL_SPEED

        size = cfg.BONUS_SIZE
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = (x, y)

        if Bonus._font is None:
            Bonus._font = pygame.font.SysFont("consolas", 18, bold=True)

    def update(self) -> None:
        """ Moves the Bonus down the screen for the current frame. """
        self.rect.y += self.vy

    def draw(self, screen: pygame.Surface) -> None:
        """ Renders the Bonus as a colored badge with its letter. """
        pygame.draw.rect(screen, self.color, self.rect, border_radius=6)
        pygame.draw.rect(screen, cfg.WHITE, self.rect, width=2, border_radius=6)

        label = Bonus._font.render(self.letter, True, cfg.BLACK)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def is_off_screen(self) -> bool:
        """ True once the Bonus has fallen past the bottom of the screen. """
        return self.rect.top > cfg.HEIGHT

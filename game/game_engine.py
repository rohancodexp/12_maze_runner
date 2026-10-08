import pygame
import time

from game.maze import generate_maze, solve, CELL
from game.player import Player


FPS = 60

BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)

COLS, ROWS = 15, 13

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 60


class GameEngine:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Runner")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont(
            "monospace",
            36,
            bold=True
        )

        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)

        self.player = Player(0, 0)

        self.exit_rect = pygame.Rect(
            (COLS - 1) * CELL + 5,
            (ROWS - 1) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        self.start_time = time.time()
        self.elapsed = 0
        self.won = False

        # Task 2: BFS hint state.
        self.show_hint = False
        self.path = []

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                # Generate a new maze.
                if event.key == pygame.K_r:
                    self.reset()

                # Toggle BFS shortest-path hint.
                if event.key == pygame.K_h:
                    self.show_hint = not self.show_hint

                    if self.show_hint:
                        self.update_hint()
                    else:
                        self.path = []

        return True

    def update_hint(self):
        # Convert the player's pixel position into
        # the maze cell containing the player.
        start = (
            self.player.rect.centery // CELL,
            self.player.rect.centerx // CELL
        )

        # Exit is always the bottom-right cell.
        goal = (
            ROWS - 1,
            COLS - 1
        )

        self.path = solve(start, goal)

    def update(self):
        if self.won:
            return

        keys = pygame.key.get_pressed()

        # Existing player movement and Task 1 wall collision.
        self.player.move(
            keys,
            self.walls,
            ROWS,
            COLS
        )

        self.elapsed = time.time() - self.start_time

        # Recalculate the shortest path whenever the
        # player moves while the hint is enabled.
        if self.show_hint:
            self.update_hint()

        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

    def draw_hint(self):
        if not self.path:
            return

        # Semi-transparent cell overlay.
        hint_surface = pygame.Surface(
            (CELL, CELL),
            pygame.SRCALPHA
        )

        hint_surface.fill(
            (255, 220, 50, 100)
        )

        for r, c in self.path:
            self.screen.blit(
                hint_surface,
                (c * CELL, r * CELL)
            )

    def draw_maze(self):
        wall_w = 3

        for r in range(ROWS):
            for c in range(COLS):
                x = c * CELL
                y = r * CELL

                w = self.walls[r][c]

                # North
                if w[0]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x + CELL, y),
                        wall_w
                    )

                # South
                if w[1]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                # East
                if w[2]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                # West
                if w[3]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x, y + CELL),
                        wall_w
                    )

    def draw(self):
        self.screen.fill(BG)

        # Draw the maze first.
        self.draw_maze()

        # Task 2: draw BFS hint over the maze.
        if self.show_hint:
            self.draw_hint()

        # Draw exit.
        pygame.draw.rect(
            self.screen,
            EXIT_COLOR,
            self.exit_rect,
            border_radius=4
        )

        ex_label = self.font.render(
            "EXIT",
            True,
            (20, 80, 20)
        )

        self.screen.blit(
            ex_label,
            (
                self.exit_rect.x + 2,
                self.exit_rect.y + 4
            )
        )

        # Draw player.
        self.player.draw(self.screen)

        # HUD.
        hud = pygame.Rect(
            0,
            ROWS * CELL,
            WIDTH,
            60
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        time_surf = self.font.render(
            f"Time: {self.elapsed:.1f}s   R = New Maze   H = Hint",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            time_surf,
            (
                10,
                ROWS * CELL + 18
            )
        )

        # Win overlay.
        if self.won:
            overlay = pygame.Surface(
                (WIDTH, ROWS * CELL),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 120)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            msg = self.big_font.render(
                f"Solved in {self.elapsed:.1f}s!",
                True,
                (80, 240, 80)
            )

            sub = self.font.render(
                "Press R for a new maze",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                msg,
                (
                    WIDTH // 2 - msg.get_width() // 2,
                    ROWS * CELL // 2 - 30
                )
            )

            self.screen.blit(
                sub,
                (
                    WIDTH // 2 - sub.get_width() // 2,
                    ROWS * CELL // 2 + 20
                )
            )

        pygame.display.flip()

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
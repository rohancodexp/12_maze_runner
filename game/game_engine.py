import pygame
import time

from game.maze import generate_maze, solve, CELL
from game.player import Player
from game.leaderboard import add_score, load_leaderboard


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

        # Task 3: Fog of War.
        # Create the fog surface once and reuse it.
        self.fog = pygame.Surface(
            (WIDTH, ROWS * CELL),
            pygame.SRCALPHA
        )

        # Visibility radius:
        # 3 cells + half a cell.
        self.fog_radius = 3 * CELL + CELL // 2

        self.reset()

    def reset(self):
        # Generate a new maze.
        self.walls = generate_maze(COLS, ROWS)

        # Reset player.
        self.player = Player(0, 0)

        # Exit is always the bottom-right cell.
        self.exit_rect = pygame.Rect(
            (COLS - 1) * CELL + 5,
            (ROWS - 1) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        # Reset timer.
        self.start_time = time.time()
        self.elapsed = 0

        # Reset game state.
        self.won = False

        # Task 2: BFS hint state.
        self.show_hint = False
        self.path = []

        # Task 4: leaderboard state.
        self.current_score = None
        self.leaderboard = load_leaderboard()

        # Task 3: immediately update fog
        # around the newly reset player.
        self.update_fog()

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

    def update_fog(self):
        """Update the Fog of War around the player."""

        # Cover the complete maze area with dark fog.
        self.fog.fill((0, 0, 0, 240))

        # Use the player's current pixel position
        # as the center of the visible region.
        center = self.player.rect.center

        # Create a transparent circular hole around
        # the player.
        pygame.draw.circle(
            self.fog,
            (0, 0, 0, 0),
            center,
            self.fog_radius
        )

    def update(self):
        # Once the player wins, stop updating the run.
        if self.won:
            return

        keys = pygame.key.get_pressed()

        # Existing player movement and Task 1
        # wall collision.
        self.player.move(
            keys,
            self.walls,
            ROWS,
            COLS
        )

        # Task 3: update Fog of War after movement.
        self.update_fog()

        # Update timer.
        self.elapsed = time.time() - self.start_time

        # Task 2: recalculate BFS while hint is active.
        if self.show_hint:
            self.update_hint()

        # Check whether the player reached the exit.
        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

            # Finalize the current run time.
            self.current_score = self.elapsed

            # Add the completed run to the leaderboard.
            # This happens only once because self.won becomes True.
            self.leaderboard = add_score(
                self.current_score
            )

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

        # ----------------------------------------
        # MAZE AREA
        # ----------------------------------------

        # 1. Draw maze.
        self.draw_maze()

        # 2. Draw BFS hint.
        if self.show_hint:
            self.draw_hint()

        # 3. Draw exit.
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

        # 4. Draw player.
        self.player.draw(self.screen)

        # 5. Draw Fog of War.
        # The fog covers only the maze area.
        self.screen.blit(
            self.fog,
            (0, 0)
        )

        # ----------------------------------------
        # HUD
        # ----------------------------------------

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

        # ----------------------------------------
        # WIN SCREEN
        # ----------------------------------------

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

            # Completion message.
            msg = self.big_font.render(
                f"Solved in {self.elapsed:.1f}s!",
                True,
                (80, 240, 80)
            )

            self.screen.blit(
                msg,
                (
                    WIDTH // 2 - msg.get_width() // 2,
                    ROWS * CELL // 2 - 105
                )
            )

            # Restart message.
            sub = self.font.render(
                "Press R for a new maze",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                sub,
                (
                    WIDTH // 2 - sub.get_width() // 2,
                    ROWS * CELL // 2 - 60
                )
            )

            # Leaderboard title.
            leaderboard_title = self.font.render(
                "TOP 5",
                True,
                (240, 220, 80)
            )

            self.screen.blit(
                leaderboard_title,
                (
                    WIDTH // 2
                    - leaderboard_title.get_width() // 2,
                    ROWS * CELL // 2 - 20
                )
            )

            # Leaderboard entries.
            for index, score in enumerate(self.leaderboard):

                # Highlight the current run if it appears
                # in the top five.
                is_current = (
                    self.current_score is not None
                    and abs(score - self.current_score) < 0.000001
                )

                if is_current:
                    entry_color = (80, 240, 80)
                else:
                    entry_color = (200, 200, 200)

                entry = self.font.render(
                    f"{index + 1}. {score:.2f}s",
                    True,
                    entry_color
                )

                self.screen.blit(
                    entry,
                    (
                        WIDTH // 2
                        - entry.get_width() // 2,
                        ROWS * CELL // 2
                        + 10
                        + index * 28
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
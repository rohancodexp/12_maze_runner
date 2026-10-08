import pygame
import time

from game.maze import generate_maze, solve, CELL
from game.player import Player
from game.leaderboard import add_score, load_leaderboard


FPS = 60
HUD_HEIGHT = 60

BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)

# Default menu/window size.
MENU_COLS = 15
MENU_ROWS = 13

# Difficulty configuration.
DIFFICULTIES = {
    "Easy": (10, 8),
    "Medium": (15, 13),
    "Hard": (20, 18),
}


class GameEngine:
    MENU = "MENU"
    PLAYING = "PLAYING"
    WON = "WON"

    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "monospace",
            22
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            36,
            bold=True
        )

        self.title_font = pygame.font.SysFont(
            "monospace",
            48,
            bold=True
        )

        self.screen = pygame.display.set_mode(
            (
                MENU_COLS * CELL,
                MENU_ROWS * CELL + HUD_HEIGHT
            )
        )

        pygame.display.set_caption("Maze Runner")

        # ----------------------------------------
        # GAME STATE
        # ----------------------------------------

        self.state = self.MENU

        self.difficulty = None

        self.cols = MENU_COLS
        self.rows = MENU_ROWS

        self.width = self.cols * CELL
        self.height = self.rows * CELL + HUD_HEIGHT

        # ----------------------------------------
        # GAME DATA
        # ----------------------------------------

        self.walls = None
        self.player = None
        self.exit_rect = None

        # Timer.
        self.start_time = 0
        self.elapsed = 0

        # Win state.
        self.won = False

        # BFS hint.
        self.show_hint = False
        self.path = []

        # Leaderboard.
        self.current_score = None
        self.leaderboard = load_leaderboard()

        # Fog.
        self.fog = None
        self.fog_radius = 3 * CELL + CELL // 2

        # Menu button hover state.
        self.hovered_difficulty = None

    # =========================================================
    # WINDOW / DIFFICULTY
    # =========================================================

    def resize_window(self):
        """Resize the Pygame window for the current maze size."""

        self.width = self.cols * CELL
        self.height = self.rows * CELL + HUD_HEIGHT

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

    def select_difficulty(self, difficulty):
        """Start a new game using the selected difficulty."""

        self.difficulty = difficulty

        self.cols, self.rows = DIFFICULTIES[difficulty]

        self.resize_window()

        self.reset()

    # =========================================================
    # RESET / GAME INITIALIZATION
    # =========================================================

    def reset(self):
        """Generate a fresh maze for the current difficulty."""

        if self.difficulty is None:
            return

        # Generate maze using the selected dimensions.
        self.walls = generate_maze(
            self.cols,
            self.rows
        )

        # Player starts in the top-left cell.
        self.player = Player(0, 0)

        # Exit is always in the bottom-right cell.
        self.exit_rect = pygame.Rect(
            (self.cols - 1) * CELL + 5,
            (self.rows - 1) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        # ----------------------------------------
        # TIMER
        # ----------------------------------------

        self.start_time = time.time()
        self.elapsed = 0

        # ----------------------------------------
        # GAME STATE
        # ----------------------------------------

        self.state = self.PLAYING
        self.won = False

        # ----------------------------------------
        # BFS
        # ----------------------------------------

        self.show_hint = False
        self.path = []

        # ----------------------------------------
        # LEADERBOARD
        # ----------------------------------------

        self.current_score = None
        self.leaderboard = load_leaderboard()

        # ----------------------------------------
        # FOG
        # ----------------------------------------

        # Recreate the fog surface for the selected
        # maze dimensions.
        self.fog = pygame.Surface(
            (
                self.cols * CELL,
                self.rows * CELL
            ),
            pygame.SRCALPHA
        )

        self.update_fog()

    # =========================================================
    # RETURN TO MENU
    # =========================================================

    def return_to_menu(self):
        """Return to the difficulty-selection menu."""

        self.state = self.MENU

        self.difficulty = None

        self.walls = None
        self.player = None
        self.exit_rect = None

        self.show_hint = False
        self.path = []

        self.won = False
        self.current_score = None

        self.hovered_difficulty = None

        # Return to the default menu window size.
        self.cols = MENU_COLS
        self.rows = MENU_ROWS

        self.resize_window()

    # =========================================================
    # MENU
    # =========================================================

    def get_menu_buttons(self):
        """Return the difficulty button rectangles."""

        button_width = 280
        button_height = 60
        gap = 20

        total_height = (
            3 * button_height
            + 2 * gap
        )

        start_y = (
            self.height // 2
            - total_height // 2
            + 45
        )

        x = (
            self.width // 2
            - button_width // 2
        )

        buttons = {}

        for index, difficulty in enumerate(DIFFICULTIES):
            y = start_y + index * (
                button_height + gap
            )

            buttons[difficulty] = pygame.Rect(
                x,
                y,
                button_width,
                button_height
            )

        return buttons

    def handle_menu_event(self, event):
        """Handle mouse interaction with the menu."""

        if event.type == pygame.MOUSEMOTION:
            buttons = self.get_menu_buttons()

            self.hovered_difficulty = None

            for difficulty, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    self.hovered_difficulty = difficulty
                    break

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                return

            buttons = self.get_menu_buttons()

            for difficulty, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    self.select_difficulty(
                        difficulty
                    )
                    return

    def draw_menu(self):
        """Draw the difficulty-selection menu."""

        self.screen.fill(BG)

        title = self.title_font.render(
            "MAZE RUNNER",
            True,
            (40, 40, 60)
        )

        self.screen.blit(
            title,
            (
                self.width // 2
                - title.get_width() // 2,
                80
            )
        )

        subtitle = self.font.render(
            "Choose Difficulty",
            True,
            (70, 70, 80)
        )

        self.screen.blit(
            subtitle,
            (
                self.width // 2
                - subtitle.get_width() // 2,
                150
            )
        )

        buttons = self.get_menu_buttons()

        for difficulty, rect in buttons.items():

            if difficulty == self.hovered_difficulty:
                button_color = (80, 120, 200)
                text_color = (255, 255, 255)
            else:
                button_color = (60, 70, 100)
                text_color = (230, 230, 230)

            pygame.draw.rect(
                self.screen,
                button_color,
                rect,
                border_radius=8
            )

            label = self.font.render(
                difficulty,
                True,
                text_color
            )

            self.screen.blit(
                label,
                (
                    rect.centerx
                    - label.get_width() // 2,
                    rect.centery
                    - label.get_height() // 2
                )
            )

            cols, rows = DIFFICULTIES[difficulty]

            size_label = self.font.render(
                f"{cols} x {rows}",
                True,
                text_color
            )

            self.screen.blit(
                size_label,
                (
                    rect.right
                    - size_label.get_width()
                    - 15,
                    rect.centery
                    - size_label.get_height() // 2
                )
            )

        pygame.display.flip()

    # =========================================================
    # EVENTS
    # =========================================================

    def handle_events(self):
        """Handle events based on the current game state."""

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            # ----------------------------------------
            # MENU
            # ----------------------------------------

            if self.state == self.MENU:
                self.handle_menu_event(event)

            # ----------------------------------------
            # PLAYING
            # ----------------------------------------

            elif self.state == self.PLAYING:

                if event.type == pygame.KEYDOWN:

                    # R = regenerate current difficulty.
                    if event.key == pygame.K_r:
                        self.reset()

                    # H = toggle BFS hint.
                    elif event.key == pygame.K_h:
                        self.show_hint = not self.show_hint

                        if self.show_hint:
                            self.update_hint()
                        else:
                            self.path = []

                    # ESC = return to menu.
                    elif event.key == pygame.K_ESCAPE:
                        self.return_to_menu()

            # ----------------------------------------
            # WON
            # ----------------------------------------

            elif self.state == self.WON:

                if event.type == pygame.KEYDOWN:

                    # R = replay same difficulty.
                    if event.key == pygame.K_r:
                        self.reset()

                    # ESC = return to menu.
                    elif event.key == pygame.K_ESCAPE:
                        self.return_to_menu()

        return True

    # =========================================================
    # BFS
    # =========================================================

    def update_hint(self):
        """Recalculate BFS from the player's current cell."""

        if self.player is None:
            self.path = []
            return

        start = (
            self.player.rect.centery // CELL,
            self.player.rect.centerx // CELL
        )

        goal = (
            self.rows - 1,
            self.cols - 1
        )

        self.path = solve(
            start,
            goal
        )

    # =========================================================
    # FOG OF WAR
    # =========================================================

    def update_fog(self):
        """Update the Fog of War around the player."""

        if self.fog is None or self.player is None:
            return

        # Cover the entire maze area.
        self.fog.fill(
            (0, 0, 0, 240)
        )

        # Player's current pixel position.
        center = self.player.rect.center

        # Transparent visibility circle.
        pygame.draw.circle(
            self.fog,
            (0, 0, 0, 0),
            center,
            self.fog_radius
        )

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self):
        """Update gameplay only while in PLAYING state."""

        if self.state != self.PLAYING:
            return

        keys = pygame.key.get_pressed()

        # Existing player movement and Task 1
        # wall collision.
        self.player.move(
            keys,
            self.walls,
            self.rows,
            self.cols
        )

        # Update fog after player movement.
        self.update_fog()

        # Update timer.
        self.elapsed = (
            time.time()
            - self.start_time
        )

        # Recalculate BFS if enabled.
        if self.show_hint:
            self.update_hint()

        # Check exit collision.
        if self.player.rect.colliderect(
            self.exit_rect
        ):
            self.won = True

            # Finalize current score.
            self.current_score = self.elapsed

            # Persist leaderboard.
            self.leaderboard = add_score(
                self.current_score
            )

            # Enter WON state.
            self.state = self.WON

    # =========================================================
    # DRAW MAZE
    # =========================================================

    def draw_maze(self):
        """Draw the maze using the current dimensions."""

        wall_w = 3

        for r in range(self.rows):
            for c in range(self.cols):

                x = c * CELL
                y = r * CELL

                walls = self.walls[r][c]

                # North
                if walls[0]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x + CELL, y),
                        wall_w
                    )

                # South
                if walls[1]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                # East
                if walls[2]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                # West
                if walls[3]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x, y + CELL),
                        wall_w
                    )

    # =========================================================
    # DRAW BFS HINT
    # =========================================================

    def draw_hint(self):
        """Draw the current BFS path."""

        if not self.path:
            return

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
                (
                    c * CELL,
                    r * CELL
                )
            )

    # =========================================================
    # DRAW GAME
    # =========================================================

    def draw_game(self):
        """Draw PLAYING/WON game screen."""

        self.screen.fill(BG)

        # ----------------------------------------
        # MAZE
        # ----------------------------------------

        self.draw_maze()

        # ----------------------------------------
        # BFS
        # ----------------------------------------

        if self.show_hint:
            self.draw_hint()

        # ----------------------------------------
        # EXIT
        # ----------------------------------------

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

        # ----------------------------------------
        # PLAYER
        # ----------------------------------------

        self.player.draw(
            self.screen
        )

        # ----------------------------------------
        # FOG
        # ----------------------------------------

        if self.fog is not None:
            self.screen.blit(
                self.fog,
                (0, 0)
            )

        # ----------------------------------------
        # HUD
        # ----------------------------------------

        hud = pygame.Rect(
            0,
            self.rows * CELL,
            self.width,
            HUD_HEIGHT
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        time_surf = self.font.render(
            (
                f"Time: {self.elapsed:.1f}s   "
                "R = New Maze   "
                "H = Hint   "
                "ESC = Menu"
            ),
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            time_surf,
            (
                10,
                self.rows * CELL + 18
            )
        )

        # ----------------------------------------
        # WIN OVERLAY
        # ----------------------------------------

        if self.state == self.WON:
            self.draw_win_overlay()

        pygame.display.flip()

    # =========================================================
    # WIN SCREEN
    # =========================================================

    def draw_win_overlay(self):
        """Draw the completion and leaderboard overlay."""

        overlay = pygame.Surface(
            (
                self.width,
                self.rows * CELL
            ),
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
                self.width // 2
                - msg.get_width() // 2,
                45
            )
        )

        # Controls.
        sub = self.font.render(
            "R = Replay   ESC = Menu",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            sub,
            (
                self.width // 2
                - sub.get_width() // 2,
                90
            )
        )

        # Difficulty label.
        difficulty_label = self.font.render(
            f"Difficulty: {self.difficulty}",
            True,
            (220, 220, 220)
        )

        self.screen.blit(
            difficulty_label,
            (
                self.width // 2
                - difficulty_label.get_width() // 2,
                125
            )
        )

        # Leaderboard title.
        title = self.font.render(
            "TOP 5",
            True,
            (240, 220, 80)
        )

        self.screen.blit(
            title,
            (
                self.width // 2
                - title.get_width() // 2,
                165
            )
        )

        # Leaderboard entries.
        for index, score in enumerate(
            self.leaderboard
        ):

            is_current = (
                self.current_score is not None
                and abs(
                    score - self.current_score
                ) < 0.000001
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
                    self.width // 2
                    - entry.get_width() // 2,
                    200 + index * 30
                )
            )

    # =========================================================
    # MAIN DRAW
    # =========================================================

    def draw(self):
        """Draw the correct screen for the current state."""

        if self.state == self.MENU:
            self.draw_menu()

        elif self.state in (
            self.PLAYING,
            self.WON
        ):
            self.draw_game()

    # =========================================================
    # MAIN LOOP
    # =========================================================

    def run(self):
        running = True

        while running:
            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()
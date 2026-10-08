import pygame
from game.maze import CELL

SPEED = 3

class Player:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        x = c*CELL + CELL//2
        y = r*CELL + CELL//2
        self.rect = pygame.Rect(x-10, y-10, 20, 20)
        self.color = (60,120,220)

    def move(self, keys, walls, rows, cols):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = SPEED

        # Wall-aware movement (check cell boundaries)
        new_rect = self.rect.move(dx, 0)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect
        new_rect = self.rect.move(0, dy)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

    def _hits_wall(self, rect, walls, rows, cols):
        # Keep the player inside the maze boundaries.
        if rect.left < 0 or rect.top < 0:
            return True
        if rect.right > cols * CELL or rect.bottom > rows * CELL:
            return True

        # Check the cells touched by the player's rectangle.
        left = rect.left // CELL
        right = (rect.right - 1) // CELL
        top = rect.top // CELL
        bottom = (rect.bottom - 1) // CELL

        # Check vertical movement across north/south walls.
        for r in range(top, bottom + 1):
            for c in range(left, right + 1):
                if r > 0 and rect.top < r * CELL and walls[r][c][0]:
                    return True
                if r < rows - 1 and rect.bottom > (r + 1) * CELL and walls[r][c][1]:
                    return True

        # Check horizontal movement across west/east walls.
        for r in range(top, bottom + 1):
            for c in range(left, right + 1):
                if c > 0 and rect.left < c * CELL and walls[r][c][3]:
                    return True
                if c < cols - 1 and rect.right > (c + 1) * CELL and walls[r][c][2]:
                    return True

        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)

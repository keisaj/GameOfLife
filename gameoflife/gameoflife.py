import random
import sys
import pygame
import numpy as np
from pygame.locals import *


class LifeGame:

    def __init__(self, screen_width=800, screen_height=600, cell_size=10, alive_color=(0, 200, 100),
                 dead_color=(0, 0, 0), max_fps=10):
        """
        Initialize grid, set default game state, initialize screen

        :param screen_width: Game window width
        :param screen_height: Game window height
        :param cell_size: Diameter of circles
        :param alive_color: RGB tuple e.g. (255, 255, 255) for cells
        :param dead_color: RGB tuple e.g. (255, 255, 255)
        :param max_fps: Framerate cap to limit game speed
        """
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.alive_color = alive_color
        self.dead_color = dead_color
        self.max_fps = max_fps

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clear_screen()
        pygame.display.flip()

        self.last_update_completed = 0
        self.desired_milliseconds_between_updates = (1.0 / self.max_fps) * 1000.0

        self.active_grid = 0
        self.grids = []
        self.num_cols = int(self.screen_width / self.cell_size)
        self.num_rows = int(self.screen_height / self.cell_size)
        self.init_grids()
        self.paused = False
        self.game_over = False

        self.drawing = False
        self.mouse_position = (0, 0)
        self.last_pos = None
        self.erasing = False
        self.left = 1
        self.right = 3

    def init_grids(self):
        """
        Create the default active and inactive grid

        :return: None
        """
        self.grids.append(self.create_grid())
        self.grids.append(self.create_grid())
        self.set_grid()

    def create_grid(self):
        """
        Generate array of zeros

        :return:
        """
        return np.zeros(self.num_cols * self.num_rows).reshape(self.num_cols, self.num_rows)

    def set_grid(self, value=None, grid=0):
        """
        Examples:
            set_grid(0) # all dead
            set_grid(1) # all alive
            set_grid() # random
            sset_grid(None) # random

        :param grid: Index of grid, for active/inactive (0 or 1)
        :param value: Celue to set the cell to (0 or 1)
        :return:
        """

        for c in range(self.num_cols):
            for r in range(self.num_rows):
                if value is None:
                    cell_value = random.randint(0, 1)
                else:
                    cell_value = value
                self.grids[grid][c][r] = cell_value

    def clear_screen(self):
        """
        Fill whole screen with dead color

        :return:
        """
        self.screen.fill(self.dead_color)

    def get_cell(self, column_number, row_number):
        """
        Get the alive/dead (0/1) state of a specific cell in active grid

        :param column_number:
        :param row_number:
        :return: 0 or 1 depending on state of cell. Defaults to 0 (dead)
        """
        try:
            cell_value = self.grids[self.active_grid][column_number][row_number]
        except:
            cell_value = 0
        return cell_value

    def check_cell_neighbors(self, col_index, row_index):
        """
        Get the number of alive neighbor cells and determine the state of the cell
        for the next generation. Determine whether, dies, survives or is born.

        :param col_index: Column number of cell to check
        :param row_index: Row number of cell to check
        :return: The state the cell should be in next generation (0 or 1)
        """
        # Get the number of alive cells surrounding current cell
        num_alive_neighbors = 0
        for i in range(-1, 2):  # Edges are wrapped around
            for j in range(-1, 2):
                col = (col_index + i + self.num_cols) % self.num_cols
                row = (row_index + j + self.num_rows) % self.num_rows
                num_alive_neighbors += self.get_cell(col, row)

        num_alive_neighbors -= self.get_cell(col_index, row_index)

        # Rule for life and death
        if self.grids[self.active_grid][col_index][row_index] == 1:  # alive
            if num_alive_neighbors > 3:  # Overpopulation
                return 0
            if num_alive_neighbors < 2:  # Underpopulation
                return 0
            if num_alive_neighbors == 2 or num_alive_neighbors == 3:
                return 1
            else:
                return 0
        elif self.grids[self.active_grid][col_index][row_index] == 0:  # dead
            if num_alive_neighbors == 3:
                return 1  # come to life

        return self.grids[self.active_grid][col_index][row_index]

    def update_generation(self):
        """
        Checks neighbors for each cell and updates them by switching grids.

        :return:
        """
        # Inspect the current active generation
        self.set_grid(0, self.inactive_grid())
        for c in range(self.num_cols):
            for r in range(self.num_rows):
                next_gen_state = self.check_cell_neighbors(c, r)
                # Set inactive grid future cell state
                self.grids[self.inactive_grid()][c][r] = next_gen_state
        self.active_grid = self.inactive_grid()

    def inactive_grid(self):
        """
        Simple helper function to get the index of the inactive grid grid
        If active grid is 0 will return 1 and vice-versa

        :return:
        """
        return (self.active_grid + 1) % 2

    def draw_grid(self):
        """
        Given the grid and cell states, draw the cells on the screen

        :return:
        """
        self.clear_screen()
        for c in range(self.num_cols):
            for r in range(self.num_rows):
                if self.grids[self.active_grid][c][r] == 1:
                    color = self.alive_color
                    # R = random.randint(1, 255)
                    # G = random.randint(1, 255)
                    # B = random.randint(1, 255)
                    # color = (R, G, B)
                else:
                    color = self.dead_color
                # pygame.draw.circle(self.screen,
                #                    color,
                #                    (int(c * self.cell_size + (self.cell_size / 2)),
                #                     int(r * self.cell_size + (self.cell_size / 2))),
                #                    int(self.cell_size / 2),
                #                    0)

                pygame.draw.rect(self.screen,
                                 color,
                                 (c * self.cell_size, r * self.cell_size, self.cell_size-2, self.cell_size-2),
                                 )

        pygame.display.flip()

    def handle_events(self):
        """
        Handle any keypresses
        s - start/stp (pause) the game
        q - quit
        r - randomize grid
        c - clears the board

        Handles mouse events, allowing to draw with while mouse button left is down
        and erases when mouse button right is down.
        In order to draw pausing is needed.

        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # print("key pressed")
                if event.unicode == 's':  # if event is keypress of "s" then toggle pause game
                    # print("Togglin pause.")
                    if self.paused:
                        self.paused = False
                        print("Game unpaused.")
                    else:
                        self.paused = True
                        print("Game paused.")
                elif event.unicode == 'r':  # if event is keypress of "r" then randomize grid
                    print("Randomizind grid.")
                    self.active_grid = 0
                    self.set_grid(None, self.active_grid)  # randomize
                    self.set_grid(0, self.inactive_grid())  # set to 0
                    self.draw_grid()
                elif event.unicode == 'q':  # if event is keypress of "q" the quit
                    print("Exiting.")
                    self.game_over = True
                elif event.unicode == 'c':  # clears board
                    print("Clearing grid.")
                    self.set_grid(0, self.active_grid)  # set to 0
                    self.set_grid(0, self.inactive_grid())  # set to 0
                    self.draw_grid()

            if event.type == MOUSEMOTION:
                if not self.erasing:
                    self.draw_with_mouse()
                if self.erasing:
                    self.draw_with_mouse(erase=True)
            elif event.type == MOUSEBUTTONUP:
                self.mouse_position = (0, 0)
                self.drawing = False
                self.erasing = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == self.left:
                    self.drawing = True
                    self.draw_with_mouse()
                if event.button == self.right:  # if right mouse button is on mouse goes in erasing mode
                    self.erasing = True
                    self.drawing = True
                    self.draw_with_mouse(erase=True)

            if event.type == pygame.QUIT:
                sys.exit()

    def draw_with_mouse(self, erase=False):
        """
        While in paused mode, changing values of cells according to the mouse position
        If erase is True, it allows to erase alive cells.

        :return:
        """
        c = 1
        if erase:
            c = 0
        if self.drawing:
            self.mouse_position = pygame.mouse.get_pos()
            if self.last_pos is not None:
                self.grids[self.active_grid][int(self.mouse_position[0] / self.cell_size)][
                    int(self.mouse_position[1] / self.cell_size)] = c
                self.draw_grid()
            self.last_pos = self.mouse_position

    def run(self):
        """
        Kick off the game and loop forever until quit state

        :return:
        """
        while True:
            if self.game_over:
                return
            self.handle_events()
            if self.paused:
                continue
            self.update_generation()
            self.draw_grid()
            self.cap_frame_rate()

    def cap_frame_rate(self):
        """
        If game is running too fast and updating frames to frequently,
        just wait to maintain stable framerate

        :return:
        """
        # cap framerate at 60fps if time since the last frame draw < 1/60th of a second, sleep for remaining time
        now = pygame.time.get_ticks()
        milliseconds_since_last_update = now - self.last_update_completed
        time_to_sleep = self.desired_milliseconds_between_updates - milliseconds_since_last_update
        if time_to_sleep > 0:
            pygame.time.delay(int(time_to_sleep))
        self.last_update_completed = now


if __name__ == '__main__':
    """
    Lunch a game of life
    """
    game = LifeGame(screen_height=1000, screen_width=1200)
    game.run()

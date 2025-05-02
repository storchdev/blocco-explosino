import cv2
import numpy as np
from PIL import ImageGrab, Image
import sys
from block import Block
from itertools import permutations


class Grid:
    def __init__(self, grid):
        self.grid = grid
        self.length = len(self.grid)
    
    def __str__(self):
        lines = []
        for i in range(self.length):
            lines.append(''.join(str(b) for b in self.grid[i]))
        return '\n'.join(lines)

    @classmethod
    def empty(cls):
        return cls([[0 for _ in range(8)] for _ in range(8)])
    
    def copy(self):
        return Grid(self.grid)

    def possible_moves(self, block):
        for i in range(self.length - block.w + 1):
            for j in range(self.length - block.h + 1):
                ok = True
                for x, y in block.coords:
                    if self.grid[i+x][j+y] == 1:
                        ok = False
                        break
                if ok:
                    yield (i, j)

    def apply_move(self, block, ij):
        i, j = ij
        for x, y in block.coords:
            if self.grid[i+x][j+y] == 1:
                raise RuntimeError("not a valid move")
            self.grid[i+x][j+y] = 1

        # scan for vertical or horizontal runs

        for i in range(self.length):
            if all(cell == 1 for cell in self.grid[i]):
                for j in self.grid[i]:
                    self.grid[i][j] = 0

        for j in range(self.length):
            if all(row[j] == 1 for row in self.grid):
                for row in self.grid:
                    row[j] = 0

    def get_best_moves(self, ss, s):
        onebyone = Image.open('onebyone-filtered.png').convert('RGB')
        # onebyone = onebyone.resize((s, s))

        onebyone.show()
        onebyone = cv2.cvtColor(np.array(onebyone), cv2.COLOR_RGB2GRAY)
        # _, onebyone = cv2.threshold(onebyone, )

        # sharpening convolution
        sharpen_kernel = np.array([
            [ 0, -1,  0],
            [-1,  5, -1],
            [ 0, -1,  0]
        ])

        ss = cv2.filter2D(ss, -1, sharpen_kernel)
        cv2.imshow("a",ss)
        cv2.waitKey(0)
        _, ss = cv2.threshold(ss, 60, 255, cv2.THRESH_BINARY_INV)
        cv2.imshow("a",ss)
        cv2.waitKey(0)

        cv2.imwrite('test.png', ss)

        #read height and width of template image    
        h, w = onebyone.shape[0], onebyone.shape[1]

        if s is None:
            s = w
        
        print(f's={s}')

        res = cv2.matchTemplate(ss,onebyone,cv2.TM_CCOEFF_NORMED)
        threshold = 0.5
        loc = np.where(res >= threshold)

        # if len(loc) < 4:
        #     print("Not enough blocks detected in screenshot.")
        #     sys.exit(1)

        coords = [(int(a), int(b)) for a, b in zip(*loc[::-1])]
        print(coords)

        blocks = []

        thresh = (s * 1.2) ** 2

        while len(coords) > 0:
            # start current block with an arbitrary coord
            block = [coords.pop()]

            # find all coords with a distance less than thresh to add to current block
            for c1x, c1y in block:
                i = 0
                while i < len(coords):
                    c2x, c2y = coords[i]
                    if (c2x - c1x) ** 2 + (c2y - c1y) ** 2 < thresh:
                        block.append(coords.pop(i))
                    else:
                        i += 1

            blocks.append(Block.from_raw_coords(block, s))

        print(blocks)
        # brute force search 

        lowest_perimeter = float('inf')
        lowest_moves = []
        lowest_grid = None

        grid = self.grid

        for b0, b1, b2 in permutations(blocks):
            gridcpy = grid.copy()
            for move0 in grid.possible_moves(b0):
                for move1 in grid.possible_moves(b1):
                    for move2 in grid.possible_moves(b2):
                        gridcpy.apply_move(b0, move0)
                        gridcpy.apply_move(b1, move1)
                        gridcpy.apply_move(b2, move2)

                        p = gridcpy.get_perimeter()
                        if p < lowest_perimeter:
                            lowest_perimeter = p
                            lowest_moves = [
                                (b0, move0),
                                (b1, move1),
                                (b2, move2)
                            ]
                            # lowest_grid = gridcpy

        # return lowest_grid, lowest_moves
        return lowest_moves

    def display_moves(self, moves):
        ascii_grid = ['.'] * (self.length**2)
        for i in range(self.length):
            for j in range(self.length):
                if self.grid[i][j] == 1:
                    ascii_grid[i][j] = '+'
        
        for b, i, j in moves:
            for x, y in b.coords:
                ascii_grid[i+x][j+y] = '@'
        
        return ascii_grid

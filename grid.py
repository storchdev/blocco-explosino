import cv2
import numpy as np
from PIL import ImageGrab, Image
import sys
from block import Block
from itertools import permutations
from copy import deepcopy


def compute_iou(box1, box2):
    """computes IoU between two boxes"""
    x1, y1, x2, y2 = box1
    x1b, y1b, x2b, y2b = box2

    xi1 = max(x1, x1b)
    yi1 = max(y1, y1b)
    xi2 = min(x2, x2b)
    yi2 = min(y2, y2b)

    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2b - x1b) * (y2b - y1b)
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area != 0 else 0


def non_max_suppression(boxes, scores, iou_thresh=0.8):
    """performs non-maximum suppression"""
    idxs = np.argsort(scores)[::-1]
    keep = []

    while len(idxs) > 0:
        current = idxs[0]
        keep.append(current)
        remove = []

        for i in idxs[1:]:
            iou = compute_iou(boxes[current], boxes[i])
            if iou > iou_thresh:
                remove.append(i)

        idxs = np.array([i for i in idxs[1:] if i not in remove])

    return [boxes[i] for i in keep]


class Grid:
    def __init__(self, grid):
        self.grid = grid
        self.length = len(self.grid)
    
    def __str__(self):
        """binary string representation"""

        mapping = ['.', 'o']
        ascii_grid = ['.'] * (self.length ** 2)

        for i in range(self.length):
            for j in range(self.length):
                ascii_grid[j*self.length + i] = mapping[self.grid[i][j]]

        string = []
        for i, char in enumerate(ascii_grid):
            if i > 0 and i % self.length == 0:
                string.append('\n')
            string.append(char)
        return ''.join(string)

    @classmethod
    def empty(cls):
        return cls([[0 for _ in range(8)] for _ in range(8)])
    
    def copy(self):
        """deepcopy of grid including matrix and subarrays"""

        return Grid(deepcopy(self.grid))

    def possible_moves(self, block):
        """returns list of possible moves for a given block"""
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
        """applies a move, while altering the current grid"""
        i, j = ij
        for x, y in block.coords:
            if self.grid[i+x][j+y] == 1:
                raise RuntimeError("not a valid move")
            self.grid[i+x][j+y] = 1

        # scan for vertical or horizontal runs

        for i in range(self.length):
            if all(cell == 1 for cell in self.grid[i]):
                for j in range(self.length):
                    self.grid[i][j] = 0

        for j in range(self.length):
            if all(row[j] == 1 for row in self.grid):
                for row in self.grid:
                    row[j] = 0
        
    def get_perimeter(self):
        """returns the total perimeter of the stuff inside the grid (not including grid edges)"""
        perimeter = 0

        # Directions: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for i in range(self.length):
            for j in range(self.length):
                if self.grid[i][j] == 1:
                    # Check 4 neighboring cells
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        # If neighbor is out of bounds or is 0, count the edge
                        if ni < 0 or ni >= self.length or  nj < 0 or nj >= self.length or self.grid[ni][nj] == 0:
                            perimeter += 1

        return perimeter

    def get_best_moves(self, ss, s, *, output_progress=True):
        """dumb cv2 template matching + brute force perimeter optimizing"""

        onebyone = Image.open('onebyone-16x.png').convert('RGB')
        onebyone = cv2.cvtColor(np.array(onebyone), cv2.COLOR_RGB2GRAY)

        #read height and width of template image    
        h, w = onebyone.shape[0], onebyone.shape[1]

        if s is None:
            s = w
        
        # print(f's={s}')

        result = cv2.matchTemplate(ss,onebyone,cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))

        boxes = [(x, y, x + w, y + h) for (x, y) in locations]
        scores = [result[y, x] for (x, y) in locations]

        # mns
        filtered_boxes = non_max_suppression(boxes, scores, iou_thresh=0.5)

        # draw rectangles
        for (x1, y1, x2, y2) in filtered_boxes:
            cv2.rectangle(ss, (x1, y1), (x2, y2), (255, 0, 0), 1) 

        cv2.imwrite('vision.png', ss)

        if len(filtered_boxes) < 3:
            print('Not enough squares detected in screenshot.')
            sys.exit(1)

        coords = [(x1, y1) for (x1, y1, _, _) in filtered_boxes]
        blocks = []
        thresh = (s * 1.7) ** 2

        while coords:
            start = coords.pop()
            block = [start]
            queue = [start]

            while queue:
                c1x, c1y = queue.pop()
                i = 0
                while i < len(coords):
                    c2x, c2y = coords[i]
                    if (c2x - c1x) ** 2 + (c2y - c1y) ** 2 < thresh:
                        neighbor = coords.pop(i)
                        block.append(neighbor)
                        queue.append(neighbor)
                    else:
                        i += 1

            blocks.append(Block.from_raw_coords(block, s))

        if len(blocks) != 3:
            print('There must be exactly 3 blocks detected in screenshot. Check vision.png to see what the computer saw.')
            sys.exit(1)

        print(f'{len(filtered_boxes)} squares, {len(blocks)} blocks detected')
        # print('\n'.join(str(b) for b in blocks))

        # brute force search 
        lowest_perimeter = float('inf')
        lowest_moves = []

        # grid = self.grid
        progress = 0

        for b0, b1, b2 in permutations(blocks):
            for move0 in self.possible_moves(b0):
                grid1 = self.copy()
                grid1.apply_move(b0, move0)

                for move1 in grid1.possible_moves(b1):
                    grid2 = grid1.copy()
                    grid2.apply_move(b1, move1)

                    for move2 in grid2.possible_moves(b2):
                        grid3 = grid2.copy()
                        grid3.apply_move(b2, move2)

                        p = grid3.get_perimeter()
                        
                        if output_progress:
                            print(f'Simulated {progress} moves...\r', end="")
                            progress += 1

                        if p < lowest_perimeter:
                            lowest_perimeter = p
                            lowest_moves = [
                                (b0, move0),
                                (b1, move1),
                                (b2, move2)
                            ]
                            # lowest_grid = grid3
        if output_progress:
            print()
        # return lowest_grid, lowest_moves
        return lowest_moves

    def display_move(self, block, ij):
        """returns an ascii string highlighting the block if it were placed at a position"""

        ascii_grid = ['.'] * (self.length**2)
        # use transposed coordinates (swap i and j) for ascii_grid

        for i in range(self.length):
            for j in range(self.length):
                if self.grid[i][j] == 1:
                    ascii_grid[j*self.length + i] = 'o'
        
        for x, y in block.coords:
            ascii_grid[(ij[0]+x) + (ij[1]+y)*self.length] = '@'
        
        string = []
        for i, char in enumerate(ascii_grid):
            if i > 0 and i % self.length == 0:
                string.append('\n')
            string.append(char)
        return ''.join(string)

import pyautogui
import numpy as np
import cv2
import sys

from grid import Grid


with open('calibration.txt') as f:
    try:
        corner1, corner2, s = f.read().split('\n', 2)

        x, y = map(int, corner1.split())
        x1, y1 = map(int, corner2.split())
        s = int(s)
    except:
        print("Loading calibration settings failed. Try running the calibration script.")
        sys.exit(1)

with open('grid.txt') as f:
    bits = [int(c) for c in f.read() if c == '0' or c == '1']
    if len(bits) != 64:
        grid = Grid.empty()
    else:
        raw_matrix = [bits[i:i+8] for i in range(0, 64, 8)]  
        # transpose, so that i = x-axis and j = y-axis
        grid = Grid([[raw_matrix[j][i] for j in range(8)] for i in range(8)])

while True:
    print('--- PRESS ENTER FOR NEXT ROUND, S TO SAVE ---')
    cmd = input()

    if cmd.lower() in ['s', 'save']:
        with open('grid.txt', 'w') as f:
            f.write(str(grid))
        sys.exit(0)


    ss = cv2.cvtColor(np.array(pyautogui.screenshot(region=(x, y, x1 - x, y1 - y))), cv2.COLOR_RGB2GRAY)
    moves = grid.get_best_moves(ss, s)

    for block, move in moves:
        # print(block)
        # print(move)
        # print('---')
        grid.apply_move(block, move)
        print(grid.display_move(block, move))
        print()
    
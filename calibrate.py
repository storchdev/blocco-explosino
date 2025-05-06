import pyautogui
import time


print("""----------
DIRECTIONS:
1. After pressing the enter key, you will have 5 seconds to move your mouse to the TOP LEFT CORNER OF THE SCREENSHOT AREA.
2. After pressing the enter key again, you will have 5 seconds to move your mouse to the BOTTOM RIGHT CORNER OF THE SCREENSHOT AREA.
3. After pressing the enter key again, you will have 5 seconds to move your mouse to the LEFT SIDE OF ANY 1x1 BLOCK INSIDE THE SCREENSHOT AREA.
4. After pressing the enter key again, you will have 5 seconds to move your mouse to the LEFT SIDE OF ANY 1x1 BLOCK INSIDE THE SCREENSHOT AREA.
----------""")
input()
print("Move your mouse to the TOP LEFT CORNER!")
time.sleep(5)
p1 = pyautogui.position()
print(f"First corner at: {p1}")

input()
print("Move your mouse to the BOTTOM RIGHT CORNER!")
time.sleep(5)
p2 = pyautogui.position()
print(f"Second corner at: {p2}")

# input()
# print("Move your mouse to the LEFT SIDE OF ANY BLOCK IN THAT AREA!")
# time.sleep(5)
# p3 = pyautogui.position()
# print(f"Left side x-coordinate: {p3.x}")

# input()
# print("Move your mouse to the RIGHT SIDE OF THE SAME BLOCK!")
# time.sleep(5)
# p4 = pyautogui.position()
# print(f"Right side x-coordinate: {p4.x}")

# s = p4.x - p3.x
# print(f"Block side length: {s}")
# Write to file
with open("calibration.txt", "w") as f:
    f.write(f"{p1.x} {p1.y}\n")
    f.write(f"{p2.x} {p2.y}\n")
    # f.write(f"{s}\n")

print("Coordinates saved to calibration.txt")

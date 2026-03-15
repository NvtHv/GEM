import pyautogui
import numpy as np
from actions.base_action import BaseAction
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT, CAM_MARGIN, SMOOTHING_FACTOR , SENSITIVITY

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

class CursorMove(BaseAction):
    def __init__(self):
        self.prev_x, self.prev_y = 0, 0

    def execute(self, cx , cy):
        x = np.interp(cx, [CAM_MARGIN, CAMERA_WIDTH - CAM_MARGIN], [0, SCREEN_WIDTH])
        y = np.interp(cy, [CAM_MARGIN, CAMERA_HEIGHT - CAM_MARGIN], [0, SCREEN_HEIGHT])

        x = SCREEN_WIDTH/2 + (x - SCREEN_WIDTH/2) * SENSITIVITY
        y = SCREEN_HEIGHT/2 + (y - SCREEN_HEIGHT/2) * SENSITIVITY

        x = self.prev_x + (x - self.prev_x) / SMOOTHING_FACTOR
        y = self.prev_y + (y - self.prev_y) / SMOOTHING_FACTOR

        pyautogui.moveTo(int(x), int(y))
        self.prev_x, self.prev_y = x, y
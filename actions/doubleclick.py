import pyautogui
from actions.base_action import BaseAction

class DoubleClick(BaseAction):
    def execute(self):
        pyautogui.doubleClick()
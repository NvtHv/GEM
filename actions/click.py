import pyautogui
from actions.base_action import BaseAction

class Click(BaseAction):
    def execute(self):
        pyautogui.click()
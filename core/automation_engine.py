import logging
import time
from typing import Any, Dict, List, Optional

import pyautogui
from PIL import ImageGrab

logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = True


class AutomationEngine:
    def __init__(self, delay: float = 0.1):
        self.delay = delay

    def type_text(self, text: str, interval: float = 0.05):
        pyautogui.write(text, interval=interval)
        time.sleep(self.delay)

    def press_key(self, key: str):
        pyautogui.press(key)
        time.sleep(self.delay)

    def mouse_click(self, x: int, y: int, button: str = 'left'):
        pyautogui.click(x, y, button=button)
        time.sleep(self.delay)

    def mouse_move(self, x: int, y: int, duration: float = 0.3):
        pyautogui.moveTo(x, y, duration=duration)

    def mouse_scroll(self, clicks: int = 5, direction: str = 'down'):
        if direction == 'down':
            pyautogui.scroll(-clicks)
        else:
            pyautogui.scroll(clicks)

    def screenshot(self, path: str = 'screenshot.png'):
        img = ImageGrab.grab()
        img.save(path)
        return path

    async def execute_workflow(self, workflow_steps: List[Dict[str, Any]]):
        for step in workflow_steps:
            action = step.get('type')
            if action == 'click':
                self.mouse_click(step['x'], step['y'])
            elif action == 'type':
                self.type_text(step['text'])
            elif action == 'press':
                self.press_key(step['key'])
            elif action == 'wait':
                time.sleep(step.get('duration', 1))
            elif action == 'screenshot':
                self.screenshot(step.get('path', 'screenshot.png'))

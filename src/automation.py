import time
import pyautogui
import pyperclip


class WhatsAppAutomation:
    """
    Handles desktop automation for WhatsApp Web using PyAutoGUI.
    """

    # -----------------------------
    # Screen Coordinates
    # -----------------------------
    # Chrome icon (taskbar)
    CHROME_COORDINATES = (1321, 1045)

    # Visible chat selection
    DRAG_START_COORDINATES = (909, 240)
    DRAG_END_COORDINATES = (1849, 912)

    # Empty area to deselect highlighted text
    CHAT_DESELECT_COORDINATES = (909, 240)

    # Message input box
    INPUT_BOX_COORDINATES = (1113, 961)

    # Send button (optional)
    SEND_BUTTON_COORDINATES = (1870, 976)

    def __init__(self) -> None:
        # Keep emergency stop enabled
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.2

    def open_whatsapp(self) -> None:
        """
        Bring Chrome (with WhatsApp Web) to the foreground.
        """
        pyautogui.click(*self.CHROME_COORDINATES)
        time.sleep(2)

    def select_chat_area(self) -> None:
        """
        Highlight the visible chat messages.
        """
        pyautogui.moveTo(*self.DRAG_START_COORDINATES, duration=0.2)

        pyautogui.dragTo(
            *self.DRAG_END_COORDINATES,
            duration=1.5,
            button="left",
        )

        time.sleep(0.3)

    def copy_chat_history(self) -> str:
        """
        Copy highlighted chat into clipboard.

        Returns:
            str: Chat history text.
        """
        pyperclip.copy("")

        pyautogui.hotkey("ctrl", "c")
        time.sleep(1)

        chat_history = pyperclip.paste()

        pyautogui.click(*self.CHAT_DESELECT_COORDINATES)
        time.sleep(0.3)

        if not chat_history.strip():
            raise RuntimeError("Clipboard is empty. Chat selection failed.")

        return chat_history

    def focus_message_box(self) -> None:
        """
        Focus the WhatsApp message input.
        """
        pyautogui.click(*self.INPUT_BOX_COORDINATES)
        time.sleep(0.3)

    def send_message(self, message: str) -> None:
        """
        Paste and send a message.
        """
        if not message.strip():
            return

        self.focus_message_box()

        pyperclip.copy(message)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)

        pyautogui.press("enter")
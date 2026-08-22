import time
import logging
import pyautogui
import pyperclip
import pygetwindow as gw
from src.config import settings


class ChromeNotFoundError(Exception):
    """
    Raised when Google Chrome is not running.
    """
    pass


class WhatsAppNotOpenError(Exception):
    """
    Raised when WhatsApp Web is not open/active.
    """
    pass


class ChatInputNotFoundError(Exception):
    """
    Raised when the message input box is not found.
    """
    pass


class WhatsAppAutomation:
    """
    Handles desktop automation for WhatsApp Web using PyAutoGUI.
    """

    # -----------------------------
    # Screen Coordinates (Keep existing drag-selection and deselect logic)
    # -----------------------------
    # Visible chat selection
    DRAG_START_COORDINATES = (909, 240)
    DRAG_END_COORDINATES = (1849, 912)

    # Empty area to deselect highlighted text
    CHAT_DESELECT_COORDINATES = (909, 240)

    def __init__(self) -> None:
        # Keep emergency stop enabled
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.2

    def open_chrome(self) -> None:
        """
        Locates the Chrome window and brings it to the foreground.

        Raises:
            ChromeNotFoundError: If Google Chrome is not running.
        """
        logging.info("Searching for Chrome window...")
        chrome_windows = gw.getWindowsWithTitle("Chrome")
        if not chrome_windows:
            chrome_windows = gw.getWindowsWithTitle("Google Chrome")

        if not chrome_windows:
            raise ChromeNotFoundError("Google Chrome is not running.")

        chrome_win = chrome_windows[0]
        try:
            if chrome_win.isMinimized:
                chrome_win.restore()
            chrome_win.activate()
            logging.info("Chrome activated")
        except Exception as e:
            logging.warning(f"Could not activate Chrome window: {e}")

        # Wait 1 second after activating
        time.sleep(1)

    def verify_whatsapp_tab(self) -> bool:
        """
        Seares for the WhatsApp Web tab using image template matching.

        Returns:
            bool: True if the tab is successfully verified and clicked.

        Raises:
            WhatsAppNotOpenError: If the WhatsApp Web tab is not found.
        """
        logging.info("Locating WhatsApp Web tab on screen...")
        try:
            tab_pos = pyautogui.locateOnScreen(str(settings.WHATSAPP_TAB), confidence=0.85)
        except Exception as e:
            logging.error(f"Error during locateOnScreen for whatsapp_tab.png: {e}")
            tab_pos = None

        if tab_pos is not None:
            logging.info("WhatsApp tab detected")
            pyautogui.click(pyautogui.center(tab_pos))
            time.sleep(1)
            return True
        else:
            raise WhatsAppNotOpenError(
                "WhatsApp Web tab not found. Please open WhatsApp Web in Chrome."
            )

    def wait_for_user_chat_selection(self) -> None:
        """
        Pauses execution and prompts the user to select the chat in WhatsApp.
        """
        logging.info("Waiting for user chat selection")
        print("\nWhatsApp Web detected.")
        print("Please open any WhatsApp chat.")
        print("Press ENTER when ready...")
        input()

    def select_chat_area(self) -> None:
        """
        Highlight the visible chat messages.
        """
        logging.info("Highlighting the chat area...")
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
        logging.info("Chat copied")
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

        Raises:
            ChatInputNotFoundError: If the input box template is not found on screen.
        """
        logging.info("Locating chat input box...")
        try:
            input_pos = pyautogui.locateOnScreen(str(settings.CHAT_INPUT), confidence=0.85)
        except Exception as e:
            logging.error(f"Error locating chat_input.png: {e}")
            input_pos = None

        if input_pos is not None:
            logging.info("Focusing input box...")
            pyautogui.click(pyautogui.center(input_pos))
            time.sleep(0.3)
        else:
            raise ChatInputNotFoundError("Message input box not found.")

    def click_send_button(self) -> None:
        """
        Locates and clicks the WhatsApp send button.
        """
        logging.info("Locating and clicking send button...")
        try:
            send_pos = pyautogui.locateOnScreen(str(settings.SEND_BUTTON), confidence=0.85)
        except Exception as e:
            logging.error(f"Error locating send_button.png: {e}")
            send_pos = None

        if send_pos is not None:
            pyautogui.click(pyautogui.center(send_pos))
            time.sleep(0.3)
        else:
            logging.warning("Send button not found.")

    def open_whatsapp(self) -> None:
        """
        Legacy compatibility wrapper.
        """
        self.open_chrome()
        self.verify_whatsapp_tab()
        self.wait_for_user_chat_selection()

    def send_message(self, message: str) -> None:
        """
        Pasts and sends a message, falling back to click_send_button if Enter fails.
        """
        if not message.strip():
            return

        self.focus_message_box()

        pyperclip.copy(message)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)

        pyautogui.press("enter")
        time.sleep(0.5)

        # Fallback check
        try:
            send_pos = pyautogui.locateOnScreen(str(settings.SEND_BUTTON), confidence=0.85)
            if send_pos is not None:
                logging.warning("Enter key failed to send. Clicking the send button...")
                self.click_send_button()
        except Exception as e:
            logging.error(f"Error checking send button visibility: {e}")
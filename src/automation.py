import time
import pyautogui
import pyperclip

class WhatsAppAutomation:
    """
    Handles GUI-based automation tasks for WhatsApp or browser-based chat applications.
    
    Uses screen coordinates to simulate user interaction, copy chat histories,
    and send responses. Coordinates are stored as class variables for ease of customization.
    """

    # --- Screen Coordinates (Customizable per Screen Resolution) ---
    # Coordinates of the browser/desktop icon on the taskbar to launch or focus the window
    ICON_COORDINATES = (1639, 1412)
    
    # Drag-selection boundaries to highlight chat messages
    DRAG_START_COORDINATES = (972, 202)
    DRAG_END_COORDINATES = (2213, 1278)
    
    # Coordinates of a safe, neutral space in the UI to click and deselect highlighted text
    CHAT_DESELECT_COORDINATES = (1994, 281)
    
    # Coordinates of the text message input box
    INPUT_BOX_COORDINATES = (1808, 1328)

    def open_whatsapp(self) -> None:
        """
        Simulates a mouse click on the WhatsApp icon to open or focus the window.
        """
        # Click the WhatsApp/Chrome window icon to bring it to the foreground
        pyautogui.click(self.ICON_COORDINATES[0], self.ICON_COORDINATES[1])
        
        # Allow 1 second for the window to transition and gain system focus
        time.sleep(1.0)

    def select_chat_area(self) -> None:
        """
        Simulates mouse movement and drag actions to select and highlight chat logs.
        """
        # Move the cursor to the starting point of the message logs
        pyautogui.moveTo(self.DRAG_START_COORDINATES[0], self.DRAG_START_COORDINATES[1])
        
        # Perform drag selection down to the end of the logs to highlight messages
        pyautogui.dragTo(
            self.DRAG_END_COORDINATES[0],
            self.DRAG_END_COORDINATES[1],
            duration=2.0,
            button='left'
        )

    def copy_chat_history(self) -> str:
        """
        Copies the currently highlighted chat history to the system clipboard.
        
        Returns:
            str: The copied raw chat history text.
            
        Raises:
            RuntimeError: If clipboard copying fails or clipboard contents are empty.
        """
        # Clear the clipboard to ensure we do not read stale data if the copy fails
        pyperclip.copy("")
        
        # Trigger the system copy hotkey (Ctrl + C)
        pyautogui.hotkey('ctrl', 'c')
        
        # Allow time for the operating system clipboard API to register the copied text
        time.sleep(1.5)
        
        # Retrieve the copied text
        chat_history = pyperclip.paste()
        
        # Raise an exception if no content was copied
        if not chat_history or not chat_history.strip():
            raise RuntimeError(
                "Failed to copy chat history. Clipboard is empty. "
                "Ensure the chat window is in focus and text is highlighted."
            )
            
        # Click a neutral area to clear the active highlight, preparing the UI for the next cycle
        pyautogui.click(self.CHAT_DESELECT_COORDINATES[0], self.CHAT_DESELECT_COORDINATES[1])
        time.sleep(0.5)
        
        return chat_history

    def focus_message_box(self) -> None:
        """
        Clicks on the chat input field to focus the cursor for typing.
        """
        # Click inside the text message box to focus the cursor
        pyautogui.click(self.INPUT_BOX_COORDINATES[0], self.INPUT_BOX_COORDINATES[1])
        
        # Wait a short duration to ensure focus is complete
        time.sleep(0.5)

    def send_message(self, message: str) -> None:
        """
        Copies the response message to the clipboard, pastes it into the chat input, and sends it.
        
        Args:
            message (str): The response string to type and send.
        """
        if not message:
            return

        # Copy the message content to the clipboard for reliability over fast-typing simulation
        pyperclip.copy(message)
        
        # Paste the message into the text input box using system hotkey (Ctrl + V)
        pyautogui.hotkey('ctrl', 'v')
        
        # Brief pause to ensure the OS registers the paste action before sending
        time.sleep(0.5)
        
        # Press Enter key to send the message
        pyautogui.press('enter')

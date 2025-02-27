import tkinter as tk
from PIL import Image
import pystray


class SystemTrayApp:
    """A simple application that can be minimized to the system tray."""

    def __init__(self, root):
        self.root = root
        self.root.title("System Tray App")
        self.root.geometry('500x250')
        self.root.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)

    def minimize_to_tray(self):
        """Minimize the window to the system tray."""
        self.root.withdraw()
        image = Image.open("app.ico")
        menu = (pystray.MenuItem('Quit', self.quit_window),
                pystray.MenuItem('Show', self.show_window))
        icon = pystray.Icon("name", image, "System Tray App", menu)
        icon.run()

    def quit_window(self, icon):
        """Stop the system tray icon and destroy the window."""
        icon.stop()
        self.root.destroy()

    def show_window(self, icon):
        """Stop the system tray icon and show the window."""
        icon.stop()
        self.root.after(0, self.root.deiconify)


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemTrayApp(root)
    root.mainloop()
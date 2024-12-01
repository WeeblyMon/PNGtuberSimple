import sys
import os
import time
import json
import signal
from threading import Thread
from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
from comtypes import CoInitialize, CoUninitialize
from PyQt5 import QtWidgets, QtCore, QtGui

# Configuration file path
CONFIG_PATH = "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "TARGET_APP": "EDCoPilot.exe",
    "VOLUME_THRESHOLD": 0.2,
    "IMAGE_HIGH_VOLUME": "640px-Neurofumo.png",
    "IMAGE_LOW_VOLUME": "640px-Neurofumodark.png",
    "MAX_IMAGE_SIZE": 700,
    "INCREASE_SIZE_KEY": "Up",
    "DECREASE_SIZE_KEY": "Down",
    "CLOSE_KEY": "F4"  # Default key to close the application
}

# Create config file if it doesn't exist
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)

# Load configuration from the file
with open(CONFIG_PATH, "r") as file:
    CONFIG = json.load(file)


class VolumeMonitor(Thread):
    """Thread to monitor volume levels with retry logic."""

    def __init__(self, callback):
        super().__init__(daemon=True)
        self.callback = callback
        self.running = True

    def run(self):
        """Main loop to monitor audio levels."""
        CoInitialize()
        try:
            while self.running:
                print("Searching for target application...")
                target_session = None
                sessions = AudioUtilities.GetAllSessions()

                for session in sessions:
                    if session.Process and session.Process.name().lower() == CONFIG["TARGET_APP"].lower():
                        target_session = session
                        break

                if target_session:
                    print(f"Target application {CONFIG['TARGET_APP']} found!")
                    meter = target_session._ctl.QueryInterface(IAudioMeterInformation)

                    # Start monitoring volume
                    while self.running:
                        try:
                            peak_volume = meter.GetPeakValue()
                            self.callback(peak_volume)
                        except Exception as exc:
                            print(f"Error fetching volume: {exc}")
                            self.callback(0.0)
                        time.sleep(0.1)
                else:
                    print(f"Error: {CONFIG['TARGET_APP']} not found. Retrying in 15 seconds...")
                    self.callback(0.0)  # Reset volume indicator
                    time.sleep(15)
        finally:
            CoUninitialize()

    def stop(self):
        """Stop the volume monitor thread."""
        self.running = False


class ImageLabel(QtWidgets.QLabel):
    """Custom QLabel to handle mouse events for moving and resizing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._drag_active = False
        self._drag_position = QtCore.QPoint()
        self.setAlignment(QtCore.Qt.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.parent().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            self.parent().move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.parent().adjust_scale(delta)


class App(QtWidgets.QWidget):
    """Main application class."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.config = CONFIG

        # Verify images exist
        if not os.path.exists(self.config["IMAGE_HIGH_VOLUME"]) or not os.path.exists(self.config["IMAGE_LOW_VOLUME"]):
            print("Error: Image files not found.")
            sys.exit(1)

        # Load images
        self.image_high_orig = QtGui.QPixmap(self.config["IMAGE_HIGH_VOLUME"])
        self.image_low_orig = QtGui.QPixmap(self.config["IMAGE_LOW_VOLUME"])

        # Initialize scaling variables
        self.scale = 1.0
        self.target_scale = 1.0
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.timeout.connect(self.animate_resize)
        self.animation_timer.start(16)

        # Setup UI
        self.label = ImageLabel(self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Start volume monitor
        self.monitor = VolumeMonitor(self.update_image)
        self.monitor.start()

        # Load initial image
        self.current_image = None
        self.update_image(0.0)

        # Key bindings
        QtWidgets.QShortcut(QtGui.QKeySequence(self.config['INCREASE_SIZE_KEY']), self, self.increase_size)
        QtWidgets.QShortcut(QtGui.QKeySequence(self.config['DECREASE_SIZE_KEY']), self, self.decrease_size)
        QtWidgets.QShortcut(QtGui.QKeySequence(self.config['CLOSE_KEY']), self, self.close)

    def update_image(self, volume):
        """Switch images based on audio volume."""
        if volume > self.config["VOLUME_THRESHOLD"]:
            new_image = self.image_high_orig
        else:
            new_image = self.image_low_orig

        if self.current_image != new_image:
            self.current_image = new_image
            self.resize_image()

    def resize_image(self):
        """Resize current image based on scale."""
        if self.current_image:
            new_size = self.current_image.size() * self.scale
            scaled_pixmap = self.current_image.scaled(new_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label.setPixmap(scaled_pixmap)
            self.adjustSize()

    def adjust_scale(self, delta):
        """Adjust scale based on mouse wheel."""
        if delta > 0:
            self.target_scale = min(2.0, self.target_scale + 0.1)
        else:
            self.target_scale = max(0.1, self.target_scale - 0.1)

    def increase_size(self):
        """Increase the image size."""
        self.target_scale = min(2.0, self.target_scale + 0.1)

    def decrease_size(self):
        """Decrease the image size."""
        self.target_scale = max(0.1, self.target_scale - 0.1)

    def animate_resize(self):
        """Smoothly animate image resizing."""
        if abs(self.target_scale - self.scale) > 0.001:
            step = 0.02 if self.target_scale > self.scale else -0.02
            self.scale += step
            self.scale = round(self.scale, 4)
            self.resize_image()

    def closeEvent(self, event):
        """Handle the application close event."""
        print("Shutting down application...")
        self.monitor.stop()
        self.monitor.join(timeout=2)
        event.accept()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    app = QtWidgets.QApplication(sys.argv)
    main_app = App()
    main_app.show()
    sys.exit(app.exec_())

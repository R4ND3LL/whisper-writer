import os
import sys
import time
from audioplayer import AudioPlayer
from pynput.keyboard import Controller
from PyQt5.QtCore import QObject, QProcess
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox

from key_listener import KeyListener
from result_thread import ResultThread
from ui.main_window import MainWindow
from ui.settings_window import SettingsWindow
from ui.status_window import StatusWindow
from ui.theme_manager import ThemeManager
from transcription import create_local_model
from input_simulation import InputSimulator
from utils import ConfigManager

# Import wake/sleep state management (Qt-based)
try:
    from wake_sleep_state_manager import WakeSleepStateManager
    _WAKE_SLEEP_AVAILABLE = True
except ImportError:
    # Fallback if wake/sleep not available
    WakeSleepStateManager = None
    _WAKE_SLEEP_AVAILABLE = False


class WhisperWriterApp(QObject):
    def __init__(self):
        """
        Initialize the application, opening settings window if no configuration file is found.
        """
        super().__init__()
        
        # Setup high DPI support BEFORE creating QApplication
        ThemeManager.setup_high_dpi_support()
        
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon(os.path.join('assets', 'ww-logo.png')))

        ConfigManager.initialize()
        
        # Apply theme and font scaling after config is loaded
        self.theme_manager = ThemeManager()
        self.theme_manager.apply_theme(self.app, ConfigManager)

        self.settings_window = SettingsWindow()
        self.settings_window.settings_closed.connect(self.on_settings_closed)
        self.settings_window.settings_saved.connect(self.restart_app)

        config_exists = ConfigManager.config_file_exists()
        
        if config_exists:
            self.initialize_components()
        else:
            print('No valid configuration file found. Opening settings window...')
            self.settings_window.show()

    def initialize_components(self):
        """
        Initialize the components of the application.
        """
        self.input_simulator = InputSimulator()

        self.key_listener = KeyListener()
        self.key_listener.add_callback("on_activate", self.on_activation)
        self.key_listener.add_callback("on_deactivate", self.on_deactivation)

        model_options = ConfigManager.get_config_section('model_options')
        model_path = model_options.get('local', {}).get('model_path')
        self.local_model = create_local_model() if not model_options.get('use_api') else None

        self.result_thread = None

        self.main_window = MainWindow()
        self.main_window.openSettings.connect(self.settings_window.show)
        self.main_window.startListening.connect(self.key_listener.start)
        self.main_window.closeApp.connect(self.exit_app)

        hide_status = ConfigManager.get_config_value('misc', 'hide_status_window')
        
        if not hide_status:
            self.status_window = StatusWindow()

        # Setup wake/sleep state management (after status window creation)
        self.setup_wake_sleep_management()

        self.create_tray_icon()
        self.main_window.show()

    def setup_wake_sleep_management(self):
        """
        Setup wake/sleep state management using Qt signals
        """
        if not _WAKE_SLEEP_AVAILABLE:
            return
        
        # Get the state manager instance
        self.wake_sleep_manager = WakeSleepStateManager.get_instance()
        
        # Connect signal to update status window when state changes
        if hasattr(self, 'status_window') and self.status_window:
            self.wake_sleep_manager.stateChanged.connect(self.status_window.update_wake_sleep_state)
        
        # Initialize state based on config
        try:
            WakeSleepStateManager.initialize_from_config()
        except Exception as e:
            print(f"Error initializing wake/sleep state from config: {e}")
            WakeSleepStateManager.set_state('awake')


    def create_tray_icon(self):
        """
        Create the system tray icon and its context menu.
        """
        self.tray_icon = QSystemTrayIcon(QIcon(os.path.join('assets', 'ww-logo.png')), self.app)

        tray_menu = QMenu()

        show_action = QAction('WhisperWriter Main Menu', self.app)
        show_action.triggered.connect(self.main_window.show)
        tray_menu.addAction(show_action)

        settings_action = QAction('Open Settings', self.app)
        settings_action.triggered.connect(self.settings_window.show)
        tray_menu.addAction(settings_action)

        exit_action = QAction('Exit', self.app)
        exit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def cleanup(self):
        if self.key_listener:
            self.key_listener.stop()
        if self.input_simulator:
            self.input_simulator.cleanup()
        
        # Qt signals are automatically disconnected when objects are destroyed
        # No manual cleanup needed for wake/sleep state manager

    def exit_app(self):
        """
        Exit the application.
        """
        self.cleanup()
        QApplication.quit()

    def restart_app(self):
        """Restart the application to apply the new settings."""
        self.cleanup()
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)
    
    def refresh_theme(self):
        """
        Refresh the theme without restarting the app (for theme/font changes).
        """
        try:
            print("Refreshing theme...")
            ConfigManager.reload_config()
            self.theme_manager.apply_theme(self.app, ConfigManager)
        except Exception as e:
            print(f"[ERROR] Failed to refresh theme: {e}")

    def on_settings_closed(self):
        """
        If settings is closed without saving on first run, initialize the components with default values.
        """
        if not os.path.exists(os.path.join('src', 'config.yaml')):
            QMessageBox.information(
                self.settings_window,
                'Using Default Values',
                'Settings closed without saving. Default values are being used.'
            )
            self.initialize_components()

    def on_activation(self):
        """
        Called when the activation key combination is pressed.
        """
        if self.result_thread and self.result_thread.isRunning():
            recording_mode = ConfigManager.get_config_value('recording_options', 'recording_mode')
            if recording_mode == 'press_to_toggle':
                self.result_thread.stop_recording()
            elif recording_mode == 'continuous':
                self.stop_result_thread()
            return

        self.start_result_thread()

    def on_deactivation(self):
        """
        Called when the activation key combination is released.
        """
        if ConfigManager.get_config_value('recording_options', 'recording_mode') == 'hold_to_record':
            if self.result_thread and self.result_thread.isRunning():
                self.result_thread.stop_recording()

    def start_result_thread(self):
        """
        Start the result thread to record audio and transcribe it.
        """
        if self.result_thread and self.result_thread.isRunning():
            return

        self.result_thread = ResultThread(self.local_model)
        hide_status = ConfigManager.get_config_value('misc', 'hide_status_window')
        if not hide_status:
            self.result_thread.statusSignal.connect(self.status_window.updateStatus)
            self.status_window.closeSignal.connect(self.stop_result_thread)
        self.result_thread.resultSignal.connect(self.on_transcription_complete)
        self.result_thread.start()

    def stop_result_thread(self):
        """
        Stop the result thread.
        """
        if self.result_thread and self.result_thread.isRunning():
            self.result_thread.stop()

    def on_transcription_complete(self, result):
        """
        When the transcription is complete, type the result and start listening for the activation key again.
        """
        self.input_simulator.typewrite(result)

        if ConfigManager.get_config_value('misc', 'noise_on_completion'):
            AudioPlayer(os.path.join('assets', 'beep.wav')).play(block=True)

        if ConfigManager.get_config_value('recording_options', 'recording_mode') == 'continuous':
            self.start_result_thread()
        else:
            self.key_listener.start()

    def run(self):
        """
        Start the application.
        """
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    app = WhisperWriterApp()
    app.run()

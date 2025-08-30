"""
Theme Manager for PyQt5 Applications
Handles dark mode detection, theme switching, and high DPI scaling
"""

import os
import sys
import winreg
from typing import Optional, Dict, Any
from PyQt5 import QtWidgets, QtCore, QtGui


class ThemeManager(QtCore.QObject):
    """
    Manages themes and high DPI scaling for PyQt5 applications
    
    Features:
    - Windows dark mode detection
    - Dynamic theme switching
    - High DPI scaling configuration
    - Cross-window theme application
    """
    
    theme_changed = QtCore.pyqtSignal(bool)  # True for dark, False for light
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_theme = None
        self._stylesheets = {
            'light': self._get_light_stylesheet(),
            'dark': self._get_dark_stylesheet()
        }
    
    @staticmethod
    def configure_high_dpi():
        """
        Configure high DPI scaling for PyQt5 applications
        MUST be called before creating QApplication
        """
        # Enable high DPI scaling (Qt 5.6+)
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        
        # Optional environment variables for fine-tuning
        os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
        os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    
    @staticmethod
    def detect_windows_dark_mode() -> bool:
        """
        Detect if Windows is using dark mode
        
        Returns:
            bool: True if dark mode is enabled, False otherwise
        """
        try:
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            reg_keypath = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
            
            try:
                reg_key = winreg.OpenKey(registry, reg_keypath)
            except FileNotFoundError:
                return False
            
            for i in range(1024):
                try:
                    value_name, value, _ = winreg.EnumValue(reg_key, i)
                    if value_name == 'AppsUseLightTheme':
                        return value == 0  # 0 = dark mode, 1 = light mode
                except OSError:
                    break
            
            return False
        except ImportError:
            # winreg not available (non-Windows)
            return False
    
    def apply_theme(self, app: QtWidgets.QApplication, dark_mode: Optional[bool] = None):
        """
        Apply theme to the entire application
        
        Args:
            app: QApplication instance
            dark_mode: True for dark, False for light, None for auto-detect
        """
        if dark_mode is None:
            dark_mode = self.detect_windows_dark_mode()
        
        theme_key = 'dark' if dark_mode else 'light'
        
        if self._current_theme != theme_key:
            self._current_theme = theme_key
            app.setStyleSheet(self._stylesheets[theme_key])
            self.theme_changed.emit(dark_mode)
    
    def toggle_theme(self, app: QtWidgets.QApplication):
        """Toggle between light and dark themes"""
        current_is_dark = self._current_theme == 'dark'
        self.apply_theme(app, not current_is_dark)
    
    def _get_dark_stylesheet(self) -> str:
        """Get dark theme stylesheet"""
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            selection-background-color: #0078d4;
        }
        
        QDialog {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            padding: 6px 12px;
            border-radius: 3px;
            color: #ffffff;
            font-size: 9pt;
        }
        
        QPushButton:hover {
            background-color: #404040;
            border-color: #6a6a6a;
        }
        
        QPushButton:pressed {
            background-color: #2a2a2a;
            border-color: #0078d4;
        }
        
        QPushButton:disabled {
            background-color: #1e1e1e;
            color: #666666;
            border-color: #333333;
        }
        
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #555555;
            padding: 4px;
            border-radius: 2px;
            color: #ffffff;
            selection-background-color: #0078d4;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #0078d4;
        }
        
        QLabel {
            color: #ffffff;
            background-color: transparent;
        }
        
        QComboBox {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            padding: 4px 8px;
            border-radius: 2px;
            color: #ffffff;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-style: solid;
            border-width: 4px 4px 0 4px;
            border-color: transparent transparent #ffffff transparent;
        }
        
        QComboBox QAbstractItemView {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            color: #ffffff;
            selection-background-color: #0078d4;
        }
        
        QCheckBox {
            color: #ffffff;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #555555;
            border-radius: 2px;
            background-color: #2b2b2b;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }
        
        QGroupBox {
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px 0 4px;
        }
        
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #2b2b2b;
        }
        
        QTabBar::tab {
            background-color: #3c3c3c;
            color: #ffffff;
            padding: 6px 12px;
            border: 1px solid #555555;
            border-bottom: none;
        }
        
        QTabBar::tab:selected {
            background-color: #2b2b2b;
            border-color: #0078d4;
        }
        
        QTabBar::tab:hover {
            background-color: #404040;
        }
        """
    
    def _get_light_stylesheet(self) -> str:
        """Get light theme stylesheet"""
        return """
        QMainWindow {
            background-color: #ffffff;
            color: #000000;
        }
        
        QWidget {
            background-color: #ffffff;
            color: #000000;
            selection-background-color: #0078d4;
        }
        
        QDialog {
            background-color: #ffffff;
            color: #000000;
        }
        
        QPushButton {
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            padding: 6px 12px;
            border-radius: 3px;
            color: #000000;
            font-size: 9pt;
        }
        
        QPushButton:hover {
            background-color: #e5e5e5;
            border-color: #adadad;
        }
        
        QPushButton:pressed {
            background-color: #d4d4d4;
            border-color: #0078d4;
        }
        
        QPushButton:disabled {
            background-color: #f5f5f5;
            color: #999999;
            border-color: #e0e0e0;
        }
        
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            padding: 4px;
            border-radius: 2px;
            color: #000000;
            selection-background-color: #0078d4;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #0078d4;
        }
        
        QLabel {
            color: #000000;
            background-color: transparent;
        }
        
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            padding: 4px 8px;
            border-radius: 2px;
            color: #000000;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-style: solid;
            border-width: 4px 4px 0 4px;
            border-color: transparent transparent #000000 transparent;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            color: #000000;
            selection-background-color: #0078d4;
        }
        
        QCheckBox {
            color: #000000;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #cccccc;
            border-radius: 2px;
            background-color: #ffffff;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }
        
        QGroupBox {
            color: #000000;
            border: 1px solid #cccccc;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px 0 4px;
        }
        
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #f0f0f0;
            color: #000000;
            padding: 6px 12px;
            border: 1px solid #cccccc;
            border-bottom: none;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-color: #0078d4;
        }
        
        QTabBar::tab:hover {
            background-color: #e5e5e5;
        }
        """


class AdvancedThemeManager(ThemeManager):
    """
    Extended theme manager with external library support
    Requires: pip install qdarkstyle darkdetect
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._use_external_themes = self._check_external_dependencies()
    
    def _check_external_dependencies(self) -> bool:
        """Check if external theme libraries are available"""
        try:
            import qdarkstyle
            import darkdetect
            return True
        except ImportError:
            return False
    
    def detect_system_theme(self) -> bool:
        """
        Detect system theme using darkdetect library
        Fallback to registry-based detection on Windows
        """
        if self._use_external_themes:
            try:
                import darkdetect
                return darkdetect.isDark()
            except ImportError:
                pass
        
        # Fallback to Windows registry detection
        return self.detect_windows_dark_mode()
    
    def apply_professional_theme(self, app: QtWidgets.QApplication, dark_mode: Optional[bool] = None):
        """
        Apply professional theme using QDarkStyleSheet if available
        Otherwise falls back to custom stylesheets
        """
        if dark_mode is None:
            dark_mode = self.detect_system_theme()
        
        if self._use_external_themes:
            try:
                import qdarkstyle
                if dark_mode:
                    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
                else:
                    # QDarkStyleSheet doesn't have a light theme, use custom
                    app.setStyleSheet(self._stylesheets['light'])
                
                self._current_theme = 'dark' if dark_mode else 'light'
                self.theme_changed.emit(dark_mode)
                return
            except ImportError:
                pass
        
        # Fallback to custom themes
        self.apply_theme(app, dark_mode)


def example_usage():
    """Example of how to use the ThemeManager"""
    
    # MUST be called before creating QApplication
    ThemeManager.configure_high_dpi()
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Create theme manager
    theme_manager = ThemeManager()
    
    # Create main window
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Theme Manager Example")
    window.resize(400, 300)
    
    # Central widget with controls
    central_widget = QtWidgets.QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QtWidgets.QVBoxLayout(central_widget)
    
    # Theme toggle button
    toggle_button = QtWidgets.QPushButton("Toggle Theme")
    toggle_button.clicked.connect(lambda: theme_manager.toggle_theme(app))
    layout.addWidget(toggle_button)
    
    # Some sample widgets
    layout.addWidget(QtWidgets.QLabel("Sample Label"))
    layout.addWidget(QtWidgets.QLineEdit("Sample text input"))
    
    combo = QtWidgets.QComboBox()
    combo.addItems(["Option 1", "Option 2", "Option 3"])
    layout.addWidget(combo)
    
    checkbox = QtWidgets.QCheckBox("Sample checkbox")
    layout.addWidget(checkbox)
    
    # Apply initial theme (auto-detect)
    theme_manager.apply_theme(app)
    
    # Show window
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    example_usage()
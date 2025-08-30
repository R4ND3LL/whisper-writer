import os
import sys
import winreg
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont


class ThemeManager:
    """Manages dark/light themes and DPI scaling for the application."""
    
    def __init__(self):
        self.is_dark_mode = False
        self.base_font_size = 9  # Default Qt font size
        self.scale_factor = 1.0
        
    @staticmethod
    def setup_high_dpi_support():
        """Enable high DPI support before QApplication creation."""
        try:
            # Enable high DPI scaling
            if hasattr(Qt, 'AA_EnableHighDpiScaling'):
                QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
                QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            
            # Set DPI awareness for Windows
            if sys.platform == 'win32':
                try:
                    import ctypes
                    # Try SetProcessDPIAware first (Windows Vista+)
                    try:
                        ctypes.windll.user32.SetProcessDPIAware()
                    except:
                        # Fallback to SetProcessDpiAwarenessContext (Windows 10+)
                        try:
                            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
                        except:
                            pass  # Graceful fallback if both fail
                except ImportError:
                    pass  # ctypes not available
                    
        except Exception as e:
            print(f"[WARNING] Could not enable high DPI support: {e}")
    
    def detect_windows_dark_mode(self):
        """Detect Windows dark mode setting from registry."""
        try:
            # Check Windows 10/11 theme setting
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                # AppsUseLightTheme: 0 = dark, 1 = light
                apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return apps_use_light_theme == 0
        except (FileNotFoundError, OSError, WindowsError):
            # Fallback: try system theme setting
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                    system_uses_light_theme, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
                    return system_uses_light_theme == 0
            except (FileNotFoundError, OSError, WindowsError):
                return False  # Default to light mode if detection fails
    
    def calculate_dpi_scale_factor(self, app):
        """Calculate DPI scale factor based on system settings."""
        try:
            # Get the primary screen
            screen = app.primaryScreen()
            if screen:
                dpi = screen.logicalDotsPerInch()
                # Standard DPI is 96, calculate scale factor
                self.scale_factor = max(1.0, dpi / 96.0)
                print(f"[INFO] Detected DPI: {dpi}, Scale factor: {self.scale_factor:.2f}")
                return self.scale_factor
        except Exception as e:
            print(f"[WARNING] Could not detect DPI: {e}")
        
        return 1.0  # Default scale factor
    
    def get_scaled_font_size(self, base_size=None):
        """Get font size adjusted for DPI scaling."""
        if base_size is None:
            base_size = self.base_font_size
        return int(base_size * self.scale_factor)
    
    def get_ui_scale_factor(self):
        """Get the UI scale factor for window sizing."""
        return self.scale_factor
    
    @classmethod
    def get_current_scale_factor(cls, config_manager=None):
        """Get the current scale factor without creating a full theme manager."""
        font_scale_percent = 0
        if config_manager:
            try:
                font_scale_percent = config_manager.get_config_value('misc', 'font_scale_percent') or 0
            except:
                pass
        
        if font_scale_percent > 0:
            return font_scale_percent / 100.0
        else:
            # Default to reasonable scale for high DPI
            return 1.25  # Assume 125% if auto
    
    def apply_theme(self, app, config_manager=None):
        """Apply the theme to the application based on config settings."""
        try:
            # Get theme settings from config
            theme_mode = "auto"
            font_scale_percent = 0  # 0 = automatic DPI scaling
            
            if config_manager:
                try:
                    theme_mode = config_manager.get_config_value('misc', 'theme_mode') or "auto"
                    font_scale_percent = config_manager.get_config_value('misc', 'font_scale_percent') or 0
                    # Also check old config name for backward compatibility
                    if font_scale_percent == 0:
                        old_scale = config_manager.get_config_value('misc', 'font_scale') or 0.0
                        if old_scale > 0:
                            font_scale_percent = int(old_scale * 100)
                except:
                    pass  # Use defaults if config unavailable
            
            # Determine theme based on settings
            if theme_mode == "dark":
                self.is_dark_mode = True
                print("[INFO] Using forced dark theme")
            elif theme_mode == "light":
                self.is_dark_mode = False
                print("[INFO] Using forced light theme")
            else:  # auto
                self.is_dark_mode = self.detect_windows_dark_mode()
                print(f"[INFO] Auto-detected theme: {'Dark' if self.is_dark_mode else 'Light'}")
            
            # Calculate DPI scaling
            if font_scale_percent > 0:
                self.scale_factor = font_scale_percent / 100.0
                print(f"[INFO] Using manual font scale: {font_scale_percent}% ({self.scale_factor:.2f}x)")
            else:
                self.calculate_dpi_scale_factor(app)
                print(f"[INFO] Using automatic DPI scale: {self.scale_factor:.2f}x")
            
            # Apply stylesheet
            if self.is_dark_mode:
                stylesheet = self.get_dark_stylesheet()
            else:
                stylesheet = self.get_light_stylesheet()
            
            app.setStyleSheet(stylesheet)
            
            # Set application font with proper scaling
            font = QFont()
            font.setPointSize(self.get_scaled_font_size())
            app.setFont(font)
            
            print(f"[INFO] Applied {('dark' if self.is_dark_mode else 'light')} theme with {self.scale_factor:.2f}x scaling")
            
        except Exception as e:
            print(f"[ERROR] Failed to apply theme: {e}")
            # Fallback to minimal light theme
            self.apply_fallback_theme(app)
    
    def apply_fallback_theme(self, app):
        """Apply a minimal fallback theme if main theming fails."""
        try:
            # Basic font scaling at minimum
            font = QFont()
            font.setPointSize(self.get_scaled_font_size())
            app.setFont(font)
            print("[INFO] Applied fallback theme with font scaling")
        except Exception as e:
            print(f"[WARNING] Even fallback theming failed: {e}")
    
    def get_dark_stylesheet(self):
        """Return dark theme stylesheet."""
        font_size = self.get_scaled_font_size()
        button_height = int(32 * self.scale_factor)
        spacing = int(8 * self.scale_factor)
        
        return f"""
/* Dark Theme Stylesheet */
* {{
    background-color: #2b2b2b;
    color: #ffffff;
    font-size: {font_size}pt;
}}

QWidget {{
    background-color: #2b2b2b;
    color: #ffffff;
    font-size: {font_size}pt;
}}

/* Force all input widgets to dark theme */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: #3a3a3a !important;
    border: 1px solid #555555 !important;
    border-radius: 4px !important;
    padding: {spacing}px !important;
    color: #ffffff !important;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: #0078d4 !important;
    background-color: #3a3a3a !important;
    color: #ffffff !important;
}}

/* Force all containers to dark */
QFrame, QScrollArea, QGroupBox {{
    background-color: #2b2b2b !important;
    color: #ffffff !important;
}}

/* Force table and list styling */
QTableWidget, QListWidget, QTreeWidget {{
    background-color: #2b2b2b !important;
    alternate-background-color: #333333 !important;
    color: #ffffff !important;
    gridline-color: #555555 !important;
}}

QTableWidget::item, QListWidget::item, QTreeWidget::item {{
    background-color: transparent !important;
    color: #ffffff !important;
    padding: {spacing}px !important;
}}

QMainWindow {{
    background-color: #2b2b2b;
}}

QDialog {{
    background-color: #2b2b2b;
}}

/* Buttons */
QPushButton {{
    background-color: #404040 !important;
    border: 1px solid #555555 !important;
    border-radius: 4px !important;
    padding: {max(4, spacing//2)}px 12px !important;
    min-height: {max(24, button_height//2)}px !important;
    color: #ffffff !important;
}}

QPushButton:hover {{
    background-color: #4a4a4a !important;
    border-color: #777777 !important;
}}

QPushButton:pressed {{
    background-color: #353535 !important;
}}

QPushButton:disabled {{
    background-color: #333333 !important;
    color: #777777 !important;
    border-color: #444444 !important;
}}

/* Compact buttons for regex settings and other areas that need less vertical space */
QWidget[objectName*="regex"] QPushButton,
QGroupBox QPushButton,
QPushButton[text="Test Rules"],
QPushButton[text="Add Rule"],
QPushButton[text="Edit"],
QPushButton[text="Delete"],
QPushButton[text="Import..."],
QPushButton[text="Export..."] {{
    padding: 3px 8px !important;
    min-height: 20px !important;
    margin: 1px !important;
}}

/* Viewport and ScrollArea content fixes */
QAbstractScrollArea {{
    background-color: #2b2b2b !important;
    color: #ffffff !important;
}}

QScrollArea > QWidget > QWidget {{
    background-color: #2b2b2b !important;
}}

QAbstractScrollArea::corner {{
    background-color: #2b2b2b !important;
}}

/* Test input areas and result areas */
QTextEdit#test_input, QTextEdit#test_output {{
    background-color: #3a3a3a !important;
    color: #ffffff !important;
    border: 1px solid #555555 !important;
}}

/* Any remaining white backgrounds */
QWidget[class="white_background"] {{
    background-color: #2b2b2b !important;
    color: #ffffff !important;
}}

/* Combo Boxes */
QComboBox {{
    background-color: #3a3a3a !important;
    border: 1px solid #555555 !important;
    border-radius: 4px !important;
    padding: {spacing}px !important;
    color: #ffffff !important;
}}

QComboBox:hover {{
    border-color: #777777 !important;
}}

QComboBox::drop-down {{
    border: none !important;
    background-color: #404040 !important;
}}

QComboBox::down-arrow {{
    border: none !important;
    background-color: transparent !important;
}}

QComboBox QAbstractItemView {{
    background-color: #3a3a3a !important;
    border: 1px solid #555555 !important;
    selection-background-color: #0078d4 !important;
    color: #ffffff !important;
}}

/* Check Boxes */
QCheckBox {{
    color: #ffffff;
    spacing: {spacing}px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
}}

QCheckBox::indicator:unchecked {{
    background-color: #3a3a3a;
    border: 1px solid #555555;
    border-radius: 2px;
}}

QCheckBox::indicator:checked {{
    background-color: #0078d4;
    border: 1px solid #0078d4;
    border-radius: 2px;
}}

/* Spin Boxes */
QSpinBox, QDoubleSpinBox {{
    background-color: #3a3a3a !important;
    border: 1px solid #555555 !important;
    border-radius: 4px !important;
    padding: {spacing}px !important;
    color: #ffffff !important;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: #0078d4 !important;
    background-color: #3a3a3a !important;
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    background-color: #404040 !important;
    border: none !important;
    border-radius: 2px !important;
    width: 16px !important;
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    border-left: 4px solid transparent !important;
    border-right: 4px solid transparent !important;
    border-bottom: 6px solid #ffffff !important;
    border-top: none !important;
    width: 0px !important;
    height: 0px !important;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background-color: #404040 !important;
    border: none !important;
    border-radius: 2px !important;
    width: 16px !important;
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    border-left: 4px solid transparent !important;
    border-right: 4px solid transparent !important;
    border-top: 6px solid #ffffff !important;
    border-bottom: none !important;
    width: 0px !important;
    height: 0px !important;
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
    background-color: #4a4a4a !important;
}}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: #4a4a4a !important;
}}

/* Group Boxes */
QGroupBox {{
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #2b2b2b;
}}

/* CollapsibleGroupBox specific styling */
QFrame[objectName="header_frame"] {{
    background-color: #404040 !important;
    border: 1px solid #555555 !important;
    border-radius: 3px !important;
    color: #ffffff !important;
}}

QFrame[objectName="content_frame"] {{
    background-color: #2b2b2b !important;
    border: 1px solid #555555 !important;
    border-top: none !important;
    border-radius: 0px 0px 3px 3px !important;
    color: #ffffff !important;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid #555555;
    background-color: #2b2b2b;
}}

QTabBar::tab {{
    background-color: #404040;
    border: 1px solid #555555;
    padding: {spacing}px 16px;
    color: #ffffff;
}}

QTabBar::tab:selected {{
    background-color: #0078d4;
    border-bottom: 1px solid #0078d4;
}}

QTabBar::tab:hover {{
    background-color: #4a4a4a;
}}

/* Tables */
QTableWidget {{
    background-color: #2b2b2b;
    alternate-background-color: #333333;
    gridline-color: #555555;
    color: #ffffff;
}}

QTableWidget::item {{
    padding: {spacing}px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: #0078d4;
}}

QHeaderView::section {{
    background-color: #404040;
    color: #ffffff;
    padding: {spacing}px;
    border: 1px solid #555555;
}}

/* List Widget */
QListWidget {{
    background-color: #2b2b2b;
    border: 1px solid #555555;
    color: #ffffff;
}}

QListWidget::item {{
    padding: {spacing}px;
}}

QListWidget::item:selected {{
    background-color: #0078d4;
}}

/* Scroll Bars */
QScrollBar:vertical {{
    background-color: #2b2b2b;
    width: 16px;
    border: 1px solid #555555;
}}

QScrollBar::handle:vertical {{
    background-color: #555555;
    border-radius: 4px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #777777;
}}

/* Labels */
QLabel {{
    color: #ffffff;
}}

/* Tool Buttons (Help buttons) */
QToolButton {{
    background-color: #404040;
    border: 1px solid #555555;
    border-radius: 12px;
    color: #ffffff;
    font-weight: bold;
    width: 24px;
    height: 24px;
}}

QToolButton:hover {{
    background-color: #0078d4;
    border-color: #0078d4;
}}

/* Tooltips - Dark Theme */
QToolTip {{
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 8px;
    font-size: 16px;
    font-weight: normal;
}}

/* System Tray (if applicable) */
QMenu {{
    background-color: #3a3a3a;
    border: 1px solid #555555;
    color: #ffffff;
}}

QMenu::item:selected {{
    background-color: #0078d4;
}}

/* Window title bar and close button for dark theme */
QLabel {{
    color: #ffffff !important;
}}

/* Override close button colors for dark theme */
QPushButton[objectName="close_button"] {{
    color: #ffffff !important;
    background-color: transparent !important;
    margin: 4px !important;
}}

QPushButton[objectName="close_button"]:hover {{
    color: #ffffff !important;
    background-color: #ff4444 !important;
    margin: 2px !important;
}}

/* Aggressive fix for any remaining white backgrounds */
QWidget > QWidget {{
    background-color: #2b2b2b !important;
}}

/* Specifically target common problem widgets */
QFrame > QWidget, QScrollArea > QWidget, QGroupBox > QWidget {{
    background-color: #2b2b2b !important;
    color: #ffffff !important;
}}

/* Fix for any custom widgets that might have white backgrounds */
QWidget[objectName*="content"], QWidget[objectName*="widget"], QWidget[objectName*="frame"] {{
    background-color: #2b2b2b !important;
    color: #ffffff !important;
}}

/* Final catchall for any stubborn white backgrounds */
QWidget[style*="background-color: rgb(255, 255, 255)"], 
QWidget[style*="background-color: white"],
QWidget[style*="background: white"] {{
    background-color: #2b2b2b !important;
    color: #ffffff !important;
}}
"""
    
    def get_light_stylesheet(self):
        """Return light theme stylesheet with proper scaling."""
        font_size = self.get_scaled_font_size()
        button_height = int(32 * self.scale_factor)
        spacing = int(8 * self.scale_factor)
        
        return f"""
/* Light Theme Stylesheet */
QWidget {{
    background-color: #ffffff;
    color: #000000;
    font-size: {font_size}pt;
}}

QMainWindow {{
    background-color: #ffffff;
}}

QDialog {{
    background-color: #ffffff;
}}

/* Buttons */
QPushButton {{
    background-color: #f0f0f0;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: {max(4, spacing//2)}px 12px;
    min-height: {max(24, button_height//2)}px;
    color: #000000;
}}

QPushButton:hover {{
    background-color: #e5e5e5;
    border-color: #999999;
}}

QPushButton:pressed {{
    background-color: #d9d9d9;
}}

QPushButton:disabled {{
    background-color: #f5f5f5;
    color: #888888;
    border-color: #dddddd;
}}

/* Compact buttons for regex settings and other areas that need less vertical space */
QWidget[objectName*="regex"] QPushButton,
QGroupBox QPushButton,
QPushButton[text="Test Rules"],
QPushButton[text="Add Rule"],
QPushButton[text="Edit"],
QPushButton[text="Delete"],
QPushButton[text="Import..."],
QPushButton[text="Export..."] {{
    padding: 3px 8px !important;
    min-height: 20px !important;
    margin: 1px !important;
}}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: {spacing}px;
    color: #000000;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: #0078d4;
}}

/* Combo Boxes */
QComboBox {{
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: {spacing}px;
    color: #000000;
}}

QComboBox:hover {{
    border-color: #999999;
}}

QComboBox::drop-down {{
    border: none;
    background-color: #f0f0f0;
}}

QComboBox QAbstractItemView {{
    background-color: #ffffff;
    border: 1px solid #cccccc;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
    color: #000000;
}}

/* Check Boxes */
QCheckBox {{
    color: #000000;
    spacing: {spacing}px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
}}

QCheckBox::indicator:unchecked {{
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 2px;
}}

QCheckBox::indicator:checked {{
    background-color: #0078d4;
    border: 1px solid #0078d4;
    border-radius: 2px;
}}

/* Spin Boxes */
QSpinBox, QDoubleSpinBox {{
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: {spacing}px;
    color: #000000;
}}

/* Group Boxes */
QGroupBox {{
    color: #000000;
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #ffffff;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid #cccccc;
    background-color: #ffffff;
}}

QTabBar::tab {{
    background-color: #f0f0f0;
    border: 1px solid #cccccc;
    padding: {spacing}px 16px;
    color: #000000;
}}

QTabBar::tab:selected {{
    background-color: #0078d4;
    color: #ffffff;
    border-bottom: 1px solid #0078d4;
}}

QTabBar::tab:hover {{
    background-color: #e5e5e5;
}}

/* Tables */
QTableWidget {{
    background-color: #ffffff;
    alternate-background-color: #f9f9f9;
    gridline-color: #cccccc;
    color: #000000;
}}

QTableWidget::item {{
    padding: {spacing}px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: #0078d4;
    color: #ffffff;
}}

QHeaderView::section {{
    background-color: #f0f0f0;
    color: #000000;
    padding: {spacing}px;
    border: 1px solid #cccccc;
}}

/* List Widget */
QListWidget {{
    background-color: #ffffff;
    border: 1px solid #cccccc;
    color: #000000;
}}

QListWidget::item {{
    padding: {spacing}px;
}}

QListWidget::item:selected {{
    background-color: #0078d4;
    color: #ffffff;
}}

/* Scroll Bars */
QScrollBar:vertical {{
    background-color: #f0f0f0;
    width: 16px;
    border: 1px solid #cccccc;
}}

QScrollBar::handle:vertical {{
    background-color: #cccccc;
    border-radius: 4px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #999999;
}}

/* Labels */
QLabel {{
    color: #000000;
}}

/* Tool Buttons (Help buttons) */
QToolButton {{
    background-color: #f0f0f0;
    border: 1px solid #cccccc;
    border-radius: 12px;
    color: #000000;
    font-weight: bold;
    width: 24px;
    height: 24px;
}}

QToolButton:hover {{
    background-color: #0078d4;
    color: #ffffff;
    border-color: #0078d4;
}}

/* Tooltips - Light Theme */
QToolTip {{
    background-color: #ffffcc;
    color: #000000;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 8px;
    font-size: 16px;
    font-weight: normal;
}}

/* System Tray (if applicable) */
QMenu {{
    background-color: #ffffff;
    border: 1px solid #cccccc;
    color: #000000;
}}

QMenu::item:selected {{
    background-color: #0078d4;
    color: #ffffff;
}}
"""
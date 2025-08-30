"""
DPI Manager for PyQt5 Applications
Advanced high DPI scaling and font management
"""

import os
import sys
import ctypes
from typing import Dict, Tuple, Optional
from PyQt5 import QtWidgets, QtCore, QtGui


class DPIManager:
    """
    Manages high DPI scaling for PyQt5 applications
    
    Features:
    - Windows DPI awareness configuration
    - Dynamic DPI change handling
    - Font scaling management
    - Per-monitor DPI support
    """
    
    def __init__(self):
        self._base_font_size = 9
        self._dpi_scale_factor = 1.0
        self._original_sizes: Dict[str, int] = {}
    
    @staticmethod
    def configure_dpi_awareness():
        """
        Configure Windows DPI awareness
        MUST be called before creating QApplication
        """
        if sys.platform == "win32":
            try:
                # Set process DPI aware (Windows 8.1+)
                ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            except (AttributeError, OSError):
                try:
                    # Fallback for older Windows versions
                    ctypes.windll.user32.SetProcessDPIAware()
                except (AttributeError, OSError):
                    pass
        
        # Configure Qt DPI settings
        os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
        os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
        
        # Enable Qt high DPI scaling
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        
        # Optional: Disable platform integration for custom DPI handling
        # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton, True)
    
    @staticmethod
    def get_system_dpi() -> Tuple[int, int]:
        """Get system DPI (x, y)"""
        if sys.platform == "win32":
            try:
                hdc = ctypes.windll.user32.GetDC(0)
                dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                dpi_y = ctypes.windll.gdi32.GetDeviceCaps(hdc, 90)  # LOGPIXELSY
                ctypes.windll.user32.ReleaseDC(0, hdc)
                return dpi_x, dpi_y
            except (AttributeError, OSError):
                pass
        
        # Fallback to Qt method
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            return int(screen.logicalDotsPerInchX()), int(screen.logicalDotsPerInchY())
        
        return 96, 96  # Default DPI
    
    @staticmethod
    def get_dpi_scale_factor() -> float:
        """Get current DPI scale factor relative to 96 DPI"""
        dpi_x, _ = DPIManager.get_system_dpi()
        return dpi_x / 96.0
    
    def setup_font_scaling(self, app: QtWidgets.QApplication):
        """Setup application font scaling based on DPI"""
        self._dpi_scale_factor = self.get_dpi_scale_factor()
        
        # Get current font
        font = app.font()
        
        # Store original size if not already stored
        if 'app_font' not in self._original_sizes:
            self._original_sizes['app_font'] = font.pointSize() or self._base_font_size
        
        # Calculate scaled font size
        scaled_size = max(8, int(self._original_sizes['app_font'] * self._dpi_scale_factor))
        
        # Apply scaled font
        font.setPointSize(scaled_size)
        app.setFont(font)
    
    def scale_widget_fonts(self, widget: QtWidgets.QWidget, base_size: Optional[int] = None):
        """Scale fonts for a specific widget and its children"""
        if base_size is None:
            base_size = self._base_font_size
        
        # Scale the widget's font
        font = widget.font()
        scaled_size = max(8, int(base_size * self._dpi_scale_factor))
        font.setPointSize(scaled_size)
        widget.setFont(font)
        
        # Recursively scale children
        for child in widget.findChildren(QtWidgets.QWidget):
            child_font = child.font()
            child_font.setPointSize(scaled_size)
            child.setFont(child_font)
    
    def create_dpi_aware_stylesheet(self, base_stylesheet: str) -> str:
        """
        Modify stylesheet to be DPI aware
        Scales pixel-based sizes according to DPI
        """
        if self._dpi_scale_factor == 1.0:
            return base_stylesheet
        
        # Simple scaling of common pixel values
        import re
        
        def scale_pixels(match):
            value = int(match.group(1))
            scaled_value = max(1, int(value * self._dpi_scale_factor))
            return f"{scaled_value}px"
        
        # Scale pixel values in the stylesheet
        scaled_stylesheet = re.sub(r'(\d+)px', scale_pixels, base_stylesheet)
        
        return scaled_stylesheet
    
    def handle_dpi_change(self, app: QtWidgets.QApplication):
        """Handle DPI changes (for multi-monitor setups)"""
        # Recalculate DPI scale factor
        new_scale_factor = self.get_dpi_scale_factor()
        
        if abs(new_scale_factor - self._dpi_scale_factor) > 0.01:
            self._dpi_scale_factor = new_scale_factor
            
            # Reapply font scaling
            self.setup_font_scaling(app)
            
            # Notify all windows to update their fonts
            for window in app.topLevelWindows():
                if hasattr(window, 'winId') and window.winId():
                    widget = app.widgetAt(window.geometry().center())
                    if widget:
                        self.scale_widget_fonts(widget.window())


class DPIAwareWindow(QtWidgets.QMainWindow):
    """
    Base class for DPI-aware windows
    Automatically handles DPI changes and font scaling
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dpi_manager = DPIManager()
        self._base_font_sizes: Dict[QtWidgets.QWidget, int] = {}
        
        # Setup DPI handling
        self._setup_dpi_handling()
    
    def _setup_dpi_handling(self):
        """Setup DPI change handling"""
        # Store original font sizes
        self._store_font_sizes()
        
        # Apply initial scaling
        self.dpi_manager.scale_widget_fonts(self)
    
    def _store_font_sizes(self):
        """Store original font sizes for all widgets"""
        for widget in self.findChildren(QtWidgets.QWidget):
            font = widget.font()
            self._base_font_sizes[widget] = font.pointSize() or 9
    
    def changeEvent(self, event):
        """Handle window change events including DPI changes"""
        if event.type() == QtCore.QEvent.WindowStateChange:
            # Check if DPI might have changed (window moved to different monitor)
            app = QtWidgets.QApplication.instance()
            if app:
                self.dpi_manager.handle_dpi_change(app)
        
        super().changeEvent(event)
    
    def add_widget(self, widget: QtWidgets.QWidget, base_font_size: Optional[int] = None):
        """Add a widget with proper DPI scaling"""
        if base_font_size:
            self._base_font_sizes[widget] = base_font_size
        
        self.dpi_manager.scale_widget_fonts(widget, base_font_size)
        return widget


def create_dpi_test_window():
    """Create a test window to demonstrate DPI scaling"""
    
    class DPITestWindow(DPIAwareWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("DPI Scaling Test")
            self.resize(500, 400)
            
            # Central widget
            central_widget = QtWidgets.QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QtWidgets.QVBoxLayout(central_widget)
            
            # DPI info
            dpi_x, dpi_y = DPIManager.get_system_dpi()
            scale_factor = DPIManager.get_dpi_scale_factor()
            
            info_label = QtWidgets.QLabel(
                f"System DPI: {dpi_x} x {dpi_y}\n"
                f"Scale Factor: {scale_factor:.2f}"
            )
            layout.addWidget(info_label)
            
            # Font size samples
            for size in [8, 10, 12, 14, 16]:
                label = QtWidgets.QLabel(f"Font size {size}pt")
                font = label.font()
                font.setPointSize(size)
                label.setFont(font)
                layout.addWidget(label)
            
            # Buttons with different sizes
            small_btn = QtWidgets.QPushButton("Small Button")
            small_btn.setMaximumHeight(25)
            layout.addWidget(small_btn)
            
            normal_btn = QtWidgets.QPushButton("Normal Button")
            layout.addWidget(normal_btn)
            
            large_btn = QtWidgets.QPushButton("Large Button")
            large_btn.setMinimumHeight(50)
            layout.addWidget(large_btn)
            
            # Text input
            text_edit = QtWidgets.QTextEdit()
            text_edit.setPlainText("This is a sample text area for testing DPI scaling.")
            text_edit.setMaximumHeight(100)
            layout.addWidget(text_edit)
    
    return DPITestWindow()


def example_usage():
    """Example of DPI manager usage"""
    
    # MUST configure DPI before creating QApplication
    DPIManager.configure_dpi_awareness()
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Create DPI manager
    dpi_manager = DPIManager()
    
    # Setup application-wide font scaling
    dpi_manager.setup_font_scaling(app)
    
    # Create test window
    window = create_dpi_test_window()
    window.show()
    
    # Print DPI information
    dpi_x, dpi_y = DPIManager.get_system_dpi()
    scale_factor = DPIManager.get_dpi_scale_factor()
    
    print(f"System DPI: {dpi_x} x {dpi_y}")
    print(f"Scale Factor: {scale_factor:.2f}")
    
    return app.exec_()


if __name__ == "__main__":
    example_usage()
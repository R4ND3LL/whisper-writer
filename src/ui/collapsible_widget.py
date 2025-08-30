from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect, QParallelAnimationGroup
from PyQt5.QtGui import QFont


class CollapsibleGroupBox(QWidget):
    """A truly collapsible group box that hides/shows content with animations."""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.is_expanded = True
        self.content_height = 0
        
        self.init_ui(title)
    
    def init_ui(self, title):
        """Initialize the user interface."""
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        
        # Header frame
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header_frame")
        self.header_frame.setFrameStyle(QFrame.Box)
        # Remove hardcoded styling - let global theme handle it
        
        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 4, 8, 4)
        self.header_frame.setLayout(header_layout)
        
        # Toggle button (arrow)
        self.toggle_button = QPushButton()
        self.toggle_button.setFixedSize(20, 20)
        # Remove hardcoded hover color - let global theme handle it
        self.toggle_button.clicked.connect(self.toggle_expanded)
        header_layout.addWidget(self.toggle_button)
        
        # Title label
        self.title_label = QLabel(title)
        font = QFont()
        font.setBold(True)
        self.title_label.setFont(font)
        header_layout.addWidget(self.title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Content frame
        self.content_frame = QFrame()
        self.content_frame.setObjectName("content_frame")
        self.content_frame.setFrameStyle(QFrame.Box)
        # Remove hardcoded white background - let global theme handle it
        
        # Content layout (this is where users add their widgets)
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_frame.setLayout(self.content_layout)
        
        # Add to main layout
        self.main_layout.addWidget(self.header_frame)
        self.main_layout.addWidget(self.content_frame)
        
        # Update arrow state
        self.update_arrow()
        
        # Animation setup
        self.animation = QPropertyAnimation(self.content_frame, b"maximumHeight")
        self.animation.setDuration(200)  # 200ms animation
    
    def addWidget(self, widget):
        """Add a widget to the content area."""
        self.content_layout.addWidget(widget)
    
    def addLayout(self, layout):
        """Add a layout to the content area."""
        self.content_layout.addLayout(layout)
    
    def setTitle(self, title):
        """Set the group box title."""
        self.title_label.setText(title)
    
    def setExpanded(self, expanded):
        """Set the expanded state without animation."""
        if self.is_expanded != expanded:
            self.is_expanded = expanded
            self.update_arrow()
            
            if expanded:
                self.content_frame.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
                self.content_frame.show()
            else:
                self.content_frame.setMaximumHeight(0)
                self.content_frame.hide()
    
    def toggle_expanded(self):
        """Toggle the expanded state with smooth animation."""
        self.is_expanded = not self.is_expanded
        self.update_arrow()
        
        # Get the content height if we don't have it yet
        if self.content_height == 0:
            self.content_frame.show()
            self.content_frame.setMaximumHeight(16777215)
            self.content_height = self.content_frame.sizeHint().height()
        
        # Animate the collapse/expand
        if self.is_expanded:
            # Expanding
            self.content_frame.show()
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.content_height)
            self.animation.finished.connect(self.on_expand_finished)
        else:
            # Collapsing  
            self.animation.setStartValue(self.content_height)
            self.animation.setEndValue(0)
            self.animation.finished.connect(self.on_collapse_finished)
        
        self.animation.start()
    
    def on_expand_finished(self):
        """Called when expand animation finishes."""
        self.content_frame.setMaximumHeight(16777215)  # Allow natural sizing
        try:
            self.animation.finished.disconnect()
        except:
            pass
    
    def on_collapse_finished(self):
        """Called when collapse animation finishes."""
        self.content_frame.hide()
        try:
            self.animation.finished.disconnect()
        except:
            pass
    
    def update_arrow(self):
        """Update the arrow direction based on expanded state."""
        if self.is_expanded:
            self.toggle_button.setText("▼")
        else:
            self.toggle_button.setText("▶")
    
    def isExpanded(self):
        """Return whether the group is currently expanded."""
        return self.is_expanded
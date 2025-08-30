from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QValidator


class FontScaleSpinBox(QSpinBox):
    """Custom spinbox for font scaling with Auto (0) and 100-150% range."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 130)  # Changed from 150 to 130
        self.setSpecialValueText("Auto")
        # Don't set suffix here - handle it in textFromValue to avoid double %
        self.setToolTip("Font scaling: Auto = automatic DPI detection, 100-130% = manual scaling")
    
    def stepBy(self, steps):
        """Override step behavior to skip 1-99% range."""
        current = self.value()
        
        if steps > 0:  # Stepping up
            if current == 0:
                self.setValue(100)  # Jump from Auto to 100%
            else:
                super().stepBy(steps)
        else:  # Stepping down  
            if current == 100:
                self.setValue(0)  # Jump from 100% to Auto
            else:
                super().stepBy(steps)
    
    def validate(self, input_text, pos):
        """Validate input to ensure only 0 or 100-150 are allowed."""
        state, text, position = super().validate(input_text, pos)
        
        if state == QValidator.Acceptable:
            try:
                value = int(input_text.replace('%', '').replace('Auto', '0'))
                if value != 0 and (value < 100 or value > 130):  # Changed from 150 to 130
                    return (QValidator.Invalid, text, position)
            except ValueError:
                pass
        
        return (state, text, position)
    
    def valueFromText(self, text):
        """Convert text to value, handling 'Auto' text."""
        if 'Auto' in text:
            return 0
        try:
            return int(text.replace('%', ''))
        except ValueError:
            return self.value()  # Return current value if invalid
    
    def textFromValue(self, value):
        """Convert value to text, handling special case for 0."""
        if value == 0:
            return "Auto"
        return f"{value}%"
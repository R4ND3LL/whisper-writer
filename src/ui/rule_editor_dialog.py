import sys
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QCheckBox, QSpinBox, QGroupBox, QLabel, QMessageBox,
    QTabWidget, QWidget, QComboBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import ConfigManager


class RuleEditorDialog(QDialog):
    """Dialog for editing regex replacement rules."""
    
    def __init__(self, rule=None, parent=None):
        super().__init__(parent)
        self.rule = rule or {}
        self.setWindowTitle("Edit Rule" if rule else "Add New Rule")
        self.setModal(True)
        self.resize(900, 800)
        
        # Set up live preview timer BEFORE creating UI
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)
        
        self.init_ui()
        self.load_rule_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Basic settings tab
        self.create_basic_tab()
        
        # Advanced settings tab
        self.create_advanced_tab()
        
        # Test tab
        self.create_test_tab()
        
        # Templates tab
        self.create_templates_tab()
        
        # Dialog buttons
        buttons_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        buttons_layout.addWidget(self.ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def create_basic_tab(self):
        """Create the basic settings tab."""
        basic_tab = QWidget()
        layout = QFormLayout()
        basic_tab.setLayout(layout)
        
        # Pattern input
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("Enter search pattern (regex or plain text)")
        self.pattern_edit.textChanged.connect(self.on_pattern_changed)
        layout.addRow("Pattern:", self.pattern_edit)
        
        # Replacement input  
        self.replacement_edit = QLineEdit()
        self.replacement_edit.setPlaceholderText("Enter replacement text")
        self.replacement_edit.textChanged.connect(self.schedule_preview_update)
        layout.addRow("Replacement:", self.replacement_edit)
        
        # Description input
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Optional description of what this rule does")
        layout.addRow("Description:", self.description_edit)
        
        # Rule type
        self.is_regex_checkbox = QCheckBox("Use Regular Expression")
        self.is_regex_checkbox.setChecked(True)
        self.is_regex_checkbox.stateChanged.connect(self.on_regex_type_changed)
        layout.addRow("Type:", self.is_regex_checkbox)
        
        # Enabled
        self.enabled_checkbox = QCheckBox("Rule Enabled")
        self.enabled_checkbox.setChecked(True)
        layout.addRow("Status:", self.enabled_checkbox)
        
        # Priority
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 100)
        self.priority_spin.setValue(50)
        self.priority_spin.setToolTip("Lower numbers run first")
        layout.addRow("Priority:", self.priority_spin)
        
        self.tabs.addTab(basic_tab, "Basic")
    
    def create_advanced_tab(self):
        """Create the advanced settings tab."""
        advanced_tab = QWidget()
        layout = QVBoxLayout()
        advanced_tab.setLayout(layout)
        
        # Regex flags group
        flags_group = QGroupBox("Regular Expression Flags")
        flags_layout = QVBoxLayout()
        flags_group.setLayout(flags_layout)
        
        self.ignorecase_checkbox = QCheckBox("Ignore case (re.IGNORECASE)")
        flags_layout.addWidget(self.ignorecase_checkbox)
        
        self.multiline_checkbox = QCheckBox("Multiline mode (re.MULTILINE)")
        flags_layout.addWidget(self.multiline_checkbox)
        
        self.dotall_checkbox = QCheckBox("Dot matches newlines (re.DOTALL)")
        flags_layout.addWidget(self.dotall_checkbox)
        
        self.verbose_checkbox = QCheckBox("Verbose mode (re.VERBOSE)")
        flags_layout.addWidget(self.verbose_checkbox)
        
        layout.addWidget(flags_group)
        
        # Help text
        help_group = QGroupBox("Quick Reference")
        help_layout = QVBoxLayout()
        help_group.setLayout(help_layout)
        
        help_text = QLabel("""
<b>Common Regex Patterns:</b><br>
• \\b - Word boundary<br>
• \\d - Any digit (0-9)<br>
• \\w - Any word character<br>
• \\s - Any whitespace<br>
• + - One or more<br>
• * - Zero or more<br>
• ? - Zero or one<br>
• (group) - Capture group<br>
• [abc] - Character class<br><br>
<b>Replacement:</b><br>
• $1, $2 - Captured groups<br>
• \\n - Newline<br>
• \\t - Tab
        """)
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)
        
        layout.addWidget(help_group)
        
        self.tabs.addTab(advanced_tab, "Advanced")
    
    def create_test_tab(self):
        """Create the test tab."""
        test_tab = QWidget()
        layout = QVBoxLayout()
        test_tab.setLayout(layout)
        
        # Test input
        layout.addWidget(QLabel("Test Input:"))
        self.test_input = QTextEdit()
        self.test_input.setMaximumHeight(100)
        self.test_input.setPlaceholderText("Enter text to test your rule...")
        self.test_input.textChanged.connect(self.schedule_preview_update)
        layout.addWidget(self.test_input)
        
        # Test button
        test_button = QPushButton("Test Rule")
        test_button.clicked.connect(self.test_rule)
        layout.addWidget(test_button)
        
        # Test output
        layout.addWidget(QLabel("Test Output:"))
        self.test_output = QTextEdit()
        self.test_output.setMaximumHeight(100)
        self.test_output.setReadOnly(True)
        layout.addWidget(self.test_output)
        
        # Live preview
        self.live_preview_checkbox = QCheckBox("Live Preview")
        self.live_preview_checkbox.setChecked(True)
        layout.addWidget(self.live_preview_checkbox)
        
        self.tabs.addTab(test_tab, "Test")
    
    def create_templates_tab(self):
        """Create the templates tab."""
        templates_tab = QWidget()
        layout = QVBoxLayout()
        templates_tab.setLayout(layout)
        
        layout.addWidget(QLabel("Choose from common templates:"))
        
        # Templates list
        self.templates_list = QListWidget()
        self.load_templates()
        self.templates_list.itemDoubleClicked.connect(self.apply_template)
        layout.addWidget(self.templates_list)
        
        # Apply template button
        apply_template_button = QPushButton("Apply Selected Template")
        apply_template_button.clicked.connect(self.apply_selected_template)
        layout.addWidget(apply_template_button)
        
        self.tabs.addTab(templates_tab, "Templates")
    
    def load_templates(self):
        """Load available templates into the list."""
        try:
            templates_data = ConfigManager.get_rule_templates()
            templates = templates_data.get('templates', {})
            
            for category, category_data in templates.items():
                # Add category header
                category_name = category_data.get('name', category.replace('_', ' ').title())
                category_item = QListWidgetItem(f"--- {category_name} ---")
                category_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
                category_item.setData(Qt.UserRole, None)
                self.templates_list.addItem(category_item)
                
                # Add rules in category - get rules from the 'rules' key
                category_rules = category_data.get('rules', [])
                for rule in category_rules:
                    pattern = rule.get('pattern', '')
                    description = rule.get('description', pattern)
                    
                    # Truncate long patterns for display
                    display_pattern = pattern[:50] + "..." if len(pattern) > 50 else pattern
                    
                    item_text = f"{description} ({display_pattern})"
                    list_item = QListWidgetItem(item_text)
                    list_item.setData(Qt.UserRole, rule)
                    self.templates_list.addItem(list_item)
                    
        except Exception as e:
            error_item = QListWidgetItem(f"Error loading templates: {str(e)}")
            error_item.setFlags(Qt.NoItemFlags)
            self.templates_list.addItem(error_item)
    
    def apply_template(self, item):
        """Apply a template when double-clicked."""
        rule_data = item.data(Qt.UserRole)
        if rule_data:
            self.apply_rule_data(rule_data)
    
    def apply_selected_template(self):
        """Apply the currently selected template."""
        current_item = self.templates_list.currentItem()
        if current_item:
            rule_data = current_item.data(Qt.UserRole)
            if rule_data:
                self.apply_rule_data(rule_data)
    
    def apply_rule_data(self, rule_data):
        """Apply rule data to the form fields."""
        self.pattern_edit.setText(rule_data.get('pattern', ''))
        self.replacement_edit.setText(rule_data.get('replacement', ''))
        self.description_edit.setText(rule_data.get('description', ''))
        self.is_regex_checkbox.setChecked(rule_data.get('is_regex', True))
        self.enabled_checkbox.setChecked(rule_data.get('enabled', True))
        self.priority_spin.setValue(rule_data.get('priority', 50))
        
        # Apply flags
        flags = rule_data.get('flags', [])
        self.ignorecase_checkbox.setChecked('ignorecase' in flags)
        self.multiline_checkbox.setChecked('multiline' in flags)
        self.dotall_checkbox.setChecked('dotall' in flags)
        self.verbose_checkbox.setChecked('verbose' in flags)
        
        # Switch to basic tab
        self.tabs.setCurrentIndex(0)
    
    def load_rule_data(self):
        """Load existing rule data into the form."""
        if not self.rule:
            return
        
        self.pattern_edit.setText(self.rule.get('pattern', ''))
        self.replacement_edit.setText(self.rule.get('replacement', ''))
        self.description_edit.setText(self.rule.get('description', ''))
        self.is_regex_checkbox.setChecked(self.rule.get('is_regex', True))
        self.enabled_checkbox.setChecked(self.rule.get('enabled', True))
        self.priority_spin.setValue(self.rule.get('priority', 50))
        
        # Load flags
        flags = self.rule.get('flags', [])
        self.ignorecase_checkbox.setChecked('ignorecase' in flags)
        self.multiline_checkbox.setChecked('multiline' in flags)
        self.dotall_checkbox.setChecked('dotall' in flags)
        self.verbose_checkbox.setChecked('verbose' in flags)
    
    def on_pattern_changed(self):
        """Handle pattern text changes."""
        self.validate_pattern()
        self.schedule_preview_update()
    
    def on_regex_type_changed(self):
        """Handle regex type checkbox change."""
        is_regex = self.is_regex_checkbox.isChecked()
        
        # Enable/disable regex-specific controls
        self.ignorecase_checkbox.setEnabled(is_regex)
        self.multiline_checkbox.setEnabled(is_regex)
        self.dotall_checkbox.setEnabled(is_regex)
        self.verbose_checkbox.setEnabled(is_regex)
        
        self.validate_pattern()
        self.schedule_preview_update()
    
    def validate_pattern(self):
        """Validate the current pattern."""
        pattern = self.pattern_edit.text()
        is_regex = self.is_regex_checkbox.isChecked()
        
        if not pattern:
            self.pattern_edit.setStyleSheet("")
            return True
        
        if is_regex:
            try:
                import re
                flags = self.get_regex_flags()
                re.compile(pattern, flags)
                self.pattern_edit.setStyleSheet("QLineEdit { border: 2px solid green; }")
                return True
            except re.error:
                self.pattern_edit.setStyleSheet("QLineEdit { border: 2px solid red; }")
                return False
        else:
            # Plain text is always valid
            self.pattern_edit.setStyleSheet("QLineEdit { border: 2px solid green; }")
            return True
    
    def get_regex_flags(self):
        """Get the current regex flags as integer."""
        import re
        flags = 0
        
        if self.ignorecase_checkbox.isChecked():
            flags |= re.IGNORECASE
        if self.multiline_checkbox.isChecked():
            flags |= re.MULTILINE
        if self.dotall_checkbox.isChecked():
            flags |= re.DOTALL
        if self.verbose_checkbox.isChecked():
            flags |= re.VERBOSE
            
        return flags
    
    def get_flags_list(self):
        """Get the current flags as a list of strings."""
        flags = []
        
        if self.ignorecase_checkbox.isChecked():
            flags.append('ignorecase')
        if self.multiline_checkbox.isChecked():
            flags.append('multiline')
        if self.dotall_checkbox.isChecked():
            flags.append('dotall')
        if self.verbose_checkbox.isChecked():
            flags.append('verbose')
            
        return flags
    
    def schedule_preview_update(self):
        """Schedule a preview update (debounced)."""
        if self.live_preview_checkbox.isChecked():
            self.preview_timer.start(500)  # 500ms delay
    
    def update_preview(self):
        """Update the live preview."""
        self.test_rule()
    
    def test_rule(self):
        """Test the current rule against the test input."""
        pattern = self.pattern_edit.text()
        replacement = self.replacement_edit.text()
        test_text = self.test_input.toPlainText()
        is_regex = self.is_regex_checkbox.isChecked()
        
        if not pattern or not test_text:
            self.test_output.setText("")
            return
        
        try:
            if is_regex:
                import re
                flags = self.get_regex_flags()
                compiled_pattern = re.compile(pattern, flags)
                result = compiled_pattern.sub(replacement, test_text)
            else:
                # Plain text replacement
                if self.ignorecase_checkbox.isChecked():
                    import re
                    result = re.sub(re.escape(pattern), replacement, test_text, flags=re.IGNORECASE)
                else:
                    result = test_text.replace(pattern, replacement)
            
            self.test_output.setText(result)
            
        except Exception as e:
            self.test_output.setText(f"Error: {str(e)}")
    
    def accept(self):
        """Accept the dialog if validation passes."""
        if not self.validate_pattern():
            QMessageBox.warning(
                self,
                "Invalid Pattern",
                "Please fix the pattern before saving."
            )
            return
        
        if not self.pattern_edit.text().strip():
            QMessageBox.warning(
                self,
                "Missing Pattern",
                "Please enter a pattern."
            )
            return
        
        super().accept()
    
    def get_rule(self):
        """Get the rule data from the form."""
        rule_data = {
            'pattern': self.pattern_edit.text(),
            'replacement': self.replacement_edit.text(),
            'description': self.description_edit.text(),
            'enabled': self.enabled_checkbox.isChecked(),
            'is_regex': self.is_regex_checkbox.isChecked(),
            'priority': self.priority_spin.value()
        }
        
        # Add flags if any are set
        flags = self.get_flags_list()
        if flags:
            rule_data['flags'] = flags
        
        return rule_data
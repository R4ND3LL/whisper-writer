import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QCheckBox, QMessageBox, QFileDialog,
    QTextEdit, QLabel, QSplitter, QGroupBox, QLineEdit, QToolButton
)
from PyQt5.QtCore import Qt, pyqtSignal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import ConfigManager


class RegexSettingsWidget(QWidget):
    """Widget for managing regex replacement rules."""
    
    rules_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_rules()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create splitter for table and test area
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # Rules table section
        rules_group = QGroupBox("Regex Rules")
        rules_layout = QVBoxLayout()
        rules_group.setLayout(rules_layout)
        
        # Create table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)  # Reduced from 6 to 5 columns
        self.rules_table.setHorizontalHeaderLabels([
            "Pattern", "Replacement", "Type", "Description", "Actions"
        ])
        
        # Set table properties
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)           # Pattern
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Replacement  
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Description
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Actions
        
        rules_layout.addWidget(self.rules_table)
        
        # Buttons row
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Rule")
        self.add_button.clicked.connect(self.add_rule)
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.create_help_button(
            "Add Rule: Create a new text replacement rule.\n\n"
            "• Use 'Regex' mode for pattern matching (e.g., \\bum+\\b to match 'um', 'umm')\n"
            "• Use 'Text' mode for simple word replacement (case-insensitive)\n"
            "• Set priority (lower numbers run first)\n"
            "• Test your rules with sample text before saving"
        ))
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_selected_rule)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.create_help_button(
            "Edit Rule: Modify the selected text replacement rule.\n\n"
            "• Double-click any rule to edit it\n"
            "• Use the Templates tab to browse pre-built rules\n"
            "• Test your changes with the live preview feature"
        ))
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected_rule)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.create_help_button(
            "Delete Rule: Remove the selected rule permanently.\n\n"
            "• You'll be asked to confirm before deletion\n"
            "• Deleted rules cannot be recovered\n"
            "• Consider disabling rules instead if unsure"
        ))
        
        buttons_layout.addStretch()
        
        self.import_button = QPushButton("Import...")
        self.import_button.clicked.connect(self.import_rules)
        buttons_layout.addWidget(self.import_button)
        buttons_layout.addWidget(self.create_help_button(
            "Import Rules: Load rules from a YAML or JSON file.\n\n"
            "• Share rule sets between computers\n"
            "• Choose to replace existing rules or add to them\n"
            "• Supports both .yaml and .json file formats\n"
            "• Rules are validated before import"
        ))
        
        self.export_button = QPushButton("Export...")
        self.export_button.clicked.connect(self.export_rules)
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.create_help_button(
            "Export Rules: Save your rules to a file for backup or sharing.\n\n"
            "• Create backups of your custom rules\n"
            "• Share rule sets with others\n"
            "• Choose YAML (human-readable) or JSON format\n"
            "• All rules are validated before export"
        ))
        
        rules_layout.addLayout(buttons_layout)
        splitter.addWidget(rules_group)
        
        # Test area section
        test_group = QGroupBox("Test Rules")
        test_layout = QVBoxLayout()
        test_group.setLayout(test_layout)
        
        # Input text
        test_layout.addWidget(QLabel("Test Input:"))
        self.test_input = QTextEdit()
        self.test_input.setMaximumHeight(80)
        self.test_input.setPlaceholderText("Enter text to test regex rules...")
        test_layout.addWidget(self.test_input)
        
        # Test button with help
        test_button_layout = QHBoxLayout()
        test_button = QPushButton("Test Rules")
        test_button.clicked.connect(self.test_rules)
        test_button_layout.addWidget(test_button)
        test_button_layout.addWidget(self.create_help_button(
            "Test Rules: Preview how your rules will transform text.\n\n"
            "• Type sample text in the input area\n"
            "• Click 'Test Rules' to see the result after all rules are applied\n"
            "• Rules are applied in priority order (lower numbers first)\n"
            "• Use this to verify rules work before dictating"
        ))
        test_button_layout.addStretch()
        test_layout.addLayout(test_button_layout)
        
        # Output text
        test_layout.addWidget(QLabel("Test Output:"))
        self.test_output = QTextEdit()
        self.test_output.setMaximumHeight(80)
        self.test_output.setReadOnly(True)
        test_layout.addWidget(self.test_output)
        
        splitter.addWidget(test_group)
        
        # Set splitter proportions (more space for rules table)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        # Enable/disable buttons based on selection
        self.rules_table.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()
    
    def create_help_button(self, help_text):
        """Create a help button with tooltip text."""
        help_button = QToolButton()
        help_button.setText('?')
        help_button.setFixedSize(20, 20)
        help_button.setStyleSheet("""
            QToolButton {
                background-color: #e1e1e1;
                border: 1px solid #adadad;
                border-radius: 10px;
                font-weight: bold;
                color: #333;
            }
            QToolButton:hover {
                background-color: #d4d4d4;
            }
        """)
        help_button.setToolTip(help_text)
        help_button.clicked.connect(lambda: QMessageBox.information(
            self, 'Help', help_text
        ))
        return help_button
    
    def load_rules(self):
        """Load rules from configuration into the table."""
        rules = ConfigManager.get_regex_rules()
        
        self.rules_table.setRowCount(len(rules))
        
        for row, rule in enumerate(rules):
            # Pattern
            pattern_item = QTableWidgetItem(rule.get('pattern', ''))
            self.rules_table.setItem(row, 0, pattern_item)
            
            # Replacement
            replacement_item = QTableWidgetItem(rule.get('replacement', ''))
            self.rules_table.setItem(row, 1, replacement_item)
            
            # Type - make it read-only
            rule_type = "Text" if not rule.get('is_regex', True) else "Regex"
            type_item = QTableWidgetItem(rule_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)  # Remove editable flag
            type_item.setToolTip("Use the Edit button to change between Regex and Text modes")
            self.rules_table.setItem(row, 2, type_item)
            
            # Description - make it read-only  
            description_item = QTableWidgetItem(rule.get('description', ''))
            description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)  # Remove editable flag
            description_item.setToolTip("Use the Edit button to modify the description")
            self.rules_table.setItem(row, 3, description_item)
            
            # Actions - add quick action buttons with tighter spacing
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(1, 1, 1, 1)  # Minimal margins
            actions_layout.setSpacing(1)  # Minimal spacing between buttons
            
            # Toggle enabled button with much more distinct styling
            is_enabled = rule.get('enabled', True)
            
            # Use simpler symbols that fit better in small buttons
            if is_enabled:
                toggle_button = QPushButton("●")  # Filled circle for enabled
                toggle_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 1px solid #2E7D32;
                        border-radius: 3px;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 0px;
                        margin: 0px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                        border-color: #1B5E20;
                    }
                """)
                toggle_button.setToolTip("ENABLED - Click to disable")
            else:
                toggle_button = QPushButton("○")  # Empty circle for disabled
                toggle_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: 1px solid #C62828;
                        border-radius: 3px;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 0px;
                        margin: 0px;
                    }
                    QPushButton:hover {
                        background-color: #da190b;
                        border-color: #B71C1C;
                    }
                """)
                toggle_button.setToolTip("DISABLED - Click to enable")
            
            toggle_button.setFixedSize(28, 24)  # Slightly wider for better visibility
            toggle_button.clicked.connect(lambda checked, r=row: self.toggle_rule_enabled(r))
            actions_layout.addWidget(toggle_button)
            
            # Duplicate button with simpler symbol
            dup_button = QPushButton("∞")  # Infinity symbol suggests duplication/copying
            dup_button.setFixedSize(28, 24)  # Match toggle button size
            dup_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: 1px solid #F57C00;
                    border-radius: 3px;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 0px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                    border-color: #E65100;
                }
            """)
            dup_button.setToolTip("DUPLICATE - Create a copy of this rule")
            dup_button.clicked.connect(lambda checked, r=row: self.duplicate_rule(r))
            actions_layout.addWidget(dup_button)
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.rules_table.setCellWidget(row, 4, actions_widget)
    
    def add_rule(self):
        """Add a new rule via dialog."""
        from ui.rule_editor_dialog import RuleEditorDialog
        
        dialog = RuleEditorDialog()
        if dialog.exec_() == dialog.Accepted:
            rule = dialog.get_rule()
            ConfigManager.add_regex_rule(**rule)
            self.load_rules()
            self.rules_changed.emit()
    
    def edit_selected_rule(self):
        """Edit the selected rule."""
        current_row = self.rules_table.currentRow()
        if current_row < 0:
            return
        
        from ui.rule_editor_dialog import RuleEditorDialog
        
        # Get current rule data
        rules = ConfigManager.get_regex_rules()
        if current_row >= len(rules):
            return
        
        current_rule = rules[current_row]
        
        dialog = RuleEditorDialog(current_rule)
        if dialog.exec_() == dialog.Accepted:
            rule_updates = dialog.get_rule()
            ConfigManager.update_regex_rule(current_row, **rule_updates)
            self.load_rules()
            self.rules_changed.emit()
    
    def delete_selected_rule(self):
        """Delete the selected rule after confirmation."""
        current_row = self.rules_table.currentRow()
        if current_row < 0:
            return
        
        # Get rule info for confirmation (Pattern is now column 0)
        pattern = self.rules_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, 
            'Delete Rule',
            f'Are you sure you want to delete the rule "{pattern}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            ConfigManager.remove_regex_rule(current_row)
            self.load_rules()
            self.rules_changed.emit()
    
    
    def import_rules(self):
        """Import rules from a file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            'Import Rules',
            '',
            'YAML files (*.yaml *.yml);;JSON files (*.json);;All files (*)'
        )
        
        if file_path:
            try:
                # Determine format from file extension
                format_type = 'yaml'
                if file_path.lower().endswith(('.json',)):
                    format_type = 'json'
                
                imported_rules = ConfigManager.import_rules_from_file(file_path, format_type)
                
                # Ask if user wants to append or replace
                reply = QMessageBox.question(
                    self,
                    'Import Rules',
                    f'Found {len(imported_rules)} rules. Do you want to:\n\n'
                    'Yes: Replace all existing rules\n'
                    'No: Add to existing rules\n'
                    'Cancel: Cancel import',
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Replace all rules
                    ConfigManager.set_regex_rules(imported_rules)
                elif reply == QMessageBox.No:
                    # Append to existing rules
                    existing_rules = ConfigManager.get_regex_rules()
                    existing_rules.extend(imported_rules)
                    ConfigManager.set_regex_rules(existing_rules)
                else:
                    return  # Cancel
                
                self.load_rules()
                self.rules_changed.emit()
                
                QMessageBox.information(
                    self,
                    'Import Complete',
                    f'Successfully imported {len(imported_rules)} rules.'
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Import Error',
                    f'Failed to import rules:\n{str(e)}'
                )
    
    def export_rules(self):
        """Export rules to a file."""
        rules = ConfigManager.get_regex_rules()
        if not rules:
            QMessageBox.information(
                self,
                'No Rules',
                'No rules to export.'
            )
            return
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            'Export Rules',
            'regex_rules.yaml',
            'YAML files (*.yaml *.yml);;JSON files (*.json);;All files (*)'
        )
        
        if file_path:
            try:
                # Determine format from file extension
                format_type = 'yaml'
                if file_path.lower().endswith(('.json',)):
                    format_type = 'json'
                
                ConfigManager.export_rules_to_file(file_path, rules, format_type)
                
                QMessageBox.information(
                    self,
                    'Export Complete',
                    f'Successfully exported {len(rules)} rules to:\n{file_path}'
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Export Error',
                    f'Failed to export rules:\n{str(e)}'
                )
    
    def test_rules(self):
        """Test the current rules against the input text."""
        input_text = self.test_input.toPlainText()
        if not input_text.strip():
            self.test_output.setText("Please enter test input text.")
            return
        
        try:
            # Import the regex plugin to test
            from plugins.available.regex_plugin import RegexProcessor
            
            # Get current rules from config
            current_rules = ConfigManager.get_regex_rules()
            
            # Create processor instance with current rules
            processor = RegexProcessor(current_rules)
            
            # Process the text
            result = processor.process(input_text)
            
            self.test_output.setText(result)
            
        except Exception as e:
            self.test_output.setText(f"Error testing rules: {str(e)}")
    
    def update_button_states(self):
        """Update button enabled states based on selection."""
        has_selection = self.rules_table.currentRow() >= 0
        
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def toggle_rule_enabled(self, row):
        """Toggle the enabled state of a rule."""
        try:
            rules = ConfigManager.get_regex_rules()
            if 0 <= row < len(rules):
                # Toggle enabled state
                rules[row]['enabled'] = not rules[row].get('enabled', True)
                ConfigManager.set_regex_rules(rules)
                
                # Refresh the table
                self.load_rules()
                self.rules_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to toggle rule: {str(e)}')
    
    def duplicate_rule(self, row):
        """Duplicate a rule."""
        try:
            rules = ConfigManager.get_regex_rules()
            if 0 <= row < len(rules):
                # Copy the rule
                original_rule = rules[row].copy()
                original_rule['description'] = f"Copy of {original_rule.get('description', original_rule.get('pattern', 'rule'))}"
                
                # Add the copy
                ConfigManager.add_regex_rule(**original_rule)
                
                # Refresh the table
                self.load_rules()
                self.rules_changed.emit()
                
                QMessageBox.information(self, 'Rule Duplicated', 'Rule has been duplicated successfully.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to duplicate rule: {str(e)}')
    
    def save_changes(self):
        """Save any pending changes (called from parent settings window)."""
        # Changes are saved immediately when rules are modified
        # This method is here for compatibility with the settings window interface
        pass
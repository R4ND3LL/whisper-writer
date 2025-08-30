import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QCheckBox, QMessageBox, QFileDialog,
    QTextEdit, QLabel, QSplitter, QGroupBox, QLineEdit
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
        self.rules_table.setColumnCount(6)
        self.rules_table.setHorizontalHeaderLabels([
            "Enabled", "Pattern", "Replacement", "Type", "Description", "Actions"
        ])
        
        # Set table properties
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Enabled
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Pattern
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Replacement  
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Description
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Actions
        
        rules_layout.addWidget(self.rules_table)
        
        # Buttons row
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Rule")
        self.add_button.clicked.connect(self.add_rule)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_selected_rule)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected_rule)
        buttons_layout.addWidget(self.delete_button)
        
        buttons_layout.addStretch()
        
        self.import_button = QPushButton("Import...")
        self.import_button.clicked.connect(self.import_rules)
        buttons_layout.addWidget(self.import_button)
        
        self.export_button = QPushButton("Export...")
        self.export_button.clicked.connect(self.export_rules)
        buttons_layout.addWidget(self.export_button)
        
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
        
        # Test button
        test_button = QPushButton("Test Rules")
        test_button.clicked.connect(self.test_rules)
        test_layout.addWidget(test_button)
        
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
    
    def load_rules(self):
        """Load rules from configuration into the table."""
        rules = ConfigManager.get_regex_rules()
        
        self.rules_table.setRowCount(len(rules))
        
        for row, rule in enumerate(rules):
            # Enabled checkbox
            enabled_checkbox = QCheckBox()
            enabled_checkbox.setChecked(rule.get('enabled', True))
            enabled_checkbox.stateChanged.connect(lambda state, r=row: self.rule_enabled_changed(r, state))
            self.rules_table.setCellWidget(row, 0, enabled_checkbox)
            
            # Pattern
            pattern_item = QTableWidgetItem(rule.get('pattern', ''))
            self.rules_table.setItem(row, 1, pattern_item)
            
            # Replacement
            replacement_item = QTableWidgetItem(rule.get('replacement', ''))
            self.rules_table.setItem(row, 2, replacement_item)
            
            # Type
            rule_type = "Text" if not rule.get('is_regex', True) else "Regex"
            type_item = QTableWidgetItem(rule_type)
            self.rules_table.setItem(row, 3, type_item)
            
            # Description
            description_item = QTableWidgetItem(rule.get('description', ''))
            self.rules_table.setItem(row, 4, description_item)
            
            # Actions - empty for now, could add quick edit buttons later
            action_item = QTableWidgetItem('')
            self.rules_table.setItem(row, 5, action_item)
    
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
        
        # Get rule info for confirmation
        pattern = self.rules_table.item(current_row, 1).text()
        
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
    
    def rule_enabled_changed(self, row, state):
        """Handle rule enabled state change."""
        enabled = state == Qt.Checked
        ConfigManager.update_regex_rule(row, enabled=enabled)
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
            
            # Create processor instance
            processor = RegexProcessor()
            
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
    
    def save_changes(self):
        """Save any pending changes (called from parent settings window)."""
        # Changes are saved immediately when rules are modified
        # This method is here for compatibility with the settings window interface
        pass
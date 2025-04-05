import sys
import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QLabel, QFormLayout, QFrame, QCheckBox
from PySide6.QtCore import Qt

ignore_fields=['filename', 'duration', 'path']
track_fields = []

class JsonEditorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Famulus 4.0 - Capture Editor")
        self.setGeometry(300, 300, 800, 600)

        self.json_data = None
        self.file_path = None
        self.file_opened = False
        self.layout = QVBoxLayout()
        
        # Button to open JSON file
        self.open_button = QPushButton("Open Capture File")
        self.open_button.clicked.connect(self.open_json_file)
        self.layout.addWidget(self.open_button)

        # Form layout for editable fields
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        # Save button to save JSON file
        self.save_button = QPushButton("Save Capture File")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_json_file)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def open_json_file(self):

        # Clear any existing widgets in the form layout
        for i in reversed(range(self.form_layout.count())):
            widget = self.form_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Capture File", "", "Capture Files (*.cap);;All Files (*)", options=options)
        
        if file_name:
            self.file_path = file_name
            with open(file_name, 'r') as f:
                self.json_data = json.load(f)
            self.populate_form()
            self.save_button.setEnabled(True)

    def populate_form(self):
        if not self.json_data:
            return

        # Clear any existing widgets in the form layout
        for i in reversed(range(self.form_layout.count())):
            widget = self.form_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Only show "metadata" and hide "commands"
        if "metadata" in self.json_data:
            metadata = self.json_data["metadata"]
            
            # Ensure that metadata is a dictionary, otherwise, skip it
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    if key in ignore_fields: continue
                    if isinstance(value, str):  # Text field
                        edit_field = QLineEdit(value)
                        edit_field.setObjectName(key)
                        self.form_layout.addRow(QLabel(key), edit_field)
                    elif isinstance(value, int):  # Text field
                        edit_field = QLineEdit(json.dumps(value))
                        edit_field.setObjectName(key)
                        self.form_layout.addRow(QLabel(key), edit_field)
                    elif isinstance(value, dict):  # If it's a dictionary, add a nested field
                        if key == 'track':
                            title_label = QLabel("Music Track")
                            title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
                            self.form_layout.addRow(title_label)

                            # Add a separator for visual differentiation
                            separator = QFrame()
                            separator.setFrameShape(QFrame.HLine)
                            separator.setFrameShadow(QFrame.Sunken)
                            self.form_layout.addRow(separator)

                            # Special field for file picker (if the field "file_path" exists in metadata)
                            if "path" in self.json_data["metadata"]["track"]:
                                file_picker = QLineEdit(self.json_data["metadata"]["track"]["path"])
                                file_picker.setObjectName(f'{key}-path')
                                file_picker.setReadOnly(True)  # Make it non-editable
                                file_picker.setPlaceholderText("Select a file...")
                                file_picker.mousePressEvent = self.file_picker_click
                                self.form_layout.addRow(QLabel("Music Path"), file_picker)
                        
                        for value_key in value.keys():
                            if value_key in ignore_fields: continue

                            if isinstance(value[value_key], bool):  # Boolean field with a checkbox
                                checkbox = QCheckBox()
                                checkbox.setChecked(value[value_key])  # Check the checkbox if the value is True
                                checkbox.setObjectName(f'{key}-{value_key}')

                                # Connect checkbox change to update the JSON data
                                checkbox.stateChanged.connect(lambda state, key=key, subkey=value_key: self.update_checkbox_value(state, key, value_key))

                                # Add the checkbox to the form
                                self.form_layout.addRow(QLabel(value_key), checkbox)
                            else:
                                nested_field = QLineEdit(json.dumps(value[value_key]))
                                nested_field.setObjectName(f'{key}-{value_key}')
                                self.form_layout.addRow(QLabel(value_key), nested_field)
                    
                    elif isinstance(value, list):  # If it's a list, display it as JSON text
                        list_field = QLineEdit(json.dumps(value))
                        list_field.setObjectName(key)
                        self.form_layout.addRow(QLabel(key), list_field)

    def file_picker_click(self, event):
        # Open file dialog when user clicks on the file path field
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_name:
            # Update the file picker field with the selected file
            field = self.findChild(QLineEdit, 'track-path')
            if field:
                field.setText(file_name)

    def update_checkbox_value(self, state, key, subkey):
        """Update the JSON data with the new checkbox state (True or False)."""
        print (key, subkey)
        if "metadata" in self.json_data:
            # Convert checkbox state to boolean (Qt.Checked means True, Qt.Unchecked means False)
            self.json_data["metadata"][key][subkey] = state == Qt.Checked

    def save_json_file(self):
        if not self.json_data or not self.file_path:
            return
        
        # Update json_data with the current values from the form
        print ('before')
        print (self.json_data["metadata"])
        for i in range(self.form_layout.rowCount()):
            print (self.form_layout.itemAt(i, QFormLayout.FieldRole))
            print (i)
            # If open is hit twice, many items become None
            if self.form_layout.itemAt(i, QFormLayout.FieldRole) is None: continue
            field_widget = self.form_layout.itemAt(i, QFormLayout.FieldRole).widget()
            
            if isinstance(field_widget, QLineEdit) or isinstance(field_widget, QCheckBox) or isinstance(field_widget, QFileDialog):
                key = field_widget.objectName()
                
                if isinstance(field_widget, QLineEdit) or isinstance(field_widget, QFileDialog):
                    value = field_widget.text()
                    if value.lstrip('-').isdigit(): value = int(value)
                elif isinstance(field_widget, QCheckBox):
                    value = field_widget.isChecked()
                print (key, value, type(value))

                if '-' in key:
                    _key=key.split('-')[0]
                    subkey=key.split('-')[1]
                    self.json_data["metadata"][_key][subkey] = value
                else:
                    self.json_data["metadata"][key] = value

        
        # Save the updated JSON back to the file
        with open(self.file_path, 'w') as f:
            json.dump(self.json_data, f, indent=4)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JsonEditorApp()
    window.show()
    sys.exit(app.exec())

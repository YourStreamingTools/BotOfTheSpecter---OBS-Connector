import sys
import os
import keyring
import configparser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QLabel, QDialog

# Paths for settings and API key storage
settings_dir = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', 'YourStreamingTools', 'BotOfTheSpecterOBSConnector')
settings_path = os.path.join(settings_dir, 'settings.ini')

# Ensure the settings directory exists
if not os.path.exists(settings_dir):
    os.makedirs(settings_dir)

# Load settings from the INI file
def load_settings():
    config = configparser.ConfigParser()
    if os.path.exists(settings_path):
        config.read(settings_path)
        return config
    else:
        return {'OBS': {'obsUrl': 'ws://localhost', 'obsPort': '4455', 'obsPassword': ''}}

# Save settings to the INI file
def save_settings(settings):
    config = configparser.ConfigParser()
    config.read_dict(settings)
    with open(settings_path, 'w') as configfile:
        config.write(configfile)

# Settings Window
class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 300)
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText("Enter API Key")
        self.obs_url_input = QLineEdit(self)
        self.obs_url_input.setPlaceholderText("Enter OBS URL")
        self.obs_port_input = QLineEdit(self)
        self.obs_port_input.setPlaceholderText("Enter OBS Port")
        self.obs_password_input = QLineEdit(self)
        self.obs_password_input.setPlaceholderText("Enter OBS Password")
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_settings)
        layout = QVBoxLayout()
        layout.addWidget(self.api_key_input)
        layout.addWidget(self.obs_url_input)
        layout.addWidget(self.obs_port_input)
        layout.addWidget(self.obs_password_input)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def load_settings(self):
        settings = load_settings()
        api_key = keyring.get_password("BotOfTheSpecter", "apiAuthKey") or ""
        self.api_key_input.setText(api_key)
        self.obs_url_input.setText(settings['OBS']['obsUrl'])
        self.obs_port_input.setText(settings['OBS']['obsPort'])
        self.obs_password_input.setText(settings['OBS']['obsPassword'])

    def save_settings(self):
        api_key = self.api_key_input.text()
        settings = {
            'OBS': {
                'obsUrl': self.obs_url_input.text(),
                'obsPort': self.obs_port_input.text(),
                'obsPassword': self.obs_password_input.text()
            }
        }
        save_settings(settings)
        keyring.set_password("BotOfTheSpecter", "apiAuthKey", api_key)
        self.close()

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bot Of The Specter OBS Connector")
        self.setGeometry(100, 100, 800, 600)
        # Create buttons for opening settings and logs
        settings_button = QPushButton("Settings", self)
        settings_button.clicked.connect(self.open_settings)
        logs_button = QPushButton("Logs", self)
        layout = QVBoxLayout()
        layout.addWidget(settings_button)
        layout.addWidget(logs_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_settings(self):
        settings_window = SettingsWindow()
        settings_window.load_settings()
        settings_window.exec_()

# Main Application
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

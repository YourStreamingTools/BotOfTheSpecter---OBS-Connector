import sys
import os
import keyring
import configparser
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QPushButton, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QStackedWidget
from PyQt5.QtGui import QIcon

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

# API key validation function
def validate_api_key(api_key):
    try:
        response = requests.get('https://api.botofthespecter.com/checkkey', params={'api_key': api_key}, timeout=5)
        if response.status_code == 200:
            return response.json().get('status') == 'Valid API Key'
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error validating API Key: {e}")
        return False

# Settings Window
class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        title_label = QLabel("API Key Required", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding-bottom: 20px; color: #FFFFFF;")
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText("Enter API Key")
        self.api_key_input.setStyleSheet("background-color: #555555; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        save_button = QPushButton("Save API Key", self)
        save_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        save_button.clicked.connect(self.save_api_key)
        form_layout = QFormLayout()
        form_layout.addRow("API Key:", self.api_key_input)
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(save_button)
        self.setLayout(main_layout)

    def save_api_key(self):
        api_key = self.api_key_input.text()
        if validate_api_key(api_key):
            keyring.set_password("BotOfTheSpecter", "apiAuthKey", api_key)
            self.parent().stack.setCurrentIndex(0)
        else:
            error_label = QLabel("Invalid API Key. Please try again.", self)
            error_label.setStyleSheet("color: red; font-size: 12px;")
            self.layout().addWidget(error_label)

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bot Of The Specter OBS Connector")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('assets/icons/app-icon.png'))
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        self.main_page = QWidget()
        main_layout = QVBoxLayout()
        title_label = QLabel("Bot Of The Specter OBS Connector", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF;")
        settings_button = QPushButton("Settings", self)
        settings_button.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        settings_button.clicked.connect(self.show_settings)
        logs_button = QPushButton("Logs", self)
        logs_button.setStyleSheet("background-color: #FF5733; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        main_layout.addWidget(title_label)
        main_layout.addWidget(settings_button)
        main_layout.addWidget(logs_button)
        self.main_page.setLayout(main_layout)
        self.settings_page = SettingsPage()
        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.settings_page)
        self.stack.setCurrentIndex(0)

    def show_settings(self):
        self.stack.setCurrentIndex(1)

# Main Application
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    api_key = keyring.get_password("BotOfTheSpecter", "apiAuthKey")
    if not api_key:
        settings_page = SettingsPage()
        app.setActiveWindow(settings_page)
        settings_page.show()
    else:
        main_window = MainWindow()
        main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
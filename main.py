import sys
import os
import keyring
import configparser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QLabel, QDialog, QGroupBox, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon, QColor

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
        self.setWindowIcon(QIcon('assets/icons/app-icon.png'))
        title_label = QLabel("OBS Settings", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding-bottom: 20px; color: #FFFFFF;")
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText("Enter API Key")
        self.api_key_input.setStyleSheet("background-color: #555555; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        self.obs_url_input = QLineEdit(self)
        self.obs_url_input.setPlaceholderText("Enter OBS URL")
        self.obs_url_input.setStyleSheet("background-color: #555555; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        self.obs_port_input = QLineEdit(self)
        self.obs_port_input.setPlaceholderText("Enter OBS Port")
        self.obs_port_input.setStyleSheet("background-color: #555555; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        self.obs_password_input = QLineEdit(self)
        self.obs_password_input.setPlaceholderText("Enter OBS Password")
        self.obs_password_input.setEchoMode(QLineEdit.Password)
        self.obs_password_input.setStyleSheet("background-color: #555555; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        save_button = QPushButton("Save", self)
        save_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        save_button.clicked.connect(self.save_settings)
        form_layout = QFormLayout()
        form_layout.addRow("API Key:", self.api_key_input)
        form_layout.addRow("OBS URL:", self.obs_url_input)
        form_layout.addRow("OBS Port:", self.obs_port_input)
        form_layout.addRow("OBS Password:", self.obs_password_input)
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(save_button)
        self.setLayout(main_layout)

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
        self.setWindowIcon(QIcon('assets/icons/app-icon.png'))
        title_label = QLabel("Bot Of The Specter OBS Connector", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #FFFFFF;")
        settings_button = QPushButton("Settings", self)
        settings_button.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        settings_button.clicked.connect(self.open_settings)
        logs_button = QPushButton("Logs", self)
        logs_button.setStyleSheet("background-color: #FF5733; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addWidget(settings_button)
        main_layout.addWidget(logs_button)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_settings(self):
        settings_window = SettingsWindow()
        settings_window.load_settings()
        settings_window.exec_()

# Main Application
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = app.palette()
    palette.setColor(palette.Window, QColor("#333333"))
    palette.setColor(palette.WindowText, QColor("#FFFFFF"))
    palette.setColor(palette.Base, QColor("#444444"))
    palette.setColor(palette.AlternateBase, QColor("#555555"))
    palette.setColor(palette.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(palette.ToolTipText, QColor("#333333"))
    app.setPalette(palette)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

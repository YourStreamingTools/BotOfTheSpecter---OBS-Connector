import sys
import os
import configparser
import aiohttp
import asyncio
import urllib.parse
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QPushButton, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QStackedWidget, QHBoxLayout
from PyQt5.QtGui import QIcon, QColor
import socketio
from socketio import AsyncClient as SocketClient
import obswebsocket
from obswebsocket import obsws
from obswebsocket import requests as obsrequests

# Paths for storage
settings_dir = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', 'YourStreamingTools', 'BotOfTheSpecter')
icon_path = os.path.join(settings_dir, 'app-icon.ico')
settings_path = os.path.join(settings_dir, 'OBSConnectorSettings.ini')

# Globals
specterSocket = SocketClient()
VERSION = "1.0"

# Ensure the settings directory exists
if not os.path.exists(settings_dir):
    os.makedirs(settings_dir)

# Download the icon file if it does not exist
async def download_icon():
    if not os.path.exists(icon_path):
        url = 'https://cdn.botofthespecter.com/app-builds/assets/icons/app-icon.ico'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(icon_path, 'wb') as f:
                            f.write(await response.read())
        except Exception as e:
            print(f"Error downloading icon: {e}")

# Run the icon download
asyncio.run(download_icon())

# Load settings from the INI file
def load_settings():
    config = configparser.ConfigParser()
    if os.path.exists(settings_path):
        config.read(settings_path)
        if 'VERSION' in config:
            stored_version = config['VERSION'].get('version', None)
            if stored_version != VERSION:
                api_settings = dict(config.items('API')) if 'API' in config else {}
                obs_settings = dict(config.items('OBS')) if 'OBS' in config else {}
                os.remove(settings_path)
                config = configparser.ConfigParser()
                config.add_section('VERSION')
                config.set('VERSION', 'version', VERSION)
                config.add_section('API')
                for key, value in api_settings.items():
                    config.set('API', key, value)
                config.add_section('OBS')
                for key, value in obs_settings.items():
                    config.set('OBS', key, value)
                with open(settings_path, 'w') as f:
                    config.write(f)
        else:
            api_settings = dict(config.items('API')) if 'API' in config else {}
            obs_settings = dict(config.items('OBS')) if 'OBS' in config else {}
            os.remove(settings_path)
            config = configparser.ConfigParser()
            config.add_section('VERSION')
            config.set('VERSION', 'version', VERSION)
            config.add_section('API')
            for key, value in api_settings.items():
                config.set('API', key, value)
            config.add_section('OBS')
            for key, value in obs_settings.items():
                config.set('OBS', key, value)
            with open(settings_path, 'w') as f:
                config.write(f)
    else:
        config.add_section('VERSION')
        config.set('VERSION', 'version', VERSION)
        config.add_section('API')
        config.set('API', 'apiKey', '')
        config.add_section('OBS')
        config.set('OBS', 'server_ip', 'localhost')
        config.set('OBS', 'server_port', '4455')
        config.set('OBS', 'server_password', '')
        with open(settings_path, 'w') as f:
            config.write(f)
    return config

# Save settings to the INI file
def save_settings(config):
    with open(settings_path, 'w') as configfile:
        config.write(configfile)

# Get the settings for the OBS WebSocket Server
async def obs_websocket_settings():
    settings = load_settings()
    server_ip = settings.get('OBS', 'server_ip', fallback='localhost')
    server_port = settings.get('OBS', 'server_port', fallback='4455')
    server_password = settings.get('OBS', 'server_password', fallback='')
    return server_ip, server_port, server_password

# API key validation function
async def validate_api_key(api_key):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.botofthespecter.com/checkkey', params={'api_key': api_key}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('status') == 'Valid API Key'
        return False
    except aiohttp.exceptions.RequestException as e:
        return False

# WebSocket connection event handler
async def specter_websocket(specter_thread):
    specter_websocket_uri = "wss://websocket.botofthespecter.com"
    while True:
        try:
            await specterSocket.connect(specter_websocket_uri)
            specter_thread.connection_status.emit(True)
            await specterSocket.wait()
        except socketio.exceptions.ConnectionError as e:
            specter_thread.connection_status.emit(False)
            await asyncio.sleep(10)
        except Exception as e:
            specter_thread.connection_status.emit(False)
            await asyncio.sleep(10)

# Function to connect to OBS WebSocket server
async def obs_websocket(obs_thread):
    cancellation_event = asyncio.Event()
    while True:
        try:
            server_ip, server_port, server_password = await obs_websocket_settings()
            obsSocket = obsws(server_ip, server_port, server_password)
            obsSocket.connect()
            obs_thread.obs_connection_status.emit(True)
            obsSocket.register(on_event)
            await cancellation_event.wait()
            if cancellation_event.is_set():
                break
        except obswebsocket.exceptions.ConnectionFailure as ConnectionFailure:
            obs_thread.obs_connection_status.emit(False)
            await asyncio.sleep(10)
        except Exception as e:
            obs_thread.obs_connection_status.emit(False)
            await asyncio.sleep(10)
        if obsSocket.connected:
            obsSocket.disconnect()

# Handle OBS events and send them to Specter server
def on_event(event):
    asyncio.run(send_obs_event_to_specter(event))

async def send_obs_event_to_specter(event):
    try:
        simplified_event = {}
        event_type = getattr(event, 'update_type', None)
        if event_type == 'SceneItemEnableStateChanged':
            simplified_event = {
                'event-name': event_type,
                'scene-name': getattr(event, 'sceneName', None),
                'source-name': getattr(event, 'itemName', None),
                'item-enabled': getattr(event, 'itemEnabled', None)
            }
        elif event_type == 'SceneListChanged':
            simplified_event = {
                'event-name': event_type,
                'scenes': [scene['name'] for scene in getattr(event, 'scenes', [])]
            }
        elif event_type == 'SceneCreated':
            simplified_event = {
                'event-name': event_type,
                'scene-name': getattr(event, 'sceneName', None),
                'sources': [source['sourceName'] for source in getattr(event, 'sources', [])]
            }
        elif event_type == 'SceneTransitionStarted':
            simplified_event = {
                'event-name': event_type,
                'from-scene': getattr(event, 'from_scene', None),
                'to-scene': getattr(event, 'to_scene', None),
            }
        elif event_type == 'SceneTransitionVideoEnded':
            simplified_event = {
                'event-name': event_type,
            }
        elif event_type == 'CurrentProgramSceneChanged':
            simplified_event = {
                'event-name': event_type,
                'scene-name': getattr(event, 'scene_name', None)
            }
        elif event_type == 'SceneTransitionEnded':
            simplified_event = {
                'event-name': event_type,
            }
        API_TOKEN = load_settings()['API'].get('apiKey')
        params = {
            'code': API_TOKEN,
            'event': 'OBS_EVENT',
            'data': simplified_event
        }
        async with aiohttp.ClientSession() as session:
            encoded_params = urllib.parse.urlencode(params)
            url = f'https://websocket.botofthespecter.com/notify?{encoded_params}'
            async with session.get(url) as response:
                if response.status == 200:
                    print(f"HTTP event 'OBS_EVENT' sent successfully with params: {params}")
                else:
                    print(f"Failed to send HTTP event 'OBS_EVENT'. Status: {response.status}")
    except Exception as e:
        print(f"Error sending OBS event to Specter: {e}")

# Handle successful registration or connection
@specterSocket.event
async def event_success(data):
    if hasattr(SpecterWebSocketThread, 'connection_status'):
        SpecterWebSocketThread.connection_status.emit(True)

# Handle server errors or failure to connect
@specterSocket.event
async def event_failure(data):
    if hasattr(SpecterWebSocketThread, 'connection_status'):
        SpecterWebSocketThread.connection_status.emit(False)

# Handle disconnection
@specterSocket.event
async def disconnect():
    if hasattr(SpecterWebSocketThread, 'connection_status'):
        SpecterWebSocketThread.connection_status.emit(False)

# Settings Window
class SettingsPage(QWidget):
    api_key_saved = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        title_label = QLabel("Specter System API Key", self)
        title_label.setAlignment(Qt.AlignHCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding-bottom: 20px; color: #FFFFFF;")
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText("Enter API Key")
        self.api_key_input.setStyleSheet("background-color: #555555; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        settings = load_settings()
        api_key = settings['API'].get('apiKey', '') if 'API' in settings else ''
        self.api_key_input.setText(api_key)
        save_button = QPushButton("Save API Key", self)
        save_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        save_button.clicked.connect(self.save_api_key)
        self.error_label = QLabel("", self)
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        back_button = QPushButton("Back", self)
        back_button.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        back_button.clicked.connect(self.go_back)
        form_layout = QFormLayout()
        form_layout.addRow("API Key:", self.api_key_input)
        form_layout.addRow(self.error_label)
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(save_button)
        main_layout.addWidget(back_button)
        self.setLayout(main_layout)

    def save_api_key(self):
        api_key = self.api_key_input.text()
        settings = load_settings()
        if settings:
            try:
                if api_key != settings['API'].get('apiKey', ''):
                    if asyncio.run(validate_api_key(api_key)):
                        settings.set('API', 'apiKey', api_key)
                        save_settings(settings)
                        self.error_label.setText("")
                        self.api_key_saved.emit()
                        self.main_window.show_main_page()
                    else:
                        self.error_label.setText("Invalid API Key. Please try again.")
                else:
                    self.error_label.setText("API Key is already set.")
            except AttributeError:
                if api_key != settings['API'].get('apikey', ''):
                    if asyncio.run(validate_api_key(api_key)):
                        settings.set('API', 'apiKey', api_key)
                        save_settings(settings)
                        self.error_label.setText("")
                        self.api_key_saved.emit()
                        self.main_window.show_main_page()
                    else:
                        self.error_label.setText("Invalid API Key. Please try again.")
                else:
                    self.error_label.setText("API Key is already set.")
        else:
            self.error_label.setText("Failed to load settings.")
    
    def go_back(self):
        self.main_window.show_main_page()

# OBS Settings Window
class OBSSettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        title_label = QLabel("OBS WebSocket Settings", self)
        title_label.setAlignment(Qt.AlignHCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding-bottom: 20px; color: #FFFFFF;")
        settings = load_settings()
        self.server_ip_input = QLineEdit(self)
        self.server_ip_input.setText(settings.get('OBS', 'server_ip', fallback='localhost'))
        self.server_ip_input.setPlaceholderText("Enter OBS WebSocket IP")
        self.server_ip_input.setStyleSheet("background-color: #555555; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        self.server_port_input = QLineEdit(self)
        self.server_port_input.setText(settings.get('OBS', 'server_port', fallback='4455'))
        self.server_port_input.setPlaceholderText("Enter OBS WebSocket Port")
        self.server_port_input.setStyleSheet("background-color: #555555; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        self.server_password_input = QLineEdit(self)
        self.server_password_input.setText(settings.get('OBS', 'server_password', fallback=''))
        self.server_password_input.setPlaceholderText("Enter OBS WebSocket Password")
        self.server_password_input.setStyleSheet("background-color: #555555; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        save_button = QPushButton("Save OBS Settings", self)
        save_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        save_button.clicked.connect(self.save_obs_settings)
        back_button = QPushButton("Back", self)
        back_button.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        back_button.clicked.connect(self.go_back)
        form_layout = QFormLayout()
        form_layout.addRow("Server IP:", self.server_ip_input)
        form_layout.addRow("Server Port:", self.server_port_input)
        form_layout.addRow("Server Password:", self.server_password_input)
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(save_button)
        main_layout.addWidget(back_button)
        self.setLayout(main_layout)

    def save_obs_settings(self):
        server_ip = self.server_ip_input.text()
        server_port = self.server_port_input.text()
        server_password = self.server_password_input.text()
        settings = load_settings()
        settings.set('OBS', 'server_ip', server_ip)
        settings.set('OBS', 'server_port', server_port)
        settings.set('OBS', 'server_password', server_password)
        save_settings(settings)
        self.main_window.show_main_page()

    def go_back(self):
        self.main_window.show_main_page()

# Thread for running Specter websocket
class SpecterWebSocketThread(QThread):
    connection_status = pyqtSignal(bool)
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(specter_websocket(self))
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            pass
        finally:
            loop.close()

# Thread for running OBS websocket
class OBSWebSocketThread(QThread):
    obs_connection_status = pyqtSignal(bool)
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(obs_websocket(self))
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            pass
        finally:
            loop.close()

# MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BotOfTheSpecter OBS Connector")
        self.setGeometry(100, 100, 500, 250)
        self.setWindowIcon(QIcon(icon_path))
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        # Main page layout
        self.main_page = QWidget()
        main_layout = QVBoxLayout()
        # Title label
        title_label = QLabel("BotOfTheSpecter OBS Connector", self)
        title_label.setAlignment(Qt.AlignHCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        # Connection status labels
        self.connection_status_label = QLabel("Specter WebSocket Connection: Not Connected", self)
        self.connection_status_label.setAlignment(Qt.AlignCenter)
        self.connection_status_label.setStyleSheet("font-size: 16px; color: #FF0000;")
        self.obs_connection_status_label = QLabel("OBS WebSocket Connection: Not Connected", self)
        self.obs_connection_status_label.setAlignment(Qt.AlignCenter)
        self.obs_connection_status_label.setStyleSheet("font-size: 16px; color: #FF0000;")
        # Group the connection status labels
        status_layout = QVBoxLayout()
        status_layout.setSpacing(0)
        status_layout.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.connection_status_label)
        status_layout.addWidget(self.obs_connection_status_label)
        # Buttons layout
        button_layout = QHBoxLayout()
        api_key_button = QPushButton("API Key", self)
        api_key_button.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        api_key_button.clicked.connect(self.show_api_key_page)
        obs_settings_button = QPushButton("OBS Settings", self)
        obs_settings_button.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        obs_settings_button.clicked.connect(self.show_obs_settings_page)
        button_layout.addWidget(api_key_button)
        button_layout.addWidget(obs_settings_button)
        # Add elements to the main layout
        main_layout.addWidget(title_label)
        main_layout.addLayout(status_layout)
        main_layout.addLayout(button_layout)
        self.main_page.setLayout(main_layout)
        self.stack.addWidget(self.main_page)
        # Settings pages
        self.settings_page = SettingsPage(self)
        self.settings_page.api_key_saved.connect(self.show_main_page)
        self.stack.addWidget(self.settings_page)
        self.obs_settings_page = OBSSettingsPage(self)
        self.stack.addWidget(self.obs_settings_page)
        # Start separate threads for each WebSocket connection
        self.specter_thread = SpecterWebSocketThread()
        self.specter_thread.connection_status.connect(self.update_connection_status)
        self.specter_thread.start()
        self.obs_thread = OBSWebSocketThread()
        self.obs_thread.obs_connection_status.connect(self.update_obs_connection_status)
        self.obs_thread.start()
        # Load settings and display the appropriate page
        settings = load_settings()
        if not settings.get('API', 'apiKey'):
            self.show_api_key_page()
        else:
            self.show_main_page()

    def show_api_key_page(self):
        self.stack.setCurrentWidget(self.settings_page)

    def show_obs_settings_page(self):
        self.stack.setCurrentWidget(self.obs_settings_page)

    def show_main_page(self):
        self.stack.setCurrentWidget(self.main_page)

    def update_connection_status(self, connected):
        if connected:
            self.connection_status_label.setText("Specter WebSocket Connection: Connected")
            self.connection_status_label.setStyleSheet("font-size: 16px; color: #00FF00;")
        else:
            self.connection_status_label.setText("Specter WebSocket Connection: Not Connected")
            self.connection_status_label.setStyleSheet("font-size: 16px; color: #FF0000;")

    def update_obs_connection_status(self, connected):
        if connected:
            self.obs_connection_status_label.setText("OBS WebSocket Connection: Connected")
            self.obs_connection_status_label.setStyleSheet("font-size: 16px; color: #00FF00;")
        else:
            self.obs_connection_status_label.setText("OBS WebSocket Connection: Not Connected")
            self.obs_connection_status_label.setStyleSheet("font-size: 16px; color: #FF0000;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = app.palette()
    palette.setColor(palette.Window, QColor("#333333"))
    palette.setColor(palette.WindowText, QColor("#FFFFFF"))
    palette.setColor(palette.Base, QColor("#444444"))
    palette.setColor(palette.AlternateBase, QColor("#555555"))
    palette.setColor(palette.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(palette.ToolTipText, QColor("#000000"))
    app.setPalette(palette)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
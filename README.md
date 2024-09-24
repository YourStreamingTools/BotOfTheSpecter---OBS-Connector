# BotOfTheSpecter - OBS Connector

An Electron application that connects BotOfTheSpecter to OBS via WebSockets. This tool allows you to automate OBS actions based on events received from the BotOfTheSpecter WebSocket server.

## What It Does

- **Connects BotOfTheSpecter to OBS**: Facilitates communication between BotOfTheSpecter and OBS to automate streaming workflows.
- **Secure API Key Management**: Prompts you to enter your API Auth Key and securely stores it for future use.
- **Real-time Event Handling**: Receives events from the BotOfTheSpecter WebSocket server and logs them within the application.

## How It Works

1. **API Key Entry**: Upon launching the application, you will be prompted to enter your API Auth Key.
2. **WebSocket Connection**: After successful validation, the application automatically connects to the BotOfTheSpecter WebSocket server using your API Key.
3. **Event Logging**: The application logs all received events, which can be viewed within the app's interface.

---

This is an early version of the application, focusing on establishing a secure connection and receiving events. Future updates will include more features and functionalities to enhance your streaming experience.
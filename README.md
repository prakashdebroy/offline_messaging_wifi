# Secure WiFi Chat

This project is a secure chat application that enables encrypted communication between two devices over a local WiFi network. It utilizes AES encryption to ensure message confidentiality and supports automatic server discovery using UDP broadcasting.

## Features
- **AES-256 Encryption**: Messages are encrypted using a secure password-derived key.
- **WPA3 Network Check**: Warns the user if they are not connected to a WPA3-secured network.
- **Automatic Server Discovery**: Uses UDP broadcasting to detect available servers.
- **Bidirectional Chat**: Allows two-way encrypted messaging between a server and a client.
- **Multi-threaded Handling**: Ensures smooth message transmission and reception.
- **Offline Messaging**: Can be used offline, No internet is required.

## Requirements
- Python 3.x
- Required libraries:
  - `socket`
  - `threading`
  - `hashlib`
  - `subprocess`
  - `Crypto` 
  - `base64`
  - `os`
  - `time`

## Installation
1. Clone the repository or download the script.
   ```bash
   git clone https://github.com/prakashdebroy/offline_messaging_wifi.git
   ```
2. Install dependencies using:
   ```bash
   pip install pycryptodome
   ```

## Usage
### Starting as Server
1. Run the script and select **server mode**:
   ```bash
   python secure_chat.py
   ```
2. Enter a shared encryption password when prompted.
3. The server will wait for client connections and broadcast its presence.

### Starting as Client
1. Run the script and select **client mode**:
   ```bash
   python secure_chat.py
   ```
2. Enter the same shared encryption password.
3. The client will attempt to discover and connect to the server automatically.

## Security Considerations
- The application encrypts messages using AES-256 encryption with CFB mode.
- If connected to a non-WPA3 network, additional security measures should be considered.
- The encryption key is derived from the user-provided password using SHA-256.

## Notes
- Both the server and client must use the same password for successful authentication.
- The application only works on a local WiFi network and does not support internet-based messaging.

## License
This project is open-source and free to use. Modify and distribute as needed.

---
**File Name:** `README.md`


import socket
import threading
import hashlib
import subprocess
from Crypto.Cipher import AES
import base64
import os
import time

# AES encryption/decryption class
class SecureChat:
    def __init__(self, password):
        self.key = hashlib.sha256(password.encode()).digest()
        
    def encrypt(self, plaintext):
        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        ciphertext = iv + cipher.encrypt(plaintext.encode())
        return base64.b64encode(ciphertext).decode()
    
    def decrypt(self, encrypted_text):
        try:
            encrypted_text = base64.b64decode(encrypted_text)
            iv = encrypted_text[:16]
            cipher = AES.new(self.key, AES.MODE_CFB, iv)
            return cipher.decrypt(encrypted_text[16:]).decode()
        except:
            return None  # Return None if decryption fails

# Function to check if connected to a WPA3 network
def check_wpa3():
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
        if "WPA3" in output:
            print("[INFO] Connected to a WPA3-secured WiFi network.")
        else:
            print("[WARNING] You are NOT connected to a WPA3 network. Encryption will still be used, but your WiFi security may be weaker.")
    except Exception as e:
        print(f"[ERROR] Unable to check WPA3 status: {e}")

# Function to broadcast server presence
def broadcast_server(port=5001):
    server_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while True:
        try:
            server_broadcast.sendto(b"CHAT_SERVER", ('<broadcast>', port))
            time.sleep(2)
        except:
            break

# Function to discover server IP
def discover_server(port=5001, timeout=5):
    client_discovery = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_discovery.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_discovery.bind(("", port))
    client_discovery.settimeout(timeout)
    
    try:
        while True:
            data, addr = client_discovery.recvfrom(1024)
            if data == b"CHAT_SERVER":
                print(f"[DISCOVERY] Found server at {addr[0]}")
                return addr[0]
    except:
        print("[DISCOVERY] No server found.")
    return None

# Server function
def start_server(password, port=5000):
    check_wpa3()
    chat = SecureChat(password)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow socket reuse
    server.bind(("0.0.0.0", port))
    server.listen(5)
    
    threading.Thread(target=broadcast_server, daemon=True).start()
    
    print("[SERVER] Waiting for connections...")
    
    while True:
        conn, addr = server.accept()
        print(f"[SERVER] Connection from {addr}")
        
        # Send verification message to check password match
        conn.send(chat.encrypt("AUTH_CHECK").encode())
        response = conn.recv(1024).decode()
        if chat.decrypt(response) != "AUTH_CHECK":
            print("[SERVER] Incorrect password. Rejecting client.")
            conn.close()
            continue  # Wait for another connection
        
        print("[SERVER] Password verified. Connection established.")

        def receive_messages():
            while True:
                try:
                    encrypted_msg = conn.recv(1024).decode()
                    if not encrypted_msg:
                        print("[SERVER] Client disconnected.")
                        break
                    print(f"Friend: {chat.decrypt(encrypted_msg)}")
                except:
                    print("[SERVER] Client disconnected unexpectedly.")
                    break

            conn.close()  # Ensure the socket is closed before waiting for another connection

        threading.Thread(target=receive_messages, daemon=True).start()

        while True:
            msg = input("").strip()
            if msg:
                try:
                    conn.send(chat.encrypt(msg).encode())
                except:
                    break  # Exit sending loop if the client disconnects

        conn.close()  # Close connection after chat ends

# Client function
def start_client(password, port=5000):
    check_wpa3()
    
    while True:
        server_ip = discover_server()
        if not server_ip:
            print("[ERROR] No server found. Retrying in 5 seconds...")
            time.sleep(5)
            continue
        
        chat = SecureChat(password)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((server_ip, port))
        except:
            print("[CLIENT] Unable to connect. Retrying...")
            time.sleep(5)
            continue
        
        # Verify password with server
        client.send(chat.encrypt("AUTH_CHECK").encode())
        response = client.recv(1024).decode()
        if chat.decrypt(response) != "AUTH_CHECK":
            print("[CLIENT] Incorrect password. Disconnecting.")
            client.close()
            return
        
        print(f"[CLIENT] Connected to server at {server_ip}")
        
        def receive_messages():
            while True:
                try:
                    encrypted_msg = client.recv(1024).decode()
                    if not encrypted_msg:
                        print("[CLIENT] Disconnected from server.")
                        break
                    print(f"Friend: {chat.decrypt(encrypted_msg)}")
                except:
                    print("[CLIENT] Connection lost.")
                    break
            
            client.close()  # Ensure the socket is closed after disconnect

        threading.Thread(target=receive_messages, daemon=True).start()
        
        while True:
            msg = input("").strip()
            if msg:
                try:
                    client.send(chat.encrypt(msg).encode())
                except:
                    break  # Exit sending loop if the server disconnects
        
        client.close()
        break  # Exit the loop and stop retrying after disconnection

if __name__ == "__main__":
    mode = input("Start as (s)erver or (c)lient? ").strip().lower()
    password = input("Enter shared password for encryption: ")
    
    if mode == "s":
        start_server(password)
    elif mode == "c":
        start_client(password)
    else:
        print("Invalid mode selected.")

        
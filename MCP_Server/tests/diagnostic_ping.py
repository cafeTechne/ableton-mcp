import socket
import json
import time
import sys

def ping_ableton(port=9877):
    print(f"Attempting to connect to Ableton on port {port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect(('localhost', port))
        
        # Try to receive greeting
        try:
            greeting = sock.recv(1024).decode('utf-8')
            print(f"Received Greeting: {greeting}")
        except socket.timeout:
            print("No greeting received (timeout), but connected.")
        
        # Send a simple command that should DEFINITELY exist
        # We'll try 'get_song_context' which I just added, or 'get_session_info' which is core.
        cmd = {"type": "get_session_info", "params": {}}
        print(f"Sending check command: {json.dumps(cmd)}")
        sock.sendall(json.dumps(cmd).encode('utf-8'))
        
        time.sleep(0.5)
        response = sock.recv(4096).decode('utf-8')
        print(f"Received Response: {response}")
        
        sock.close()
        print("Diagnostic complete.")
        return True
    except ConnectionRefusedError:
        print("FAILED: Connection Refused. Is the Remote Script enabled in Ableton Preferences?")
    except Exception as e:
        print(f"FAILED with error: {str(e)}")
    return False

if __name__ == "__main__":
    ping_ableton()

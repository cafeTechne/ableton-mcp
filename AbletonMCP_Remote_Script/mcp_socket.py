# mcp_socket.py
from __future__ import absolute_import, print_function, unicode_literals
import socket
import json
import threading
import time
import traceback
import os

# Change queue import for Python 2
try:
    import Queue as queue  # Python 2
except ImportError:
    import queue  # Python 3

class AbletonMCPServer(object):
    """
    Handles the threaded socket server for AbletonMCP.
    Decoupled from Live API, communicating via callbacks.
    """
    def __init__(self, port, log_callback, command_callback):
        self.port = port
        self.log_message = log_callback
        self.process_command = command_callback
        self.host = os.environ.get("ABLETON_MCP_HOST", "localhost")
        
        self.socket = None
        self.server_thread_obj = None
        self.running = False
        self.client_threads = []

    def start(self):
        """Start the socket server in a separate thread"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            
            self.running = True
            self.server_thread_obj = threading.Thread(target=self._server_loop)
            self.server_thread_obj.daemon = True
            self.server_thread_obj.start()
            
            self.log_message("Server started on port " + str(self.port))
            return True
        except Exception as e:
            self.log_message("Error starting server: " + str(e))
            return False

    def stop(self):
        """Stop the server and close connections"""
        self.log_message("Stopping server...")
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        if self.server_thread_obj and self.server_thread_obj.is_alive():
            # Wait briefly
            self.server_thread_obj.join(1.0)
            
        # Clean up client threads
        for t in self.client_threads[:]:
            if t.is_alive():
                self.log_message("Client thread still alive during stop")
        
        self.log_message("Server stopped")

    def _server_loop(self):
        """Main server loop accepting connections"""
        try:
            self.log_message("Server thread started")
            self.socket.settimeout(1.0)
            
            while self.running:
                try:
                    client, address = self.socket.accept()
                    self.log_message("Connection accepted from " + str(address))
                    
                    t = threading.Thread(target=self._handle_client, args=(client,))
                    t.daemon = True
                    t.start()
                    
                    self.client_threads.append(t)
                    self.client_threads = [x for x in self.client_threads if x.is_alive()]
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log_message("Server accept error: " + str(e))
                    time.sleep(0.5)
        except Exception as e:
            self.log_message("Server thread crashed: " + str(e))

    def _handle_client(self, client):
        """Handle individual client connection"""
        client.settimeout(None)
        
        # Send greeting for handshake
        try:
            greeting = json.dumps({"status": "connected", "message": "AbletonMCP Ready"})
            try:
                client.sendall(greeting.encode('utf-8'))
            except AttributeError:
                client.sendall(greeting)
        except Exception as e:
            self.log_message("Error sending greeting: " + str(e))
            
        buffer = ''
        
        try:
            while self.running:
                try:
                    data = client.recv(8192)
                    if not data:
                        break
                    
                    # Buffer logic
                    try:
                        buffer += data.decode('utf-8')
                    except AttributeError:
                        buffer += data
                    
                    # Parse JSON
                    try:
                        while buffer: # Process all complete JSON objects in buffer if multiple?
                            # Simple JSON parser that relies on finding a valid object
                            # Actually, standard json.loads parses the whole string. 
                            # If we have partial data, it fails.
                            # We might have multiple concatenated JSONs or partial.
                            # The original code just did `json.loads(buffer)` and if successful cleared buffer.
                            # This implies the client sends one command at a time and we wait for it.
                            # But if we receive partial, we wait.
                            
                            # However, if we receive "}{", json.loads fails.
                            # The original code:
                            # command = json.loads(buffer)
                            # buffer = ''
                            # This assumes one command per buffer accumulation cycle until valid.
                            
                            command = json.loads(buffer)
                            buffer = '' # Clear buffer
                            
                            self.log_message("Received command: " + str(command.get("type", "unknown")))
                            
                            # CALLBACK
                            response = self.process_command(command)
                            
                            # Send response
                            resp_str = json.dumps(response)
                            try:
                                client.sendall(resp_str.encode('utf-8'))
                            except AttributeError:
                                client.sendall(resp_str)
                                
                    except ValueError:
                        # Incomplete JSON, continue waiting for data
                        continue
                        
                except Exception as e:
                    self.log_message("Error handling client data: " + str(e))
                    # Try sending error
                    err = {"status": "error", "message": str(e)}
                    try:
                        s = json.dumps(err)
                        try:
                             client.sendall(s.encode('utf-8'))
                        except AttributeError:
                             client.sendall(s)
                    except:
                        break
                    if not isinstance(e, ValueError):
                        break
        except Exception as e:
            self.log_message("Client handler error: " + str(e))
        finally:
            try:
                client.close()
            except: pass

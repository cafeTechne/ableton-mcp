# Mock _Framework.ControlSurface
import sys
from types import ModuleType

# Mock the structure if not exists
if "_Framework" not in sys.modules:
    framework = ModuleType("_Framework")
    sys.modules["_Framework"] = framework
    
    cs_mod = ModuleType("ControlSurface")
    class ControlSurface:
        def __init__(self, c): pass
        def log_message(self, m): print("LOG:", m)
        def show_message(self, m): print("MSG:", m)
        def song(self): return None
        def disconnect(self): pass
    
    cs_mod.ControlSurface = ControlSurface
    sys.modules["_Framework.ControlSurface"] = cs_mod
    framework.ControlSurface = cs_mod

# Mock modules to avoid import errors
import AbletonMCP_Remote_Script
from AbletonMCP_Remote_Script import AbletonMCP
from AbletonMCP_Remote_Script.mcp_socket import AbletonMCPServer

print("Import successful!")
s = AbletonMCPServer(9999, lambda x: print(x), lambda x: {})
print("Server instantiated.")

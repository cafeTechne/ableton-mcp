import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server

print(f"server._resolve_sample_uri: {server._resolve_sample_uri}")
try:
    print(f"Code varnames: {server._resolve_sample_uri.__code__.co_varnames}")
except:
    pass

print(f"server._resolve_uri_by_name: {server._resolve_uri_by_name}")
try:
    print(f"Code varnames: {server._resolve_uri_by_name.__code__.co_varnames}")
except:
    pass

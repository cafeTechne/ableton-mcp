import sys
import os
import json
import time
from unittest.mock import MagicMock
from pathlib import Path

# Add parent directory to path to import server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server

# Disable trace for this utility
if "ABLETON_MCP_TRACE" in os.environ:
    del os.environ["ABLETON_MCP_TRACE"]

def regenerate():
    print("--- Regenerating Caches ---")
    conn = server.get_ableton_connection()
    if not conn.connect():
        print("ERROR: Connect to Ableton first.")
        return

    ctx = MagicMock()
    
    # 1. Devices
    print("Fetching loadable devices...")
    try:
        # Increase timeout or try small batches? Remote script handles listing.
        res_json = server.list_loadable_devices(ctx, category="all", max_items=2000)
        res = json.loads(res_json)
        count = res.get("count", 0)
        print(f"Index contains {count} devices.")
        # Cache is written automatically by the tool
    except Exception as e:
        print(f"Error listing devices: {e}")

    # 2. Samples
    # Not exposed as 'list_loadable_samples'. We usually search.
    # To seed sample cache, we might need a specific tool or just mock it with common items?
    # User said "Browser is too large...". 
    # We can search for generic terms to populate it: "Kick", "Snare", "Hihat", "Bass".
    keywords = ["Kick", "Snare", "Clap", "Hat", "Bass", "Pad", "Synth"]
    print(f"Seeding sample cache with keywords: {keywords}")
    
    print(f"Seeding sample cache with keywords: {keywords}")
    
    sample_items = []
    try:
        for kw in keywords:
            print(f"  Searching '{kw}'...")
            # Use search_loadable_devices but targeting samples category
            # This calls Live search.
            res_json = server.search_loadable_devices(ctx, query=kw, category="samples", max_items=20)
            items = json.loads(res_json).get("items", [])
            print(f"    Found {len(items)} items.")
            sample_items.extend(items)
            
        # Write accumulated samples to SAMPLE_CACHE_FILE
        # Deduplicate by uri
        unique_items = {item["uri"]: item for item in sample_items if "uri" in item}
        final_list = list(unique_items.values())
        
        data = {"count": len(final_list), "items": final_list}
        server.SAMPLE_CACHE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Sample cache populated with {len(final_list)} unique items.")
        
    except Exception as e:
        print(f"  Error seeding samples: {e}")
            
    print("Cache regeneration complete (check MCP_Server/cache/).")

if __name__ == "__main__":
    regenerate()

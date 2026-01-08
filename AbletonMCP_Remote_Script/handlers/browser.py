"""
Browser Handler Module for AbletonMCP Remote Script.

This module handles browser operations including navigation,
loading devices, and managing content.

Key Responsibilities:
    - Browser navigation
    - Load devices/instruments/effects
    - Preview samples
    - Hotswap support

For Future Agents:
    - Browser provides access to Live's content library
    - Use hotswap_target to load into selected device slot
    - Browser has hierarchical structure (folders, items)
    - Some operations require the browser view to be visible

Live 11 API Reference:
    - Live.Browser.Browser class
    - Live.Browser.BrowserItem class
    - See: https://nsuspray.github.io/Live_API_Doc/11.0.0.xml
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase

try:
    import Live
except ImportError:
    Live = None


class BrowserHandler(HandlerBase):
    """
    Handler for browser operations in AbletonMCP.
    
    Provides access to Live's browser for loading devices,
    samples, and other content.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
    """
    
    @property
    def browser(self):
        """Get the Live browser object."""
        if Live:
            return Live.Application.get_application().browser
        return None
    
    # =========================================================================
    # Browser Structure
    # =========================================================================
    
    def get_browser_tree(self, max_depth=2):
        """
        Get the top-level browser structure.
        
        Args:
            max_depth (int): Maximum depth to traverse (default 2)
        
        Returns:
            dict: Browser tree with categories and items
        
        Live API:
            Browser properties: sounds, drums, instruments, etc.
        """
        try:
            browser = self.browser
            if not browser:
                raise RuntimeError("Browser not available")
            
            def item_to_dict(item, depth=0):
                """Convert BrowserItem to dictionary."""
                info = {
                    "name": item.name,
                    "is_folder": item.is_folder,
                    "is_loadable": item.is_loadable,
                    "is_device": item.is_device
                }
                
                if item.is_folder and depth < max_depth:
                    children = []
                    for child in item.children:
                        children.append(item_to_dict(child, depth + 1))
                    info["children"] = children
                    info["child_count"] = len(children)
                
                return info
            
            # Get main categories
            categories = {
                "sounds": item_to_dict(browser.sounds) if browser.sounds else None,
                "drums": item_to_dict(browser.drums) if browser.drums else None,
                "instruments": item_to_dict(browser.instruments) if browser.instruments else None,
                "audio_effects": item_to_dict(browser.audio_effects) if browser.audio_effects else None,
                "midi_effects": item_to_dict(browser.midi_effects) if browser.midi_effects else None,
                "max_for_live": item_to_dict(browser.max_for_live) if browser.max_for_live else None,
                "plugins": item_to_dict(browser.plugins) if browser.plugins else None,
                "clips": item_to_dict(browser.clips) if browser.clips else None,
                "samples": item_to_dict(browser.samples) if browser.samples else None,
                "packs": item_to_dict(browser.packs) if browser.packs else None,
                "user_library": item_to_dict(browser.user_library) if browser.user_library else None
            }
            
            # Filter None values
            return {k: v for k, v in categories.items() if v is not None}
        except Exception as e:
            self._log("Error getting browser tree: " + str(e))
            raise
    
    def get_browser_category(self, category_name, max_items=50):
        """
        Get items from a specific browser category.
        
        Args:
            category_name (str): Category name (sounds, drums, instruments, etc.)
            max_items (int): Maximum items to return
        
        Returns:
            dict: Category contents
        
        Live API:
            Browser.sounds, Browser.drums, etc.
        """
        try:
            browser = self.browser
            if not browser:
                raise RuntimeError("Browser not available")
            
            category_map = {
                "sounds": browser.sounds,
                "drums": browser.drums,
                "instruments": browser.instruments,
                "audio_effects": browser.audio_effects,
                "midi_effects": browser.midi_effects,
                "max_for_live": browser.max_for_live,
                "plugins": browser.plugins,
                "clips": browser.clips,
                "samples": browser.samples,
                "packs": browser.packs,
                "user_library": browser.user_library
            }
            
            category = category_map.get(category_name.lower())
            if not category:
                raise ValueError("Unknown category: {}".format(category_name))
            
            items = []
            count = 0
            for item in category.children:
                if count >= max_items:
                    break
                items.append({
                    "name": item.name,
                    "is_folder": item.is_folder,
                    "is_loadable": item.is_loadable,
                    "uri": item.uri
                })
                count += 1
            
            return {
                "category": category_name,
                "item_count": len(items),
                "items": items
            }
        except Exception as e:
            self._log("Error getting browser category: " + str(e))
            raise
    
    # =========================================================================
    # Loading Content
    # =========================================================================
    
    def _find_browser_item_by_uri(self, browser, uri):
        """
        Recursively search for a browser item with a matching URI.
        """
        if not uri:
            return None
        
        # Helper to search a container
        def search_container(container):
            for child in container.children:
                if getattr(child, "uri", "") == uri:
                    return child
                if getattr(child, "is_folder", False):
                    found = search_container(child)
                    if found:
                        return found
            return None

        # Search main categories
        # Note: Access needs to be safe as some categories might be None
        categories = [
            getattr(browser, 'instruments', None),
            getattr(browser, 'audio_effects', None),
            getattr(browser, 'midi_effects', None),
            getattr(browser, 'max_for_live', None),
            getattr(browser, 'plugins', None),
            getattr(browser, 'clips', None),
            getattr(browser, 'samples', None),
            getattr(browser, 'packs', None),
            getattr(browser, 'user_library', None),
            getattr(browser, 'current_project', None)
        ]
        
        for category in categories:
            if category:
                found = search_container(category)
                if found:
                    return found
        return None

    def load_item_by_uri(self, uri):
        """
        Load a browser item by its URI.
        
        Args:
            uri (str): Browser item URI
        
        Returns:
            dict: Load result
        """
        try:
            browser = self.browser
            if not browser:
                raise RuntimeError("Browser not available")
            
            item = self._find_browser_item_by_uri(browser, uri)
            if not item:
                raise ValueError("Browser item with URI '{}' not found".format(uri))
                
            browser.load_item(item)
            return {
                "loaded": True,
                "uri": uri,
                "name": item.name
            }
        except Exception as e:
            self._log("Error loading item by URI: " + str(e))
            raise

    def preview_item_by_uri(self, uri):
        """
        Preview a browser item by its URI.
        
        Args:
            uri (str): Browser item URI
            
        Returns:
            dict: Preview result
        """
        try:
            browser = self.browser
            if not browser:
                raise RuntimeError("Browser not available")
                
            item = self._find_browser_item_by_uri(browser, uri)
            if not item:
                raise ValueError("Browser item with URI '{}' not found".format(uri))
                
            browser.preview_item(item)
            return {
                "previewing": True,
                "uri": uri,
                "name": item.name
            }
        except Exception as e:
            self._log("Error previewing item: " + str(e))
            raise

    
    def hotswap_target_enabled(self):
        """
        Check if hotswap mode is available.
        
        Returns:
            dict: Hotswap state
        
        Live API:
            Browser.hotswap_target (property)
        """
        try:
            browser = self.browser
            if not browser:
                raise RuntimeError("Browser not available")
            
            return {
                "hotswap_enabled": browser.hotswap_target is not None
            }
        except Exception as e:
            self._log("Error checking hotswap: " + str(e))
            raise
    
    # =========================================================================
    # Search
    # =========================================================================
    
    def filter_browser(self, filter_type):
        """
        Set the browser filter type.
        
        Args:
            filter_type (int): Filter type index
                0 = All, 1 = Sounds, 2 = Drums, 3 = Instruments, etc.
        
        Returns:
            dict: Filter result
        
        Live API:
            Browser.filter_type (int property)
        """
        try:
            browser = self.browser
            if not browser:
                raise RuntimeError("Browser not available")
            
            browser.filter_type = int(filter_type)
            return {
                "filter_type": browser.filter_type
            }
        except Exception as e:
            self._log("Error setting filter type: " + str(e))
            raise
    
    # =========================================================================
    # Preview
    # =========================================================================
    
    def stop_preview(self):
        """
        Stop any currently previewing sample.
        
        Returns:
            dict: Stop result
        
        Live API:
            Browser.stop_preview()
        """
        try:
            browser = self.browser
            if not browser:
                raise RuntimeError("Browser not available")
            
            browser.stop_preview()
            return {"stopped": True}
        except Exception as e:
            self._log("Error stopping preview: " + str(e))
            raise
    
    # =========================================================================
    # Browser State
    # =========================================================================
    
    def get_browser_state(self):
        """
        Get current browser state for LLM context.
        
        Returns:
            dict: Browser state including filter and hotswap
        """
        try:
            browser = self.browser
            if not browser:
                raise RuntimeError("Browser not available")
            
            return {
                "filter_type": browser.filter_type,
                "hotswap_enabled": browser.hotswap_target is not None
            }
        except Exception as e:
            self._log("Error getting browser state: " + str(e))
            raise

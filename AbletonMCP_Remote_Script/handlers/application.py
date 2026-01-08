"""
Application Handler Module for AbletonMCP Remote Script.

This module handles application-level operations including view switching,
browser control, and Live version information.

Key Responsibilities:
    - View focus and visibility (Session/Arrangement/Detail)
    - View scrolling and zooming
    - Browser mode control
    - Live version information
    - Dialog handling

For Future Agents:
    - Application.View controls what's visible in the Live window
    - Main views are: Session, Arranger, Detail/Clip, Detail/DeviceChain, Browser
    - Use focus_view to bring a view forward
    - Use show_view/hide_view for view visibility

Live 11 API Reference:
    - Live.Application.Application class
    - Live.Application.Application.View class
    - See: https://nsuspray.github.io/Live_API_Doc/11.0.0.xml
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase

try:
    import Live
except ImportError:
    # For static analysis - Live module only available in Ableton
    Live = None


class ApplicationHandler(HandlerBase):
    """
    Handler for application-level operations in AbletonMCP.
    
    Provides access to view control, browser, and application info
    that affects the Live window and user interface.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
    """
    
    @property
    def application(self):
        """Get the Live application object."""
        if Live:
            return Live.Application.get_application()
        return None
    
    @property
    def app_view(self):
        """Get the application view object."""
        app = self.application
        return app.view if app else None
    
    # =========================================================================
    # Application Info
    # =========================================================================
    
    def get_live_version(self):
        """
        Get Live version information.
        
        Returns:
            dict: Version info including major, minor, bugfix
        
        Live API:
            Application.get_major_version()
            Application.get_minor_version()
            Application.get_bugfix_version()
        """
        try:
            app = self.application
            if not app:
                raise RuntimeError("Application not available")
            
            return {
                "major": app.get_major_version(),
                "minor": app.get_minor_version(),
                "bugfix": app.get_bugfix_version(),
                "version_string": "{}.{}.{}".format(
                    app.get_major_version(),
                    app.get_minor_version(),
                    app.get_bugfix_version()
                )
            }
        except Exception as e:
            self._log("Error getting Live version: " + str(e))
            raise
    
    # =========================================================================
    # View Control
    # =========================================================================
    
    def get_available_views(self):
        """
        Get a list of available main views.
        
        Returns:
            dict: List of available view identifiers
        
        Live API:
            Application.View.available_main_views()
        """
        try:
            view = self.app_view
            if not view:
                raise RuntimeError("Application view not available")
            
            views = list(view.available_main_views())
            return {
                "views": views,
                "count": len(views)
            }
        except Exception as e:
            self._log("Error getting available views: " + str(e))
            raise
    
    def focus_view(self, view_name):
        """
        Show and focus a specific view.
        
        Args:
            view_name (str): View identifier, e.g.:
                - "Session" - Session View
                - "Arranger" - Arrangement View
                - "Detail/Clip" - Clip Detail View
                - "Detail/DeviceChain" - Device Chain View
                - "Browser" - Browser panel
        
        Returns:
            dict: Focus result
        
        Live API:
            Application.View.focus_view(identifier)
        """
        try:
            view = self.app_view
            if not view:
                raise RuntimeError("Application view not available")
            
            view.focus_view(view_name)
            return {
                "focused": True,
                "view": view_name
            }
        except Exception as e:
            self._log("Error focusing view: " + str(e))
            raise
    
    def show_view(self, view_name):
        """
        Show a specific view.
        
        Unlike focus_view, this makes the view visible but may not
        bring it to the front.
        
        Args:
            view_name (str): View identifier
        
        Returns:
            dict: Show result
        
        Live API:
            Application.View.show_view(identifier)
        """
        try:
            view = self.app_view
            if not view:
                raise RuntimeError("Application view not available")
            
            view.show_view(view_name)
            return {
                "shown": True,
                "view": view_name
            }
        except Exception as e:
            self._log("Error showing view: " + str(e))
            raise
    
    def hide_view(self, view_name):
        """
        Hide a specific view.
        
        Args:
            view_name (str): View identifier
        
        Returns:
            dict: Hide result
        
        Live API:
            Application.View.hide_view(identifier)
        """
        try:
            view = self.app_view
            if not view:
                raise RuntimeError("Application view not available")
            
            view.hide_view(view_name)
            return {
                "hidden": True,
                "view": view_name
            }
        except Exception as e:
            self._log("Error hiding view: " + str(e))
            raise
    
    def is_view_visible(self, view_name, main_window_only=True):
        """
        Check if a view is currently visible.
        
        Args:
            view_name (str): View identifier
            main_window_only (bool): If False, also checks second window
        
        Returns:
            dict: Visibility state
        
        Live API:
            Application.View.is_view_visible(identifier, main_window_only)
        """
        try:
            view = self.app_view
            if not view:
                raise RuntimeError("Application view not available")
            
            visible = view.is_view_visible(view_name, main_window_only)
            return {
                "view": view_name,
                "visible": visible,
                "main_window_only": main_window_only
            }
        except Exception as e:
            self._log("Error checking view visibility: " + str(e))
            raise
    
    def get_focused_document_view(self):
        """
        Get the currently focused document view.
        
        Returns either "Session" or "Arranger".
        
        Returns:
            dict: Current focused view name
        
        Live API:
            Application.View.focused_document_view (property)
        """
        try:
            view = self.app_view
            if not view:
                raise RuntimeError("Application view not available")
            
            return {
                "focused_document_view": view.focused_document_view
            }
        except Exception as e:
            self._log("Error getting focused document view: " + str(e))
            raise
    
    # =========================================================================
    # View Navigation
    # =========================================================================
    
    def scroll_view(self, direction, view_name, animate=True):
        """
        Scroll a view in the specified direction.
        
        Args:
            direction (int): Direction to scroll
                0 = up, 1 = down, 2 = left, 3 = right
            view_name (str): View identifier to scroll
            animate (bool): Whether to animate the scroll
        
        Returns:
            dict: Scroll result
        
        Live API:
            Application.View.scroll_view(direction, identifier, animate)
        """
        try:
            view = self.app_view
            if not view:
                raise RuntimeError("Application view not available")
            
            view.scroll_view(direction, view_name, animate)
            
            directions = {0: "up", 1: "down", 2: "left", 3: "right"}
            return {
                "scrolled": True,
                "view": view_name,
                "direction": directions.get(direction, str(direction))
            }
        except Exception as e:
            self._log("Error scrolling view: " + str(e))
            raise
    
    def zoom_view(self, direction, view_name, animate=True):
        """
        Zoom a view in or out.
        
        Args:
            direction (int): Zoom direction
                Positive = zoom in, Negative = zoom out
            view_name (str): View identifier to zoom
            animate (bool): Whether to animate the zoom
        
        Returns:
            dict: Zoom result
        
        Live API:
            Application.View.zoom_view(direction, identifier, animate)
        """
        try:
            view = self.app_view
            if not view:
                raise RuntimeError("Application view not available")
            
            view.zoom_view(direction, view_name, animate)
            return {
                "zoomed": True,
                "view": view_name,
                "direction": "in" if direction > 0 else "out"
            }
        except Exception as e:
            self._log("Error zooming view: " + str(e))
            raise
    
    # =========================================================================
    # Browser
    # =========================================================================
    
    def toggle_browser(self):
        """
        Toggle the browser panel and hotswap mode.
        
        Reveals the device chain, browser, and starts hotswap for
        the selected device. Calling again stops hotswap.
        
        Returns:
            dict: Toggle result
        
        Live API:
            Application.View.toggle_browse()
        """
        try:
            view = self.app_view
            if not view:
                raise RuntimeError("Application view not available")
            
            view.toggle_browse()
            return {
                "toggled": True,
                "browse_mode": view.browse_mode
            }
        except Exception as e:
            self._log("Error toggling browser: " + str(e))
            raise
    
    def get_browse_mode(self):
        """
        Get the current browser/hotswap mode state.
        
        Returns:
            dict: Browse mode state
        
        Live API:
            Application.View.browse_mode (property)
        """
        try:
            view = self.app_view
            if not view:
                raise RuntimeError("Application view not available")
            
            return {
                "browse_mode": view.browse_mode
            }
        except Exception as e:
            self._log("Error getting browse mode: " + str(e))
            raise
    
    # =========================================================================
    # Dialogs
    # =========================================================================
    
    def get_dialog_state(self):
        """
        Get information about any open dialogs.
        
        Returns:
            dict: Dialog state including message and button count
        
        Live API:
            Application.open_dialog_count
            Application.current_dialog_message
            Application.current_dialog_button_count
        """
        try:
            app = self.application
            if not app:
                raise RuntimeError("Application not available")
            
            return {
                "open_dialog_count": app.open_dialog_count,
                "current_dialog_message": app.current_dialog_message,
                "current_dialog_button_count": app.current_dialog_button_count
            }
        except Exception as e:
            self._log("Error getting dialog state: " + str(e))
            raise
    
    def press_dialog_button(self, button_index):
        """
        Press a button on the current dialog.
        
        Args:
            button_index (int): Button index (0-based) to press
        
        Returns:
            dict: Press result
        
        Live API:
            Application.press_current_dialog_button(index)
        """
        try:
            app = self.application
            if not app:
                raise RuntimeError("Application not available")
            
            if app.open_dialog_count == 0:
                raise RuntimeError("No dialog is currently open")
            
            app.press_current_dialog_button(button_index)
            return {
                "pressed": True,
                "button_index": button_index
            }
        except Exception as e:
            self._log("Error pressing dialog button: " + str(e))
            raise
    
    # =========================================================================
    # Application Overview
    # =========================================================================
    
    def get_application_overview(self):
        """
        Get a complete application state overview for LLM context.
        
        Returns comprehensive state of views, browse mode, and version.
        
        Returns:
            dict: Complete application state
        """
        try:
            app = self.application
            view = self.app_view
            
            if not app or not view:
                raise RuntimeError("Application not available")
            
            return {
                "version": {
                    "major": app.get_major_version(),
                    "minor": app.get_minor_version(),
                    "bugfix": app.get_bugfix_version()
                },
                "focused_document_view": view.focused_document_view,
                "browse_mode": view.browse_mode,
                "available_views": list(view.available_main_views()),
                "open_dialog_count": app.open_dialog_count
            }
        except Exception as e:
            self._log("Error getting application overview: " + str(e))
            raise

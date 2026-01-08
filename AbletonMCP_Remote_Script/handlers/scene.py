"""
Scene Handler Module for AbletonMCP Remote Script.

This module handles scene-level operations in Session View including
scene creation, deletion, properties, and tempo.

Key Responsibilities:
    - Scene creation and deletion
    - Scene renaming and color
    - Scene tempo and time signature
    - Scene launching
    - Scene duplication

For Future Agents:
    - Scenes are horizontal rows in Session View
    - Each scene has clip slots on every track
    - Scenes can have tempo/time signature changes
    - song.scenes returns the Vector of all scenes

Live 11 API Reference:
    - Live.Scene.Scene class
    - See: https://nsuspray.github.io/Live_API_Doc/11.0.0.xml
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class SceneHandler(HandlerBase):
    """
    Handler for scene operations in AbletonMCP.
    
    Provides access to Session View scenes for launching,
    organizing, and setting scene properties.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
    """
    
    def _get_scene(self, scene_index):
        """
        Get a scene by index.
        
        Args:
            scene_index (int): Scene index (0-based)
        
        Returns:
            Scene: The scene object
        
        Raises:
            IndexError: If scene index is out of range
        """
        scenes = self.song.scenes
        if scene_index < 0 or scene_index >= len(scenes):
            raise IndexError("Scene index {} out of range (0-{})".format(
                scene_index, len(scenes) - 1))
        return scenes[scene_index]
    
    # =========================================================================
    # Scene Information
    # =========================================================================
    
    def get_scene_info(self, scene_index):
        """
        Get detailed information about a scene.
        
        Args:
            scene_index (int): Scene index (0-based)
        
        Returns:
            dict: Scene information including name, tempo, color
        
        Live API:
            Scene properties: name, tempo, color, is_empty, is_triggered
        """
        try:
            scene = self._get_scene(scene_index)
            
            info = {
                "index": scene_index,
                "name": scene.name,
                "color": scene.color,
                "color_index": scene.color_index,
                "is_empty": scene.is_empty,
                "is_triggered": scene.is_triggered
            }
            
            # Scene tempo (0 means no tempo change for this scene)
            if hasattr(scene, 'tempo'):
                info["tempo"] = scene.tempo
            
            # Time signature if available
            if hasattr(scene, 'signature_numerator'):
                info["time_signature"] = {
                    "numerator": scene.signature_numerator,
                    "denominator": scene.signature_denominator
                }
            
            return info
        except Exception as e:
            self._log("Error getting scene info: " + str(e))
            raise
    
    def get_all_scenes(self):
        """
        Get information about all scenes.
        
        Returns a summary of each scene for efficient batch queries.
        
        Returns:
            dict: List of scene info
        """
        try:
            scenes = []
            for idx, scene in enumerate(self.song.scenes):
                scenes.append({
                    "index": idx,
                    "name": scene.name,
                    "color": scene.color,
                    "is_empty": scene.is_empty,
                    "tempo": scene.tempo if hasattr(scene, 'tempo') else 0
                })
            
            return {
                "scene_count": len(scenes),
                "scenes": scenes
            }
        except Exception as e:
            self._log("Error getting all scenes: " + str(e))
            raise
    
    # =========================================================================
    # Scene Properties
    # =========================================================================
    
    def set_scene_name(self, scene_index, name):
        """
        Set a scene's name.
        
        Args:
            scene_index (int): Scene index (0-based)
            name (str): New scene name
        
        Returns:
            dict: Updated scene info
        
        Live API:
            Scene.name (str property, writable)
        """
        try:
            scene = self._get_scene(scene_index)
            scene.name = str(name)
            return {
                "scene_index": scene_index,
                "name": scene.name
            }
        except Exception as e:
            self._log("Error setting scene name: " + str(e))
            raise
    
    def set_scene_color(self, scene_index, color):
        """
        Set a scene's color.
        
        Args:
            scene_index (int): Scene index (0-based)
            color (int): Color value (RGB integer)
        
        Returns:
            dict: Updated scene info
        
        Live API:
            Scene.color (int property, writable)
        """
        try:
            scene = self._get_scene(scene_index)
            scene.color = int(color)
            return {
                "scene_index": scene_index,
                "color": scene.color
            }
        except Exception as e:
            self._log("Error setting scene color: " + str(e))
            raise
    
    def set_scene_color_index(self, scene_index, color_index):
        """
        Set a scene's color by palette index.
        
        Args:
            scene_index (int): Scene index (0-based)
            color_index (int): Color palette index (0-69)
        
        Returns:
            dict: Updated scene info
        
        Live API:
            Scene.color_index (int property, writable)
        """
        try:
            scene = self._get_scene(scene_index)
            scene.color_index = int(color_index)
            return {
                "scene_index": scene_index,
                "color_index": scene.color_index,
                "color": scene.color
            }
        except Exception as e:
            self._log("Error setting scene color index: " + str(e))
            raise
    
    def set_scene_tempo(self, scene_index, tempo):
        """
        Set a scene's tempo.
        
        When this scene is triggered, the song tempo will change to
        this value. Set to 0 to disable tempo change.
        
        Args:
            scene_index (int): Scene index (0-based)
            tempo (float): Tempo in BPM, or 0 for no tempo change
        
        Returns:
            dict: Updated scene info
        
        Live API:
            Scene.tempo (float property, writable)
        """
        try:
            scene = self._get_scene(scene_index)
            
            tempo = float(tempo)
            if tempo < 0:
                raise ValueError("Tempo must be 0 or positive")
            
            scene.tempo = tempo
            return {
                "scene_index": scene_index,
                "tempo": scene.tempo
            }
        except Exception as e:
            self._log("Error setting scene tempo: " + str(e))
            raise
    
    def set_scene_time_signature(self, scene_index, numerator, denominator):
        """
        Set a scene's time signature.
        
        When this scene is triggered, the time signature will change.
        
        Args:
            scene_index (int): Scene index (0-based)
            numerator (int): Time signature numerator (1-99)
            denominator (int): Time signature denominator (1, 2, 4, 8, 16)
        
        Returns:
            dict: Updated scene info
        
        Live API:
            Scene.set_temp_signature(numerator, denominator)
        """
        try:
            scene = self._get_scene(scene_index)
            
            # Validate ranges
            numerator = int(numerator)
            denominator = int(denominator)
            
            if numerator < 1 or numerator > 99:
                raise ValueError("Numerator must be 1-99")
            if denominator not in (1, 2, 4, 8, 16):
                raise ValueError("Denominator must be 1, 2, 4, 8, or 16")
            
            # Note: The actual method name may vary
            if hasattr(scene, 'set_temp_signature'):
                scene.set_temp_signature(numerator, denominator)
            else:
                # Try direct property assignment if available
                scene.signature_numerator = numerator
                scene.signature_denominator = denominator
            
            return {
                "scene_index": scene_index,
                "signature_numerator": numerator,
                "signature_denominator": denominator
            }
        except Exception as e:
            self._log("Error setting scene time signature: " + str(e))
            raise
    
    # =========================================================================
    # Scene Launching
    # =========================================================================
    
    def fire_scene(self, scene_index, force_legato=False):
        """
        Fire a scene (launch all clips in the scene).
        
        Args:
            scene_index (int): Scene index (0-based)
            force_legato (bool): If True, clips start immediately in sync
        
        Returns:
            dict: Fire result
        
        Live API:
            Scene.fire()
            Scene.fire_as_selected(force_legato)
        """
        try:
            scene = self._get_scene(scene_index)
            
            if force_legato:
                scene.fire_as_selected(force_legato)
            else:
                scene.fire()
            
            return {
                "fired": True,
                "scene_index": scene_index,
                "scene_name": scene.name
            }
        except Exception as e:
            self._log("Error firing scene: " + str(e))
            raise
    
    def select_scene(self, scene_index):
        """
        Select a scene in the UI.
        
        Args:
            scene_index (int): Scene index (0-based)
        
        Returns:
            dict: Selection result
        
        Live API:
            Song.view.selected_scene (Scene property, writable)
        """
        try:
            scene = self._get_scene(scene_index)
            self.song.view.selected_scene = scene
            return {
                "selected": True,
                "scene_index": scene_index,
                "scene_name": scene.name
            }
        except Exception as e:
            self._log("Error selecting scene: " + str(e))
            raise
    
    # =========================================================================
    # Scene Creation/Deletion
    # =========================================================================
    
    def create_scene(self, index=-1):
        """
        Create a new empty scene.
        
        Args:
            index (int): Where to insert (-1 = at end)
        
        Returns:
            dict: New scene info
        
        Live API:
            Song.create_scene(index)
        """
        try:
            if index < 0:
                index = len(self.song.scenes)
            
            new_scene = self.song.create_scene(index)
            return {
                "created": True,
                "scene_index": index,
                "scene_name": new_scene.name,
                "scene_count": len(self.song.scenes)
            }
        except Exception as e:
            self._log("Error creating scene: " + str(e))
            raise
    
    def delete_scene(self, scene_index):
        """
        Delete a scene.
        
        Must have at least 2 scenes to delete one.
        
        Args:
            scene_index (int): Scene index to delete
        
        Returns:
            dict: Deletion result
        
        Live API:
            Song.delete_scene(index)
        """
        try:
            scenes = self.song.scenes
            if len(scenes) <= 1:
                raise RuntimeError("Cannot delete the last scene")
            
            if scene_index < 0 or scene_index >= len(scenes):
                raise IndexError("Scene index out of range")
            
            self.song.delete_scene(scene_index)
            return {
                "deleted": True,
                "scene_index": scene_index,
                "scene_count": len(self.song.scenes)
            }
        except Exception as e:
            self._log("Error deleting scene: " + str(e))
            raise
    
    def duplicate_scene(self, scene_index):
        """
        Duplicate a scene.
        
        Creates a copy of the scene with all its clips.
        
        Args:
            scene_index (int): Scene index to duplicate
        
        Returns:
            dict: New scene info
        
        Live API:
            Song.duplicate_scene(index)
        """
        try:
            self._get_scene(scene_index)  # Validate index
            self.song.duplicate_scene(scene_index)
            
            return {
                "duplicated": True,
                "source_index": scene_index,
                "new_index": scene_index + 1,
                "scene_count": len(self.song.scenes)
            }
        except Exception as e:
            self._log("Error duplicating scene: " + str(e))
            raise
    
    def move_scene(self, scene_index, target_index):
        """
        Move a scene to a new position.
        
        Args:
            scene_index (int): Scene to move
            target_index (int): Destination index
        
        Returns:
            dict: Move result
        
        Live API:
            Song.move_scene(scene_index, target_index)
        """
        try:
            self._get_scene(scene_index)  # Validate source
            
            if target_index < 0:
                target_index = 0
            elif target_index >= len(self.song.scenes):
                target_index = len(self.song.scenes) - 1
            
            self.song.move_scene(scene_index, target_index)
            return {
                "moved": True,
                "source_index": scene_index,
                "target_index": target_index
            }
        except Exception as e:
            self._log("Error moving scene: " + str(e))
            raise
    
    # =========================================================================
    # Scene Overview
    # =========================================================================
    
    def get_scene_overview(self):
        """
        Get a complete scene overview for LLM context.
        
        Returns summary with highlighted/selected scene info.
        
        Returns:
            dict: Complete scene state
        """
        try:
            selected = self.song.view.selected_scene
            selected_idx = None
            
            scenes = []
            for idx, scene in enumerate(self.song.scenes):
                if scene == selected:
                    selected_idx = idx
                    
                scenes.append({
                    "index": idx,
                    "name": scene.name,
                    "tempo": scene.tempo if hasattr(scene, 'tempo') else 0,
                    "is_empty": scene.is_empty,
                    "is_triggered": scene.is_triggered
                })
            
            return {
                "scene_count": len(scenes),
                "selected_scene": selected_idx,
                "scenes": scenes
            }
        except Exception as e:
            self._log("Error getting scene overview: " + str(e))
            raise

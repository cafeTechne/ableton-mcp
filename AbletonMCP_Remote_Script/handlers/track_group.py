"""
Track Group Handler Module for AbletonMCP Remote Script.

This module handles track grouping operations including group creation,
folding/unfolding, and group track management.

Key Responsibilities:
    - Create groups from selected tracks
    - Fold/unfold group tracks
    - Get group membership information
    - Manage group properties

For Future Agents:
    - Group tracks are special tracks that contain other tracks
    - is_foldable indicates if a track is a group
    - is_grouped indicates if a track is inside a group
    - group_track property points to the parent group
    - Folded groups hide their member tracks

Live 11 API Reference:
    - Live.Track.Track class (is_foldable, fold_state, group_track)
    - See: https://nsuspray.github.io/Live_API_Doc/11.0.0.xml
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class TrackGroupHandler(HandlerBase):
    """
    Handler for track grouping operations in AbletonMCP.
    
    Provides access to group track creation, folding, and
    membership queries.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
    """
    
    # =========================================================================
    # Group Information
    # =========================================================================
    
    def get_group_info(self, track_index):
        """
        Get information about a group track.
        
        Args:
            track_index (int): Track index (0-based)
        
        Returns:
            dict: Group info including fold state and member count
        
        Raises:
            RuntimeError: If track is not a group track
        
        Live API:
            Track.is_foldable (bool)
            Track.fold_state (bool)
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            
            if not track.is_foldable:
                raise RuntimeError("Track {} is not a group track".format(track_index))
            
            # Count members (tracks that have this as group_track)
            members = []
            for idx, t in enumerate(tracks):
                if hasattr(t, 'group_track') and t.group_track == track:
                    members.append({
                        "index": idx,
                        "name": t.name,
                        "is_visible": t.is_visible
                    })
            
            return {
                "track_index": track_index,
                "name": track.name,
                "is_foldable": True,
                "fold_state": track.fold_state,  # True = folded
                "member_count": len(members),
                "members": members
            }
        except Exception as e:
            self._log("Error getting group info: " + str(e))
            raise
    
    def get_all_groups(self):
        """
        Get information about all group tracks.
        
        Returns:
            dict: List of all group tracks with their states
        """
        try:
            groups = []
            for idx, track in enumerate(self.song.tracks):
                if track.is_foldable:
                    groups.append({
                        "index": idx,
                        "name": track.name,
                        "fold_state": track.fold_state,
                        "color": track.color
                    })
            
            return {
                "group_count": len(groups),
                "groups": groups
            }
        except Exception as e:
            self._log("Error getting all groups: " + str(e))
            raise
    
    def get_track_group_membership(self, track_index):
        """
        Get group membership info for a track.
        
        Args:
            track_index (int): Track index
        
        Returns:
            dict: Membership info with parent group if any
        
        Live API:
            Track.is_grouped (bool)
            Track.group_track (Track or None)
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            
            result = {
                "track_index": track_index,
                "track_name": track.name,
                "is_grouped": track.is_grouped,
                "is_foldable": track.is_foldable,
                "is_visible": track.is_visible
            }
            
            if track.is_grouped and track.group_track:
                # Find parent group index
                parent = track.group_track
                parent_idx = None
                for idx, t in enumerate(tracks):
                    if t == parent:
                        parent_idx = idx
                        break
                
                result["group_track"] = {
                    "index": parent_idx,
                    "name": parent.name
                }
            
            return result
        except Exception as e:
            self._log("Error getting track group membership: " + str(e))
            raise
    
    # =========================================================================
    # Fold Operations
    # =========================================================================
    
    def fold_group(self, track_index):
        """
        Fold a group track (hide members).
        
        Args:
            track_index (int): Group track index
        
        Returns:
            dict: New fold state
        
        Raises:
            RuntimeError: If track is not a group track
        
        Live API:
            Track.fold_state = True
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            
            if not track.is_foldable:
                raise RuntimeError("Track {} is not a group track".format(track_index))
            
            track.fold_state = True
            return {
                "track_index": track_index,
                "fold_state": True,
                "folded": True
            }
        except Exception as e:
            self._log("Error folding group: " + str(e))
            raise
    
    def unfold_group(self, track_index):
        """
        Unfold a group track (show members).
        
        Args:
            track_index (int): Group track index
        
        Returns:
            dict: New fold state
        
        Raises:
            RuntimeError: If track is not a group track
        
        Live API:
            Track.fold_state = False
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            
            if not track.is_foldable:
                raise RuntimeError("Track {} is not a group track".format(track_index))
            
            track.fold_state = False
            return {
                "track_index": track_index,
                "fold_state": False,
                "unfolded": True
            }
        except Exception as e:
            self._log("Error unfolding group: " + str(e))
            raise
    
    def toggle_group_fold(self, track_index):
        """
        Toggle a group track's fold state.
        
        Args:
            track_index (int): Group track index
        
        Returns:
            dict: New fold state
        
        Live API:
            Track.fold_state (bool property)
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            
            if not track.is_foldable:
                raise RuntimeError("Track {} is not a group track".format(track_index))
            
            track.fold_state = not track.fold_state
            return {
                "track_index": track_index,
                "fold_state": track.fold_state
            }
        except Exception as e:
            self._log("Error toggling group fold: " + str(e))
            raise
    
    # =========================================================================
    # Track Properties
    # =========================================================================
    
    def set_track_color(self, track_index, color=None, color_index=None):
        """
        Set a track's color.
        
        Args:
            track_index (int): Track index
            color (int, optional): RGB color value
            color_index (int, optional): Palette index (0-69)
        
        Returns:
            dict: Updated color
        
        Live API:
            Track.color (int property)
            Track.color_index (int property)
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            
            if color_index is not None:
                track.color_index = int(color_index)
            elif color is not None:
                track.color = int(color)
            
            return {
                "track_index": track_index,
                "color": track.color,
                "color_index": track.color_index
            }
        except Exception as e:
            self._log("Error setting track color: " + str(e))
            raise
    
    def get_track_freeze_state(self, track_index):
        """
        Get a track's freeze capability and state.
        
        Args:
            track_index (int): Track index
        
        Returns:
            dict: Freeze state info
        
        Live API:
            Track.can_be_frozen (bool)
            Track.is_frozen (bool)
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            
            return {
                "track_index": track_index,
                "can_be_frozen": track.can_be_frozen,
                "is_frozen": track.is_frozen
            }
        except Exception as e:
            self._log("Error getting freeze state: " + str(e))
            raise
    
    def stop_track_clips(self, track_index):
        """
        Stop all clips on a track.
        
        Args:
            track_index (int): Track index
        
        Returns:
            dict: Stop result
        
        Live API:
            Track.stop_all_clips()
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            track.stop_all_clips()
            
            return {
                "stopped": True,
                "track_index": track_index,
                "track_name": track.name
            }
        except Exception as e:
            self._log("Error stopping track clips: " + str(e))
            raise
    
    # =========================================================================
    # Track Overview
    # =========================================================================
    
    def get_tracks_overview(self):
        """
        Get a complete tracks overview for LLM context.
        
        Returns comprehensive state of all tracks including
        groups, visibility, and basic properties.
        
        Returns:
            dict: Complete tracks state
        """
        try:
            tracks_list = []
            for idx, track in enumerate(self.song.tracks):
                track_info = {
                    "index": idx,
                    "name": track.name,
                    "color": track.color,
                    "mute": track.mute,
                    "solo": track.solo,
                    "arm": track.arm if hasattr(track, 'arm') else False,
                    "is_foldable": track.is_foldable,
                    "is_grouped": track.is_grouped,
                    "is_visible": track.is_visible,
                    "has_midi_input": track.has_midi_input,
                    "has_audio_input": track.has_audio_input
                }
                
                if track.is_foldable:
                    track_info["fold_state"] = track.fold_state
                
                if track.is_grouped and track.group_track:
                    for gidx, gt in enumerate(self.song.tracks):
                        if gt == track.group_track:
                            track_info["group_track_index"] = gidx
                            break
                
                tracks_list.append(track_info)
            
            return {
                "track_count": len(tracks_list),
                "tracks": tracks_list
            }
        except Exception as e:
            self._log("Error getting tracks overview: " + str(e))
            raise

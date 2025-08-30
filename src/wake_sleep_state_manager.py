"""
Qt-based Wake/Sleep State Manager for WhisperWriter

This replaces the broken singleton observer pattern with PyQt5 signals/slots
to ensure thread-safe UI updates that survive dynamic plugin loading.
"""

from PyQt5.QtCore import QObject, pyqtSignal
from typing import Optional
from utils import ConfigManager


class WakeSleepStateManager(QObject):
    """
    Qt-based state manager for wake/sleep functionality.
    Uses signals instead of observers for reliable UI updates.
    """
    
    # Signal emitted when wake/sleep state changes
    stateChanged = pyqtSignal(str)  # 'awake' or 'sleeping'
    
    _instance: Optional['WakeSleepStateManager'] = None
    
    def __init__(self):
        super().__init__()
        self._state = 'awake'  # Default state
    
    @classmethod
    def get_instance(cls) -> 'WakeSleepStateManager':
        """Get or create the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def get_state(cls) -> str:
        """Get current wake/sleep state"""
        instance = cls.get_instance()
        return instance._state
    
    @classmethod 
    def set_state(cls, new_state: str) -> None:
        """Set wake/sleep state and emit signal"""
        instance = cls.get_instance()
        old_state = instance._state
        
        if new_state != old_state:
            instance._state = new_state
            instance.stateChanged.emit(new_state)
            print(f"Wake/Sleep state changed to: {new_state}")
    
    @classmethod
    def initialize_from_config(cls):
        """Initialize state from configuration"""
        try:
            config = ConfigManager.get_config()
            plugin_config = config.get('plugins', {}).get('wake_sleep_processor', {})
            initial_state = plugin_config.get('initial_state', 'awake')
            cls.set_state(initial_state)
        except Exception as e:
            print(f"[ERROR] Error initializing wake/sleep state from config: {e}")
            cls.set_state('awake')
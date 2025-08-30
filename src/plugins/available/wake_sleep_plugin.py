"""
Wake/Sleep word processor plugin for WhisperWriter

This plugin detects wake words (to start transcription output) and sleep words 
(to suppress transcription output) in the transcribed text stream.

When sleeping:
- Recording continues but transcription output is suppressed
- Status window shows sleep indicator
- Wake words can bring the system back to awake state

When awake:
- Transcription output is normal
- Sleep words can put the system to sleep
"""

import re
from typing import Dict, Any, Optional
from plugins.base import ProcessorPlugin
from processing.base import TextProcessor

# Import the Qt-based state manager instead of the broken singleton
try:
    from wake_sleep_state_manager import WakeSleepStateManager
    _STATE_MANAGER_AVAILABLE = True
except ImportError:
    _STATE_MANAGER_AVAILABLE = False
    print("[ERROR] Failed to import WakeSleepStateManager - wake/sleep functionality disabled")


class WakeSleepProcessor(TextProcessor):
    """
    Processor that detects wake and sleep words in transcribed text
    """
    
    def get_name(self) -> str:
        """Return the name of this processor"""
        return "Wake/Sleep Word Processor"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the WakeSleepProcessor with configuration
        
        Args:
            config: Plugin configuration dictionary
        """
        super().__init__()
        
        # Default configuration
        default_config = {
            'enabled': True,
            'wake_words': ['hey whisper', 'start dictation', 'wake up'],
            'sleep_words': ['go to sleep', 'stop dictating', 'sleep mode'],
            'case_sensitive': False,
            'exact_match': False,
            'initial_state': 'awake'
        }
        
        # Merge with provided config
        if config:
            default_config.update(config)
        self.config = default_config
        
        # Initialize state if not already set
        if _STATE_MANAGER_AVAILABLE:
            if WakeSleepStateManager.get_state() == "awake" and self.config['initial_state'] == 'sleeping':
                WakeSleepStateManager.set_state('sleeping')
        
        # Prepare search patterns
        self._prepare_patterns()
    
    def _prepare_patterns(self):
        """Prepare regex patterns for wake and sleep words"""
        flags = 0 if self.config['case_sensitive'] else re.IGNORECASE
        
        # Prepare wake word patterns
        self.wake_patterns = []
        for wake_word in self.config['wake_words']:
            if self.config['exact_match']:
                # Exact match: phrase at start/end of sentence or standalone with punctuation boundaries
                pattern = rf'(?:^|\.|!|\?)\s*{re.escape(wake_word)}\s*(?:[.!?]|\s|$)'
            else:
                # Partial match: phrase can appear anywhere in transcription, ignoring punctuation
                pattern = rf'\b{re.escape(wake_word)}[.!?]*\b'
            
            self.wake_patterns.append(re.compile(pattern, flags))
        
        # Prepare sleep word patterns  
        self.sleep_patterns = []
        for sleep_word in self.config['sleep_words']:
            if self.config['exact_match']:
                # Exact match: phrase at start/end of sentence or standalone with punctuation boundaries
                pattern = rf'(?:^|\.|!|\?)\s*{re.escape(sleep_word)}\s*(?:[.!?]|\s|$)'
            else:
                # Partial match: phrase can appear anywhere in transcription, ignoring punctuation
                pattern = rf'\b{re.escape(sleep_word)}[.!?]*\b'
            
            self.sleep_patterns.append(re.compile(pattern, flags))
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process the transcribed text for wake/sleep words
        
        Args:
            text: The transcribed text to process
            context: Optional context dictionary (unused but required by interface)
            
        Returns:
            str: Empty string if sleeping (suppresses output), 
                 original text if awake, or text with wake/sleep words removed
        """
        if not self.config['enabled'] or not text.strip():
            return text
        
        current_state = WakeSleepStateManager.get_state() if _STATE_MANAGER_AVAILABLE else 'awake'
        text_changed = False
        processed_text = text
        
        from utils import ConfigManager
        
        # Check for wake words
        wake_detected = False
        for i, pattern in enumerate(self.wake_patterns):
            if pattern.search(processed_text):
                wake_detected = True
                if current_state == 'sleeping' and _STATE_MANAGER_AVAILABLE:
                    WakeSleepStateManager.set_state('awake')
                    print(f"Wake word detected: transitioning to awake state")
                
                # Remove the wake word from output (optional behavior)
                if self.config['exact_match']:
                    # For exact match, return empty since the entire phrase was a wake word
                    return ''
                else:
                    # For partial match, remove just the wake word
                    processed_text = pattern.sub('', processed_text)
                    text_changed = True
                break
        
        
        # Check for sleep words  
        sleep_detected = False
        for i, pattern in enumerate(self.sleep_patterns):
            if pattern.search(processed_text):
                sleep_detected = True
                if current_state == 'awake' and _STATE_MANAGER_AVAILABLE:
                    WakeSleepStateManager.set_state('sleeping')
                    print(f"Sleep word detected: transitioning to sleeping state")
                
                # Remove the sleep word from output (optional behavior)
                if self.config['exact_match']:
                    # For exact match, return empty since the entire phrase was a sleep word
                    return ''
                else:
                    # For partial match, remove just the sleep word
                    processed_text = pattern.sub('', processed_text)
                    text_changed = True
                break
        
        
        # Clean up whitespace if text was modified
        if text_changed:
            processed_text = re.sub(r'\s+', ' ', processed_text.strip())
        
        # If currently sleeping, suppress all output
        if _STATE_MANAGER_AVAILABLE and WakeSleepStateManager.get_state() == 'sleeping':
            return ''
        
        # Return processed text (may have wake/sleep words removed)
        return processed_text
    
    def get_priority(self) -> int:
        """
        Return the priority of this processor (lower numbers run first)
        Wake/sleep detection should run very early, after silence removal
        """
        return 5  # Run after silence removal (priority 1) but before other processing


def create_processor(config: Dict[str, Any]) -> WakeSleepProcessor:
    """
    Factory function to create the WakeSleepProcessor
    
    Args:
        config: Plugin configuration from config file
        
    Returns:
        WakeSleepProcessor instance
    """
    return WakeSleepProcessor(config)


class WakeSleepPlugin(ProcessorPlugin):
    """Plugin wrapper for wake/sleep word processing"""
    
    def __init__(self):
        self.config = {}
        self.enabled = False
        self.processor = None
    
    def get_name(self) -> str:
        """Return the plugin name"""
        return "wake_sleep_processor"
    
    def get_version(self) -> str:
        """Return the plugin version"""
        return "1.0.0"
    
    def initialize(self, config: Dict[str, Any]):
        """Initialize plugin with configuration"""
        self.config = config
        self.enabled = config.get('enabled', True)
        
        if self.enabled:
            self.processor = WakeSleepProcessor(config)
            print(f"WakeSleepPlugin: Initialized with {len(config.get('wake_words', []))} wake words and {len(config.get('sleep_words', []))} sleep words")
        else:
            print("WakeSleepPlugin: Disabled in configuration")
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self.enabled
    
    def get_processor(self) -> Optional[WakeSleepProcessor]:
        """Get the text processor instance"""
        return self.processor if self.enabled else None
"""
Built-in text processors migrated from original post_process_transcription
"""
import re
from typing import Optional, Dict, Any
from .base import TextProcessor


class SilenceRemovalProcessor(TextProcessor):
    """Remove silence artifacts (dots) from transcription"""
    
    def get_name(self) -> str:
        return "SilenceRemoval"
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Remove silence patterns from text"""
        if not text:
            return text
            
        # If entire text is just dots and spaces - it's silence
        if re.match(r'^[\s\.]+$', text):
            return ''
        
        # Remove excessive dots (3+ dots with spaces between them)
        # This keeps normal sentence periods but removes silence artifacts
        text = re.sub(r'(\s*\.\s*){3,}', ' ', text)
        
        return text


class WhitespaceNormalizer(TextProcessor):
    """Normalize whitespace in text"""
    
    def get_name(self) -> str:
        return "WhitespaceNormalizer"
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Strip leading/trailing whitespace"""
        if not text:
            return text
        return text.strip()


class TrailingPeriodProcessor(TextProcessor):
    """Remove trailing period if configured"""
    
    def get_name(self) -> str:
        return "TrailingPeriod"
    
    def is_enabled(self) -> bool:
        """Only enabled if configured"""
        try:
            try:
                from utils import ConfigManager
            except ImportError:
                from src.utils import ConfigManager
            return ConfigManager.get_config_value('post_processing', 'remove_trailing_period', False)
        except (RuntimeError, KeyError):
            # Default to False if config not available
            return False
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Remove trailing period"""
        if not text:
            return text
            
        if text.endswith('.'):
            return text[:-1]
        return text


class CapitalizationProcessor(TextProcessor):
    """Handle capitalization based on config"""
    
    def get_name(self) -> str:
        return "Capitalization"
    
    def is_enabled(self) -> bool:
        """Only enabled if configured"""
        try:
            try:
                from utils import ConfigManager
            except ImportError:
                from src.utils import ConfigManager
            return ConfigManager.get_config_value('post_processing', 'remove_capitalization', False)
        except (RuntimeError, KeyError):
            # Default to False if config not available
            return False
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Convert to lowercase if configured"""
        if not text:
            return text
        return text.lower()


class TrailingSpaceProcessor(TextProcessor):
    """Add trailing space if configured"""
    
    def get_name(self) -> str:
        return "TrailingSpace"
    
    def is_enabled(self) -> bool:
        """Only enabled if configured"""
        try:
            try:
                from utils import ConfigManager
            except ImportError:
                from src.utils import ConfigManager
            return ConfigManager.get_config_value('post_processing', 'add_trailing_space', True)
        except (RuntimeError, KeyError):
            # Default to True if config not available
            return True
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Add trailing space to non-empty text"""
        # Only add trailing space if there's actual content
        if text:
            return text + ' '
        return text
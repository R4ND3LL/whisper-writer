"""
Base classes for text processing pipeline
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class TextProcessor(ABC):
    """Base class for all text processors"""
    
    @abstractmethod
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process text and return modified version
        
        Args:
            text: Input text to process
            context: Optional context dictionary with metadata
            
        Returns:
            Processed text
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return processor name for logging and debugging"""
        pass
    
    def is_enabled(self) -> bool:
        """Check if processor is enabled (can be overridden)"""
        return True


class ProcessingPipeline:
    """Manages chain of text processors"""
    
    def __init__(self):
        self.processors = []
        self.debug = False
    
    def add_processor(self, processor: TextProcessor):
        """
        Add processor to pipeline
        
        Args:
            processor: TextProcessor instance to add
        """
        if processor and processor.is_enabled():
            self.processors.append(processor)
            if self.debug:
                print(f"Added processor: {processor.get_name()}")
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Run text through all processors in order
        
        Args:
            text: Input text to process
            context: Optional context dictionary
            
        Returns:
            Fully processed text
        """
        if not text:
            return text
        
        result = text
        for processor in self.processors:
            try:
                if processor.is_enabled():
                    result = processor.process(result, context or {})
                    if self.debug:
                        print(f"After {processor.get_name()}: {repr(result[:50])}")
            except Exception as e:
                print(f"Error in processor {processor.get_name()}: {e}")
                # Continue with other processors even if one fails
                
        return result
    
    def get_processor_names(self) -> list:
        """Get list of processor names in pipeline"""
        return [p.get_name() for p in self.processors]
    
    def clear(self):
        """Remove all processors from pipeline"""
        self.processors.clear()
    
    def __len__(self) -> int:
        """Return number of processors in pipeline"""
        return len(self.processors)
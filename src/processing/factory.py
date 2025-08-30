"""
Factory for creating and managing the processing pipeline
"""
from .base import ProcessingPipeline
from .builtin_processors import (
    SilenceRemovalProcessor,
    WhitespaceNormalizer,
    TrailingPeriodProcessor,
    CapitalizationProcessor,
    TrailingSpaceProcessor
)


def create_default_pipeline() -> ProcessingPipeline:
    """
    Create pipeline with default processors in correct order
    
    Returns:
        ProcessingPipeline configured with built-in processors
    """
    pipeline = ProcessingPipeline()
    
    # Add processors in the same order as original post_process_transcription
    # 1. Remove silence artifacts first
    pipeline.add_processor(SilenceRemovalProcessor())
    
    # 2. Normalize whitespace
    pipeline.add_processor(WhitespaceNormalizer())
    
    # 3. Remove trailing period if configured
    pipeline.add_processor(TrailingPeriodProcessor())
    
    # 4. Handle capitalization if configured
    pipeline.add_processor(CapitalizationProcessor())
    
    # 5. Add trailing space last (if configured)
    pipeline.add_processor(TrailingSpaceProcessor())
    
    return pipeline


# Global pipeline instance (singleton pattern)
_pipeline = None


def get_pipeline() -> ProcessingPipeline:
    """
    Get or create the global pipeline instance
    
    Returns:
        The global ProcessingPipeline instance
    """
    global _pipeline
    if _pipeline is None:
        _pipeline = create_default_pipeline()
    return _pipeline


def reset_pipeline():
    """Reset the global pipeline (useful for testing)"""
    global _pipeline
    _pipeline = None
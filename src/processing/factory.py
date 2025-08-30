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
    Create pipeline with default processors and plugins in correct order
    
    Returns:
        ProcessingPipeline configured with built-in processors and plugins
    """
    pipeline = ProcessingPipeline()
    
    # Add built-in processors in the same order as original
    # 1. Remove silence artifacts first (priority: very early)
    pipeline.add_processor(SilenceRemovalProcessor())
    
    # 2. Normalize whitespace (priority: early)
    pipeline.add_processor(WhitespaceNormalizer())
    
    # 3. Load and apply plugins (they run here, after basic cleanup)
    try:
        from plugins.manager import get_plugin_manager
        
        # Try to get config for plugin initialization
        try:
            try:
                from utils import ConfigManager
            except ImportError:
                from src.utils import ConfigManager
            
            config = ConfigManager.get_config()
            if config:  # Only if config is loaded
                manager = get_plugin_manager()
                
                # Discover plugins
                manager.discover_plugins()
                
                # Initialize with config
                manager.initialize_plugins(config)
                
                # Add enabled plugins to pipeline
                manager.apply_processor_plugins(pipeline)
        except (RuntimeError, ImportError) as e:
            # Config not available yet, skip plugins
            print(f"Plugins not loaded: {e}")
            
    except ImportError:
        # Plugin system not available
        pass
    
    # 4. Remove trailing period if configured (priority: late)
    pipeline.add_processor(TrailingPeriodProcessor())
    
    # 5. Handle capitalization if configured (priority: late)
    pipeline.add_processor(CapitalizationProcessor())
    
    # 6. Add trailing space last (priority: very late)
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
"""
Plugin manager for discovering and loading plugins
"""
import importlib
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from .base import Plugin, ProcessorPlugin


class PluginManager:
    """Manages plugin discovery, loading, and initialization"""
    
    def __init__(self):
        self.plugins: List[Plugin] = []
        self.processor_plugins: List[ProcessorPlugin] = []
        self._initialized = False
    
    def discover_plugins(self, plugin_dir: str = None):
        """
        Discover and load plugins from directory
        
        Args:
            plugin_dir: Directory path relative to src/ (default: "plugins/available")
        """
        if plugin_dir is None:
            # Default to plugins/available relative to this file
            base_dir = Path(__file__).parent
            plugin_path = base_dir / "available"
        else:
            plugin_path = Path(plugin_dir)
        
        if not plugin_path.exists():
            print(f"Plugin directory does not exist: {plugin_path}")
            plugin_path.mkdir(parents=True, exist_ok=True)
            return
        
        # Add src directory to Python path if needed
        src_dir = Path(__file__).parent.parent  # Go up to src/
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
        
        # Scan for plugin files
        for file_path in plugin_path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue  # Skip private files
            
            module_name = file_path.stem
            try:
                # Try to import the module
                full_module_name = f"plugins.available.{module_name}"
                
                # Clear any cached version first
                if full_module_name in sys.modules:
                    del sys.modules[full_module_name]
                
                module = importlib.import_module(full_module_name)
                
                # Look for Plugin subclasses in the module
                for attr_name in dir(module):
                    if attr_name.startswith("_"):
                        continue
                    
                    attr = getattr(module, attr_name)
                    
                    # Check if it's a class and subclass of Plugin
                    if (isinstance(attr, type) and 
                        issubclass(attr, Plugin) and 
                        attr not in [Plugin, ProcessorPlugin]):
                        
                        try:
                            # Instantiate the plugin
                            plugin_instance = attr()
                            self.register_plugin(plugin_instance)
                            print(f"Discovered plugin: {plugin_instance.get_name()} v{plugin_instance.get_version()}")
                        except Exception as e:
                            print(f"Failed to instantiate plugin {attr_name}: {e}")
                            
            except ImportError as e:
                print(f"Failed to import plugin module {module_name}: {e}")
            except Exception as e:
                print(f"Error processing plugin {module_name}: {e}")
    
    def register_plugin(self, plugin: Plugin):
        """
        Register a plugin instance
        
        Args:
            plugin: Plugin instance to register
        """
        self.plugins.append(plugin)
        
        # Also track processor plugins specifically
        if isinstance(plugin, ProcessorPlugin):
            self.processor_plugins.append(plugin)
    
    def initialize_plugins(self, config: Dict[str, Any]):
        """
        Initialize all plugins with configuration
        
        Args:
            config: Full configuration dictionary
        """
        plugins_config = config.get('plugins', {})
        
        for plugin in self.plugins:
            try:
                # Get plugin-specific config
                plugin_name = plugin.get_name()
                plugin_config = plugins_config.get(plugin_name, {})
                
                # Initialize the plugin
                plugin.initialize(plugin_config)
                
                if plugin.is_enabled():
                    print(f"Initialized plugin: {plugin_name} (enabled)")
                else:
                    print(f"Initialized plugin: {plugin_name} (disabled)")
                    
            except Exception as e:
                print(f"Failed to initialize plugin {plugin.get_name()}: {e}")
        
        self._initialized = True
    
    def get_enabled_processor_plugins(self) -> List[ProcessorPlugin]:
        """
        Get list of enabled processor plugins sorted by priority
        
        Returns:
            List of enabled ProcessorPlugin instances
        """
        enabled = [p for p in self.processor_plugins if p.is_enabled()]
        # Sort by priority (lower number = higher priority = earlier in pipeline)
        return sorted(enabled, key=lambda p: p.get_priority())
    
    def apply_processor_plugins(self, pipeline):
        """
        Add enabled processor plugins to a pipeline
        
        Args:
            pipeline: ProcessingPipeline instance to add processors to
        """
        for plugin in self.get_enabled_processor_plugins():
            try:
                processor = plugin.get_processor()
                if processor:
                    pipeline.add_processor(processor)
                    print(f"Added plugin processor: {plugin.get_name()}")
            except Exception as e:
                print(f"Failed to add processor from plugin {plugin.get_name()}: {e}")
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered plugins
        
        Returns:
            List of plugin info dictionaries
        """
        return [
            {
                'name': p.get_name(),
                'version': p.get_version(),
                'enabled': p.is_enabled(),
                'description': p.get_description(),
                'type': 'processor' if isinstance(p, ProcessorPlugin) else 'generic'
            }
            for p in self.plugins
        ]


# Global plugin manager instance
_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """
    Get or create the global plugin manager
    
    Returns:
        The global PluginManager instance
    """
    global _manager
    if _manager is None:
        _manager = PluginManager()
    return _manager


def reset_plugin_manager():
    """Reset the global plugin manager (useful for testing)"""
    global _manager
    _manager = None
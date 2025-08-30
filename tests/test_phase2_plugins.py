"""
Phase 2 Plugin System Test
Verify plugin discovery, loading, and processing works

Run with: python tests/test_phase2_plugins.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import ConfigManager
from processing.factory import create_default_pipeline, reset_pipeline
from plugins.manager import get_plugin_manager, reset_plugin_manager
from transcription import post_process_transcription

# Initialize config
ConfigManager.initialize()


def test_plugin_discovery():
    """Test that plugins are discovered"""
    reset_plugin_manager()  # Start fresh
    manager = get_plugin_manager()
    
    # Discover plugins
    manager.discover_plugins()
    
    # Check we found some plugins
    plugins = manager.list_plugins()
    print(f"[PASS] Discovered {len(plugins)} plugin(s)")
    
    # Check regex plugin specifically
    plugin_names = [p['name'] for p in plugins]
    assert 'regex_processor' in plugin_names, "regex_processor plugin not found"
    print("[PASS] regex_processor plugin discovered")
    
    return plugins


def test_plugin_initialization():
    """Test that plugins initialize with config"""
    reset_plugin_manager()
    manager = get_plugin_manager()
    
    # Discover and initialize
    manager.discover_plugins()
    manager.initialize_plugins(ConfigManager.get_config())
    
    # Check enabled plugins
    enabled = manager.get_enabled_processor_plugins()
    print(f"[PASS] {len(enabled)} plugin(s) enabled")
    
    # Verify regex plugin is enabled (based on config)
    config = ConfigManager.get_config()
    if config and config.get('plugins', {}).get('regex_processor', {}).get('enabled'):
        plugin_names = [p.get_name() for p in enabled]
        assert 'regex_processor' in plugin_names, "regex_processor should be enabled"
        print("[PASS] regex_processor is enabled as configured")


def test_plugin_in_pipeline():
    """Test that plugins are added to the pipeline"""
    reset_pipeline()  # Clear cached pipeline
    reset_plugin_manager()
    
    # Create new pipeline (should load plugins)
    pipeline = create_default_pipeline()
    
    # Check processor count
    processor_names = pipeline.get_processor_names()
    print(f"[PASS] Pipeline has {len(processor_names)} processors")
    print(f"       Processors: {', '.join(processor_names)}")
    
    # If regex plugin is enabled, it should be in the pipeline
    config = ConfigManager.get_config()
    if config and config.get('plugins', {}).get('regex_processor', {}).get('enabled'):
        assert 'RegexProcessor' in processor_names, "RegexProcessor not in pipeline"
        print("[PASS] RegexProcessor added to pipeline")


def test_regex_replacements():
    """Test that regex rules actually work"""
    reset_pipeline()
    reset_plugin_manager()
    
    # Test cases based on our config rules
    test_cases = [
        # Test forward slash replacement
        ("Say forward slash please", "Say / please"),
        ("Use FORWARD SLASH here", "Use / here"),  # Case insensitive
        
        # Test new line replacement
        ("First line new line second line", "First line \n second line"),
        
        # Test filler word removal
        ("Um hello there", " hello there"),
        ("I think um that uh we should", "I think  that  we should"),
        ("Umm this is ummm a test", " this is  a test"),
        
        # Combined test
        ("Um please use forward slash", " please use /"),
    ]
    
    for input_text, expected_base in test_cases:
        result = post_process_transcription(input_text)
        
        # Account for trailing space that might be added
        result_stripped = result.rstrip()
        expected_stripped = expected_base.rstrip()
        
        # Check if the core transformation worked
        assert expected_stripped in result_stripped or result_stripped == expected_stripped, \
            f"Failed: '{input_text}' -> '{result}' (expected '{expected_base}')"
    
    print("[PASS] Regex replacements working correctly")


def test_plugin_disable():
    """Test that plugins can be disabled"""
    # Get config reference
    config = ConfigManager.get_config()
    if not config:
        print("[SKIP] Config not available for disable test")
        return
        
    # Temporarily disable the plugin
    original_enabled = config.get('plugins', {}).get('regex_processor', {}).get('enabled', False)
    
    try:
        # Disable plugin
        if 'plugins' not in config:
            config['plugins'] = {}
        if 'regex_processor' not in config['plugins']:
            config['plugins']['regex_processor'] = {}
        config['plugins']['regex_processor']['enabled'] = False
        
        # Reset and recreate
        reset_pipeline()
        reset_plugin_manager()
        
        # Test that forward slash is NOT replaced when disabled
        result = post_process_transcription("Say forward slash please")
        assert "/" not in result, "Regex should not apply when disabled"
        print("[PASS] Plugin correctly disabled when configured off")
        
    finally:
        # Restore original setting
        config['plugins']['regex_processor']['enabled'] = original_enabled
        reset_pipeline()
        reset_plugin_manager()


def test_backward_compatibility():
    """Ensure Phase 1 functionality still works"""
    # Test original functionality
    assert post_process_transcription(". . . .") == "", "Silence removal broken"
    
    result = post_process_transcription("Hello world")
    assert "Hello" in result or "hello" in result, "Basic processing broken"
    
    print("[PASS] Backward compatibility maintained")


def run_all_tests():
    """Run all Phase 2 tests"""
    print("\n" + "="*50)
    print("PHASE 2 PLUGIN SYSTEM TESTS")
    print("="*50 + "\n")
    
    try:
        plugins = test_plugin_discovery()
        print()
        
        test_plugin_initialization()
        print()
        
        test_plugin_in_pipeline()
        print()
        
        config = ConfigManager.get_config()
        if config and config.get('plugins', {}).get('regex_processor', {}).get('enabled'):
            test_regex_replacements()
            print()
            
            test_plugin_disable()
            print()
        else:
            print("[SKIP] Regex tests skipped (plugin not enabled in config)")
            print()
        
        test_backward_compatibility()
        
        print("\n" + "="*50)
        print("ALL PHASE 2 TESTS PASSED!")
        print("Plugin system is working correctly.")
        print("="*50 + "\n")
        
        # Summary
        print("Summary:")
        for plugin in plugins:
            status = "enabled" if plugin['enabled'] else "disabled"
            print(f"  - {plugin['name']} v{plugin['version']} ({status})")
            if plugin['description']:
                print(f"    {plugin['description']}")
        
        return True
        
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        print("\nIf tests fail, you can rollback with:")
        print("  git checkout -- src/processing/factory.py")
        print("  rm -rf src/plugins/")
        return False
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
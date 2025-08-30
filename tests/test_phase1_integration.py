"""
Phase 1 Integration Test
Run this after refactoring to ensure nothing broke

Run with: python tests/test_phase1_integration.py
"""
import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import after path is set
from src.transcription import post_process_transcription
from src.utils import ConfigManager

# Initialize ConfigManager at module level
ConfigManager.initialize()


def test_silence_removal():
    """Test that silence (dots only) is still removed"""
    test_cases = [
        (". . . . .", ""),
        ("...", ""),
        ("   .  .  .  ", ""),
        (". . . . . . . . .", ""),
    ]
    
    for input_text, expected in test_cases:
        result = post_process_transcription(input_text)
        assert result == expected, f"Failed: '{input_text}' -> '{result}' (expected '{expected}')"
    
    print("[PASS] Silence removal works")


def test_dot_sequences():
    """Test that dot sequences are cleaned but normal text preserved"""
    test_cases = [
        ("Hello. . . . . world", "Hello world"),
        ("Testing. . . . .", "Testing"),
        ("One. Two. Three.", "One. Two. Three."),  # Normal periods preserved
        ("Start . . . . middle . . . . end", "Start middle end"),
    ]
    
    for input_text, expected_base in test_cases:
        result = post_process_transcription(input_text)
        # Account for potential trailing space from config
        assert result in [expected_base, expected_base + " "], \
            f"Failed: '{input_text}' -> '{result}'"
    
    print("[PASS] Dot sequence cleaning works")


def test_config_dependent_processing():
    """Test configuration-dependent processing"""
    # Config already initialized at module level
    
    # Test a normal transcription
    result = post_process_transcription("Hello World")
    
    # Check it returns something (exact result depends on config)
    assert result, "Empty result for normal text"
    assert "Hello" in result or "hello" in result, "Text not preserved"
    
    print("[PASS] Configuration-dependent processing works")


def test_empty_input():
    """Test empty input handling"""
    test_cases = [
        "",
        None,
        "   ",  # Just spaces
    ]
    
    for input_text in test_cases:
        result = post_process_transcription(input_text)
        assert result == "", f"Failed for empty input: '{input_text}' -> '{result}'"
    
    print("[PASS] Empty input handling works")


def test_pipeline_structure():
    """Test that the pipeline structure is working"""
    from src.processing.factory import get_pipeline
    
    pipeline = get_pipeline()
    
    # Check pipeline has processors
    assert len(pipeline) > 0, "Pipeline has no processors"
    
    # Check expected processors are present
    processor_names = pipeline.get_processor_names()
    assert "SilenceRemoval" in processor_names, "SilenceRemoval processor missing"
    assert "WhitespaceNormalizer" in processor_names, "WhitespaceNormalizer missing"
    
    print(f"[PASS] Pipeline has {len(pipeline)} processors: {', '.join(processor_names)}")


def test_backwards_compatibility():
    """Ensure the function signature and behavior is compatible"""
    # Test that function exists and accepts a string
    result = post_process_transcription("Test")
    assert isinstance(result, str), "Function should return a string"
    
    # Test that it handles the same edge cases as before
    assert post_process_transcription(". . .") == ""
    
    print("[PASS] Backwards compatibility maintained")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*50)
    print("PHASE 1 INTEGRATION TESTS")
    print("="*50 + "\n")
    
    try:
        test_silence_removal()
        test_dot_sequences()
        test_config_dependent_processing()
        test_empty_input()
        test_pipeline_structure()
        test_backwards_compatibility()
        
        print("\n" + "="*50)
        print("ALL PHASE 1 TESTS PASSED!")
        print("The application should work exactly as before.")
        print("="*50 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        print("\nIf tests fail, you can rollback with:")
        print("  git checkout -- src/transcription.py")
        print("  rm -rf src/processing/")
        return False
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
"""
Live test of regex plugin functionality
Tests the actual transcription pipeline with regex replacements
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from utils import ConfigManager
from transcription import post_process_transcription

# Initialize config
ConfigManager.initialize()

print("Testing Regex Plugin with Real Transcription Pipeline")
print("=" * 50)

# Test cases that simulate what Whisper might output
test_cases = [
    # Test forward slash
    ("Please use forward slash in the path", 
     "Please use / in the path"),
    
    # Test new line  
    ("First paragraph new line Second paragraph",
     "First paragraph \n Second paragraph"),
    
    # Test filler words
    ("Um let me think about um that",
     " let me think about  that"),
     
    ("Uh hello there uh how are you",
     " hello there  how are you"),
    
    # Combined test
    ("Um please type forward slash and then new line",
     " please type / and then \n"),
     
    # Normal text should pass through
    ("This is normal text without triggers",
     "This is normal text without triggers"),
]

all_passed = True

for input_text, expected_base in test_cases:
    result = post_process_transcription(input_text)
    
    # Account for potential trailing space
    result_stripped = result.rstrip()
    expected_stripped = expected_base.rstrip()
    
    # Check if transformation worked
    if result_stripped == expected_stripped or expected_stripped in result_stripped:
        print(f"[PASS]")
        print(f"  Input:    '{input_text}'")
        print(f"  Expected: '{expected_base}'")
        print(f"  Got:      '{result}'")
    else:
        print(f"[FAIL]")
        print(f"  Input:    '{input_text}'")
        print(f"  Expected: '{expected_base}'")
        print(f"  Got:      '{result}'")
        all_passed = False
    print()

print("=" * 50)
if all_passed:
    print("All regex replacements working correctly!")
    print("\nYou can now say:")
    print("  - 'forward slash' becomes /")
    print("  - 'new line' becomes [actual newline]")
    print("  - 'um' and 'uh' are removed")
else:
    print("Some tests failed. Check configuration.")
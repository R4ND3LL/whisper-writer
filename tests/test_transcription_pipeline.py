"""
Quick test to verify transcription pipeline works end-to-end
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.utils import ConfigManager
from src.transcription import post_process_transcription

# Initialize config
ConfigManager.initialize()

print("Testing transcription pipeline...")
print("-" * 40)

# Test cases that would come from Whisper
test_cases = [
    # Normal transcription
    ("Hello world", "Should preserve normal text"),
    
    # Silence artifacts
    (". . . . .", "Should remove pure silence"),
    ("Testing. . . . . done", "Should clean dot sequences"),
    
    # Mixed case
    ("The Quick Brown Fox", "Should handle mixed case"),
    
    # Edge cases
    ("", "Should handle empty"),
    ("   ", "Should handle spaces"),
    
    # Sentence ending
    ("This is a test.", "Should handle period based on config"),
]

for input_text, description in test_cases:
    result = post_process_transcription(input_text)
    print(f"\n{description}:")
    print(f"  Input:  '{input_text}'")
    print(f"  Output: '{result}'")

print("\n" + "-" * 40)
print("Pipeline test complete!")
print("\nPipeline structure:")

from src.processing.factory import get_pipeline
pipeline = get_pipeline()
for i, processor in enumerate(pipeline.processors, 1):
    enabled = "enabled" if processor.is_enabled() else "disabled"
    print(f"  {i}. {processor.get_name()} ({enabled})")

print(f"\nTotal processors: {len(pipeline)}")
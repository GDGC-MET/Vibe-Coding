"""
Tests for the LocalRulesProvider emoji detection functionality.
"""
import unittest
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_vibe_chat.providers.local_rules import LocalRulesProvider


class TestEmojiDetection(unittest.TestCase):
    """Test cases for emoji detection in LocalRulesProvider."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.provider = LocalRulesProvider()
    
    def test_basic_emoji_detection(self):
        """Test detection of basic emotion keywords."""
        test_cases = [
            ("I am happy", "happy"),
            ("This makes me sad", "sad"),
            ("I am angry", "angry"),
            ("I love this", "love"),
            ("I am excited", "excited")
        ]
        
        for test_input, emotion in test_cases:
            with self.subTest(input=test_input):
                response = self.provider.generate(test_input)
                # Check that response contains an emoji for the emotion
                self.assertTrue(any(emoji in response for emoji in self.provider._emoji_keywords[emotion]))
    
    def test_word_variations(self):
        """Test detection of emotion word variations."""
        test_cases = [
            ("This is exciting", "excited"),
            ("I am confused", "confused"),
            ("This is surprising", "surprised"),
            ("I am thinking", "thinking")
        ]
        
        for test_input, emotion in test_cases:
            with self.subTest(input=test_input):
                response = self.provider.generate(test_input)
                self.assertTrue(any(emoji in response for emoji in self.provider._emoji_keywords[emotion]))
    
    def test_case_insensitive_detection(self):
        """Test that emoji detection is case insensitive."""
        response = self.provider.generate("HAPPY")
        self.assertTrue(any(emoji in response for emoji in self.provider._emoji_keywords["happy"]))
    
    def test_no_emoji_for_unrecognized_keywords(self):
        """Test that no emoji is added for unrecognized keywords."""
        response = self.provider.generate("I am hungry")
        # Check that response doesn't contain any emojis from our mapping
        all_emojis = []
        for emoji_list in self.provider._emoji_keywords.values():
            all_emojis.extend(emoji_list)
        
        self.assertFalse(any(emoji in response for emoji in all_emojis))
    
    def test_emoji_with_existing_responses(self):
        """Test that emojis are properly added to existing response patterns."""
        # Test gym response with emoji
        response = self.provider.generate("I am happy about my gym workout")
        self.assertTrue(any(gym_response in response for gym_response in self.provider._motivation))
        self.assertTrue(any(emoji in response for emoji in self.provider._emoji_keywords["happy"]))
        
        # Test hello response with emoji
        response = self.provider.generate("hello, I am excited")
        self.assertIn("Hey there", response)
        self.assertTrue(any(emoji in response for emoji in self.provider._emoji_keywords["excited"]))


if __name__ == '__main__':
    unittest.main()

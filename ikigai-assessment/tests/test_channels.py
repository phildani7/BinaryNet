"""
Unit tests for individual scoring channels
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import numpy as np
from src.phase2_scoring.channel1_ctt.classical_scorer import (
    ClassicalTestTheoryScorer, LikertRubric
)
from src.phase2_scoring.channel3_nlp.nlp_scorer import (
    NLPFeatureExtractor, NLPScorer
)
from src.phase2_scoring.channel4_qualitative.framework_scorer import (
    IntensityCoder, ConvictionCoder, CoherenceCoder
)


class TestCTTChannel:
    """Test Classical Test Theory scoring"""

    def test_likert_rubric_high_score(self):
        """Test that detailed, emotional responses get high scores"""
        response = """
        I am absolutely passionate about teaching. When I'm helping someone
        learn a new concept and see that moment of understanding, time
        completely disappears. I've been doing this for years and it never
        gets old. For example, last year I mentored a student who went from
        struggling to building her first model.
        """

        score = LikertRubric.score_response(response, 'love')
        assert score >= 4, "Detailed response should score high"

    def test_likert_rubric_low_score(self):
        """Test that brief responses get low scores"""
        response = "I like teaching"

        score = LikertRubric.score_response(response, 'love')
        assert score <= 2, "Brief response should score low"

    def test_normalize_to_100(self):
        """Test normalization to 0-100 scale"""
        scorer = ClassicalTestTheoryScorer()

        # Test scale conversion
        assert scorer._normalize_to_100(1, 1, 5) == 0
        assert scorer._normalize_to_100(5, 1, 5) == 100
        assert scorer._normalize_to_100(3, 1, 5) == 50

    def test_score_dimension(self):
        """Test dimension scoring"""
        scorer = ClassicalTestTheoryScorer()

        responses = [
            {
                'response_text': 'I love data analysis and teaching',
                'question_dimension': 'love'
            },
            {
                'response_text': 'Passionate about helping others learn',
                'question_dimension': 'love'
            }
        ]

        result = scorer.score_dimension(responses, 'love')

        assert result.dimension_id == 'love'
        assert 0 <= result.normalized_score <= 100
        assert 0 <= result.reliability_alpha <= 1


class TestNLPChannel:
    """Test NLP/ML scoring"""

    def test_feature_extraction(self):
        """Test linguistic feature extraction"""
        text = """
        I definitely love teaching data science. I'm passionate about it
        and have been doing this for years. For example, last week I helped
        a student who was struggling.
        """

        features = NLPFeatureExtractor.extract_features(text)

        assert features['word_count'] > 0
        assert features['sentence_count'] > 0
        assert features['certainty_count'] > 0  # "definitely"
        assert features['positive_emotion_count'] > 0  # "love", "passionate"

    def test_conviction_ratio(self):
        """Test conviction vs hedging detection"""
        # High conviction text
        certain_text = "I definitely know this absolutely works. I'm certain."
        features_certain = NLPFeatureExtractor.extract_features(certain_text)

        # High hedging text
        uncertain_text = "I think maybe this might work. I guess it could."
        features_uncertain = NLPFeatureExtractor.extract_features(uncertain_text)

        assert features_certain['conviction_ratio'] > features_uncertain['conviction_ratio']

    def test_nlp_scorer(self):
        """Test complete NLP scoring"""
        scorer = NLPScorer()

        response = """
        I am passionate about teaching data science because it transforms lives.
        I love seeing students go from confused to confident. This work energizes
        me and I feel excited every time I help someone learn.
        """

        result = scorer.score_response(response, 'love')

        assert 0 <= result.combined_score <= 100
        assert -1 <= result.sentiment_score <= 1
        assert 0 <= result.semantic_similarity_score <= 1


class TestQualitativeChannel:
    """Test Qualitative Framework Method"""

    def test_intensity_coder(self):
        """Test intensity coding"""
        # High intensity (detailed, emotional)
        high_text = """
        I am deeply passionate about this work. Let me give you several examples.
        First, there was the time when... Second, I remember vividly how...
        This is profoundly meaningful to me because...
        """

        high_score = IntensityCoder.code_intensity(high_text, 'passionate')

        # Low intensity (brief mention)
        low_text = "I like this work"
        low_score = IntensityCoder.code_intensity(low_text, 'like')

        assert high_score > low_score
        assert 1 <= high_score <= 5
        assert 1 <= low_score <= 5

    def test_conviction_coder(self):
        """Test conviction coding"""
        # Strong conviction
        strong_text = "I definitely know this. I'm absolutely certain. I will always do this."
        strong_score = ConvictionCoder.code_conviction(strong_text)

        # Weak conviction
        weak_text = "I think maybe this might work. I guess it could be okay."
        weak_score = ConvictionCoder.code_conviction(weak_text)

        assert strong_score > weak_score
        assert 1 <= strong_score <= 5
        assert 1 <= weak_score <= 5

    def test_coherence_coder(self):
        """Test narrative coherence"""
        # Coherent narrative with linking
        coherent_responses = [
            "I love teaching data science",
            "As I mentioned, teaching connects to my passion for helping others",
            "This ties into what I said earlier about education"
        ]

        coherent_score = CoherenceCoder.code_coherence(coherent_responses, 'love')

        # Fragmented narrative
        fragmented_responses = [
            "I like data",
            "Sometimes I teach",
            "Money is important"
        ]

        fragmented_score = CoherenceCoder.code_coherence(fragmented_responses, 'love')

        assert coherent_score >= fragmented_score
        assert 1 <= coherent_score <= 5


class TestValidation:
    """Test validation metrics"""

    def test_cross_channel_comparison(self):
        """Test that we can compare channels"""
        from src.validation.cross_channel_validator import CrossChannelValidator

        validator = CrossChannelValidator()

        channel1_scores = {'love': 75, 'good_at': 80}
        channel2_scores = {'love': 70, 'good_at': 85}

        comparison = validator.compare_two_channels(
            channel1_scores,
            channel2_scores,
            'ctt',
            'irt'
        )

        assert 'love' in comparison
        assert 'good_at' in comparison
        assert comparison['love']['absolute_difference'] == 5


def run_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("Running Unit Tests")
    print("="*80 + "\n")

    # Run with pytest if available
    try:
        pytest.main([__file__, '-v'])
    except:
        # Manual test running
        print("pytest not available, running tests manually...\n")

        test_classes = [
            TestCTTChannel(),
            TestNLPChannel(),
            TestQualitativeChannel(),
            TestValidation()
        ]

        passed = 0
        failed = 0

        for test_class in test_classes:
            print(f"\n{test_class.__class__.__name__}:")
            for method_name in dir(test_class):
                if method_name.startswith('test_'):
                    try:
                        method = getattr(test_class, method_name)
                        method()
                        print(f"  ✓ {method_name}")
                        passed += 1
                    except Exception as e:
                        print(f"  ✗ {method_name}: {e}")
                        failed += 1

        print(f"\n{'='*80}")
        print(f"Results: {passed} passed, {failed} failed")
        print("="*80 + "\n")


if __name__ == "__main__":
    run_tests()

"""
Channel 4: Qualitative Framework Method Scoring
Systematic thematic analysis with intensity and coherence coding
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class QualitativeCode:
    """Individual qualitative code"""
    theme_label: str
    theme_description: str
    dimension: str
    frequency: int  # Number of mentions
    intensity: int  # 1-5 scale
    pervasiveness: float  # Percentage of transcript
    conviction: int  # 1-5 scale
    coherence: int  # 1-5 scale
    example_quotes: List[str] = field(default_factory=list)


@dataclass
class FrameworkScore:
    """Framework Method score result"""
    dimension_id: str
    frequency_score: float
    intensity_score: float
    pervasiveness_score: float
    conviction_score: float
    coherence_score: float
    combined_score: float  # 0-100
    themes: List[QualitativeCode]


class IntensityCoder:
    """
    Systematic intensity coding on 1-5 ordinal scale

    Based on elaboration depth and emotional weight
    """

    INTENSITY_RUBRIC = {
        5: {
            "label": "Extensive elaboration",
            "criteria": [
                "Vivid imagery and rich detail",
                "Multiple interconnected examples",
                "Strong emotional language throughout",
                "Deeply meaningful connections articulated"
            ]
        },
        4: {
            "label": "Rich detail",
            "criteria": [
                "Multiple examples provided",
                "Emotional language present",
                "Clear narrative thread"
            ]
        },
        3: {
            "label": "Moderate elaboration",
            "criteria": [
                "At least one example with some detail",
                "Some emotional content"
            ]
        },
        2: {
            "label": "Minimal detail",
            "criteria": [
                "Mentioned with minimal elaboration",
                "Limited emotional content"
            ]
        },
        1: {
            "label": "Brief mention",
            "criteria": [
                "Only mentioned in passing",
                "No elaboration"
            ]
        }
    }

    @staticmethod
    def code_intensity(text: str, theme: str) -> int:
        """
        Code intensity of theme discussion

        Args:
            text: Full text segment
            theme: Theme being evaluated

        Returns:
            Intensity score (1-5)
        """
        text_lower = text.lower()
        theme_lower = theme.lower()

        # Count mentions
        mentions = text_lower.count(theme_lower)

        # Check for elaboration indicators
        has_vivid_language = any(
            word in text_lower
            for word in ['vividly', 'clearly', 'specifically', 'exactly', 'precisely']
        )

        has_examples = any(
            phrase in text_lower
            for phrase in ['for example', 'for instance', 'such as', 'like when']
        )

        # Count emotional words
        emotional_words = ['passion', 'love', 'excited', 'energized', 'fulfilled',
                          'thrilled', 'enthusiastic', 'deeply', 'strongly']
        emotion_count = sum(1 for word in emotional_words if word in text_lower)

        # Word count for this theme (approximate)
        words = text.split()
        word_count = len(words)

        # Scoring logic
        score = 1

        if word_count > 50:
            score = max(score, 2)
        if word_count > 100:
            score = max(score, 3)
        if word_count > 150:
            score = max(score, 4)

        if has_examples:
            score = min(5, score + 1)

        if emotion_count >= 2:
            score = min(5, score + 1)

        if has_vivid_language:
            score = min(5, score + 1)

        return score


class ConvictionCoder:
    """
    Code conviction level based on language patterns

    Strong conviction: "definitely", "absolutely", declarative statements
    Weak conviction: "maybe", "I think", "kind of"
    """

    STRONG_CONVICTION_MARKERS = [
        'definitely', 'absolutely', 'certainly', 'always', 'never',
        'clearly', 'obviously', 'without doubt', 'unquestionably'
    ]

    MODERATE_CONVICTION_MARKERS = [
        'usually', 'often', 'generally', 'typically', 'regularly'
    ]

    WEAK_CONVICTION_MARKERS = [
        'maybe', 'perhaps', 'possibly', 'might', 'could', 'may',
        'i think', 'i guess', 'kind of', 'sort of', 'probably',
        'i believe', 'seems like'
    ]

    @staticmethod
    def code_conviction(text: str) -> int:
        """
        Code conviction level (1-5)

        Args:
            text: Text to analyze

        Returns:
            Conviction score (1-5)
        """
        text_lower = text.lower()

        # Count markers
        strong_count = sum(
            1 for marker in ConvictionCoder.STRONG_CONVICTION_MARKERS
            if marker in text_lower
        )

        moderate_count = sum(
            1 for marker in ConvictionCoder.MODERATE_CONVICTION_MARKERS
            if marker in text_lower
        )

        weak_count = sum(
            1 for marker in ConvictionCoder.WEAK_CONVICTION_MARKERS
            if marker in text_lower
        )

        # Check for first-person declarative
        first_person_declarative = (
            text_lower.count(' i am ') +
            text_lower.count(' i have ') +
            text_lower.count(' i will ')
        )

        # Scoring
        total_markers = strong_count + moderate_count + weak_count

        if total_markers == 0:
            # Use first-person declarative as proxy
            if first_person_declarative >= 3:
                return 4
            elif first_person_declarative >= 1:
                return 3
            else:
                return 3  # Neutral

        # Calculate conviction ratio
        if total_markers > 0:
            conviction_ratio = (
                (strong_count * 2 + moderate_count * 1) /
                (total_markers * 2)
            )

            # Map to 1-5 scale
            if conviction_ratio > 0.8:
                return 5
            elif conviction_ratio > 0.6:
                return 4
            elif conviction_ratio > 0.4:
                return 3
            elif conviction_ratio > 0.2:
                return 2
            else:
                return 1

        return 3


class CoherenceCoder:
    """
    Code narrative coherence across responses

    High coherence: Consistent story, logical connections, meta-awareness
    Low coherence: Contradictions, fragmented, minimal integration
    """

    @staticmethod
    def code_coherence(all_responses: List[str], dimension: str) -> int:
        """
        Code narrative coherence (1-5)

        Args:
            all_responses: All responses for participant
            dimension: Dimension being evaluated

        Returns:
            Coherence score (1-5)
        """
        combined_text = " ".join(all_responses).lower()

        # Look for integration/linking words
        linking_phrases = [
            'connects to', 'relates to', 'ties into', 'building on',
            'as i mentioned', 'like i said', 'this connects back to',
            'consistent with', 'aligns with'
        ]

        linking_count = sum(
            1 for phrase in linking_phrases
            if phrase in combined_text
        )

        # Look for contradictions
        contradiction_patterns = [
            (r'i love .+ but i also hate', True),
            (r'passionate about .+ however .+ not interested', True),
            (r'good at .+ but terrible at', False),  # Not always contradiction
        ]

        has_contradictions = any(
            re.search(pattern, combined_text)
            for pattern, is_contradiction in contradiction_patterns
            if is_contradiction
        )

        # Meta-awareness indicators
        meta_phrases = [
            'i notice', 'i realize', 'pattern i see', 'theme that emerges',
            'consistent thread', 'looking back', 'reflecting on'
        ]

        meta_count = sum(
            1 for phrase in meta_phrases
            if phrase in combined_text
        )

        # Calculate coherence
        score = 3  # Start neutral

        if linking_count >= 3:
            score += 1
        if meta_count >= 2:
            score += 1
        if has_contradictions:
            score -= 2

        return max(1, min(5, score))


class FrameworkMethodScorer:
    """
    Framework Method scoring implementation

    Implements five-stage Framework Method:
    1. Familiarization (implicit - reads all data)
    2. Coding Framework (uses dimensional structure)
    3. Indexing (applies codes systematically)
    4. Charting (organizes in matrix)
    5. Interpretation (generates scores)

    Quantification via:
    - Frequency counting
    - Intensity rating (1-5)
    - Pervasiveness (% of transcript)
    - Conviction coding (1-5)
    - Coherence assessment (1-5)
    """

    def __init__(self):
        self.intensity_coder = IntensityCoder()
        self.conviction_coder = ConvictionCoder()
        self.coherence_coder = CoherenceCoder()

    def code_dimension(
        self,
        responses: List[Dict[str, Any]],
        dimension: str,
        full_transcript: str
    ) -> FrameworkScore:
        """
        Apply Framework Method coding to dimension

        Args:
            responses: Responses specific to this dimension
            dimension: Dimension ID
            full_transcript: Complete transcript for coherence analysis

        Returns:
            FrameworkScore with all metrics
        """
        # Extract themes (simplified - in production use proper qualitative analysis)
        themes = self._extract_themes(responses, dimension)

        # Code each theme
        coded_themes = []
        for theme in themes:
            coded_theme = self._code_theme(theme, responses, full_transcript, dimension)
            coded_themes.append(coded_theme)

        # Calculate aggregate scores
        frequency_score = self._calculate_frequency_score(coded_themes)
        intensity_score = self._calculate_intensity_score(coded_themes)
        pervasiveness_score = self._calculate_pervasiveness_score(coded_themes)
        conviction_score = self._calculate_conviction_score(responses)
        coherence_score = self._calculate_coherence_score(full_transcript, dimension)

        # Weighted composite
        combined_score = (
            0.20 * frequency_score +
            0.30 * intensity_score +
            0.20 * pervasiveness_score +
            0.15 * conviction_score +
            0.15 * coherence_score
        ) * 100  # Scale to 0-100

        return FrameworkScore(
            dimension_id=dimension,
            frequency_score=frequency_score,
            intensity_score=intensity_score,
            pervasiveness_score=pervasiveness_score,
            conviction_score=conviction_score,
            coherence_score=coherence_score,
            combined_score=combined_score,
            themes=coded_themes
        )

    def _extract_themes(
        self,
        responses: List[Dict[str, Any]],
        dimension: str
    ) -> List[str]:
        """Extract themes from responses (simplified)"""
        # In production, use proper thematic analysis
        # For now, return dimension as single theme

        combined_text = " ".join([r.get('response_text', '') for r in responses])

        # Simple keyword extraction
        if dimension == 'love':
            themes = ['passion', 'enjoyment', 'fulfillment']
        elif dimension == 'good_at':
            themes = ['skills', 'expertise', 'strengths']
        elif dimension == 'world_needs':
            themes = ['problems', 'impact', 'contribution']
        elif dimension == 'paid_for':
            themes = ['income', 'market', 'viability']
        else:
            themes = ['general']

        # Filter to themes actually mentioned
        combined_lower = combined_text.lower()
        present_themes = [t for t in themes if t in combined_lower]

        return present_themes if present_themes else [dimension]

    def _code_theme(
        self,
        theme: str,
        responses: List[Dict[str, Any]],
        full_transcript: str,
        dimension: str
    ) -> QualitativeCode:
        """Code a single theme"""
        combined_text = " ".join([r.get('response_text', '') for r in responses])

        # Frequency
        frequency = combined_text.lower().count(theme.lower())

        # Intensity
        intensity = self.intensity_coder.code_intensity(combined_text, theme)

        # Pervasiveness
        theme_words = len([w for w in combined_text.split() if theme.lower() in w.lower()])
        total_words = len(full_transcript.split())
        pervasiveness = (theme_words / total_words * 100) if total_words > 0 else 0

        # Conviction
        conviction = self.conviction_coder.code_conviction(combined_text)

        # Coherence
        coherence = self.coherence_coder.code_coherence(
            [r.get('response_text', '') for r in responses],
            dimension
        )

        # Extract example quotes
        quotes = self._extract_quotes(combined_text, theme, max_quotes=2)

        return QualitativeCode(
            theme_label=theme,
            theme_description=f"Theme: {theme} in {dimension}",
            dimension=dimension,
            frequency=frequency,
            intensity=intensity,
            pervasiveness=pervasiveness,
            conviction=conviction,
            coherence=coherence,
            example_quotes=quotes
        )

    @staticmethod
    def _extract_quotes(text: str, theme: str, max_quotes: int = 2) -> List[str]:
        """Extract relevant quotes mentioning theme"""
        sentences = text.split('.')
        quotes = []

        for sentence in sentences:
            if theme.lower() in sentence.lower() and len(sentence.strip()) > 20:
                quotes.append(sentence.strip() + '.')
                if len(quotes) >= max_quotes:
                    break

        return quotes

    @staticmethod
    def _calculate_frequency_score(themes: List[QualitativeCode]) -> float:
        """Calculate normalized frequency score (0-1)"""
        if not themes:
            return 0.0

        total_frequency = sum(t.frequency for t in themes)
        # Normalize (assume max frequency of 10 is excellent)
        normalized = min(1.0, total_frequency / 10)

        return normalized

    @staticmethod
    def _calculate_intensity_score(themes: List[QualitativeCode]) -> float:
        """Calculate average intensity score (0-1)"""
        if not themes:
            return 0.0

        avg_intensity = np.mean([t.intensity for t in themes])
        # Convert 1-5 scale to 0-1
        normalized = (avg_intensity - 1) / 4

        return normalized

    @staticmethod
    def _calculate_pervasiveness_score(themes: List[QualitativeCode]) -> float:
        """Calculate pervasiveness score (0-1)"""
        if not themes:
            return 0.0

        total_pervasiveness = sum(t.pervasiveness for t in themes)
        # Normalize (assume 20% is excellent)
        normalized = min(1.0, total_pervasiveness / 20)

        return normalized

    def _calculate_conviction_score(self, responses: List[Dict[str, Any]]) -> float:
        """Calculate overall conviction score (0-1)"""
        combined_text = " ".join([r.get('response_text', '') for r in responses])
        conviction = self.conviction_coder.code_conviction(combined_text)

        # Convert 1-5 to 0-1
        return (conviction - 1) / 4

    def _calculate_coherence_score(self, full_transcript: str, dimension: str) -> float:
        """Calculate coherence score (0-1)"""
        responses_text = [full_transcript]  # Simplified
        coherence = self.coherence_coder.code_coherence(responses_text, dimension)

        # Convert 1-5 to 0-1
        return (coherence - 1) / 4


def score_session_qualitative(
    session_responses: List[Dict[str, Any]],
    full_transcript: str
) -> Dict[str, Any]:
    """
    Score a complete assessment session using Framework Method

    Args:
        session_responses: List of all question responses
        full_transcript: Complete transcript

    Returns:
        Complete qualitative scoring results
    """
    # Group responses by dimension
    dimension_responses = {
        'love': [],
        'good_at': [],
        'world_needs': [],
        'paid_for': []
    }

    for response in session_responses:
        dim = response.get('question_dimension')
        if dim in dimension_responses:
            dimension_responses[dim].append(response)

    # Initialize scorer
    scorer = FrameworkMethodScorer()

    # Score each dimension
    dimension_scores = {}
    for dim, responses in dimension_responses.items():
        if responses:
            framework_score = scorer.code_dimension(responses, dim, full_transcript)
            dimension_scores[dim] = framework_score

    # Calculate intersections
    intersection_scores = {}
    normalized_scores = {dim: score.combined_score for dim, score in dimension_scores.items()}

    if 'love' in normalized_scores and 'good_at' in normalized_scores:
        intersection_scores['passion'] = np.sqrt(normalized_scores['love'] * normalized_scores['good_at'])

    if 'love' in normalized_scores and 'world_needs' in normalized_scores:
        intersection_scores['mission'] = np.sqrt(normalized_scores['love'] * normalized_scores['world_needs'])

    if 'good_at' in normalized_scores and 'paid_for' in normalized_scores:
        intersection_scores['profession'] = np.sqrt(normalized_scores['good_at'] * normalized_scores['paid_for'])

    if 'world_needs' in normalized_scores and 'paid_for' in normalized_scores:
        intersection_scores['vocation'] = np.sqrt(normalized_scores['world_needs'] * normalized_scores['paid_for'])

    # Overall ikigai
    all_scores = list(normalized_scores.values())
    overall_ikigai = np.prod(all_scores) ** 0.25 if len(all_scores) == 4 else 0

    return {
        'channel': 'qual',
        'dimension_scores': {
            dim: {
                'frequency_score': score.frequency_score,
                'intensity_score': score.intensity_score,
                'pervasiveness_score': score.pervasiveness_score,
                'conviction_score': score.conviction_score,
                'coherence_score': score.coherence_score,
                'normalized_score': score.combined_score,
                'themes': [
                    {
                        'label': theme.theme_label,
                        'frequency': theme.frequency,
                        'intensity': theme.intensity,
                        'conviction': theme.conviction
                    }
                    for theme in score.themes
                ]
            }
            for dim, score in dimension_scores.items()
        },
        'intersection_scores': intersection_scores,
        'overall_alignment': {
            'overall_ikigai_score': overall_ikigai
        },
        'method': 'Qualitative Framework Method',
        'version': '1.0'
    }

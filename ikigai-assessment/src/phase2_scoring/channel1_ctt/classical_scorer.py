"""
Channel 1: Classical Test Theory (CTT) Scoring
Traditional psychometric approach with Likert scales and factor analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CTTScore:
    """Classical Test Theory score result"""
    dimension_id: str
    raw_score: float
    normalized_score: float  # 0-100 scale
    z_score: float
    t_score: float
    percentile_rank: float
    subscale_scores: Dict[str, float]
    reliability_alpha: float


class LikertRubric:
    """
    Rubric for converting qualitative responses to Likert scores

    Based on behavioral anchors as specified in research document
    """

    SCORING_RUBRIC = {
        5: {
            "label": "Very Strong",
            "criteria": [
                "Multiple detailed examples with rich emotional language",
                "Consistent enthusiasm throughout response",
                "Explicit passion statements",
                "Natural integration across responses",
                "Evidence of deep engagement (flow states, time distortion)"
            ]
        },
        4: {
            "label": "Strong",
            "criteria": [
                "Several examples with emotional content",
                "Clear enthusiasm present",
                "Some narrative integration",
                "Specific details provided"
            ]
        },
        3: {
            "label": "Moderate",
            "criteria": [
                "At least one clear example",
                "Positive language but limited depth",
                "Basic engagement evident"
            ]
        },
        2: {
            "label": "Weak",
            "criteria": [
                "Brief mention",
                "Generic language",
                "Minimal engagement or detail"
            ]
        },
        1: {
            "label": "Minimal/Absent",
            "criteria": [
                "No clear evidence",
                "Only mentioned when prompted",
                "Very limited response"
            ]
        }
    }

    @staticmethod
    def score_response(
        response_text: str,
        dimension: str,
        features: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Score a qualitative response on 1-5 Likert scale

        Args:
            response_text: Participant's response
            dimension: Which ikigai dimension (love, good_at, world_needs, paid_for)
            features: Optional pre-extracted features (word_count, sentiment, etc.)

        Returns:
            Likert score (1-5)
        """
        if not response_text or len(response_text.strip()) < 10:
            return 1  # Minimal/Absent

        # Extract basic features if not provided
        if features is None:
            features = {
                'word_count': len(response_text.split()),
                'sentence_count': response_text.count('.') + response_text.count('!') + response_text.count('?'),
                'has_emotional_language': any(
                    word in response_text.lower()
                    for word in ['love', 'passion', 'excited', 'energized', 'fulfilled', 'joy']
                ),
                'has_specific_examples': 'for example' in response_text.lower() or 'such as' in response_text.lower(),
                'has_time_references': any(
                    phrase in response_text.lower()
                    for phrase in ['lose track of time', 'hours fly by', 'time flies']
                )
            }

        # Scoring logic based on features
        score = 1  # Start with minimum

        # Word count thresholds
        if features['word_count'] > 100:
            score = max(score, 3)
        if features['word_count'] > 200:
            score = max(score, 4)
        if features['word_count'] > 300:
            score = max(score, 5)

        # Emotional language boosts score
        if features.get('has_emotional_language'):
            score = min(5, score + 1)

        # Specific examples indicate depth
        if features.get('has_specific_examples'):
            score = min(5, score + 1)

        # Flow state indicators (for "What You Love")
        if dimension == 'love' and features.get('has_time_references'):
            score = min(5, score + 1)

        return score


class ClassicalTestTheoryScorer:
    """
    Classical Test Theory scoring implementation

    Implements:
    - Likert scale scoring with rubrics
    - Subscale construction
    - Raw score calculation
    - Normalization and standardization (Z-scores, T-scores)
    - Reliability analysis (Cronbach's alpha)
    - Factor analysis (optional)
    """

    def __init__(
        self,
        normative_data: Optional[pd.DataFrame] = None,
        scale_min: int = 1,
        scale_max: int = 5
    ):
        """
        Initialize CTT scorer

        Args:
            normative_data: DataFrame with normative scores for comparison
            scale_min: Minimum Likert scale value
            scale_max: Maximum Likert scale value
        """
        self.normative_data = normative_data
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.rubric = LikertRubric()

    def score_dimension(
        self,
        responses: List[Dict[str, Any]],
        dimension: str
    ) -> CTTScore:
        """
        Score a single ikigai dimension

        Args:
            responses: List of question responses for this dimension
            dimension: Dimension ID (love, good_at, world_needs, paid_for)

        Returns:
            CTTScore object with all metrics
        """
        # Convert responses to Likert scores
        likert_scores = []
        for response in responses:
            score = self.rubric.score_response(
                response.get('response_text', ''),
                dimension,
                response.get('features')
            )
            likert_scores.append(score)

        likert_scores = np.array(likert_scores)

        # Calculate raw score (sum or mean)
        raw_score = np.mean(likert_scores)  # Using mean for easier interpretation

        # Normalize to 0-100 scale
        normalized_score = self._normalize_to_100(raw_score, self.scale_min, self.scale_max)

        # Calculate Z-score and T-score
        z_score, t_score, percentile = self._calculate_standardized_scores(
            normalized_score,
            dimension
        )

        # Calculate Cronbach's alpha (reliability)
        alpha = self._calculate_cronbach_alpha(likert_scores)

        return CTTScore(
            dimension_id=dimension,
            raw_score=raw_score,
            normalized_score=normalized_score,
            z_score=z_score,
            t_score=t_score,
            percentile_rank=percentile,
            subscale_scores={},  # Can add subscales if needed
            reliability_alpha=alpha
        )

    def score_all_dimensions(
        self,
        all_responses: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, CTTScore]:
        """
        Score all four ikigai dimensions

        Args:
            all_responses: Dict mapping dimension -> list of responses

        Returns:
            Dict mapping dimension -> CTTScore
        """
        scores = {}

        for dimension in ['love', 'good_at', 'world_needs', 'paid_for']:
            if dimension in all_responses:
                scores[dimension] = self.score_dimension(
                    all_responses[dimension],
                    dimension
                )
            else:
                logger.warning(f"No responses found for dimension: {dimension}")

        return scores

    def calculate_intersection_scores(
        self,
        dimension_scores: Dict[str, CTTScore]
    ) -> Dict[str, float]:
        """
        Calculate intersection scores using geometric mean

        Intersections:
        - Passion = √(Love × Good_At)
        - Mission = √(Love × World_Needs)
        - Profession = √(Good_At × Paid_For)
        - Vocation = √(World_Needs × Paid_For)
        """
        scores = {dim: score.normalized_score for dim, score in dimension_scores.items()}

        intersections = {}

        if 'love' in scores and 'good_at' in scores:
            intersections['passion'] = np.sqrt(scores['love'] * scores['good_at'])

        if 'love' in scores and 'world_needs' in scores:
            intersections['mission'] = np.sqrt(scores['love'] * scores['world_needs'])

        if 'good_at' in scores and 'paid_for' in scores:
            intersections['profession'] = np.sqrt(scores['good_at'] * scores['paid_for'])

        if 'world_needs' in scores and 'paid_for' in scores:
            intersections['vocation'] = np.sqrt(scores['world_needs'] * scores['paid_for'])

        return intersections

    def calculate_overall_ikigai(
        self,
        dimension_scores: Dict[str, CTTScore]
    ) -> Dict[str, float]:
        """
        Calculate overall ikigai alignment score

        Uses fourth root method: Ikigai = (Love × Good_At × World_Needs × Paid_For)^(1/4)
        """
        scores = [score.normalized_score for score in dimension_scores.values()]

        if len(scores) != 4:
            logger.warning(f"Expected 4 dimensions, got {len(scores)}")
            return {}

        # Fourth root method (multiplicative)
        overall_ikigai = np.prod(scores) ** 0.25

        # Purpose Clarity Index = Mean × (1 - CV)
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        cv = std_score / mean_score if mean_score > 0 else 0
        purpose_clarity = mean_score * (1 - cv)

        return {
            'overall_ikigai_score': overall_ikigai,
            'purpose_clarity_index': purpose_clarity,
            'coefficient_of_variation': cv,
            'mean_alignment': mean_score,
            'std_alignment': std_score
        }

    @staticmethod
    def _normalize_to_100(score: float, scale_min: float, scale_max: float) -> float:
        """Normalize score to 0-100 scale"""
        return ((score - scale_min) / (scale_max - scale_min)) * 100

    def _calculate_standardized_scores(
        self,
        normalized_score: float,
        dimension: str
    ) -> Tuple[float, float, float]:
        """
        Calculate Z-score, T-score, and percentile rank

        Uses normative data if available, otherwise uses assumed population parameters
        """
        if self.normative_data is not None and dimension in self.normative_data.columns:
            # Use actual normative statistics
            mean = self.normative_data[dimension].mean()
            std = self.normative_data[dimension].std()
        else:
            # Use assumed population parameters
            mean = 50.0  # Assume centered at 50
            std = 15.0   # Assume SD of 15

        # Z-score: z = (X - μ) / σ
        z_score = (normalized_score - mean) / std if std > 0 else 0

        # T-score: T = 50 + 10z
        t_score = 50 + 10 * z_score

        # Percentile rank (using normal distribution approximation)
        from scipy import stats
        percentile = stats.norm.cdf(z_score) * 100

        return z_score, t_score, percentile

    @staticmethod
    def _calculate_cronbach_alpha(scores: np.ndarray) -> float:
        """
        Calculate Cronbach's alpha reliability coefficient

        Formula: α = (k/(k-1)) × [1 - (Σσᵢ²/σₜ²)]
        where k = number of items, σᵢ² = variance of item i, σₜ² = variance of total

        Note: This is a simplified version for single-dimension internal consistency.
        For multi-item scales, pass all item scores.
        """
        k = len(scores)

        if k < 2:
            return np.nan  # Need at least 2 items

        # Treat each response as an "item"
        # For proper alpha calculation, need item-level variance
        # This is simplified - in production, pass matrix of all items

        item_variances = np.var(scores, ddof=1)
        total_variance = np.var(scores, ddof=1)

        if total_variance == 0:
            return 1.0  # Perfect consistency (no variance)

        alpha = (k / (k - 1)) * (1 - (item_variances / total_variance))

        return max(0, alpha)  # Alpha should be 0-1

    def calculate_factor_loadings(
        self,
        item_scores: pd.DataFrame,
        n_factors: int = 4
    ) -> Dict[str, Any]:
        """
        Perform exploratory factor analysis

        Args:
            item_scores: DataFrame with items as columns
            n_factors: Number of factors to extract

        Returns:
            Factor analysis results including loadings
        """
        from sklearn.decomposition import FactorAnalysis

        # Fit factor analysis
        fa = FactorAnalysis(n_components=n_factors, random_state=42)
        fa.fit(item_scores)

        # Extract loadings
        loadings = pd.DataFrame(
            fa.components_.T,
            columns=[f'Factor{i+1}' for i in range(n_factors)],
            index=item_scores.columns
        )

        return {
            'loadings': loadings,
            'communalities': 1 - fa.noise_variance_,
            'explained_variance': fa.score_,
        }


def score_session_ctt(
    session_responses: List[Dict[str, Any]],
    normative_data: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Score a complete assessment session using CTT

    Args:
        session_responses: List of all question responses
        normative_data: Optional normative comparison data

    Returns:
        Complete CTT scoring results
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
    scorer = ClassicalTestTheoryScorer(normative_data=normative_data)

    # Score all dimensions
    dimension_scores = scorer.score_all_dimensions(dimension_responses)

    # Calculate intersections
    intersection_scores = scorer.calculate_intersection_scores(dimension_scores)

    # Calculate overall ikigai
    overall_scores = scorer.calculate_overall_ikigai(dimension_scores)

    return {
        'channel': 'ctt',
        'dimension_scores': {
            dim: {
                'raw_score': score.raw_score,
                'normalized_score': score.normalized_score,
                'z_score': score.z_score,
                't_score': score.t_score,
                'percentile_rank': score.percentile_rank,
                'reliability_alpha': score.reliability_alpha
            }
            for dim, score in dimension_scores.items()
        },
        'intersection_scores': intersection_scores,
        'overall_alignment': overall_scores,
        'method': 'Classical Test Theory',
        'version': '1.0'
    }

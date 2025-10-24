"""
Cross-Channel Validation
Implements Bland-Altman analysis, ICC, correlations, and MTMM matrix
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from scipy import stats
from scipy.stats import pearsonr, spearmanr

logger = logging.getLogger(__name__)


@dataclass
class AgreementMetrics:
    """Agreement metrics between two channels"""
    channel_1: str
    channel_2: str
    dimension: str

    pearson_correlation: float
    spearman_correlation: float
    icc_value: float

    bland_altman_bias: float
    bland_altman_sd: float
    limits_of_agreement_lower: float
    limits_of_agreement_upper: float


class BlandAltmanAnalyzer:
    """
    Bland-Altman analysis for method comparison

    Assesses agreement between two measurement methods
    """

    @staticmethod
    def analyze(
        method1_scores: np.ndarray,
        method2_scores: np.ndarray
    ) -> Dict[str, float]:
        """
        Perform Bland-Altman analysis

        Args:
            method1_scores: Scores from first method
            method2_scores: Scores from second method

        Returns:
            Dict with bias, SD, and limits of agreement
        """
        # Calculate differences
        differences = method1_scores - method2_scores

        # Calculate means
        means = (method1_scores + method2_scores) / 2

        # Bias (mean difference)
        bias = np.mean(differences)

        # Standard deviation of differences
        sd_diff = np.std(differences, ddof=1)

        # Limits of agreement (±1.96 SD)
        loa_upper = bias + 1.96 * sd_diff
        loa_lower = bias - 1.96 * sd_diff

        return {
            'bias': bias,
            'sd': sd_diff,
            'loa_upper': loa_upper,
            'loa_lower': loa_lower,
            'mean_of_means': np.mean(means)
        }


class ICCCalculator:
    """
    Intraclass Correlation Coefficient calculation

    Measures test-retest reliability and inter-rater agreement
    """

    @staticmethod
    def calculate_icc(
        ratings: pd.DataFrame,
        icc_type: str = 'ICC(3,1)'
    ) -> float:
        """
        Calculate ICC

        Args:
            ratings: DataFrame with raters as columns, subjects as rows
            icc_type: Type of ICC ('ICC(1,1)', 'ICC(2,1)', 'ICC(3,1)', etc.)

        Returns:
            ICC value
        """
        # ICC(3,1): Two-way mixed effects, absolute agreement, single measure
        # This is most appropriate for method comparison

        n_subjects = len(ratings)
        n_raters = len(ratings.columns)

        # Grand mean
        grand_mean = ratings.values.mean()

        # Sum of squares
        ss_rows = n_raters * np.sum((ratings.mean(axis=1) - grand_mean) ** 2)
        ss_cols = n_subjects * np.sum((ratings.mean(axis=0) - grand_mean) ** 2)
        ss_total = np.sum((ratings.values - grand_mean) ** 2)
        ss_error = ss_total - ss_rows - ss_cols

        # Mean squares
        ms_rows = ss_rows / (n_subjects - 1)
        ms_cols = ss_cols / (n_raters - 1)
        ms_error = ss_error / ((n_subjects - 1) * (n_raters - 1))

        # ICC(3,1) calculation
        icc = (ms_rows - ms_error) / (ms_rows + (n_raters - 1) * ms_error)

        return icc

    @staticmethod
    def calculate_icc_simple(scores1: np.ndarray, scores2: np.ndarray) -> float:
        """Simplified ICC for two methods"""
        # Create DataFrame
        df = pd.DataFrame({
            'method1': scores1,
            'method2': scores2
        })

        return ICCCalculator.calculate_icc(df)


class CorrelationAnalyzer:
    """Calculate various correlation metrics"""

    @staticmethod
    def calculate_all_correlations(
        scores1: np.ndarray,
        scores2: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate Pearson and Spearman correlations

        Args:
            scores1: First set of scores
            scores2: Second set of scores

        Returns:
            Dict with correlation coefficients and p-values
        """
        # Pearson correlation
        pearson_r, pearson_p = pearsonr(scores1, scores2)

        # Spearman correlation
        spearman_r, spearman_p = spearmanr(scores1, scores2)

        return {
            'pearson_r': pearson_r,
            'pearson_p': pearson_p,
            'spearman_r': spearman_r,
            'spearman_p': spearman_p
        }


class MTMMMatrixBuilder:
    """
    Multitrait-Multimethod (MTMM) Matrix

    Comprehensive validity framework for multiple traits measured by multiple methods
    """

    def __init__(self, dimensions: List[str], channels: List[str]):
        """
        Initialize MTMM matrix builder

        Args:
            dimensions: List of trait/dimension names
            channels: List of method/channel names
        """
        self.dimensions = dimensions
        self.channels = channels

    def build_correlation_matrix(
        self,
        scores_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Build full MTMM correlation matrix

        Args:
            scores_df: DataFrame with columns like 'channel_dimension' (e.g., 'ctt_love')

        Returns:
            Correlation matrix
        """
        # Calculate all pairwise correlations
        corr_matrix = scores_df.corr()

        return corr_matrix

    def extract_validity_coefficients(
        self,
        corr_matrix: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Extract validity coefficients from MTMM matrix

        Returns:
            - convergent_validity: Average monotrait-heteromethod correlation
            - discriminant_validity: Average heterotrait-monomethod correlation
        """
        convergent_correlations = []
        discriminant_correlations = []

        # Extract relevant correlations
        for dim in self.dimensions:
            # Monotrait-heteromethod (convergent validity)
            for i, ch1 in enumerate(self.channels):
                for ch2 in self.channels[i+1:]:
                    col1 = f"{ch1}_{dim}"
                    col2 = f"{ch2}_{dim}"

                    if col1 in corr_matrix.columns and col2 in corr_matrix.columns:
                        corr = corr_matrix.loc[col1, col2]
                        convergent_correlations.append(corr)

            # Heterotrait-monomethod (discriminant validity)
            for ch in self.channels:
                for i, dim1 in enumerate(self.dimensions):
                    for dim2 in self.dimensions[i+1:]:
                        col1 = f"{ch}_{dim1}"
                        col2 = f"{ch}_{dim2}"

                        if col1 in corr_matrix.columns and col2 in corr_matrix.columns:
                            corr = corr_matrix.loc[col1, col2]
                            discriminant_correlations.append(corr)

        return {
            'convergent_validity_avg': np.mean(convergent_correlations) if convergent_correlations else 0,
            'discriminant_validity_avg': np.mean(discriminant_correlations) if discriminant_correlations else 0,
            'convergent_validity_min': np.min(convergent_correlations) if convergent_correlations else 0,
            'convergent_validity_max': np.max(convergent_correlations) if convergent_correlations else 0
        }


class CrossChannelValidator:
    """
    Main cross-channel validation orchestrator

    Compares all four scoring channels and generates comprehensive validation metrics
    """

    def __init__(self):
        self.ba_analyzer = BlandAltmanAnalyzer()
        self.icc_calculator = ICCCalculator()
        self.corr_analyzer = CorrelationAnalyzer()

    def compare_two_channels(
        self,
        channel1_scores: Dict[str, float],
        channel2_scores: Dict[str, float],
        channel1_id: str,
        channel2_id: str
    ) -> Dict[str, AgreementMetrics]:
        """
        Compare two channels across all dimensions

        Args:
            channel1_scores: Dict mapping dimension -> score
            channel2_scores: Dict mapping dimension -> score
            channel1_id: Channel identifier
            channel2_id: Channel identifier

        Returns:
            Dict mapping dimension -> AgreementMetrics
        """
        results = {}

        # Get common dimensions
        common_dims = set(channel1_scores.keys()) & set(channel2_scores.keys())

        for dim in common_dims:
            score1 = channel1_scores[dim]
            score2 = channel2_scores[dim]

            # For single data points, we can't calculate most metrics
            # This is meant for population-level comparisons
            # Store as lists for batch processing

            results[dim] = {
                'channel1_score': score1,
                'channel2_score': score2,
                'absolute_difference': abs(score1 - score2)
            }

        return results

    def compare_all_channels(
        self,
        all_channel_scores: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Compare all channels pairwise

        Args:
            all_channel_scores: Dict mapping channel_id -> {dimension: score}

        Returns:
            DataFrame with all pairwise comparisons
        """
        channels = list(all_channel_scores.keys())
        results = []

        for i, ch1 in enumerate(channels):
            for ch2 in channels[i+1:]:
                comparison = self.compare_two_channels(
                    all_channel_scores[ch1],
                    all_channel_scores[ch2],
                    ch1,
                    ch2
                )

                for dim, metrics in comparison.items():
                    results.append({
                        'channel_1': ch1,
                        'channel_2': ch2,
                        'dimension': dim,
                        **metrics
                    })

        return pd.DataFrame(results)

    def calculate_population_metrics(
        self,
        scores_df: pd.DataFrame,
        channel1: str,
        channel2: str,
        dimension: str
    ) -> AgreementMetrics:
        """
        Calculate population-level agreement metrics

        Args:
            scores_df: DataFrame with columns [session_id, channel, dimension, score]
            channel1: First channel
            channel2: Second channel
            dimension: Dimension to analyze

        Returns:
            AgreementMetrics object
        """
        # Filter data
        ch1_data = scores_df[
            (scores_df['channel'] == channel1) &
            (scores_df['dimension'] == dimension)
        ]['score'].values

        ch2_data = scores_df[
            (scores_df['channel'] == channel2) &
            (scores_df['dimension'] == dimension)
        ]['score'].values

        # Ensure same length
        min_len = min(len(ch1_data), len(ch2_data))
        ch1_data = ch1_data[:min_len]
        ch2_data = ch2_data[:min_len]

        # Bland-Altman
        ba_results = self.ba_analyzer.analyze(ch1_data, ch2_data)

        # Correlations
        corr_results = self.corr_analyzer.calculate_all_correlations(ch1_data, ch2_data)

        # ICC
        icc = self.icc_calculator.calculate_icc_simple(ch1_data, ch2_data)

        return AgreementMetrics(
            channel_1=channel1,
            channel_2=channel2,
            dimension=dimension,
            pearson_correlation=corr_results['pearson_r'],
            spearman_correlation=corr_results['spearman_r'],
            icc_value=icc,
            bland_altman_bias=ba_results['bias'],
            bland_altman_sd=ba_results['sd'],
            limits_of_agreement_lower=ba_results['loa_lower'],
            limits_of_agreement_upper=ba_results['loa_upper']
        )


def validate_session_scores(
    session_scores: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate scores from all channels for a single session

    Args:
        session_scores: Dict mapping channel -> scoring results

    Returns:
        Validation summary
    """
    validator = CrossChannelValidator()

    # Extract dimension scores from each channel
    channel_dimension_scores = {}

    for channel_id, results in session_scores.items():
        dimension_scores = {}

        for dim, score_data in results.get('dimension_scores', {}).items():
            # Extract normalized score
            if isinstance(score_data, dict):
                normalized = score_data.get('normalized_score', 0)
            else:
                normalized = score_data

            dimension_scores[dim] = normalized

        channel_dimension_scores[channel_id] = dimension_scores

    # Compare all channels
    comparison_df = validator.compare_all_channels(channel_dimension_scores)

    # Calculate summary statistics
    summary = {
        'channels_compared': list(channel_dimension_scores.keys()),
        'dimensions_evaluated': list(set(comparison_df['dimension'])),
        'average_absolute_difference': comparison_df['absolute_difference'].mean(),
        'max_difference': comparison_df['absolute_difference'].max(),
        'min_difference': comparison_df['absolute_difference'].min(),
        'pairwise_comparisons': comparison_df.to_dict('records')
    }

    return summary

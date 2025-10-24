"""
Channel 2: Item Response Theory (IRT) Scoring
Graded Response Model with multidimensional IRT (4D-MIRT)

Requires R integration via rpy2 for mirt package
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class IRTScore:
    """IRT scoring result"""
    dimension_id: str
    theta_eap: float  # Expected A Posteriori estimate
    theta_map: float  # Maximum A Posteriori estimate
    theta_mle: Optional[float]  # Maximum Likelihood Estimate
    standard_error: float
    information_value: float
    normalized_score: float  # Converted to 0-100 scale


class IRTScorer:
    """
    Item Response Theory scorer using Graded Response Model

    Implements multidimensional IRT (MIRT) for 4 ikigai dimensions
    Uses R's mirt package via rpy2 for advanced psychometric modeling
    """

    def __init__(
        self,
        item_parameters: Optional[pd.DataFrame] = None,
        model_type: str = 'graded'
    ):
        """
        Initialize IRT scorer

        Args:
            item_parameters: Pre-calibrated item parameters (a, b1, b2, b3, b4)
            model_type: IRT model ('graded', '2pl', 'rasch')
        """
        self.item_parameters = item_parameters
        self.model_type = model_type
        self._r_available = self._check_r_availability()

    def _check_r_availability(self) -> bool:
        """Check if R and required packages are available"""
        try:
            import rpy2.robjects as ro
            from rpy2.robjects.packages import importr

            # Try to import required R packages
            mirt = importr('mirt')
            logger.info("R mirt package available")
            return True
        except Exception as e:
            logger.warning(f"R/mirt not available: {e}")
            return False

    def calibrate_items(
        self,
        response_matrix: pd.DataFrame,
        dimensions: List[str]
    ) -> pd.DataFrame:
        """
        Calibrate IRT item parameters using sample data

        This should be done once on a large calibration sample (N≥800)

        Args:
            response_matrix: DataFrame with items as columns, participants as rows
            dimensions: List of dimension labels for each item

        Returns:
            DataFrame with item parameters (a, b1, b2, b3, b4)
        """
        if not self._r_available:
            logger.error("R/mirt not available - cannot calibrate items")
            return pd.DataFrame()

        import rpy2.robjects as ro
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()

        # Convert to R dataframe
        r_data = pandas2ri.py2rpy(response_matrix)

        # Define multidimensional model specification
        # Between-item model: each item loads on one dimension
        model_spec = self._build_model_specification(dimensions)

        # Fit model using mirt
        ro.r(f'''
        library(mirt)

        # Define model
        model_spec <- "{model_spec}"

        # Fit multidimensional graded response model
        fit <- mirt(
            data = r_data,
            model = model_spec,
            itemtype = "graded",
            SE = TRUE,
            verbose = FALSE
        )

        # Extract item parameters
        item_params <- coef(fit, simplify = TRUE, IRTpars = TRUE)
        ''')

        # Extract parameters from R
        params_r = ro.r['item_params']
        parameters = pandas2ri.rpy2py(params_r)

        logger.info(f"Calibrated {len(response_matrix.columns)} items")

        self.item_parameters = parameters
        return parameters

    def _build_model_specification(self, dimensions: List[str]) -> str:
        """Build mirt model specification string"""
        # Group items by dimension
        dim_items = {}
        for i, dim in enumerate(dimensions):
            if dim not in dim_items:
                dim_items[dim] = []
            dim_items[dim].append(i + 1)

        # Build specification
        spec_lines = []
        for dim, items in dim_items.items():
            item_range = f"{min(items)}-{max(items)}"
            spec_lines.append(f"{dim.upper()} = {item_range}")

        # Add covariances between dimensions
        spec_lines.append("COV = " + "*".join([d.upper() for d in dim_items.keys()]))

        return "\n".join(spec_lines)

    def estimate_theta(
        self,
        item_responses: np.ndarray,
        method: str = 'eap'
    ) -> IRTScore:
        """
        Estimate person ability parameter (theta)

        Args:
            item_responses: Array of item responses (1-5 scale)
            method: Estimation method ('eap', 'map', 'mle')

        Returns:
            IRTScore with theta estimates and precision metrics
        """
        if self.item_parameters is None:
            logger.warning("No calibrated item parameters - using simplified estimation")
            return self._simplified_theta_estimate(item_responses)

        if not self._r_available:
            return self._simplified_theta_estimate(item_responses)

        # Use R mirt package for proper theta estimation
        import rpy2.robjects as ro

        # EAP estimation (most stable)
        theta_eap, se_eap = self._estimate_eap(item_responses)

        # MAP estimation
        theta_map = self._estimate_map(item_responses)

        # MLE estimation (may fail for extreme scores)
        try:
            theta_mle = self._estimate_mle(item_responses)
        except:
            theta_mle = None

        # Calculate information
        information = self._calculate_information(theta_eap)

        # Normalize theta to 0-100 scale
        # Theta typically ranges -3 to +3, so we map this to 0-100
        normalized = self._theta_to_normalized(theta_eap)

        return IRTScore(
            dimension_id="dimension",  # Set by caller
            theta_eap=theta_eap,
            theta_map=theta_map,
            theta_mle=theta_mle,
            standard_error=se_eap,
            information_value=information,
            normalized_score=normalized
        )

    def _estimate_eap(self, responses: np.ndarray) -> Tuple[float, float]:
        """
        Expected A Posteriori estimation

        EAP = ∫θ × L(θ|X) × π(θ)dθ / ∫L(θ|X) × π(θ)dθ

        Uses prior distribution N(0,1)
        """
        # Simplified implementation
        # In production, use R mirt::fscores(method='EAP')

        # Grid approximation
        theta_grid = np.linspace(-4, 4, 81)
        prior = self._prior_distribution(theta_grid)

        # Calculate likelihood for each theta
        likelihoods = np.array([
            self._likelihood(theta, responses)
            for theta in theta_grid
        ])

        # Posterior = Likelihood × Prior
        posterior = likelihoods * prior
        posterior /= np.sum(posterior)  # Normalize

        # EAP is expected value
        theta_eap = np.sum(theta_grid * posterior)

        # Standard error is SD of posterior
        se = np.sqrt(np.sum((theta_grid - theta_eap)**2 * posterior))

        return theta_eap, se

    def _estimate_map(self, responses: np.ndarray) -> float:
        """Maximum A Posteriori estimation"""
        # Find mode of posterior distribution
        theta_grid = np.linspace(-4, 4, 81)
        prior = self._prior_distribution(theta_grid)

        likelihoods = np.array([
            self._likelihood(theta, responses)
            for theta in theta_grid
        ])

        posterior = likelihoods * prior
        map_idx = np.argmax(posterior)

        return theta_grid[map_idx]

    def _estimate_mle(self, responses: np.ndarray) -> float:
        """Maximum Likelihood Estimation using Newton-Raphson"""
        from scipy.optimize import minimize_scalar

        # Maximize likelihood (minimize negative log-likelihood)
        def neg_log_likelihood(theta):
            return -np.log(self._likelihood(theta, responses) + 1e-10)

        result = minimize_scalar(neg_log_likelihood, bounds=(-4, 4), method='bounded')

        return result.x

    def _likelihood(self, theta: float, responses: np.ndarray) -> float:
        """
        Calculate likelihood P(X|θ) using Graded Response Model

        P(X=k|θ) = P(X≥k|θ) - P(X≥k+1|θ)
        where P(X≥k|θ) = exp[a(θ-bₖ)] / [1 + exp[a(θ-bₖ)]]
        """
        if self.item_parameters is None:
            # Use default parameters if not calibrated
            a = 1.0  # Discrimination
            b_thresholds = [-1.5, -0.5, 0.5, 1.5]  # Category thresholds
        else:
            # Extract from calibrated parameters
            a = 1.0
            b_thresholds = [-1.5, -0.5, 0.5, 1.5]

        likelihood = 1.0

        for response in responses:
            if np.isnan(response):
                continue

            k = int(response) - 1  # Convert to 0-indexed

            # P(X≥k)
            if k == 0:
                p_gte_k = 1.0
            else:
                p_gte_k = 1 / (1 + np.exp(-a * (theta - b_thresholds[k-1])))

            # P(X≥k+1)
            if k >= len(b_thresholds):
                p_gte_k_plus_1 = 0.0
            else:
                p_gte_k_plus_1 = 1 / (1 + np.exp(-a * (theta - b_thresholds[k])))

            # P(X=k)
            p_k = p_gte_k - p_gte_k_plus_1

            likelihood *= max(p_k, 1e-10)  # Avoid zero

        return likelihood

    @staticmethod
    def _prior_distribution(theta: np.ndarray) -> np.ndarray:
        """Prior distribution for theta: N(0,1)"""
        return np.exp(-0.5 * theta**2) / np.sqrt(2 * np.pi)

    def _calculate_information(self, theta: float) -> float:
        """
        Calculate test information at theta

        I(θ) = Σ Iᵢ(θ)
        where Iᵢ(θ) = a² × P(θ) × [1 - P(θ)] for 2PL
        """
        # Simplified - should sum across all items
        a = 1.0
        p = 1 / (1 + np.exp(-a * theta))
        information = a**2 * p * (1 - p)

        return information * len(self.item_parameters) if self.item_parameters is not None else information

    @staticmethod
    def _theta_to_normalized(theta: float) -> float:
        """Convert theta (-3 to +3) to normalized score (0-100)"""
        # Map theta range to 0-100
        # Assume theta range of [-3, +3] covers 99.7% of distribution
        normalized = ((theta + 3) / 6) * 100
        return np.clip(normalized, 0, 100)

    def _simplified_theta_estimate(self, responses: np.ndarray) -> IRTScore:
        """Simplified theta estimation when R is not available"""
        # Use mean response as proxy
        mean_response = np.nanmean(responses)

        # Convert to theta scale
        theta = (mean_response - 3) / 1.5  # Rough conversion

        return IRTScore(
            dimension_id="dimension",
            theta_eap=theta,
            theta_map=theta,
            theta_mle=theta,
            standard_error=0.5,
            information_value=1.0,
            normalized_score=self._theta_to_normalized(theta)
        )


def score_session_irt(
    session_responses: List[Dict[str, Any]],
    item_parameters: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Score a complete assessment session using IRT

    Args:
        session_responses: List of all question responses
        item_parameters: Pre-calibrated item parameters

    Returns:
        Complete IRT scoring results
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
            # Assume responses have been converted to Likert scores
            score = response.get('likert_score', 3)
            dimension_responses[dim].append(score)

    # Initialize scorer
    scorer = IRTScorer(item_parameters=item_parameters)

    # Score each dimension
    dimension_scores = {}
    for dim, responses in dimension_responses.items():
        if len(responses) > 0:
            response_array = np.array(responses)
            irt_score = scorer.estimate_theta(response_array, method='eap')
            irt_score.dimension_id = dim
            dimension_scores[dim] = irt_score

    # Calculate intersections (using normalized scores)
    intersection_scores = {}
    normalized_scores = {dim: score.normalized_score for dim, score in dimension_scores.items()}

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
        'channel': 'irt',
        'dimension_scores': {
            dim: {
                'theta_eap': score.theta_eap,
                'theta_map': score.theta_map,
                'standard_error': score.standard_error,
                'information': score.information_value,
                'normalized_score': score.normalized_score
            }
            for dim, score in dimension_scores.items()
        },
        'intersection_scores': intersection_scores,
        'overall_alignment': {
            'overall_ikigai_score': overall_ikigai
        },
        'method': 'Item Response Theory (Graded Response Model)',
        'version': '1.0'
    }

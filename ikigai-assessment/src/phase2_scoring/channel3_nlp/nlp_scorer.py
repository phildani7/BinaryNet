"""
Channel 3: NLP/Machine Learning Scoring
Transformer-based semantic analysis with BERTopic and sentiment scoring
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class NLPScore:
    """NLP scoring result"""
    dimension_id: str
    semantic_similarity_score: float  # 0-1
    sentiment_score: float  # -1 to +1
    topic_relevance_score: float  # 0-1
    linguistic_features_score: float  # 0-1
    combined_score: float  # 0-100
    features: Dict[str, Any]


class NLPFeatureExtractor:
    """Extract linguistic and semantic features from text"""

    # Certainty markers
    CERTAINTY_MARKERS = [
        'definitely', 'certainly', 'absolutely', 'always', 'never',
        'clearly', 'obviously', 'undoubtedly', 'without a doubt'
    ]

    # Hedging markers
    HEDGING_MARKERS = [
        'maybe', 'perhaps', 'possibly', 'might', 'could', 'may',
        'i think', 'i guess', 'kind of', 'sort of', 'probably'
    ]

    # Emotion words (simplified - use NRC lexicon in production)
    POSITIVE_EMOTIONS = [
        'happy', 'joy', 'excited', 'enthusiastic', 'passionate',
        'love', 'energized', 'fulfilled', 'satisfied', 'thrilled'
    ]

    NEGATIVE_EMOTIONS = [
        'sad', 'frustrated', 'angry', 'disappointed', 'worried',
        'anxious', 'stressed', 'unhappy', 'dissatisfied'
    ]

    @staticmethod
    def extract_features(text: str) -> Dict[str, Any]:
        """Extract comprehensive linguistic features"""
        text_lower = text.lower()
        words = text.split()
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]

        # Basic statistics
        word_count = len(words)
        sentence_count = len(sentences)
        unique_words = len(set(words))

        features = {
            # Text statistics
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': word_count / sentence_count if sentence_count > 0 else 0,
            'lexical_diversity': unique_words / word_count if word_count > 0 else 0,

            # Conviction indicators
            'certainty_count': sum(1 for marker in NLPFeatureExtractor.CERTAINTY_MARKERS if marker in text_lower),
            'hedging_count': sum(1 for marker in NLPFeatureExtractor.HEDGING_MARKERS if marker in text_lower),
            'conviction_ratio': 0.0,  # Will be calculated

            # Emotional content
            'positive_emotion_count': sum(1 for word in NLPFeatureExtractor.POSITIVE_EMOTIONS if word in text_lower),
            'negative_emotion_count': sum(1 for word in NLPFeatureExtractor.NEGATIVE_EMOTIONS if word in text_lower),
            'emotional_intensity': 0.0,  # Will be calculated

            # Specificity (simplified)
            'contains_numbers': any(char.isdigit() for char in text),
            'contains_examples': 'for example' in text_lower or 'such as' in text_lower or 'like' in text_lower,

            # First-person usage (engagement)
            'first_person_count': text_lower.count(' i ') + text_lower.count("i'm") + text_lower.count("i've"),
        }

        # Calculate derived features
        total_markers = features['certainty_count'] + features['hedging_count']
        if total_markers > 0:
            features['conviction_ratio'] = features['certainty_count'] / total_markers
        else:
            features['conviction_ratio'] = 0.5  # Neutral

        total_emotion = features['positive_emotion_count'] + features['negative_emotion_count']
        features['emotional_intensity'] = min(1.0, total_emotion / 10)  # Normalize

        return features


class TransformerScorer:
    """
    Transformer-based semantic scoring using BERT/RoBERTa

    Uses sentence embeddings to compute semantic similarity with
    reference texts representing ideal responses
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize transformer scorer

        Args:
            model_name: Sentence-transformers model name
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load sentence transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded sentence transformer: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not load transformer model: {e}")
            self.model = None

    def compute_semantic_similarity(
        self,
        candidate_text: str,
        reference_text: str
    ) -> float:
        """
        Compute semantic similarity using cosine similarity of embeddings

        Args:
            candidate_text: Participant response
            reference_text: Ideal reference response

        Returns:
            Similarity score (0-1)
        """
        if self.model is None:
            # Fallback to simple keyword matching
            return self._simple_similarity(candidate_text, reference_text)

        from sklearn.metrics.pairwise import cosine_similarity

        # Encode both texts
        embeddings = self.model.encode([candidate_text, reference_text])

        # Compute cosine similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

        return float(similarity)

    @staticmethod
    def _simple_similarity(text1: str, text2: str) -> float:
        """Simple fallback similarity based on word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0


class SentimentAnalyzer:
    """Sentiment analysis with intensity"""

    def __init__(self):
        self.analyzer = None
        self._load_analyzer()

    def _load_analyzer(self):
        """Load VADER sentiment analyzer"""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.analyzer = SentimentIntensityAnalyzer()
            logger.info("Loaded VADER sentiment analyzer")
        except Exception as e:
            logger.warning(f"Could not load VADER: {e}")
            self.analyzer = None

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment with intensity

        Returns:
            Dict with 'compound', 'positive', 'negative', 'neutral' scores
        """
        if self.analyzer is None:
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}

        scores = self.analyzer.polarity_scores(text)
        return scores


class TopicModeler:
    """Topic modeling using BERTopic"""

    def __init__(self):
        self.model = None

    def fit_topics(self, documents: List[str], n_topics: int = 10):
        """Fit BERTopic model on documents"""
        try:
            from bertopic import BERTopic

            self.model = BERTopic(nr_topics=n_topics)
            topics, probs = self.model.fit_transform(documents)

            logger.info(f"Fitted BERTopic with {n_topics} topics")
            return topics, probs

        except Exception as e:
            logger.warning(f"BERTopic not available: {e}")
            return None, None

    def get_topic_for_document(self, document: str) -> Tuple[int, float]:
        """Get dominant topic and probability for document"""
        if self.model is None:
            return -1, 0.0

        topics, probs = self.model.transform([document])
        return topics[0], probs[0]


class NLPScorer:
    """
    Complete NLP scoring pipeline

    Combines:
    - Semantic similarity (transformers)
    - Sentiment analysis
    - Topic relevance
    - Linguistic features
    """

    # Reference texts for each dimension (ideal high-quality responses)
    REFERENCE_TEXTS = {
        'love': """
        I am absolutely passionate about teaching and mentoring others. When I'm helping
        someone learn a new concept and I see that moment of understanding in their eyes,
        time completely disappears. I've been doing this for years, both professionally
        and as a volunteer, and it never gets old. I wake up excited to engage with
        students and create learning experiences that transform their understanding.
        """,

        'good_at': """
        I have developed strong expertise in data analysis and visualization over the
        past decade. People regularly seek my guidance on complex statistical problems
        and dashboard design. I can quickly identify patterns in messy data that others
        miss, and I have a natural ability to communicate insights to non-technical
        stakeholders. I've led multiple successful analytics projects and mentored
        junior analysts on best practices.
        """,

        'world_needs': """
        I'm deeply concerned about educational inequality, particularly the lack of
        quality STEM education in underserved communities. This problem persists because
        of systemic funding gaps, teacher shortages, and limited access to technology.
        If we could solve this, millions of students would have opportunities to pursue
        careers in science and technology, breaking cycles of poverty and contributing
        innovations to society. I want to help bridge this gap through accessible online
        learning platforms and teacher training programs.
        """,

        'paid_for': """
        I've researched the market extensively. Data scientists with 5+ years of
        experience in the education technology sector typically earn between $90,000
        and $140,000 depending on location and company size. The field is growing
        rapidly, with 15% annual job growth projected. Most positions require a
        master's degree in a quantitative field plus demonstrated experience with
        Python, SQL, and machine learning. I've identified 50+ companies actively
        hiring for roles that match my skill set.
        """
    }

    def __init__(self):
        self.transformer_scorer = TransformerScorer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.feature_extractor = NLPFeatureExtractor()

    def score_response(
        self,
        response_text: str,
        dimension: str
    ) -> NLPScore:
        """
        Score a single response using NLP techniques

        Args:
            response_text: Participant's response
            dimension: Which ikigai dimension

        Returns:
            NLPScore with comprehensive metrics
        """
        # Extract linguistic features
        features = self.feature_extractor.extract_features(response_text)

        # Semantic similarity to reference
        reference = self.REFERENCE_TEXTS.get(dimension, "")
        semantic_score = self.transformer_scorer.compute_semantic_similarity(
            response_text,
            reference
        )

        # Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze_sentiment(response_text)
        sentiment_score = sentiment.get('compound', 0.0)

        # Topic relevance (simplified - in production use BERTopic)
        topic_score = self._calculate_topic_relevance(response_text, dimension)

        # Linguistic features score
        linguistic_score = self._score_linguistic_features(features, dimension)

        # Combined score (weighted)
        combined = (
            0.35 * semantic_score +
            0.25 * ((sentiment_score + 1) / 2) +  # Normalize to 0-1
            0.25 * topic_score +
            0.15 * linguistic_score
        ) * 100  # Scale to 0-100

        return NLPScore(
            dimension_id=dimension,
            semantic_similarity_score=semantic_score,
            sentiment_score=sentiment_score,
            topic_relevance_score=topic_score,
            linguistic_features_score=linguistic_score,
            combined_score=combined,
            features=features
        )

    def _calculate_topic_relevance(self, text: str, dimension: str) -> float:
        """Calculate topic relevance (simplified version)"""
        # In production, use BERTopic to identify topics and map to dimensions
        # For now, use keyword matching

        DIMENSION_KEYWORDS = {
            'love': ['passion', 'enjoy', 'love', 'excited', 'energized', 'fulfill'],
            'good_at': ['skill', 'expert', 'good at', 'talented', 'competent', 'excel'],
            'world_needs': ['problem', 'help', 'impact', 'contribute', 'serve', 'need'],
            'paid_for': ['salary', 'paid', 'earn', 'money', 'income', 'market', 'job']
        }

        keywords = DIMENSION_KEYWORDS.get(dimension, [])
        text_lower = text.lower()

        matches = sum(1 for keyword in keywords if keyword in text_lower)
        score = min(1.0, matches / 3)  # Normalize

        return score

    def _score_linguistic_features(self, features: Dict[str, Any], dimension: str) -> float:
        """Score based on linguistic features"""
        score = 0.0

        # Word count (prefer 100-300 words)
        if 100 <= features['word_count'] <= 300:
            score += 0.3
        elif features['word_count'] > 50:
            score += 0.15

        # Lexical diversity (prefer > 0.5)
        if features['lexical_diversity'] > 0.5:
            score += 0.2

        # Conviction (prefer high certainty)
        if features['conviction_ratio'] > 0.6:
            score += 0.2

        # Emotional intensity
        score += features['emotional_intensity'] * 0.15

        # Specificity
        if features['contains_examples']:
            score += 0.15

        return min(1.0, score)


def score_session_nlp(
    session_responses: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Score a complete assessment session using NLP

    Args:
        session_responses: List of all question responses

    Returns:
        Complete NLP scoring results
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
    scorer = NLPScorer()

    # Score each dimension
    dimension_scores = {}
    for dim, responses in dimension_responses.items():
        # Combine all responses for this dimension
        combined_text = " ".join([r.get('response_text', '') for r in responses])

        if combined_text.strip():
            nlp_score = scorer.score_response(combined_text, dim)
            dimension_scores[dim] = nlp_score

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
        'channel': 'nlp',
        'dimension_scores': {
            dim: {
                'semantic_similarity': score.semantic_similarity_score,
                'sentiment': score.sentiment_score,
                'topic_relevance': score.topic_relevance_score,
                'linguistic_features': score.linguistic_features_score,
                'normalized_score': score.combined_score,
                'features': score.features
            }
            for dim, score in dimension_scores.items()
        },
        'intersection_scores': intersection_scores,
        'overall_alignment': {
            'overall_ikigai_score': overall_ikigai
        },
        'method': 'NLP & Machine Learning (Transformers)',
        'version': '1.0'
    }

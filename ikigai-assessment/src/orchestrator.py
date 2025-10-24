"""
Main Orchestrator for Ikigai Assessment System

Coordinates the full pipeline:
1. Phase 1: Voice assessment via LiveKit
2. Phase 2: Four parallel scoring channels
3. Validation and comparison
4. Results storage and visualization
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.phase1_voice_assessment.livekit_session import IkigaiVoiceSession
from src.phase2_scoring.channel1_ctt.classical_scorer import score_session_ctt
from src.phase2_scoring.channel2_irt.irt_scorer import score_session_irt
from src.phase2_scoring.channel3_nlp.nlp_scorer import score_session_nlp
from src.phase2_scoring.channel4_qualitative.framework_scorer import score_session_qualitative
from src.validation.cross_channel_validator import validate_session_scores

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IkigaiAssessmentOrchestrator:
    """
    Main orchestrator coordinating entire assessment pipeline

    Manages:
    - Voice assessment session
    - Parallel scoring across 4 channels
    - Cross-channel validation
    - Results persistence
    - Report generation
    """

    def __init__(
        self,
        participant_id: str,
        config: Dict[str, Any]
    ):
        """
        Initialize orchestrator

        Args:
            participant_id: Unique participant identifier
            config: Configuration dictionary with API keys and settings
        """
        self.participant_id = participant_id
        self.config = config
        self.session_id: Optional[str] = None
        self.transcript: Optional[str] = None
        self.responses: Optional[list] = None

    async def run_full_assessment(self) -> Dict[str, Any]:
        """
        Execute complete ikigai assessment pipeline

        Returns:
            Comprehensive results dictionary
        """
        logger.info(f"Starting ikigai assessment for participant: {self.participant_id}")

        # Phase 1: Voice Assessment
        logger.info("Phase 1: Starting voice assessment...")
        voice_results = await self._run_voice_assessment()

        # Extract transcript and responses
        self.transcript = voice_results.get('transcript', '')
        self.responses = voice_results.get('responses', [])

        # Phase 2: Parallel Scoring
        logger.info("Phase 2: Running parallel scoring across 4 channels...")
        scoring_results = await self._run_parallel_scoring()

        # Validation
        logger.info("Running cross-channel validation...")
        validation_results = self._run_validation(scoring_results)

        # Compile complete results
        complete_results = {
            'session_id': self.session_id,
            'participant_id': self.participant_id,
            'timestamp': datetime.now().isoformat(),
            'voice_assessment': voice_results,
            'scoring_results': scoring_results,
            'validation': validation_results,
            'metadata': {
                'duration_minutes': voice_results.get('duration_minutes'),
                'questions_completed': voice_results.get('questions_completed'),
                'channels_executed': list(scoring_results.keys())
            }
        }

        # Store results
        logger.info("Storing results to database...")
        await self._store_results(complete_results)

        # Generate report
        logger.info("Generating participant report...")
        report = self._generate_report(complete_results)

        complete_results['report'] = report

        logger.info("Assessment completed successfully!")

        return complete_results

    async def _run_voice_assessment(self) -> Dict[str, Any]:
        """Execute Phase 1: Voice assessment via LiveKit"""
        session = IkigaiVoiceSession(
            participant_id=self.participant_id,
            livekit_url=self.config.get('livekit_url'),
            livekit_api_key=self.config.get('livekit_api_key'),
            livekit_api_secret=self.config.get('livekit_api_secret'),
            elevenlabs_api_key=self.config.get('elevenlabs_api_key')
        )

        # Run full assessment
        results = await session.run_full_assessment()

        self.session_id = results.get('session_id')

        return results

    async def _run_parallel_scoring(self) -> Dict[str, Dict[str, Any]]:
        """Execute Phase 2: All four scoring channels in parallel"""

        # Convert responses to format expected by scorers
        formatted_responses = self._format_responses_for_scoring()

        # Run all 4 channels in parallel
        tasks = [
            asyncio.to_thread(self._run_channel_1, formatted_responses),
            asyncio.to_thread(self._run_channel_2, formatted_responses),
            asyncio.to_thread(self._run_channel_3, formatted_responses),
            asyncio.to_thread(self._run_channel_4, formatted_responses)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Package results
        scoring_results = {}

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                channel_id = ['ctt', 'irt', 'nlp', 'qual'][i]
                logger.error(f"Channel {channel_id} failed: {result}")
                scoring_results[channel_id] = {'error': str(result)}
            else:
                channel_id = result.get('channel')
                scoring_results[channel_id] = result

        return scoring_results

    def _run_channel_1(self, responses: list) -> Dict[str, Any]:
        """Channel 1: Classical Test Theory"""
        logger.info("Executing Channel 1: Classical Test Theory")
        return score_session_ctt(responses)

    def _run_channel_2(self, responses: list) -> Dict[str, Any]:
        """Channel 2: Item Response Theory"""
        logger.info("Executing Channel 2: Item Response Theory")
        return score_session_irt(responses)

    def _run_channel_3(self, responses: list) -> Dict[str, Any]:
        """Channel 3: NLP/Machine Learning"""
        logger.info("Executing Channel 3: NLP & Machine Learning")
        return score_session_nlp(responses)

    def _run_channel_4(self, responses: list) -> Dict[str, Any]:
        """Channel 4: Qualitative Framework Method"""
        logger.info("Executing Channel 4: Qualitative Framework Method")
        return score_session_qualitative(responses, self.transcript)

    def _run_validation(self, scoring_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Execute cross-channel validation"""
        return validate_session_scores(scoring_results)

    def _format_responses_for_scoring(self) -> list:
        """Format responses for scoring modules"""
        # Add any extracted features or preprocessing here
        return self.responses

    async def _store_results(self, results: Dict[str, Any]):
        """Store results to database"""
        # TODO: Implement database storage
        logger.info("Results storage not yet implemented")

    def _generate_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate participant-facing report"""

        scoring = results.get('scoring_results', {})

        # Extract dimension scores from each channel
        dimension_summaries = {
            'love': {},
            'good_at': {},
            'world_needs': {},
            'paid_for': {}
        }

        for channel_id, channel_results in scoring.items():
            if 'error' in channel_results:
                continue

            for dim, score_data in channel_results.get('dimension_scores', {}).items():
                if isinstance(score_data, dict):
                    normalized = score_data.get('normalized_score', 0)
                else:
                    normalized = score_data

                dimension_summaries[dim][channel_id] = normalized

        # Calculate consensus scores (average across channels)
        consensus_scores = {}
        for dim, channel_scores in dimension_summaries.items():
            if channel_scores:
                consensus_scores[dim] = sum(channel_scores.values()) / len(channel_scores)
            else:
                consensus_scores[dim] = 0

        # Overall ikigai (fourth root of product)
        import numpy as np
        all_dims = list(consensus_scores.values())
        overall_ikigai = np.prod(all_dims) ** 0.25 if len(all_dims) == 4 else 0

        report = {
            'participant_id': self.participant_id,
            'assessment_date': results.get('timestamp'),

            'dimension_scores': consensus_scores,

            'intersections': {
                'passion': np.sqrt(consensus_scores['love'] * consensus_scores['good_at']),
                'mission': np.sqrt(consensus_scores['love'] * consensus_scores['world_needs']),
                'profession': np.sqrt(consensus_scores['good_at'] * consensus_scores['paid_for']),
                'vocation': np.sqrt(consensus_scores['world_needs'] * consensus_scores['paid_for'])
            },

            'overall_ikigai': overall_ikigai,

            'interpretation': self._generate_interpretation(consensus_scores, overall_ikigai),

            'channel_breakdown': dimension_summaries,

            'validation_summary': results.get('validation', {})
        }

        return report

    def _generate_interpretation(
        self,
        dimension_scores: Dict[str, float],
        overall_ikigai: float
    ) -> Dict[str, str]:
        """Generate human-readable interpretation"""

        interpretations = {}

        # Overall interpretation
        if overall_ikigai >= 80:
            interpretations['overall'] = "Excellent ikigai alignment! You have strong clarity across all four dimensions."
        elif overall_ikigai >= 60:
            interpretations['overall'] = "Good ikigai alignment with some areas for development."
        elif overall_ikigai >= 40:
            interpretations['overall'] = "Moderate ikigai alignment. Consider focusing on strengthening weaker dimensions."
        else:
            interpretations['overall'] = "Emerging ikigai. Significant opportunities for exploration and growth."

        # Dimension-specific
        for dim, score in dimension_scores.items():
            dim_name = {
                'love': 'Passion',
                'good_at': 'Expertise',
                'world_needs': 'Mission',
                'paid_for': 'Viability'
            }.get(dim, dim)

            if score >= 75:
                interpretations[dim] = f"Strong {dim_name} - This is a clear strength for you."
            elif score >= 50:
                interpretations[dim] = f"Developing {dim_name} - Good foundation with room to grow."
            else:
                interpretations[dim] = f"Emerging {dim_name} - Opportunity for exploration and clarification."

        return interpretations


async def main():
    """Example usage"""
    config = {
        'livekit_url': 'wss://your-livekit-server.com',
        'livekit_api_key': 'your_api_key',
        'livekit_api_secret': 'your_api_secret',
        'elevenlabs_api_key': 'your_elevenlabs_key'
    }

    orchestrator = IkigaiAssessmentOrchestrator(
        participant_id="P001",
        config=config
    )

    results = await orchestrator.run_full_assessment()

    print("\n=== Assessment Complete ===")
    print(f"Overall Ikigai Score: {results['report']['overall_ikigai']:.1f}")
    print("\nDimension Scores:")
    for dim, score in results['report']['dimension_scores'].items():
        print(f"  {dim}: {score:.1f}")


if __name__ == "__main__":
    asyncio.run(main())

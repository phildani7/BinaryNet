"""
LiveKit Voice Assessment Session
Manages real-time voice interactions for ikigai assessment
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import yaml

from livekit import rtc, api
import aiohttp

logger = logging.getLogger(__name__)


class IkigaiVoiceSession:
    """
    Manages LiveKit voice assessment session with ElevenLabs synthesis

    Implements the 20-question ikigai assessment using:
    - Motivational interviewing techniques
    - OARS framework (Open-ended, Affirmations, Reflections, Summaries)
    - Strategic pause structures for deep reflection
    """

    def __init__(
        self,
        participant_id: str,
        livekit_url: str,
        livekit_api_key: str,
        livekit_api_secret: str,
        elevenlabs_api_key: str,
        questions_config_path: str = "config/ikigai_questions.yaml"
    ):
        self.participant_id = participant_id
        self.livekit_url = livekit_url
        self.livekit_api_key = livekit_api_key
        self.livekit_api_secret = livekit_api_secret
        self.elevenlabs_api_key = elevenlabs_api_key

        # Load questions configuration
        self.questions = self._load_questions(questions_config_path)

        # Session state
        self.room: Optional[rtc.Room] = None
        self.room_name: Optional[str] = None
        self.session_id: Optional[str] = None
        self.current_question = 0
        self.responses: List[Dict[str, Any]] = []
        self.transcript: str = ""
        self.start_time: Optional[datetime] = None

    def _load_questions(self, config_path: str) -> Dict[str, Any]:
        """Load ikigai questions from YAML configuration"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config

    async def create_room(self) -> str:
        """Create LiveKit room for assessment"""
        room_name = f"ikigai-{self.participant_id}-{int(datetime.now().timestamp())}"

        # Create room using LiveKit API
        lkapi = api.LiveKitAPI(
            url=self.livekit_url,
            api_key=self.livekit_api_key,
            api_secret=self.livekit_api_secret
        )

        # Create room with specific configuration
        await lkapi.room.create_room(
            api.CreateRoomRequest(
                name=room_name,
                empty_timeout=1800,  # 30 minutes
                max_participants=2,  # Participant + AI assistant
            )
        )

        self.room_name = room_name
        logger.info(f"Created LiveKit room: {room_name}")

        return room_name

    async def generate_participant_token(self) -> str:
        """Generate access token for participant"""
        token = api.AccessToken(
            api_key=self.livekit_api_key,
            api_secret=self.livekit_api_secret
        )

        token.with_identity(self.participant_id).with_grants(
            api.VideoGrants(
                room_join=True,
                room=self.room_name,
                can_publish=True,
                can_subscribe=True,
            )
        )

        return token.to_jwt()

    async def connect_to_room(self):
        """Connect to LiveKit room"""
        self.room = rtc.Room()

        # Set up event handlers
        @self.room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            logger.info(f"Participant connected: {participant.identity}")

        @self.room.on("track_subscribed")
        def on_track_subscribed(
            track: rtc.Track,
            publication: rtc.RemoteTrackPublication,
            participant: rtc.RemoteParticipant
        ):
            logger.info(f"Track subscribed: {track.kind}")
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                # Start transcription
                asyncio.create_task(self._transcribe_audio_stream(track))

        # Connect to room
        token = await self.generate_participant_token()
        await self.room.connect(self.livekit_url, token)

        logger.info(f"Connected to room: {self.room_name}")

    async def synthesize_speech_elevenlabs(
        self,
        text: str,
        voice_id: Optional[str] = None,
        stability: float = 0.50,
        similarity: float = 0.75
    ) -> bytes:
        """
        Synthesize speech using ElevenLabs API

        Args:
            text: Text to synthesize
            voice_id: ElevenLabs voice ID (defaults to config)
            stability: Voice stability (0.0 - 1.0)
            similarity: Voice similarity (0.0 - 1.0)

        Returns:
            Audio bytes (MP3 format)
        """
        if voice_id is None:
            voice_id = self.questions['metadata']['elevenlabs']['recommended_voice_id']

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }

        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    audio_bytes = await response.read()
                    logger.info(f"Synthesized speech: {len(text)} chars -> {len(audio_bytes)} bytes")
                    return audio_bytes
                else:
                    error = await response.text()
                    raise Exception(f"ElevenLabs API error: {error}")

    async def play_audio_in_room(self, audio_bytes: bytes):
        """Play synthesized audio in LiveKit room"""
        # This is a simplified version - actual implementation would involve:
        # 1. Converting audio to proper format (PCM)
        # 2. Creating audio track
        # 3. Publishing to room
        # For production, consider using LiveKit's audio track features

        logger.info("Playing audio in room (implementation needed)")
        # TODO: Implement actual audio playback via LiveKit

    async def ask_question(self, question_number: int):
        """Ask a specific question"""
        question = self.questions['questions'][question_number]

        logger.info(f"Asking question {question_number + 1}/{len(self.questions['questions'])}")
        logger.info(f"Dimension: {question.get('dimension')}, Intensity: {question.get('intensity')}")

        # Synthesize question audio
        question_text = question['text']
        audio_bytes = await self.synthesize_speech_elevenlabs(question_text)

        # Play audio in room
        await self.play_audio_in_room(audio_bytes)

        # Wait for response (pause duration from config)
        pause_duration = question.get('pause_after', 10)
        logger.info(f"Waiting {pause_duration} seconds for response...")
        await asyncio.sleep(pause_duration)

        # Record question and response
        self.responses.append({
            "question_number": question_number + 1,
            "question_text": question_text,
            "dimension": question.get('dimension'),
            "intensity": question.get('intensity'),
            "asked_at": datetime.now().isoformat(),
            "pause_duration": pause_duration
        })

        self.current_question = question_number + 1

    async def run_full_assessment(self):
        """Run complete 20-question assessment"""
        self.start_time = datetime.now()
        logger.info(f"Starting ikigai assessment for participant: {self.participant_id}")

        # Create and connect to room
        await self.create_room()
        await self.connect_to_room()

        # Run through all questions
        total_questions = len(self.questions['questions'])
        for i in range(total_questions):
            await self.ask_question(i)

        # Closing
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() / 60
        logger.info(f"Assessment completed in {duration:.1f} minutes")

        # Disconnect
        await self.room.disconnect()

        return {
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "room_name": self.room_name,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_minutes": duration,
            "questions_completed": total_questions,
            "responses": self.responses,
            "transcript": self.transcript
        }

    async def _transcribe_audio_stream(self, audio_track: rtc.AudioTrack):
        """Transcribe audio stream using OpenAI Whisper or similar"""
        # This is a placeholder - actual implementation would:
        # 1. Capture audio frames from track
        # 2. Buffer audio data
        # 3. Send to transcription service (Whisper, Deepgram, etc.)
        # 4. Accumulate transcript

        logger.info("Starting audio transcription (implementation needed)")
        # TODO: Implement audio transcription

    async def save_session_to_database(self, db_session):
        """Save assessment session to database"""
        from src.database.models import AssessmentSession, QuestionResponse

        # Create session record
        session = AssessmentSession(
            participant_id=int(self.participant_id.split('-')[0]) if '-' in self.participant_id else None,
            livekit_room_id=self.room_name,
            livekit_session_id=self.session_id,
            transcript=self.transcript,
            completion_status='completed',
            assessment_timestamp=self.start_time
        )

        db_session.add(session)
        db_session.flush()  # Get session_id

        # Save individual responses
        for response in self.responses:
            question_response = QuestionResponse(
                session_id=session.session_id,
                question_number=response['question_number'],
                question_text=response['question_text'],
                question_dimension=response['dimension'],
                response_text="",  # Will be extracted from transcript
            )
            db_session.add(question_response)

        db_session.commit()
        logger.info(f"Saved session to database: {session.session_id}")

        return session.session_id


class TranscriptParser:
    """Parse assessment transcript to extract question responses"""

    @staticmethod
    def extract_responses(transcript: str, questions: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract individual question responses from full transcript

        Uses natural language processing to segment transcript by questions
        """
        # TODO: Implement intelligent transcript segmentation
        # Options:
        # 1. Timestamp-based segmentation (if timestamps available)
        # 2. Question text matching
        # 3. Speaker diarization to separate AI questions from participant responses

        responses = []

        # Placeholder implementation
        for i, question in enumerate(questions):
            responses.append({
                "question_number": i + 1,
                "question_text": question['text'],
                "response_text": "",  # Extract from transcript
                "dimension": question.get('dimension'),
                "word_count": 0,
                "sentiment_score": 0.0
            })

        return responses

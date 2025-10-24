"""
SQLAlchemy ORM models for Ikigai Assessment System
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, Text, Boolean, DateTime,
    DECIMAL, ForeignKey, ARRAY, CheckConstraint, UniqueConstraint,
    Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Participant(Base):
    """Participant/user information"""
    __tablename__ = "participants"

    participant_id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    demographics = Column(JSONB, nullable=True)
    consent_given = Column(Boolean, default=False)
    status = Column(String(50), default='enrolled')

    # Relationships
    sessions = relationship("AssessmentSession", back_populates="participant")


class AssessmentSession(Base):
    """Voice assessment session with LiveKit"""
    __tablename__ = "assessment_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    participant_id = Column(Integer, ForeignKey("participants.participant_id"))
    assessment_timestamp = Column(DateTime, default=func.now())
    livekit_room_id = Column(String(255))
    livekit_session_id = Column(String(255))
    audio_url = Column(Text)
    audio_duration_seconds = Column(Integer)
    transcript = Column(Text)
    transcript_metadata = Column(JSONB)
    completion_status = Column(String(50), default='in_progress')
    demographics = Column(JSONB)
    quality_flags = Column(JSONB)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    participant = relationship("Participant", back_populates="sessions")
    responses = relationship("QuestionResponse", back_populates="session")
    channel_scores = relationship("ChannelScore", back_populates="session")
    enrichment = relationship("ExternalEnrichment", back_populates="session")

    __table_args__ = (
        Index('idx_sessions_participant', 'participant_id'),
        Index('idx_sessions_status', 'completion_status'),
        Index('idx_sessions_timestamp', 'assessment_timestamp'),
    )


class QuestionResponse(Base):
    """Individual question responses extracted from transcript"""
    __tablename__ = "question_responses"

    response_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("assessment_sessions.session_id"))
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    question_dimension = Column(String(50))
    response_text = Column(Text)
    response_duration_seconds = Column(DECIMAL(5, 2))
    word_count = Column(Integer)
    sentiment_score = Column(DECIMAL(4, 3))
    emotional_intensity = Column(DECIMAL(4, 3))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    session = relationship("AssessmentSession", back_populates="responses")

    __table_args__ = (
        UniqueConstraint('session_id', 'question_number'),
        Index('idx_responses_session', 'session_id'),
        Index('idx_responses_dimension', 'question_dimension'),
    )


class DimensionDefinition(Base):
    """Ikigai dimension definitions"""
    __tablename__ = "dimension_definitions"

    dimension_id = Column(String(50), primary_key=True)
    dimension_name = Column(String(100), nullable=False)
    description = Column(Text)
    scale_min = Column(Integer, default=0)
    scale_max = Column(Integer, default=100)
    created_at = Column(DateTime, default=func.now())


class ChannelMetadata(Base):
    """Scoring channel metadata and configuration"""
    __tablename__ = "channel_metadata"

    channel_id = Column(String(50), primary_key=True)
    method_type = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(String(20))
    reliability_coefficient = Column(DECIMAL(4, 3))
    last_calibration_date = Column(DateTime)
    configuration = Column(JSONB)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ChannelScore(Base):
    """Normalized scores from all scoring channels"""
    __tablename__ = "channel_scores"

    score_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("assessment_sessions.session_id"))
    channel_id = Column(String(50), ForeignKey("channel_metadata.channel_id"))
    dimension_id = Column(String(50), ForeignKey("dimension_definitions.dimension_id"))
    raw_score = Column(DECIMAL(6, 3))
    normalized_score = Column(DECIMAL(5, 2))  # 0-100 scale
    z_score = Column(DECIMAL(6, 3))
    t_score = Column(DECIMAL(5, 2))
    percentile_rank = Column(DECIMAL(5, 2))
    confidence_interval_lower = Column(DECIMAL(5, 2))
    confidence_interval_upper = Column(DECIMAL(5, 2))
    standard_error = Column(DECIMAL(5, 3))
    processing_timestamp = Column(DateTime, default=func.now())
    processing_metadata = Column(JSONB)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    session = relationship("AssessmentSession", back_populates="channel_scores")

    __table_args__ = (
        UniqueConstraint('session_id', 'channel_id', 'dimension_id'),
        Index('idx_channel_scores_session', 'session_id'),
        Index('idx_channel_scores_channel', 'channel_id'),
        Index('idx_channel_scores_dimension', 'dimension_id'),
        Index('idx_channel_scores_composite', 'session_id', 'channel_id', 'dimension_id'),
    )


class IntersectionScore(Base):
    """Intersection scores (Passion, Mission, Profession, Vocation)"""
    __tablename__ = "intersection_scores"

    intersection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("assessment_sessions.session_id"))
    channel_id = Column(String(50), ForeignKey("channel_metadata.channel_id"))
    intersection_type = Column(String(50))  # passion, mission, profession, vocation
    score = Column(DECIMAL(5, 2))
    calculation_method = Column(String(50), default='geometric_mean')
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('session_id', 'channel_id', 'intersection_type'),
    )


class OverallAlignment(Base):
    """Overall ikigai alignment scores"""
    __tablename__ = "overall_alignment"

    alignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("assessment_sessions.session_id"))
    channel_id = Column(String(50), ForeignKey("channel_metadata.channel_id"))
    overall_ikigai_score = Column(DECIMAL(5, 2))
    purpose_clarity_index = Column(DECIMAL(5, 2))
    balance_coefficient_of_variation = Column(DECIMAL(5, 3))
    calculation_method = Column(String(50))
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('session_id', 'channel_id'),
    )


class AgreementMetric(Base):
    """Cross-channel agreement analysis"""
    __tablename__ = "agreement_metrics"

    metric_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("assessment_sessions.session_id"))
    dimension_id = Column(String(50), ForeignKey("dimension_definitions.dimension_id"))
    channel_1_id = Column(String(50), ForeignKey("channel_metadata.channel_id"))
    channel_2_id = Column(String(50), ForeignKey("channel_metadata.channel_id"))

    # Correlation and agreement
    pearson_correlation = Column(DECIMAL(4, 3))
    spearman_correlation = Column(DECIMAL(4, 3))
    icc_value = Column(DECIMAL(4, 3))

    # Bland-Altman metrics
    bland_altman_bias = Column(DECIMAL(5, 2))
    bland_altman_sd = Column(DECIMAL(5, 2))
    limits_of_agreement_lower = Column(DECIMAL(5, 2))
    limits_of_agreement_upper = Column(DECIMAL(5, 2))

    calculation_timestamp = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('session_id', 'dimension_id', 'channel_1_id', 'channel_2_id'),
    )


class ExternalEnrichment(Base):
    """O*NET occupational matches and salary data"""
    __tablename__ = "external_enrichment"

    enrichment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("assessment_sessions.session_id"))
    matched_occupation_soc = Column(String(10))
    occupation_title = Column(String(255))
    match_score = Column(DECIMAL(4, 3))
    interest_match_score = Column(DECIMAL(4, 3))
    skills_match_score = Column(DECIMAL(4, 3))
    values_match_score = Column(DECIMAL(4, 3))

    # Economic data
    median_salary = Column(Integer)
    salary_percentile_25 = Column(Integer)
    salary_percentile_75 = Column(Integer)
    job_growth_rate = Column(DECIMAL(5, 2))
    employment_level = Column(Integer)

    # Location-specific
    location_code = Column(String(10))
    location_name = Column(String(255))
    cost_of_living_index = Column(Integer)
    real_wage = Column(Integer)
    industry_concentration = Column(DECIMAL(4, 3))
    location_compatibility = Column(DECIMAL(4, 3))

    data_source = Column(String(100))
    retrieved_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

    # Relationships
    session = relationship("AssessmentSession", back_populates="enrichment")

    __table_args__ = (
        Index('idx_enrichment_session', 'session_id'),
        Index('idx_enrichment_soc', 'matched_occupation_soc'),
    )


class QualitativeCode(Base):
    """Qualitative coding for Framework Method (Channel 4)"""
    __tablename__ = "qualitative_codes"

    code_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("assessment_sessions.session_id"))
    coder_id = Column(String(100))
    dimension_id = Column(String(50), ForeignKey("dimension_definitions.dimension_id"))

    # Framework Method coding
    theme_label = Column(String(255))
    theme_description = Column(Text)
    frequency_count = Column(Integer)
    intensity_rating = Column(Integer)
    pervasiveness_percentage = Column(DECIMAL(5, 2))
    conviction_score = Column(Integer)
    coherence_rating = Column(Integer)

    # Supporting evidence
    example_quotes = Column(ARRAY(Text))
    coding_notes = Column(Text)

    coded_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        CheckConstraint('intensity_rating BETWEEN 1 AND 5'),
        CheckConstraint('conviction_score BETWEEN 1 AND 5'),
        CheckConstraint('coherence_rating BETWEEN 1 AND 5'),
        Index('idx_qual_codes_session', 'session_id'),
    )


class NLPFeature(Base):
    """NLP features extracted for Channel 3"""
    __tablename__ = "nlp_features"

    feature_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("assessment_sessions.session_id"))
    question_number = Column(Integer)
    dimension_id = Column(String(50), ForeignKey("dimension_definitions.dimension_id"))

    # Text statistics
    word_count = Column(Integer)
    sentence_count = Column(Integer)
    lexical_diversity = Column(DECIMAL(4, 3))
    avg_sentence_length = Column(DECIMAL(5, 2))

    # Sentiment and emotion
    sentiment_compound = Column(DECIMAL(4, 3))
    sentiment_positive = Column(DECIMAL(4, 3))
    sentiment_negative = Column(DECIMAL(4, 3))
    emotion_joy = Column(DECIMAL(4, 3))
    emotion_confidence = Column(DECIMAL(4, 3))

    # Linguistic features
    certainty_markers_count = Column(Integer)
    hedging_markers_count = Column(Integer)
    concrete_nouns_count = Column(Integer)
    abstract_nouns_count = Column(Integer)

    # Embeddings and topics
    sentence_embedding = Column(JSONB)
    dominant_topic = Column(Integer)
    topic_probability = Column(DECIMAL(4, 3))

    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_nlp_session', 'session_id'),
    )


class ExtractedEntity(Base):
    """Named entities (skills, interests, activities)"""
    __tablename__ = "extracted_entities"

    entity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("assessment_sessions.session_id"))
    entity_type = Column(String(50))  # SKILL, INTEREST, ACTIVITY, JOB_TITLE
    entity_text = Column(String(255))
    entity_normalized = Column(String(255))
    dimension_id = Column(String(50), ForeignKey("dimension_definitions.dimension_id"))
    confidence_score = Column(DECIMAL(4, 3))
    onet_skill_id = Column(String(50))
    mention_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_entities_session', 'session_id'),
    )


class IRTItemParameter(Base):
    """IRT item parameters for Channel 2"""
    __tablename__ = "irt_item_parameters"

    param_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    calibration_sample_id = Column(String(100))
    question_number = Column(Integer)
    dimension_id = Column(String(50), ForeignKey("dimension_definitions.dimension_id"))

    # GRM parameters
    discrimination_a = Column(DECIMAL(6, 3))
    threshold_b1 = Column(DECIMAL(6, 3))
    threshold_b2 = Column(DECIMAL(6, 3))
    threshold_b3 = Column(DECIMAL(6, 3))
    threshold_b4 = Column(DECIMAL(6, 3))

    # Item information
    max_information = Column(DECIMAL(6, 3))
    theta_at_max_info = Column(DECIMAL(6, 3))

    # Fit statistics
    chi_square = Column(DECIMAL(8, 3))
    p_value = Column(DECIMAL(5, 4))

    calibration_date = Column(DateTime)
    sample_size = Column(Integer)
    created_at = Column(DateTime, default=func.now())


class IRTThetaEstimate(Base):
    """IRT theta estimates (person parameters)"""
    __tablename__ = "irt_theta_estimates"

    theta_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("assessment_sessions.session_id"))
    dimension_id = Column(String(50), ForeignKey("dimension_definitions.dimension_id"))

    # Estimates from different methods
    theta_eap = Column(DECIMAL(6, 3))
    theta_map = Column(DECIMAL(6, 3))
    theta_mle = Column(DECIMAL(6, 3))

    # Precision
    standard_error_eap = Column(DECIMAL(6, 3))
    information_value = Column(DECIMAL(6, 3))

    estimation_method = Column(String(20), default='eap')
    created_at = Column(DateTime, default=func.now())


class AuditLog(Base):
    """Audit trail for compliance and data quality"""
    __tablename__ = "audit_log"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True))
    action_type = Column(String(100))
    actor = Column(String(100))
    action_timestamp = Column(DateTime, default=func.now())
    action_details = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)

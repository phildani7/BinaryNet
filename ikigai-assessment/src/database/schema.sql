-- Ikigai Assessment Database Schema
-- Supports multi-channel scoring with comprehensive validation metrics

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Participants table
CREATE TABLE participants (
    participant_id SERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    demographics JSONB,
    consent_given BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'enrolled'
);

-- Assessment sessions
CREATE TABLE assessment_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id INTEGER REFERENCES participants(participant_id),
    assessment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    livekit_room_id VARCHAR(255),
    livekit_session_id VARCHAR(255),
    audio_url TEXT,
    audio_duration_seconds INTEGER,
    transcript TEXT,
    transcript_metadata JSONB,
    completion_status VARCHAR(50) DEFAULT 'in_progress',
    demographics JSONB,
    quality_flags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Question responses (structured extraction from transcript)
CREATE TABLE question_responses (
    response_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_dimension VARCHAR(50), -- 'love', 'good_at', 'world_needs', 'paid_for'
    response_text TEXT,
    response_duration_seconds DECIMAL(5,2),
    word_count INTEGER,
    sentiment_score DECIMAL(4,3),
    emotional_intensity DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, question_number)
);

-- Dimension definitions
CREATE TABLE dimension_definitions (
    dimension_id VARCHAR(50) PRIMARY KEY,
    dimension_name VARCHAR(100) NOT NULL,
    description TEXT,
    scale_min INTEGER DEFAULT 0,
    scale_max INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert standard ikigai dimensions
INSERT INTO dimension_definitions (dimension_id, dimension_name, description) VALUES
    ('love', 'What You Love', 'Passion and intrinsic motivation - activities that bring joy and fulfillment'),
    ('good_at', 'What You''re Good At', 'Skills, competencies, and natural talents'),
    ('world_needs', 'What World Needs', 'Social impact, contribution, and addressing meaningful problems'),
    ('paid_for', 'What You Can Be Paid For', 'Economic viability and marketable skills');

-- Channel metadata
CREATE TABLE channel_metadata (
    channel_id VARCHAR(50) PRIMARY KEY,
    method_type VARCHAR(100) NOT NULL,
    description TEXT,
    version VARCHAR(20),
    reliability_coefficient DECIMAL(4,3),
    last_calibration_date DATE,
    configuration JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert channel definitions
INSERT INTO channel_metadata (channel_id, method_type, description, version) VALUES
    ('ctt', 'Classical Test Theory', 'Traditional psychometric scoring with Likert scales and factor analysis', '1.0'),
    ('irt', 'Item Response Theory', 'Graded Response Model with multidimensional IRT (4D-MIRT)', '1.0'),
    ('nlp', 'NLP & Machine Learning', 'Transformer-based semantic analysis with BERTopic and sentiment scoring', '1.0'),
    ('qual', 'Qualitative Framework Method', 'Systematic thematic analysis with intensity and coherence coding', '1.0');

-- Channel scores (primary scoring table)
CREATE TABLE channel_scores (
    score_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    channel_id VARCHAR(50) REFERENCES channel_metadata(channel_id),
    dimension_id VARCHAR(50) REFERENCES dimension_definitions(dimension_id),
    raw_score DECIMAL(6,3),
    normalized_score DECIMAL(5,2), -- 0-100 scale
    z_score DECIMAL(6,3),
    t_score DECIMAL(5,2),
    percentile_rank DECIMAL(5,2),
    confidence_interval_lower DECIMAL(5,2),
    confidence_interval_upper DECIMAL(5,2),
    standard_error DECIMAL(5,3),
    processing_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, channel_id, dimension_id)
);

-- Intersection scores (Passion, Mission, Profession, Vocation)
CREATE TABLE intersection_scores (
    intersection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    channel_id VARCHAR(50) REFERENCES channel_metadata(channel_id),
    intersection_type VARCHAR(50), -- 'passion', 'mission', 'profession', 'vocation'
    score DECIMAL(5,2),
    calculation_method VARCHAR(50) DEFAULT 'geometric_mean',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, channel_id, intersection_type)
);

-- Overall ikigai alignment scores
CREATE TABLE overall_alignment (
    alignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    channel_id VARCHAR(50) REFERENCES channel_metadata(channel_id),
    overall_ikigai_score DECIMAL(5,2),
    purpose_clarity_index DECIMAL(5,2),
    balance_coefficient_of_variation DECIMAL(5,3),
    calculation_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, channel_id)
);

-- Cross-channel agreement metrics
CREATE TABLE agreement_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    dimension_id VARCHAR(50) REFERENCES dimension_definitions(dimension_id),
    channel_1_id VARCHAR(50) REFERENCES channel_metadata(channel_id),
    channel_2_id VARCHAR(50) REFERENCES channel_metadata(channel_id),

    -- Correlation and agreement
    pearson_correlation DECIMAL(4,3),
    spearman_correlation DECIMAL(4,3),
    icc_value DECIMAL(4,3),

    -- Bland-Altman metrics
    bland_altman_bias DECIMAL(5,2),
    bland_altman_sd DECIMAL(5,2),
    limits_of_agreement_lower DECIMAL(5,2),
    limits_of_agreement_upper DECIMAL(5,2),

    calculation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, dimension_id, channel_1_id, channel_2_id)
);

-- MTMM (Multitrait-Multimethod) matrix storage
CREATE TABLE mtmm_matrix (
    mtmm_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_cohort VARCHAR(100),
    calculation_date DATE,
    sample_size INTEGER,
    correlation_matrix JSONB, -- Stores full 16x16 matrix
    variance_decomposition JSONB, -- Trait, method, error variance
    convergent_validity_avg DECIMAL(4,3),
    discriminant_validity_avg DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- External data integration - O*NET occupational matches
CREATE TABLE external_enrichment (
    enrichment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    matched_occupation_soc VARCHAR(10),
    occupation_title VARCHAR(255),
    match_score DECIMAL(4,3),
    interest_match_score DECIMAL(4,3),
    skills_match_score DECIMAL(4,3),
    values_match_score DECIMAL(4,3),

    -- Economic data
    median_salary INTEGER,
    salary_percentile_25 INTEGER,
    salary_percentile_75 INTEGER,
    job_growth_rate DECIMAL(5,2),
    employment_level INTEGER,

    -- Location-specific
    location_code VARCHAR(10),
    location_name VARCHAR(255),
    cost_of_living_index INTEGER,
    real_wage INTEGER,
    industry_concentration DECIMAL(4,3),
    location_compatibility DECIMAL(4,3),

    data_source VARCHAR(100),
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Qualitative coding (for Channel 4)
CREATE TABLE qualitative_codes (
    code_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    coder_id VARCHAR(100),
    dimension_id VARCHAR(50) REFERENCES dimension_definitions(dimension_id),

    -- Framework Method coding
    theme_label VARCHAR(255),
    theme_description TEXT,
    frequency_count INTEGER,
    intensity_rating INTEGER CHECK (intensity_rating BETWEEN 1 AND 5),
    pervasiveness_percentage DECIMAL(5,2),
    conviction_score INTEGER CHECK (conviction_score BETWEEN 1 AND 5),
    coherence_rating INTEGER CHECK (coherence_rating BETWEEN 1 AND 5),

    -- Supporting evidence
    example_quotes TEXT[],
    coding_notes TEXT,

    coded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inter-rater reliability tracking
CREATE TABLE inter_rater_reliability (
    irr_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_phase VARCHAR(100),
    calculation_date DATE,
    sample_size INTEGER,
    num_raters INTEGER,

    -- Reliability coefficients
    krippendorff_alpha DECIMAL(4,3),
    cohen_kappa DECIMAL(4,3),
    percent_agreement DECIMAL(5,2),

    dimension_id VARCHAR(50) REFERENCES dimension_definitions(dimension_id),
    reliability_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Validation studies
CREATE TABLE validation_studies (
    study_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_name VARCHAR(255),
    study_type VARCHAR(100), -- 'test_retest', 'convergent', 'predictive', etc.
    start_date DATE,
    end_date DATE,
    sample_size INTEGER,

    -- Results summary
    results_summary JSONB,
    primary_metric_name VARCHAR(100),
    primary_metric_value DECIMAL(6,3),

    -- Quality indicators
    power_achieved DECIMAL(4,3),
    confidence_level DECIMAL(4,3),
    effect_size DECIMAL(5,3),

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test-retest reliability data
CREATE TABLE test_retest_data (
    retest_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id INTEGER REFERENCES participants(participant_id),
    session_1_id UUID REFERENCES assessment_sessions(session_id),
    session_2_id UUID REFERENCES assessment_sessions(session_id),
    channel_id VARCHAR(50) REFERENCES channel_metadata(channel_id),
    dimension_id VARCHAR(50) REFERENCES dimension_definitions(dimension_id),

    time_interval_days INTEGER,
    score_time_1 DECIMAL(5,2),
    score_time_2 DECIMAL(5,2),
    absolute_difference DECIMAL(5,2),

    icc_individual DECIMAL(4,3),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictive validity outcomes
CREATE TABLE predictive_outcomes (
    outcome_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    follow_up_months INTEGER,
    outcome_date DATE,

    -- Career outcomes
    career_satisfaction DECIMAL(3,1) CHECK (career_satisfaction BETWEEN 1 AND 7),
    job_changed BOOLEAN,
    salary_change_percentage DECIMAL(5,2),
    goal_achievement_score DECIMAL(5,2),
    life_satisfaction DECIMAL(3,1) CHECK (life_satisfaction BETWEEN 1 AND 7),

    -- Alignment indicators
    passion_alignment_self_report DECIMAL(5,2),
    skills_utilization DECIMAL(5,2),
    impact_perception DECIMAL(5,2),
    economic_security DECIMAL(5,2),

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NLP features (for Channel 3)
CREATE TABLE nlp_features (
    feature_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    question_number INTEGER,
    dimension_id VARCHAR(50) REFERENCES dimension_definitions(dimension_id),

    -- Text statistics
    word_count INTEGER,
    sentence_count INTEGER,
    lexical_diversity DECIMAL(4,3),
    avg_sentence_length DECIMAL(5,2),

    -- Sentiment and emotion
    sentiment_compound DECIMAL(4,3),
    sentiment_positive DECIMAL(4,3),
    sentiment_negative DECIMAL(4,3),
    emotion_joy DECIMAL(4,3),
    emotion_confidence DECIMAL(4,3),

    -- Linguistic features
    certainty_markers_count INTEGER,
    hedging_markers_count INTEGER,
    concrete_nouns_count INTEGER,
    abstract_nouns_count INTEGER,

    -- Embeddings (stored as JSONB array)
    sentence_embedding JSONB,

    -- Topic modeling
    dominant_topic INTEGER,
    topic_probability DECIMAL(4,3),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Named entities extracted (skills, interests, activities)
CREATE TABLE extracted_entities (
    entity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    entity_type VARCHAR(50), -- 'SKILL', 'INTEREST', 'ACTIVITY', 'JOB_TITLE'
    entity_text VARCHAR(255),
    entity_normalized VARCHAR(255),
    dimension_id VARCHAR(50) REFERENCES dimension_definitions(dimension_id),
    confidence_score DECIMAL(4,3),
    onet_skill_id VARCHAR(50),
    mention_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IRT parameters (for Channel 2)
CREATE TABLE irt_item_parameters (
    param_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    calibration_sample_id VARCHAR(100),
    question_number INTEGER,
    dimension_id VARCHAR(50) REFERENCES dimension_definitions(dimension_id),

    -- GRM parameters
    discrimination_a DECIMAL(6,3),
    threshold_b1 DECIMAL(6,3),
    threshold_b2 DECIMAL(6,3),
    threshold_b3 DECIMAL(6,3),
    threshold_b4 DECIMAL(6,3),

    -- Item information
    max_information DECIMAL(6,3),
    theta_at_max_info DECIMAL(6,3),

    -- Fit statistics
    chi_square DECIMAL(8,3),
    p_value DECIMAL(5,4),

    calibration_date DATE,
    sample_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IRT theta estimates (person parameters)
CREATE TABLE irt_theta_estimates (
    theta_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES assessment_sessions(session_id),
    dimension_id VARCHAR(50) REFERENCES dimension_definitions(dimension_id),

    -- Estimates from different methods
    theta_eap DECIMAL(6,3),
    theta_map DECIMAL(6,3),
    theta_mle DECIMAL(6,3),

    -- Precision
    standard_error_eap DECIMAL(6,3),
    information_value DECIMAL(6,3),

    estimation_method VARCHAR(20) DEFAULT 'eap',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log for data quality and compliance
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID,
    action_type VARCHAR(100),
    actor VARCHAR(100),
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_details JSONB,
    ip_address INET,
    user_agent TEXT
);

-- Indexes for performance
CREATE INDEX idx_sessions_participant ON assessment_sessions(participant_id);
CREATE INDEX idx_sessions_status ON assessment_sessions(completion_status);
CREATE INDEX idx_sessions_timestamp ON assessment_sessions(assessment_timestamp);

CREATE INDEX idx_channel_scores_session ON channel_scores(session_id);
CREATE INDEX idx_channel_scores_channel ON channel_scores(channel_id);
CREATE INDEX idx_channel_scores_dimension ON channel_scores(dimension_id);
CREATE INDEX idx_channel_scores_composite ON channel_scores(session_id, channel_id, dimension_id);

CREATE INDEX idx_responses_session ON question_responses(session_id);
CREATE INDEX idx_responses_dimension ON question_responses(question_dimension);

CREATE INDEX idx_enrichment_session ON external_enrichment(session_id);
CREATE INDEX idx_enrichment_soc ON external_enrichment(matched_occupation_soc);

CREATE INDEX idx_nlp_session ON nlp_features(session_id);
CREATE INDEX idx_entities_session ON extracted_entities(session_id);
CREATE INDEX idx_qual_codes_session ON qualitative_codes(session_id);

-- Views for common queries

-- Comprehensive session summary
CREATE VIEW v_session_summary AS
SELECT
    s.session_id,
    s.participant_id,
    s.assessment_timestamp,
    s.completion_status,
    COUNT(DISTINCT cs.channel_id) as channels_completed,
    AVG(cs.normalized_score) as avg_score_across_all,
    json_agg(DISTINCT cs.channel_id) as channels_list
FROM assessment_sessions s
LEFT JOIN channel_scores cs ON s.session_id = cs.session_id
GROUP BY s.session_id, s.participant_id, s.assessment_timestamp, s.completion_status;

-- Cross-channel comparison view
CREATE VIEW v_cross_channel_comparison AS
SELECT
    cs.session_id,
    cs.dimension_id,
    MAX(CASE WHEN cs.channel_id = 'ctt' THEN cs.normalized_score END) as ctt_score,
    MAX(CASE WHEN cs.channel_id = 'irt' THEN cs.normalized_score END) as irt_score,
    MAX(CASE WHEN cs.channel_id = 'nlp' THEN cs.normalized_score END) as nlp_score,
    MAX(CASE WHEN cs.channel_id = 'qual' THEN cs.normalized_score END) as qual_score,
    STDDEV(cs.normalized_score) as score_std_dev,
    MAX(cs.normalized_score) - MIN(cs.normalized_score) as score_range
FROM channel_scores cs
GROUP BY cs.session_id, cs.dimension_id;

-- Comments for documentation
COMMENT ON TABLE assessment_sessions IS 'Primary table storing voice assessment sessions with LiveKit metadata and transcripts';
COMMENT ON TABLE channel_scores IS 'Normalized scores from all four scoring channels (CTT, IRT, NLP, Qualitative)';
COMMENT ON TABLE agreement_metrics IS 'Cross-channel agreement analysis including Bland-Altman and ICC metrics';
COMMENT ON TABLE external_enrichment IS 'O*NET occupational matches and BLS salary data integration';
COMMENT ON TABLE qualitative_codes IS 'Systematic qualitative coding using Framework Method';
COMMENT ON TABLE irt_theta_estimates IS 'Person ability parameters from multidimensional IRT models';

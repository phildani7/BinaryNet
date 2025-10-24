# Ikigai Assessment System - Quick Start Guide

## Overview

This system provides a comprehensive ikigai assessment combining voice-based conversational interviews with four parallel scoring methodologies to determine which approach performs best.

## Prerequisites

- Docker & Docker Compose
- Python 3.10+
- R 4.0+ (for IRT analysis)
- API Keys:
  - LiveKit (for voice sessions)
  - ElevenLabs (for AI voice synthesis)
  - OpenAI (for transcription)

## Quick Setup

### 1. Clone and Configure

```bash
cd ikigai-assessment

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# R packages for IRT
Rscript install_r_packages.R

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 3. Start Services with Docker

```bash
# Start all services (PostgreSQL, Redis, LiveKit, API, Dashboard)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
```

### 4. Initialize Database

```bash
# Create database schema
docker-compose exec postgres psql -U ikigai_user -d ikigai_db -f /docker-entrypoint-initdb.d/01-schema.sql
```

## Running an Assessment

### Option 1: Using Python Orchestrator

```python
import asyncio
from src.orchestrator import IkigaiAssessmentOrchestrator

# Configure
config = {
    'livekit_url': 'wss://your-livekit-server.com',
    'livekit_api_key': 'your_api_key',
    'livekit_api_secret': 'your_secret',
    'elevenlabs_api_key': 'your_elevenlabs_key'
}

# Run assessment
async def run_assessment():
    orchestrator = IkigaiAssessmentOrchestrator(
        participant_id="P001",
        config=config
    )

    results = await orchestrator.run_full_assessment()

    # View results
    print(f"Overall Ikigai: {results['report']['overall_ikigai']:.1f}")
    print(f"Dimensions: {results['report']['dimension_scores']}")

    return results

# Execute
results = asyncio.run(run_assessment())
```

### Option 2: Using API Endpoints

```bash
# Start a new assessment session
curl -X POST http://localhost:8000/api/v1/assessments \
  -H "Content-Type: application/json" \
  -d '{"participant_id": "P001"}'

# Get results
curl http://localhost:8000/api/v1/assessments/{session_id}/results
```

## Understanding the Four Scoring Channels

### Channel 1: Classical Test Theory (CTT)
- Traditional psychometric approach
- Likert scale scoring with behavioral anchors
- Cronbach's alpha reliability
- Z-scores and T-scores
- **Best for**: Normative comparisons

### Channel 2: Item Response Theory (IRT)
- Graded Response Model (GRM)
- Multidimensional IRT (4D-MIRT)
- Theta estimates (EAP, MAP, MLE)
- Information functions
- **Best for**: Precision measurement

### Channel 3: NLP/Machine Learning
- Transformer-based semantic analysis
- BERTopic for theme extraction
- VADER sentiment analysis
- Linguistic feature extraction
- **Best for**: Automated scoring at scale

### Channel 4: Qualitative Framework Method
- Systematic thematic analysis
- Intensity and conviction coding
- Narrative coherence assessment
- Inter-rater reliability protocols
- **Best for**: Rich narrative interpretation

## Interpreting Results

### Dimension Scores (0-100)

- **80-100**: Excellent - Strong clarity and alignment
- **60-79**: Good - Solid foundation with some development areas
- **40-59**: Moderate - Emerging clarity, focus needed
- **0-39**: Low - Significant exploration required

### Intersection Scores

- **Passion** = √(Love × Good_At)
- **Mission** = √(Love × World_Needs)
- **Profession** = √(Good_At × Paid_For)
- **Vocation** = √(World_Needs × Paid_For)

### Overall Ikigai

Overall = (Love × Good_At × World_Needs × Paid_For)^(1/4)

All four dimensions must be present for true ikigai.

## Validation Metrics

### Cross-Channel Agreement

- **Bland-Altman Analysis**: Agreement between scoring methods
- **Pearson Correlation**: r ≥ 0.70 indicates strong convergent validity
- **ICC**: ≥ 0.75 shows good test-retest reliability

### Quality Thresholds

- Cronbach's α ≥ 0.85 (high-stakes) or ≥ 0.70 (research)
- Krippendorff's Alpha ≥ 0.80 (inter-rater reliability)
- MTMM convergent validity ≥ 0.60

## Visualization Dashboard

Access the interactive dashboard at: `http://localhost:8050`

Features:
- Ikigai Venn diagram with quantitative scores
- Cross-channel comparison charts
- Bland-Altman plots
- Parallel coordinates plots
- Career pathway recommendations

## Troubleshooting

### Services won't start

```bash
# Check Docker logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U ikigai_user -d ikigai_db -c "SELECT 1;"
```

### R/IRT scoring fails

```bash
# Verify R packages installed
Rscript -e "library(mirt); print('mirt OK')"

# Reinstall R packages
Rscript install_r_packages.R
```

### NLP models fail to load

```bash
# Download required models
python -m spacy download en_core_web_sm
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

## Sample Data

Generate sample assessment data for testing:

```python
from src.utils.sample_data import generate_sample_responses

# Generate mock transcript and responses
responses = generate_sample_responses(
    participant_id="TEST001",
    quality_level="high"  # high, medium, low
)

# Score using all channels
from src.orchestrator import IkigaiAssessmentOrchestrator

orchestrator = IkigaiAssessmentOrchestrator("TEST001", config)
orchestrator.responses = responses
orchestrator.transcript = " ".join([r['response_text'] for r in responses])

scoring_results = await orchestrator._run_parallel_scoring()
```

## Next Steps

1. **Pilot Testing**: Run N=10-20 participants to refine questions
2. **Calibration Study**: Collect N=800+ for IRT parameter calibration
3. **Validation Study**: N=130 with counterbalanced design
4. **Production Deployment**: Scale to thousands of participants

## Documentation

- [Complete Research Document](docs/research_methodology.md)
- [API Documentation](docs/api.md)
- [Database Schema](docs/database.md)
- [Scoring Algorithms](docs/scoring.md)
- [Validation Methods](docs/validation.md)

## Support

For issues or questions:
- GitHub Issues: [Report a bug](https://github.com/yourusername/ikigai-assessment/issues)
- Documentation: [Read the docs](docs/)
- Email: support@example.com

## Citation

If you use this system in research:

```bibtex
@software{ikigai_assessment_2025,
  title={Ikigai Assessment System: Multi-Method Voice-Based Career Alignment},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/ikigai-assessment}
}
```

## License

[Your License] - See LICENSE file

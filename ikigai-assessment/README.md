# Ikigai Assessment System with LiveKit

A scientifically rigorous two-phase ikigai assessment system combining conversational voice recording with four parallel scoring methodologies.

## Overview

This system implements a comprehensive ikigai assessment framework that:
- Uses **LiveKit** for real-time voice-based conversational assessment (Phase 1)
- Employs **four parallel scoring channels** for comparative validation (Phase 2):
  1. Classical Test Theory (CTT)
  2. Item Response Theory (IRT)
  3. NLP/Machine Learning with Transformers
  4. Hybrid Qualitative-Quantitative Framework Method

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 1: Voice Assessment                 │
│  ┌────────────┐      ┌──────────────┐     ┌──────────────┐ │
│  │  LiveKit   │─────▶│ ElevenLabs   │────▶│ Transcript   │ │
│  │  Session   │      │ Voice AI     │     │  Generation  │ │
│  └────────────┘      └──────────────┘     └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Phase 2: Four Parallel Scoring Channels         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐│
│  │ Channel 1  │  │ Channel 2  │  │ Channel 3  │  │Channel4││
│  │    CTT     │  │    IRT     │  │   NLP/ML   │  │  Qual  ││
│  │ Psycho-    │  │  Graded    │  │ Transform- │  │ Frame- ││
│  │ metrics    │  │ Response   │  │    ers     │  │  work  ││
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘  └────┬───┘│
└─────────┼────────────────┼────────────────┼─────────────┼────┘
          │                │                │             │
          └────────────────┴────────────────┴─────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│          Cross-Channel Validation & Comparison               │
│  • Bland-Altman Analysis    • MTMM Matrix                   │
│  • Test-Retest Reliability  • Predictive Validity           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│       External Data Integration & Visualization              │
│  • O*NET Occupational Data  • BLS Salary Database           │
│  • Interactive Dashboards   • Ikigai Venn Diagrams          │
└─────────────────────────────────────────────────────────────┘
```

## Four Ikigai Dimensions

1. **What You Love** (Passion/Intrinsic Motivation)
2. **What You're Good At** (Skills/Competencies)
3. **What World Needs** (Social Impact/Contribution)
4. **What You Can Be Paid For** (Economic Viability)

## Key Features

### Phase 1: Voice Assessment
- 20 empathetic questions using motivational interviewing techniques
- LiveKit real-time communication for voice interaction
- ElevenLabs AI voice synthesis for natural conversation
- Automatic transcription and data extraction
- 25-35 minute assessment duration

### Phase 2: Four Scoring Channels

#### Channel 1: Classical Test Theory (CTT)
- Likert scale scoring with rubrics
- Cronbach's alpha reliability (target α ≥ 0.85)
- Z-scores and T-scores for normative comparison
- Factor analysis for dimensional structure

#### Channel 2: Item Response Theory (IRT)
- Graded Response Model for polytomous items
- Multidimensional IRT (4D-MIRT)
- Theta estimation via EAP/MAP/MLE
- Information functions for precision measurement
- Requires N≥800 for stable estimates

#### Channel 3: NLP/Machine Learning
- Transformer-based scoring (BERT, RoBERTa, DeBERTa)
- BERTopic for theme extraction
- Sentiment analysis with intensity
- Named Entity Recognition for skills/interests
- Semantic similarity scoring

#### Channel 4: Qualitative Framework Method
- Systematic thematic analysis
- Inter-rater reliability (Krippendorff's Alpha ≥ 0.80)
- Intensity and conviction coding
- Narrative coherence assessment

### Cross-Channel Validation
- Convergent validity (r ≥ 0.70)
- Discriminant validity (Fornell-Larcker, HTMT)
- Bland-Altman agreement analysis
- MTMM (Multitrait-Multimethod) matrix
- Test-retest reliability (ICC ≥ 0.75)

### External Enrichment
- O*NET occupational matching
- BLS salary and employment data
- Location-specific cost of living adjustments
- Career pathway recommendations

## Technology Stack

- **Backend**: Python 3.10+
- **Real-time Communication**: LiveKit
- **Voice AI**: ElevenLabs API
- **NLP**: Hugging Face Transformers, spaCy, BERTopic
- **Statistical Analysis**: R with mirt, psych packages
- **Database**: PostgreSQL with JSONB support
- **Visualization**: D3.js, Plotly Dash
- **API**: FastAPI
- **Task Queue**: Celery with Redis
- **Container**: Docker & Docker Compose

## Project Structure

```
ikigai-assessment/
├── src/
│   ├── phase1_voice_assessment/     # LiveKit voice interaction
│   ├── phase2_scoring/
│   │   ├── channel1_ctt/            # Classical Test Theory
│   │   ├── channel2_irt/            # Item Response Theory
│   │   ├── channel3_nlp/            # NLP/ML scoring
│   │   └── channel4_qualitative/    # Framework Method
│   ├── validation/                  # Cross-channel validation
│   ├── visualization/               # Dashboards and charts
│   ├── external_data/               # O*NET, BLS integration
│   ├── database/                    # Schema and models
│   └── utils/                       # Shared utilities
├── config/                          # Configuration files
├── data/                            # Data storage
├── tests/                           # Unit and integration tests
├── docs/                            # Documentation
└── scripts/                         # Utility scripts
```

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install R dependencies for IRT
Rscript install_r_packages.R

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (LiveKit, ElevenLabs, O*NET)
```

### Running the System

```bash
# Start database
docker-compose up -d postgres redis

# Run database migrations
python scripts/migrate_db.py

# Start LiveKit server (or use cloud)
docker-compose up -d livekit

# Start the API server
python src/api/main.py

# Start Celery workers for async scoring
celery -A src.workers worker --loglevel=info

# Launch dashboard
python src/visualization/app.py
```

### Running an Assessment

```python
from src.phase1_voice_assessment.session import IkigaiSession

# Create assessment session
session = IkigaiSession(participant_id="P001")

# Start LiveKit voice assessment
await session.start_voice_assessment()

# Process transcript through all 4 channels
results = await session.score_all_channels()

# Generate report
report = session.generate_report()
```

## Sample Size Requirements

- **Pilot Testing**: N=10-20
- **Method Development**: N=130 (within-subjects design)
- **Stable IRT Parameters**: N=800-1000
- **Optimal Production**: N=1500+

## Validation Metrics

### Reliability
- Cronbach's α ≥ 0.85 (high-stakes) or ≥ 0.70 (research)
- Test-retest ICC(3,1) ≥ 0.75
- Inter-rater Krippendorff's Alpha ≥ 0.80

### Validity
- Convergent: r ≥ 0.70 between channels
- Discriminant: HTMT < 0.85
- Predictive: r ≥ 0.30 with 6-month outcomes
- Model Fit: CFI > 0.95, RMSEA < 0.05

## Output Scores

Each participant receives:

1. **Four Dimension Scores** (0-100 scale)
2. **Four Intersection Scores**:
   - Passion = √(Love × Good_At)
   - Mission = √(Love × World_Needs)
   - Profession = √(Good_At × Paid_For)
   - Vocation = √(World_Needs × Paid_For)
3. **Overall Ikigai Alignment**: (Love × Good_At × World_Needs × Paid_For)^(1/4)
4. **Purpose Clarity Index**: Mean_Alignment × (1 - CV)
5. **Top Matched Occupations** with salary data
6. **Personalized Development Recommendations**

## Visualization Dashboard

- Interactive Ikigai Venn diagram with quantitative scores
- Parallel coordinates plot comparing all 4 channels
- Radar charts showing dimension profiles
- Bland-Altman agreement plots
- Heat maps of cross-channel correlations
- Career pathway recommendations

## Research Applications

This system enables comparative validation research to determine which scoring methodology performs best across:
- Agreement with expert human raters
- Predictive validity for career outcomes
- Test-retest stability
- Cost-effectiveness and scalability
- User experience and engagement

## Development Timeline

- **Months 1-3**: Question development, pilot testing
- **Months 4-6**: Channel 1 (CTT) & Channel 3 (NLP) implementation
- **Months 7-9**: Channel 2 (IRT) & Channel 4 (Qualitative) implementation
- **Months 10-12**: Data collection (N=130)
- **Months 13-15**: Validation analysis
- **Months 16-18**: Production deployment

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## License

[License Type] - See LICENSE file

## Citation

If you use this system in research, please cite:

```bibtex
@software{ikigai_assessment_2025,
  title={Ikigai Assessment System: Multi-Method Voice-Based Career Alignment},
  author={[Your Name]},
  year={2025},
  url={https://github.com/yourusername/ikigai-assessment}
}
```

## References

Based on research synthesis covering:
- Classical Test Theory and psychometrics
- Item Response Theory (Rasch, 2PL, GRM models)
- Natural Language Processing with transformers
- Qualitative research methodology (Framework Method)
- Ikigai philosophy and Purpose in Life research

## Contact

For questions or collaboration: [your-email@example.com]

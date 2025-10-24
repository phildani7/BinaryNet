# Testing the Ikigai Assessment System

This directory contains comprehensive tests for the ikigai assessment system.

## Quick Start - Text-Based Testing

### Option 1: Run Quick Test (Easiest)

```bash
# From the ikigai-assessment directory
python quick_test.py
```

This will:
- Use pre-written sample responses (no API keys needed)
- Score with all 4 channels
- Show cross-channel validation
- Display results summary

### Option 2: Run Complete Test with Options

```bash
# High-quality detailed responses
python tests/test_text_assessment.py --mode sample --quality high

# Medium-quality responses
python tests/test_text_assessment.py --mode sample --quality medium

# Low-quality brief responses
python tests/test_text_assessment.py --mode sample --quality low

# Save results to JSON
python tests/test_text_assessment.py --mode sample --quality high --output results.json
```

### Option 3: Interactive Text Entry

```bash
# Type your own responses to each question
python tests/test_text_assessment.py --mode interactive
```

## Unit Tests

Test individual components:

```bash
# Run all unit tests
python tests/test_channels.py

# Or with pytest (if installed)
pytest tests/test_channels.py -v
```

## What Gets Tested

### Channel Tests

1. **Classical Test Theory (CTT)**
   - Likert scale scoring
   - Normalization to 0-100
   - Reliability calculations

2. **Item Response Theory (IRT)**
   - Theta estimation
   - Information functions
   - Simplified scoring (when R unavailable)

3. **NLP/Machine Learning**
   - Feature extraction (word count, sentiment, etc.)
   - Conviction vs hedging detection
   - Semantic similarity

4. **Qualitative Framework Method**
   - Intensity coding (1-5 scale)
   - Conviction coding
   - Narrative coherence

5. **Cross-Channel Validation**
   - Bland-Altman analysis
   - ICC calculation
   - Correlation metrics

## Sample Response Quality Levels

### High Quality
- Detailed, thoughtful responses (200-400 words)
- Rich emotional language
- Specific examples and stories
- Clear conviction and coherence
- **Expected scores**: 70-90 across dimensions

### Medium Quality
- Moderate detail (50-100 words)
- Some specificity
- Basic engagement
- **Expected scores**: 50-70 across dimensions

### Low Quality
- Brief responses (5-20 words)
- Generic language
- Minimal detail
- **Expected scores**: 20-40 across dimensions

## Understanding Test Output

### Dimension Scores (0-100)

```
Dimension       CTT       IRT       NLP       Qual      Avg
----------------------------------------------------------------
love            85.0      82.3      87.5      84.2      84.8
good_at         78.5      76.2      80.1      79.3      78.5
world_needs     82.1      79.8      83.4      81.7      81.8
paid_for        75.3      72.9      76.8      74.5      74.9
```

### Cross-Channel Validation

- **Average Absolute Difference**: How much channels disagree
  - <10: Excellent agreement
  - 10-20: Good agreement
  - >20: Poor agreement (investigate)

- **Max Difference**: Largest disagreement between any two channels
- **Min Difference**: Smallest disagreement

## Troubleshooting

### "Module not found" errors

```bash
# Make sure you're in the ikigai-assessment directory
cd ikigai-assessment

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Missing dependencies

```bash
# Install required packages
pip install numpy pandas scipy pyyaml

# Optional (for better NLP)
pip install transformers sentence-transformers vaderSentiment
```

### R/IRT warnings

The IRT channel uses R for advanced modeling. If R is not available, it falls back to simplified scoring. This is normal for testing.

To enable full IRT:
```bash
# Install R and packages
Rscript install_r_packages.R
```

## Next Steps After Testing

1. **Review Scores**: Check if different quality levels produce expected score ranges
2. **Compare Channels**: See which channel is most sensitive to response quality
3. **Validate Metrics**: Ensure cross-channel agreement is reasonable
4. **Customize**: Modify sample responses in `test_text_assessment.py` to test edge cases
5. **Production**: Move to voice-based assessment with LiveKit when ready

## Example: Complete Test Flow

```bash
# 1. Run quick test to verify everything works
python quick_test.py

# 2. Test all quality levels
for quality in high medium low; do
    python tests/test_text_assessment.py --mode sample --quality $quality \
        --output results_${quality}.json
done

# 3. Run unit tests
python tests/test_channels.py

# 4. Compare results
python -c "
import json
for q in ['high', 'medium', 'low']:
    with open(f'results_{q}.json') as f:
        data = json.load(f)
    print(f'{q.upper()}: Overall Ikigai = {data[\"ctt\"][\"overall_alignment\"][\"overall_ikigai_score\"]:.1f}')
"
```

## Understanding the Four Channels

Each channel scores the same responses differently:

- **CTT**: Traditional psychometric approach, good for comparisons
- **IRT**: Advanced modeling, precise at different ability levels
- **NLP**: Automated, scales well, captures linguistic features
- **Qualitative**: Rich interpretation, captures narrative depth

The goal is to determine which performs best through systematic validation!

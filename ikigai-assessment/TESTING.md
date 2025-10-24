# Testing Guide - Ikigai Assessment System

## 🚀 Quick Start (No API Keys Required!)

The easiest way to test the system is using **text-based testing** - you don't need LiveKit, ElevenLabs, or any API keys!

### Option 1: One-Command Test

```bash
cd ikigai-assessment

# Run the quick test script
./run_test.sh

# Or directly with Python
python quick_test.py
```

This will:
- ✅ Use pre-written high-quality sample responses
- ✅ Score with all 4 channels (CTT, IRT, NLP, Qualitative)
- ✅ Run cross-channel validation
- ✅ Display comprehensive results

**No configuration needed!**

### Option 2: Test Different Quality Levels

```bash
# High-quality responses (detailed, thoughtful)
python tests/test_text_assessment.py --mode sample --quality high

# Medium-quality responses (moderate detail)
python tests/test_text_assessment.py --mode sample --quality medium

# Low-quality responses (brief, generic)
python tests/test_text_assessment.py --mode sample --quality low
```

### Option 3: Interactive Text Entry

```bash
# Type your own responses to each question
python tests/test_text_assessment.py --mode interactive
```

You'll be prompted with all 20 ikigai questions and can type your responses.

## 📊 Understanding Test Results

### Sample Output

```
Dimension Scores Across All Channels (0-100 scale):

Dimension       CTT       IRT       NLP       Qual      Avg
----------------------------------------------------------------------
love            85.0      82.3      87.5      84.2      84.8
good_at         78.5      76.2      80.1      79.3      78.5
world_needs     82.1      79.8      83.4      81.7      81.8
paid_for        75.3      72.9      76.8      74.5      74.9

Overall Ikigai Scores:

  CTT   : 80.2
  IRT   : 77.8
  NLP   : 82.4
  QUAL  : 80.6

CROSS-CHANNEL VALIDATION

Channels compared: ['ctt', 'irt', 'nlp', 'qual']
Average absolute difference: 3.2
Max difference: 5.4
Min difference: 1.2
```

### What This Tells You

**Dimension Scores (0-100)**
- **80-100**: Excellent alignment - strong clarity
- **60-79**: Good alignment - solid foundation
- **40-59**: Moderate - needs development
- **0-39**: Low - significant exploration needed

**Cross-Channel Agreement**
- **Avg Difference < 10**: Excellent - channels agree well
- **Avg Difference 10-20**: Good - acceptable variation
- **Avg Difference > 20**: Poor - investigate further

**Overall Ikigai Score**
- Calculated as: (Love × Good_At × World_Needs × Paid_For)^(1/4)
- All four dimensions must be present for high ikigai

## 🧪 Unit Testing

Test individual components:

```bash
# Run all unit tests
python tests/test_channels.py

# With pytest (if installed)
pytest tests/test_channels.py -v
```

### What Gets Tested

✅ **Classical Test Theory (CTT)**
- Likert scale scoring with behavioral anchors
- Score normalization (0-100)
- Reliability calculations (Cronbach's alpha)

✅ **Item Response Theory (IRT)**
- Theta estimation (EAP, MAP, MLE)
- Information functions
- Simplified fallback when R unavailable

✅ **NLP/Machine Learning**
- Feature extraction (word count, sentiment, etc.)
- Conviction vs hedging detection
- Semantic similarity scoring

✅ **Qualitative Framework Method**
- Intensity coding (1-5 scale)
- Conviction assessment
- Narrative coherence evaluation

✅ **Cross-Channel Validation**
- Bland-Altman analysis
- ICC calculation
- Correlation metrics

## 📝 Sample Response Examples

### High-Quality Response (Score: 85-90)

```
I am absolutely passionate about teaching data science to aspiring analysts.
There was this moment last year when I was mentoring a student who was
struggling with understanding machine learning concepts. We spent hours working
through examples, and I could see the frustration building. Then suddenly,
everything clicked - I saw it in her eyes, this moment of pure understanding.
She built her first predictive model that day and was so excited she stayed
up all night experimenting. Time completely disappeared during those sessions.
I love seeing people transform from confused to confident, from students to
practitioners.
```

**Why it scores high:**
- ✅ Detailed narrative (200+ words)
- ✅ Specific example with vivid details
- ✅ Emotional language ("passionate", "love")
- ✅ Evidence of flow state ("time disappeared")
- ✅ Clear impact described

### Medium-Quality Response (Score: 55-65)

```
I really enjoy working with data and helping people solve problems. I like
when I can create visualizations that make complex information easy to
understand. It feels good when my work makes a difference.
```

**Why it scores medium:**
- ✅ Some specificity mentioned
- ⚠️ Limited detail (~40 words)
- ⚠️ Generic language
- ⚠️ No specific examples

### Low-Quality Response (Score: 20-30)

```
I like data
```

**Why it scores low:**
- ❌ Minimal content (3 words)
- ❌ No elaboration
- ❌ No emotional content
- ❌ No examples or details

## 🔧 Troubleshooting

### "Module not found" Error

```bash
# Make sure you're in the right directory
cd ikigai-assessment

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Missing Dependencies

```bash
# Install core dependencies
pip install numpy pandas scipy pyyaml

# Optional: For better NLP features
pip install transformers sentence-transformers vaderSentiment spacy

# Download spaCy model
python -m spacy download en_core_web_sm
```

### R/IRT Warnings

The IRT channel uses R for advanced modeling. If R is not available, it automatically falls back to simplified scoring.

**This is completely normal for testing!**

To enable full IRT (optional):
```bash
# Install R packages
Rscript install_r_packages.R
```

## 📈 Advanced Testing

### Save Results to JSON

```bash
python tests/test_text_assessment.py \
    --mode sample \
    --quality high \
    --output results.json

# View results
cat results.json | python -m json.tool
```

### Compare Quality Levels

```bash
# Test all three quality levels
for quality in high medium low; do
    python tests/test_text_assessment.py \
        --mode sample \
        --quality $quality \
        --output results_${quality}.json
done

# Compare overall scores
for quality in high medium low; do
    echo -n "$quality: "
    cat results_${quality}.json | \
        python -c "import sys, json; data=json.load(sys.stdin); print(data['ctt']['overall_alignment']['overall_ikigai_score'])"
done
```

### Custom Sample Responses

Edit `tests/test_text_assessment.py` and modify the `_high_quality_responses()` method to test your own content.

## 🎯 What to Test

### 1. Basic Functionality
```bash
./run_test.sh
```
Verify all channels execute without errors.

### 2. Quality Sensitivity
```bash
python tests/test_text_assessment.py --quality high
python tests/test_text_assessment.py --quality low
```
Ensure low-quality responses score lower than high-quality.

### 3. Cross-Channel Agreement
```bash
python quick_test.py
```
Check that "Average absolute difference" is reasonable (< 15).

### 4. Individual Components
```bash
python tests/test_channels.py
```
Verify each scoring component works independently.

## 🚦 Success Criteria

Your test is successful if:

✅ All 4 channels execute without errors
✅ Scores are in reasonable ranges (0-100)
✅ High-quality responses score higher than low-quality
✅ Cross-channel agreement is < 20 points difference
✅ Overall ikigai score reflects dimension scores

## ⏭️ Next Steps After Testing

Once text-based testing works:

1. **Review the code** in `src/phase2_scoring/` to understand each channel
2. **Customize questions** in `config/ikigai_questions.yaml`
3. **Set up database** using `src/database/schema.sql`
4. **Configure LiveKit** for voice assessment (see QUICKSTART.md)
5. **Deploy with Docker** using `docker-compose.yml`

## 📚 More Information

- **Detailed API**: See QUICKSTART.md
- **Test Documentation**: See tests/README.md
- **Research Methodology**: See the original research document
- **Architecture**: See main README.md

## 💡 Pro Tips

- Start with `high` quality to verify everything works
- Use `low` quality to test edge cases
- Try `interactive` mode to see how your own responses score
- Check `tests/README.md` for more advanced testing options
- Look at the sample responses in `test_text_assessment.py` as templates

---

**Ready to test?**

```bash
cd ikigai-assessment
./run_test.sh
```

That's it! No configuration, no API keys, just works. 🚀

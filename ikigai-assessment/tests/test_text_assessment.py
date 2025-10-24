"""
Text-Based Testing for Ikigai Assessment System

Run assessments using text input instead of voice for development and testing
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
import json
from typing import Dict, List, Any
from datetime import datetime

from src.phase2_scoring.channel1_ctt.classical_scorer import score_session_ctt
from src.phase2_scoring.channel2_irt.irt_scorer import score_session_irt
from src.phase2_scoring.channel3_nlp.nlp_scorer import score_session_nlp
from src.phase2_scoring.channel4_qualitative.framework_scorer import score_session_qualitative
from src.validation.cross_channel_validator import validate_session_scores


class TextBasedAssessment:
    """
    Text-based assessment for testing without LiveKit/voice

    Allows manual text entry or use of pre-written responses
    """

    def __init__(self, questions_path: str = "config/ikigai_questions.yaml"):
        """Initialize with questions configuration"""
        with open(questions_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.questions = self.config['questions']
        self.responses = []

    def run_interactive_assessment(self) -> List[Dict[str, Any]]:
        """
        Run interactive text-based assessment

        User types responses to each question
        """
        print("\n" + "="*80)
        print("IKIGAI ASSESSMENT - TEXT MODE")
        print("="*80)
        print("\nYou'll be asked 20 questions about your ikigai (life purpose).")
        print("Take your time and answer thoughtfully. Type 'skip' to skip a question.\n")

        responses = []

        for i, question in enumerate(self.questions):
            # Skip context/intro questions for text mode
            if question.get('dimension') in ['context', 'action']:
                continue

            print(f"\n{'='*80}")
            print(f"Question {question['number']}/20 - {question.get('dimension', 'general').upper()}")
            print(f"{'='*80}")
            print(f"\n{question['text']}\n")

            response_text = input("Your response: ").strip()

            if response_text.lower() == 'skip':
                response_text = ""

            responses.append({
                'question_number': question['number'],
                'question_text': question['text'],
                'question_dimension': question.get('dimension'),
                'response_text': response_text,
                'timestamp': datetime.now().isoformat()
            })

        self.responses = responses
        return responses

    def load_sample_responses(self, quality: str = 'high') -> List[Dict[str, Any]]:
        """
        Load pre-written sample responses

        Args:
            quality: 'high', 'medium', or 'low' - simulates different response quality

        Returns:
            List of response dictionaries
        """
        sample_responses = self._generate_sample_responses(quality)
        self.responses = sample_responses
        return sample_responses

    def _generate_sample_responses(self, quality: str) -> List[Dict[str, Any]]:
        """Generate sample responses of varying quality"""

        if quality == 'high':
            return self._high_quality_responses()
        elif quality == 'medium':
            return self._medium_quality_responses()
        else:
            return self._low_quality_responses()

    def _high_quality_responses(self) -> List[Dict[str, Any]]:
        """High-quality detailed responses"""
        responses = []

        # What You Love responses (questions 3-6)
        responses.extend([
            {
                'question_number': 3,
                'question_dimension': 'love',
                'response_text': """
                I am absolutely passionate about teaching data science to aspiring analysts.
                There was this moment last year when I was mentoring a student who was
                struggling with understanding machine learning concepts. We spent hours working
                through examples, and I could see the frustration building. Then suddenly,
                everything clicked - I saw it in her eyes, this moment of pure understanding.
                She built her first predictive model that day and was so excited she stayed
                up all night experimenting. Time completely disappeared during those sessions.
                I love seeing people transform from confused to confident, from students to
                practitioners. That feeling of empowering others through knowledge is what
                energizes me most.
                """
            },
            {
                'question_number': 4,
                'question_dimension': 'love',
                'response_text': """
                What makes teaching so satisfying is the direct impact I see. When someone
                learns a new skill from me, it's not just abstract - they take that knowledge
                and build something real with it. I've seen students go from entry-level
                positions to leading analytics teams. That tangible transformation matters
                deeply to me because education was transformative in my own life. I grew up
                in a community with limited opportunities, and a teacher who believed in me
                changed everything. Now I get to pay that forward every single day. The
                importance to me specifically is that I know firsthand how one person's
                investment can unlock someone's entire potential.
                """
            },
            {
                'question_number': 5,
                'question_dimension': 'love',
                'response_text': """
                Great question about the distinction. Teaching definitely energizes me rather
                than relaxes me. After a full day of workshops, I'm buzzing with ideas and
                wanting to do more. It's very different from how I feel after, say, reading
                a novel, which relaxes me. With teaching, I finish and immediately want to
                plan the next session, create new examples, reach more people. It fills me
                up rather than drains me. Even when I'm physically tired, I'm mentally
                energized and excited about the next opportunity.
                """
            },
            {
                'question_number': 6,
                'question_dimension': 'love',
                'response_text': """
                If I had a full week with no constraints, I would create a comprehensive
                free online data science bootcamp. I'd spend mornings designing curriculum
                - building interactive coding exercises, recording video lectures, creating
                real-world projects. Afternoons would be live teaching sessions with students
                from around the world, working through problems together. Evenings I'd spend
                mentoring individuals one-on-one, helping them debug code and think through
                career transitions. I'd also build an open-source library of teaching
                resources so other educators could use and improve upon my materials. Every
                moment would involve teaching, learning, or creating educational content.
                """
            }
        ])

        # What You're Good At responses (questions 7-10)
        responses.extend([
            {
                'question_number': 7,
                'question_dimension': 'good_at',
                'response_text': """
                People regularly come to me for help with complex data visualization and
                storytelling with data. I have a particular talent for taking messy,
                complicated datasets and creating clear, compelling visualizations that
                non-technical stakeholders can understand immediately. Colleagues ask me
                to review their presentations before executive meetings. I've also become
                the go-to person for Python pandas optimization - I can often speed up
                someone's data processing code by 10-100x by restructuring their approach.
                My mentees seek guidance on career development in analytics, especially
                navigating the transition from technical contributor to technical leader.
                """
            },
            {
                'question_number': 8,
                'question_dimension': 'good_at',
                'response_text': """
                When I approach data analysis, I naturally start by questioning the data
                itself rather than jumping into analysis. I've noticed others often take
                data at face value, but I automatically check for biases, missing patterns,
                and data quality issues that could invalidate results. I also think in
                terms of stories and narratives - while others might create technically
                correct charts, I design visualizations that tell a coherent story with
                a clear beginning, middle, and end. I ask "so what?" constantly, pushing
                beyond describing what the data shows to explaining why it matters and
                what actions to take. This comes very naturally to me but I've learned
                it's actually quite rare.
                """
            },
            {
                'question_number': 9,
                'question_dimension': 'good_at',
                'response_text': """
                I'm most proud of building an automated analytics pipeline that reduced
                report generation time from 2 weeks to 2 hours for our finance team. The
                project required combining data from 7 different systems, each with different
                formats and update schedules. I used Python with pandas and SQLAlchemy to
                create a robust ETL process, built validation checks to catch data quality
                issues automatically, and designed interactive Tableau dashboards. The key
                skills were technical proficiency in Python and SQL, but also stakeholder
                management - I spent significant time understanding their actual needs versus
                what they initially requested. My ability to translate business requirements
                into technical solutions and explain technical constraints in business terms
                was crucial to success.
                """
            },
            {
                'question_number': 10,
                'question_dimension': 'good_at',
                'response_text': """
                If I asked three people who know me well, they would probably say I'm
                exceptionally good at making complex things simple, staying calm under
                pressure, and seeing patterns others miss. My manager would mention my
                ability to mentor junior team members effectively - apparently I have a
                gift for meeting people where they are and explaining concepts at exactly
                the right level. My best friend would say I'm great at asking questions
                that help people think through their own problems. My previous colleague
                would mention my talent for writing clear documentation - I actually enjoy
                documenting processes, which apparently makes me weird in a good way.
                """
            }
        ])

        # What World Needs responses (questions 11-14)
        responses.extend([
            {
                'question_number': 11,
                'question_dimension': 'world_needs',
                'response_text': """
                The problem that genuinely frustrates me is the massive gap in data literacy
                and analytical skills, especially in underserved communities. We live in a
                data-driven world where employers desperately need analysts, data scientists,
                and technical talent, yet millions of capable people are locked out because
                they don't have access to quality education in these skills. If this were
                solved, we'd see economic opportunity spread much more equitably. People in
                rural areas, career changers, and those without traditional four-year degrees
                could access high-paying, fulfilling careers in technology. Companies would
                have the talent they need. We'd have more diverse perspectives in tech,
                leading to better products and solutions. The economic impact alone would be
                transformative for individuals and communities.
                """
            },
            {
                'question_number': 12,
                'question_dimension': 'world_needs',
                'response_text': """
                This problem persists because of several interconnected factors. First,
                quality education is expensive and gatekept by credentials - bootcamps cost
                $15,000+, universities require degrees. Second, there's a knowledge gap about
                what's actually required - many people think they need a PhD in statistics
                when really they need practical Python skills and business acumen. Third,
                existing educational content is often created by academics or engineers who
                are brilliant but not necessarily great teachers. Finally, there's a network
                effect - people without connections in tech don't know how to break in even
                if they develop skills. The root cause is that we've made technical education
                artificially scarce and failed to create accessible, practical pathways for
                non-traditional learners.
                """
            },
            {
                'question_number': 13,
                'question_dimension': 'world_needs',
                'response_text': """
                Yes, feeling disconnected from impact definitely resonates. In my previous
                corporate role, I'd spend months building models and reports that would sit
                in a folder somewhere, and I had no idea if they actually helped anyone make
                better decisions. When I imagine making a meaningful contribution, it looks
                like creating a free, comprehensive data science program that specifically
                targets people from non-traditional backgrounds - career changers, people
                without degrees, folks in rural communities, working parents who need
                flexible learning. I want to help 10,000 people transition into data careers
                over the next 5 years. The specific communities would be people in
                Appalachia where I grew up, single parents (especially mothers) trying to
                increase their earning potential, and formerly incarcerated individuals who
                need a real path to stable employment.
                """
            },
            {
                'question_number': 14,
                'question_dimension': 'world_needs',
                'response_text': """
                If I could dedicate my life to one human need, it would be democratizing
                access to technical education and economic opportunity through data skills.
                This calls to me because I've lived both sides - I experienced what it's
                like to have limited opportunities and no clear path forward, and I've
                experienced how transformative the right education can be. There's something
                deeply meaningful about helping people gain agency over their economic
                futures. Data skills specifically are powerful because they're in high
                demand, can be learned without expensive degrees, and immediately translate
                to higher income. Education chose me as much as I chose it - I can't ignore
                the need when I have both the skills to help and the lived experience to do
                it effectively.
                """
            }
        ])

        # What You Can Be Paid For responses (questions 15-17)
        responses.extend([
            {
                'question_number': 15,
                'question_dimension': 'paid_for',
                'response_text': """
                I've done extensive research into the education technology market. Data
                science instructors with real-world industry experience typically earn
                $80,000-$150,000 depending on whether they're employed by bootcamps,
                universities, or online platforms. Senior curriculum developers at companies
                like Coursera or DataCamp earn $120,000-$180,000. Independent course creators
                on platforms like Udemy can earn anywhere from $30,000 to $500,000+ annually,
                though the median is around $50,000. Corporate training consultants who teach
                data science to enterprise clients bill $200-$400 per hour. Employers
                generally want 5+ years of industry experience, a track record of teaching
                or content creation, and strong communication skills. Technical credentials
                matter less than proven ability to teach effectively and industry credibility.
                """
            },
            {
                'question_number': 16,
                'question_dimension': 'paid_for',
                'response_text': """
                I've researched this extensively. The online learning market is growing at
                20% annually and is projected to reach $375 billion by 2026. Data science
                specifically is one of the hottest areas - LinkedIn's 2023 Jobs Report shows
                data scientist roles growing 35% year-over-year with chronic talent shortages.
                I've analyzed job postings on Indeed and see 15,000+ open data analyst
                positions in the US alone. On the education side, I've looked at Udemy's
                marketplace data showing top data science courses with 100,000+ enrollments
                at $50-200 per student. I've talked to 10+ people who successfully
                transitioned from corporate data roles to education/content creation, and
                tracked enrollment trends showing sustained 25%+ growth in data bootcamps
                despite economic uncertainty. The demand is absolutely there.
                """
            },
            {
                'question_number': 17,
                'question_dimension': 'paid_for',
                'response_text': """
                This is something I've thought about deeply. My baseline for economic security
                is $80,000 annually - enough to cover my living expenses, save adequately for
                retirement, and have emergency reserves. I'd be willing to earn less than my
                current corporate salary ($135,000) if the work is meaningful and sustainable.
                What I'm not willing to trade is long-term financial stability - I won't take
                poverty wages just because work is meaningful. My approach is to build
                multiple income streams: teaching for established platforms (stable base),
                creating my own courses (scalable income), corporate training consulting
                (high hourly rate), and eventually building a sustainable education company.
                I'm willing to take a 20-30% pay cut initially to transition, but I expect
                to match or exceed my current income within 3-5 years by building assets
                rather than just trading time for money.
                """
            }
        ])

        return responses

    def _medium_quality_responses(self) -> List[Dict[str, Any]]:
        """Medium-quality responses with some detail"""
        return [
            {
                'question_number': 3,
                'question_dimension': 'love',
                'response_text': "I really enjoy working with data and helping people solve problems. I like when I can create visualizations that make complex information easy to understand."
            },
            {
                'question_number': 4,
                'question_dimension': 'love',
                'response_text': "It's satisfying because I get to use my analytical skills and I like helping others. It feels good when my work makes a difference."
            },
            {
                'question_number': 7,
                'question_dimension': 'good_at',
                'response_text': "I'm good at Python programming and creating charts. People ask me for help with data analysis sometimes."
            },
            {
                'question_number': 11,
                'question_dimension': 'world_needs',
                'response_text': "I think there's a big need for better data education. A lot of people don't have access to learning these skills."
            },
            {
                'question_number': 15,
                'question_dimension': 'paid_for',
                'response_text': "Data scientists make around $100,000-120,000 from what I've seen on job sites. You usually need some experience and technical skills."
            }
        ]

    def _low_quality_responses(self) -> List[Dict[str, Any]]:
        """Low-quality brief responses"""
        return [
            {
                'question_number': 3,
                'question_dimension': 'love',
                'response_text': "I like data"
            },
            {
                'question_number': 4,
                'question_dimension': 'love',
                'response_text': "It's interesting"
            },
            {
                'question_number': 7,
                'question_dimension': 'good_at',
                'response_text': "Programming"
            },
            {
                'question_number': 11,
                'question_dimension': 'world_needs',
                'response_text': "Education needs improvement"
            },
            {
                'question_number': 15,
                'question_dimension': 'paid_for',
                'response_text': "Not sure"
            }
        ]

    def get_full_transcript(self) -> str:
        """Generate full transcript from responses"""
        transcript_parts = []
        for response in self.responses:
            transcript_parts.append(f"Q: {response['question_text']}")
            transcript_parts.append(f"A: {response['response_text']}")

        return "\n\n".join(transcript_parts)


def run_complete_test(quality: str = 'high', verbose: bool = True):
    """
    Run complete text-based test of all scoring channels

    Args:
        quality: 'high', 'medium', or 'low'
        verbose: Print detailed output

    Returns:
        Complete results dictionary
    """
    print("\n" + "="*80)
    print("IKIGAI ASSESSMENT - COMPLETE TEST")
    print("="*80)

    # Create assessment and load sample responses
    assessment = TextBasedAssessment()
    responses = assessment.load_sample_responses(quality=quality)
    transcript = assessment.get_full_transcript()

    if verbose:
        print(f"\nLoaded {quality}-quality sample responses")
        print(f"Total responses: {len(responses)}")
        print(f"Transcript length: {len(transcript)} characters\n")

    # Run all four scoring channels
    print("\n" + "-"*80)
    print("SCORING WITH ALL FOUR CHANNELS")
    print("-"*80)

    results = {}

    # Channel 1: Classical Test Theory
    print("\n[1/4] Running Channel 1: Classical Test Theory...")
    try:
        ctt_results = score_session_ctt(responses)
        results['ctt'] = ctt_results
        if verbose:
            print("✓ CTT scoring complete")
            print(f"    Dimension scores: {ctt_results['dimension_scores']}")
    except Exception as e:
        print(f"✗ CTT scoring failed: {e}")
        results['ctt'] = {'error': str(e)}

    # Channel 2: Item Response Theory
    print("\n[2/4] Running Channel 2: Item Response Theory...")
    try:
        irt_results = score_session_irt(responses)
        results['irt'] = irt_results
        if verbose:
            print("✓ IRT scoring complete")
            print(f"    Dimension scores: {irt_results['dimension_scores']}")
    except Exception as e:
        print(f"✗ IRT scoring failed: {e}")
        results['irt'] = {'error': str(e)}

    # Channel 3: NLP/ML
    print("\n[3/4] Running Channel 3: NLP & Machine Learning...")
    try:
        nlp_results = score_session_nlp(responses)
        results['nlp'] = nlp_results
        if verbose:
            print("✓ NLP scoring complete")
            print(f"    Dimension scores: {nlp_results['dimension_scores']}")
    except Exception as e:
        print(f"✗ NLP scoring failed: {e}")
        results['nlp'] = {'error': str(e)}

    # Channel 4: Qualitative
    print("\n[4/4] Running Channel 4: Qualitative Framework Method...")
    try:
        qual_results = score_session_qualitative(responses, transcript)
        results['qual'] = qual_results
        if verbose:
            print("✓ Qualitative scoring complete")
            print(f"    Dimension scores: {qual_results['dimension_scores']}")
    except Exception as e:
        print(f"✗ Qualitative scoring failed: {e}")
        results['qual'] = {'error': str(e)}

    # Cross-channel validation
    print("\n" + "-"*80)
    print("CROSS-CHANNEL VALIDATION")
    print("-"*80)

    try:
        validation = validate_session_scores(results)
        results['validation'] = validation

        if verbose:
            print(f"\nChannels compared: {validation['channels_compared']}")
            print(f"Average absolute difference: {validation['average_absolute_difference']:.2f}")
            print(f"Max difference: {validation['max_difference']:.2f}")
            print(f"Min difference: {validation['min_difference']:.2f}")
    except Exception as e:
        print(f"Validation failed: {e}")
        results['validation'] = {'error': str(e)}

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    # Extract normalized scores
    summary = {}
    for channel_id, channel_results in results.items():
        if channel_id == 'validation' or 'error' in channel_results:
            continue

        summary[channel_id] = {}
        for dim, score_data in channel_results.get('dimension_scores', {}).items():
            if isinstance(score_data, dict):
                summary[channel_id][dim] = score_data.get('normalized_score', 0)
            else:
                summary[channel_id][dim] = score_data

    # Print comparison table
    print("\nDimension Scores Across All Channels (0-100 scale):\n")
    print(f"{'Dimension':<15} {'CTT':<10} {'IRT':<10} {'NLP':<10} {'Qual':<10} {'Avg':<10}")
    print("-" * 70)

    for dim in ['love', 'good_at', 'world_needs', 'paid_for']:
        scores = []
        row = f"{dim:<15}"

        for ch in ['ctt', 'irt', 'nlp', 'qual']:
            score = summary.get(ch, {}).get(dim, 0)
            scores.append(score)
            row += f"{score:<10.1f}"

        avg = sum(scores) / len(scores) if scores else 0
        row += f"{avg:<10.1f}"
        print(row)

    # Calculate overall ikigai
    print("\nOverall Ikigai Scores:\n")
    for ch_id, ch_data in results.items():
        if ch_id == 'validation' or 'error' in ch_data:
            continue

        overall = ch_data.get('overall_alignment', {}).get('overall_ikigai_score', 0)
        print(f"  {ch_id.upper():<6}: {overall:.1f}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test Ikigai Assessment System')
    parser.add_argument(
        '--mode',
        choices=['interactive', 'sample'],
        default='sample',
        help='Interactive text entry or use sample responses'
    )
    parser.add_argument(
        '--quality',
        choices=['high', 'medium', 'low'],
        default='high',
        help='Quality of sample responses'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Save results to JSON file'
    )

    args = parser.parse_args()

    if args.mode == 'interactive':
        assessment = TextBasedAssessment()
        responses = assessment.run_interactive_assessment()
        # Score the responses
        # (implementation similar to run_complete_test)
    else:
        results = run_complete_test(quality=args.quality, verbose=True)

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nResults saved to: {args.output}")

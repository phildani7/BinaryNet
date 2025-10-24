#!/usr/bin/env python3
"""
Quick Test Script for Ikigai Assessment

Run this to quickly test the system without any API keys or external dependencies
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from tests.test_text_assessment import run_complete_test


def main():
    """Run quick test"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║               IKIGAI ASSESSMENT SYSTEM - QUICK TEST                    ║
║                                                                        ║
║  This will test all 4 scoring channels using sample text responses    ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
    """)

    print("\nChoose test quality:")
    print("  1. High quality (detailed, thoughtful responses)")
    print("  2. Medium quality (moderate detail)")
    print("  3. Low quality (brief responses)")
    print()

    choice = input("Enter choice (1-3) [default: 1]: ").strip() or "1"

    quality_map = {
        '1': 'high',
        '2': 'medium',
        '3': 'low'
    }

    quality = quality_map.get(choice, 'high')

    # Run the test
    results = run_complete_test(quality=quality, verbose=True)

    print("\n" + "="*80)
    print("TEST COMPLETE!")
    print("="*80)

    print("\nWhat worked:")
    for channel_id, channel_data in results.items():
        if channel_id == 'validation':
            continue
        if 'error' not in channel_data:
            print(f"  ✓ {channel_id.upper()} channel")
        else:
            print(f"  ✗ {channel_id.upper()} channel (error: {channel_data['error']})")

    print("\nNext steps:")
    print("  1. Review the scores above to see how each channel performed")
    print("  2. Try different quality levels (high/medium/low)")
    print("  3. Run interactive mode: python tests/test_text_assessment.py --mode interactive")
    print("  4. Check individual channel implementations in src/phase2_scoring/")
    print()

    return results


if __name__ == "__main__":
    main()

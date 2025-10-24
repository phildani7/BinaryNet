#!/bin/bash

# Simple test runner for Ikigai Assessment System
# No API keys or external services required!

set -e

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                        ║"
echo "║           IKIGAI ASSESSMENT SYSTEM - TEXT-BASED TEST                   ║"
echo "║                                                                        ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "quick_test.py" ]; then
    echo "Error: Please run this script from the ikigai-assessment directory"
    echo "  cd ikigai-assessment && ./run_test.sh"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    exit 1
fi

echo "✓ Found Python 3"
echo ""

# Check dependencies
echo "Checking dependencies..."
python3 -c "import numpy, pandas, scipy, yaml" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Core dependencies installed"
else
    echo "⚠ Missing dependencies. Installing..."
    pip3 install numpy pandas scipy pyyaml
fi

echo ""
echo "Starting test..."
echo ""

# Run the test
python3 quick_test.py

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                         TEST COMPLETE!                                 ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  • Try different quality levels (edit quick_test.py)"
echo "  • Run interactive mode: python tests/test_text_assessment.py --mode interactive"
echo "  • Run unit tests: python tests/test_channels.py"
echo "  • Read tests/README.md for more options"
echo ""

# Accuracy Evaluation System - Summary

## Overview

A comprehensive accuracy evaluation system has been created to measure and report on the performance of the Baseera AI RAG system. This system is designed to generate presentation-ready reports for stakeholders.

## What Was Created

### 1. **`evaluate_accuracy.py`** - Main Evaluation Script
   - Runs all test cases from `test_parameters.json`
   - Evaluates responses against ground truth data
   - Calculates accuracy scores using weighted metrics
   - Generates multiple output formats (JSON, CSV, HTML)

### 2. **`EVALUATION_GUIDE.md`** - User Documentation
   - Complete guide on how to use the evaluation system
   - Explanation of metrics and scoring
   - Troubleshooting tips
   - Presentation recommendations

## Key Features

### Evaluation Metrics

The system evaluates responses based on:

1. **Primary Failure Mode Identification (40%)**
   - Checks if the system correctly identifies the expected failure mechanism
   - Example: "Stress Corrosion Cracking" for SCC cases

2. **Keyword Relevance (30%)**
   - Matches technical keywords from ground truth
   - Measures how well the response covers expected topics

3. **Metal Type Mention (10%)**
   - Verifies the response mentions the correct material

4. **Source Sufficiency (10%)**
   - Checks if enough relevant sources were retrieved

5. **Root Cause Analysis (5%)**
   - Verifies presence of root cause discussion

6. **Recommendations (5%)**
   - Checks for actionable recommendations

### Output Formats

1. **JSON Report** - Complete data for programmatic analysis
2. **CSV Report** - Spreadsheet-compatible for data analysis
3. **HTML Report** - Presentation-ready with:
   - Visual metric cards
   - Color-coded results
   - Professional styling
   - Executive summary

## How to Use

### Basic Usage

```bash
# Make sure Django server is running
python manage.py runserver

# Run full evaluation
python evaluate_accuracy.py

# Quick test (first 5 cases only)
python evaluate_accuracy.py --quick
```

### Output Location

All reports are saved in: `evaluation_results/`

Files are timestamped for easy tracking:
- `evaluation_20241115_143022.json`
- `evaluation_20241115_143022.csv`
- `evaluation_report_20241115_143022.html`

## Ground Truth Data

The evaluation uses predefined ground truth for 15 test cases covering:
- Stress Corrosion Cracking
- Fatigue Failure
- High-Temperature Creep
- Pitting Corrosion
- Hydrogen Embrittlement
- Erosive Wear
- Intergranular Corrosion
- Thermal Fatigue
- Galvanic Corrosion
- Brittle Fracture
- Fretting Wear
- Stress-Corrosion Cracking (Chloride)
- Liquid Droplet Impingement Erosion
- Oxidation at High Temperature
- Limited Context Test

Each test case has:
- Expected primary failure mode
- Relevant keywords
- Expected metal types
- Minimum required sources

## Example Results

The evaluation generates a summary like:

```
============================================================
EVALUATION SUMMARY
============================================================
Total Tests: 15
Successful: 15
Failed: 0

📊 Accuracy Metrics:
  Average Accuracy: 76.3%
  Primary Mode Identification: 86.7%
  Average Sources Found: 3.2
  Average Response Time: 2150.5ms

⏱️  Total Evaluation Time: 32.3s
```

## Presentation Use Cases

### For Stakeholders
- Use the HTML report directly in presentations
- Highlight average accuracy and success rate
- Show specific test case examples

### For Development Team
- Use CSV/JSON for detailed analysis
- Identify low-performing test cases
- Track improvements over time

### For Management
- Executive summary metrics
- System reliability indicators
- Performance benchmarks

## Customization

The evaluation can be customized by:

1. **Modifying Ground Truth**: Edit `GROUND_TRUTH` dictionary in `evaluate_accuracy.py`
2. **Adjusting Scoring Weights**: Modify weights in `evaluate_response()` function
3. **Adding Test Cases**: Add to `test_parameters.json`

## Next Steps

1. **Run Initial Evaluation**: Get baseline metrics
   ```bash
   python evaluate_accuracy.py
   ```

2. **Review Results**: Check HTML report for presentation
   - Open `evaluation_results/evaluation_report_[timestamp].html`

3. **Identify Improvements**: Review low-scoring test cases

4. **Iterate**: Make improvements and re-run evaluation

5. **Track Progress**: Compare results over time

## Technical Details

### Dependencies
- Uses existing `test_parameters.json` for test cases
- Connects to Django API at `http://localhost:8000`
- Requires Django server to be running

### Performance
- Typical evaluation time: 30-60 seconds for 15 test cases
- Each test case takes ~2-3 seconds (API call + evaluation)
- Can run in quick mode for faster testing

### Error Handling
- Gracefully handles API errors
- Continues evaluation even if some tests fail
- Reports errors in output files

## Files Created

1. `evaluate_accuracy.py` - Main evaluation script (500+ lines)
2. `EVALUATION_GUIDE.md` - User documentation
3. `ACCURACY_EVALUATION_SUMMARY.md` - This summary file

## Integration

The evaluation system integrates seamlessly with:
- Existing `test_api.py` infrastructure
- `test_parameters.json` test cases
- Django API endpoints
- RAG service for knowledge base queries

## Support

For questions or issues:
1. Check `EVALUATION_GUIDE.md` for detailed documentation
2. Review error messages in console output
3. Check that Django server is running
4. Verify knowledge base is populated

---

**Ready to use!** Run `python evaluate_accuracy.py` to start evaluating your system's accuracy.


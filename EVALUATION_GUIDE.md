# Accuracy Evaluation Guide

This guide explains how to evaluate the accuracy of the Baseera AI RAG system for presentations and reports.

## Quick Start

1. **Make sure the Django server is running:**
   ```bash
   python manage.py runserver
   ```

2. **Run the evaluation:**
   ```bash
   python evaluate_accuracy.py
   ```

3. **View the results:**
   - Check the console output for summary
   - Open `evaluation_results/evaluation_report_[timestamp].html` for presentation-ready report
   - Check `evaluation_results/evaluation_[timestamp].csv` for spreadsheet analysis

## Evaluation Metrics

The evaluation script measures:

### 1. **Accuracy Score (0-100%)**
   - **40%** - Primary failure mode identification
   - **30%** - Keyword relevance matching
   - **10%** - Metal type mention
   - **10%** - Sufficient sources retrieved
   - **5%** - Root cause analysis present
   - **5%** - Recommendations provided

### 2. **Primary Failure Mode Identification**
   - Checks if the response correctly identifies the expected failure mechanism
   - Example: "Stress Corrosion Cracking" for SCC test cases

### 3. **Source Relevance**
   - Number of relevant documents retrieved from knowledge base
   - Minimum expected sources per test case

### 4. **Response Quality**
   - Response length and completeness
   - Presence of root cause analysis
   - Presence of actionable recommendations

## Command Line Options

```bash
# Run all test cases (default)
python evaluate_accuracy.py

# Quick mode - run only first 5 test cases
python evaluate_accuracy.py --quick

# Generate only JSON report
python evaluate_accuracy.py --output json

# Generate only HTML report
python evaluate_accuracy.py --output html

# Generate all formats (default)
python evaluate_accuracy.py --output all
```

## Output Files

All results are saved in the `evaluation_results/` directory:

1. **`evaluation_[timestamp].json`** - Complete results in JSON format
2. **`evaluation_[timestamp].csv`** - Spreadsheet-compatible data
3. **`evaluation_report_[timestamp].html`** - Presentation-ready HTML report

## Understanding the Results

### Accuracy Score Interpretation

- **70-100%**: Excellent - System correctly identified failure mode and provided comprehensive analysis
- **50-69%**: Good - System identified key aspects but may have missed some details
- **0-49%**: Needs Improvement - System struggled with this test case

### Key Metrics for Presentations

1. **Average Accuracy**: Overall system performance
2. **Primary Mode Identification Rate**: How often the system correctly identifies the failure mechanism
3. **Average Sources Found**: Knowledge base retrieval effectiveness
4. **Response Time**: System performance

## Example Output

```
🔍 Running evaluation on 15 test cases...

[1/15] Testing: Stress Corrosion Cracking (SCC)
  ✅ Accuracy: 85.0% | Sources: 4 | Time: 2340ms
[2/15] Testing: Fatigue Failure
  ✅ Accuracy: 78.5% | Sources: 3 | Time: 2100ms
...

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

## Ground Truth Data

The evaluation uses predefined ground truth for each test case:
- Expected primary failure mode
- Relevant keywords
- Expected metal types
- Minimum required sources

This data is defined in the `GROUND_TRUTH` dictionary in `evaluate_accuracy.py`.

## Customizing Evaluation

To modify evaluation criteria:

1. **Update Ground Truth**: Edit the `GROUND_TRUTH` dictionary in `evaluate_accuracy.py`
2. **Adjust Scoring Weights**: Modify the `evaluate_response()` function
3. **Add New Test Cases**: Add to `test_parameters.json`

## Troubleshooting

### Connection Error
- Make sure Django server is running on `http://localhost:8000`
- Check if the server is accessible

### Low Accuracy Scores
- Verify knowledge base is populated with documents
- Check if test cases match available knowledge base content
- Review retrieved sources in the API responses

### Missing Sources
- Ensure documents have been ingested: `python manage.py ingest_documents`
- Check ChromaDB collection has data
- Verify RAG service is working correctly

## Presentation Tips

1. **Use the HTML Report**: The generated HTML report is presentation-ready with:
   - Visual metric cards
   - Color-coded results
   - Professional styling

2. **Highlight Key Metrics**:
   - Average accuracy score
   - Primary mode identification rate
   - System reliability (success rate)

3. **Show Examples**: Include specific test case results to demonstrate system capabilities

4. **Compare Scenarios**: Run evaluations before/after improvements to show progress

## Next Steps

After evaluation:
1. Review low-scoring test cases
2. Identify areas for improvement
3. Update knowledge base if needed
4. Refine RAG search parameters
5. Re-run evaluation to measure improvements


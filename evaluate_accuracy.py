"""Accuracy evaluation script."""

import requests
import json
import sys
import base64
import mimetypes
import time
import csv
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import re
import argparse

BASE_URL = "http://localhost:8000"

GROUND_TRUTH = {
    "Stress Corrosion Cracking (SCC)": {
        "primary_failure_mode": ["stress corrosion cracking", "SCC", "stress-corrosion"],
        "keywords": ["chloride", "intergranular", "weld", "residual stress", "cracking"],
        "metal_expected": ["stainless steel", "316L"],
        "min_sources": 2
    },
    "Fatigue Failure": {
        "primary_failure_mode": ["fatigue", "cyclic", "beach marks"],
        "keywords": ["cyclic loading", "vibration", "stress concentration", "beach marks", "fracture"],
        "metal_expected": ["carbon steel", "A36"],
        "min_sources": 2
    },
    "High-Temperature Creep": {
        "primary_failure_mode": ["creep", "high-temperature"],
        "keywords": ["creep", "deformation", "grain boundary", "elevated temperature", "800", "900"],
        "metal_expected": ["Inconel", "625"],
        "min_sources": 2
    },
    "Pitting Corrosion": {
        "primary_failure_mode": ["pitting", "pitting corrosion"],
        "keywords": ["pitting", "localized", "chloride", "pit", "corrosion"],
        "metal_expected": ["stainless steel", "304"],
        "min_sources": 2
    },
    "Hydrogen Embrittlement": {
        "primary_failure_mode": ["hydrogen embrittlement", "hydrogen damage"],
        "keywords": ["hydrogen", "embrittlement", "brittle", "delayed failure", "sour gas"],
        "metal_expected": ["high-strength", "4340"],
        "min_sources": 2
    },
    "Erosive Wear": {
        "primary_failure_mode": ["erosion", "erosive wear"],
        "keywords": ["erosion", "wear", "abrasive", "particle", "material loss"],
        "metal_expected": ["carbon steel"],
        "min_sources": 1
    },
    "Intergranular Corrosion": {
        "primary_failure_mode": ["intergranular corrosion", "grain boundary"],
        "keywords": ["intergranular", "grain boundary", "sensitization", "weld"],
        "metal_expected": ["stainless steel", "304"],
        "min_sources": 2
    },
    "Thermal Fatigue": {
        "primary_failure_mode": ["thermal fatigue", "thermal cycling"],
        "keywords": ["thermal", "cycling", "fatigue", "heating", "cooling", "expansion"],
        "metal_expected": ["cast iron"],
        "min_sources": 2
    },
    "Galvanic Corrosion": {
        "primary_failure_mode": ["galvanic corrosion", "dissimilar metals"],
        "keywords": ["galvanic", "dissimilar", "aluminum", "contact", "corrosion"],
        "metal_expected": ["aluminum", "6061"],
        "min_sources": 2
    },
    "Brittle Fracture": {
        "primary_failure_mode": ["brittle fracture", "cleavage"],
        "keywords": ["brittle", "fracture", "cleavage", "low temperature", "no plastic deformation"],
        "metal_expected": ["carbon steel"],
        "min_sources": 2
    },
    "Fretting Wear": {
        "primary_failure_mode": ["fretting", "fretting wear"],
        "keywords": ["fretting", "oscillatory", "vibration", "contact", "wear"],
        "metal_expected": ["stainless steel", "316"],
        "min_sources": 1
    },
    "Stress-Corrosion Cracking (Chloride)": {
        "primary_failure_mode": ["stress corrosion cracking", "SCC", "transgranular"],
        "keywords": ["stress corrosion", "chloride", "duplex", "transgranular", "cracking"],
        "metal_expected": ["duplex", "2205"],
        "min_sources": 2
    },
    "Liquid Droplet Impingement Erosion": {
        "primary_failure_mode": ["liquid droplet erosion", "impingement"],
        "keywords": ["droplet", "impingement", "erosion", "titanium", "steam"],
        "metal_expected": ["titanium"],
        "min_sources": 1
    },
    "Oxidation at High Temperature": {
        "primary_failure_mode": ["oxidation", "high-temperature oxidation"],
        "keywords": ["oxidation", "oxide scale", "spallation", "high temperature", "superalloy"],
        "metal_expected": ["nickel", "superalloy"],
        "min_sources": 2
    },
    "Limited Context Test": {
        "primary_failure_mode": [],  # No specific failure mode expected
        "keywords": [],  # Should still provide analysis
        "metal_expected": [],
        "min_sources": 0  # May have no sources
    }
}


def encode_image_to_base64(image_path):
    """Encode an image file to base64 format for API."""
    image_path = Path(image_path)
    if not image_path.exists():
        return None
    
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            mime_type, _ = mimetypes.guess_type(str(image_path))
            if not mime_type:
                mime_type = 'image/jpeg'
            return {
                'data': base64_data,
                'mimeType': mime_type,
                'name': image_path.name
            }
    except Exception as e:
        print(f"⚠️  Warning: Failed to encode image {image_path}: {e}")
        return None


def prepare_test_params(case_params, base_dir=None):
    """Prepare test parameters, including encoding photos if present."""
    if base_dir is None:
        base_dir = Path(__file__).parent
    
    params = case_params.copy()
    
    if 'photos' in params:
        photo_paths = params['photos']
        if not isinstance(photo_paths, list):
            photo_paths = [photo_paths]
        
        encoded_photos = []
        for photo_path in photo_paths:
            if not Path(photo_path).is_absolute():
                photo_path = base_dir / photo_path
            encoded_photo = encode_image_to_base64(photo_path)
            if encoded_photo:
                encoded_photos.append(encoded_photo)
        
        if encoded_photos:
            params['photos'] = encoded_photos
        else:
            params.pop('photos', None)
    else:
        params.pop('photos', None)
    
    return params


def test_api(test_params, test_name="Test", base_dir=None):
    """Test the chat API and return full response data."""
    url = f"{BASE_URL}/api/chat"
    prepared_params = prepare_test_params(test_params, base_dir)
    
    try:
        start_time = time.time()
        response = requests.post(
            url,
            json=prepared_params,
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        response_time = (time.time() - start_time) * 1000  # ms
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'response': data.get('response', ''),
                'context_used': data.get('context_used', False),
                'num_sources': data.get('num_sources', 0),
                'response_time_ms': int(response_time),
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'context_used': False,
                'num_sources': 0,
                'response_time_ms': int(response_time),
                'error': f"HTTP {response.status_code}: {response.text[:200]}"
            }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'response': '',
            'context_used': False,
            'num_sources': 0,
            'response_time_ms': 0,
            'error': f"Connection Error: Could not connect to {BASE_URL}"
        }
    except Exception as e:
        return {
            'success': False,
            'response': '',
            'context_used': False,
            'num_sources': 0,
            'response_time_ms': 0,
            'error': str(e)
        }


def evaluate_response(test_name: str, response_text: str, num_sources: int, ground_truth: Dict) -> Dict:
    """Evaluate a single response against ground truth."""
    response_lower = response_text.lower()
    
    # Check primary failure mode identification
    primary_mode_found = False
    if ground_truth.get("primary_failure_mode"):
        for mode in ground_truth["primary_failure_mode"]:
            if mode.lower() in response_lower:
                primary_mode_found = True
                break
    
    # Count keyword matches
    keyword_matches = 0
    total_keywords = len(ground_truth.get("keywords", []))
    for keyword in ground_truth.get("keywords", []):
        if keyword.lower() in response_lower:
            keyword_matches += 1
    
    keyword_score = (keyword_matches / total_keywords * 100) if total_keywords > 0 else 0
    
    # Check metal type mention
    metal_mentioned = False
    if ground_truth.get("metal_expected"):
        for metal in ground_truth["metal_expected"]:
            if metal.lower() in response_lower:
                metal_mentioned = True
                break
    
    # Source relevance check
    sources_sufficient = num_sources >= ground_truth.get("min_sources", 0)
    
    # Response quality metrics
    response_length = len(response_text)
    has_recommendations = any(word in response_lower for word in ["recommend", "suggest", "should", "prevent", "mitigate"])
    has_root_cause = any(word in response_lower for word in ["root cause", "caused by", "due to", "result of", "attributed to"])
    has_analysis = any(word in response_lower for word in ["analysis", "examination", "investigation", "evaluation"])
    
    # Calculate overall accuracy score (weighted)
    accuracy_score = 0
    if primary_mode_found:
        accuracy_score += 40  # 40% for correct failure mode
    accuracy_score += keyword_score * 0.3  # 30% for keyword relevance
    if metal_mentioned:
        accuracy_score += 10  # 10% for metal type
    if sources_sufficient:
        accuracy_score += 10  # 10% for sufficient sources
    if has_root_cause:
        accuracy_score += 5  # 5% for root cause analysis
    if has_recommendations:
        accuracy_score += 5  # 5% for recommendations
    
    return {
        'primary_mode_identified': primary_mode_found,
        'keyword_matches': keyword_matches,
        'total_keywords': total_keywords,
        'keyword_score': round(keyword_score, 1),
        'metal_mentioned': metal_mentioned,
        'sources_sufficient': sources_sufficient,
        'response_length': response_length,
        'has_recommendations': has_recommendations,
        'has_root_cause': has_root_cause,
        'has_analysis': has_analysis,
        'accuracy_score': round(accuracy_score, 1)
    }


def run_evaluation(quick_mode=False, output_format='json'):
    """Run full evaluation on all test cases."""
    base_dir = Path(__file__).parent
    test_file = base_dir / "test_parameters.json"
    
    if not test_file.exists():
        print("❌ Could not find test_parameters.json")
        return
    
    with open(test_file, 'r') as f:
        test_cases_data = json.load(f)
    
    test_cases = test_cases_data.get('test_cases', [])
    
    if quick_mode:
        test_cases = test_cases[:5]
        print(f"🔍 Quick mode: Running first 5 test cases...\n")
    else:
        print(f"🔍 Running evaluation on {len(test_cases)} test cases...\n")
    
    results = []
    total_start_time = time.time()
    
    for i, case in enumerate(test_cases, 1):
        test_name = case['name']
        print(f"[{i}/{len(test_cases)}] Testing: {test_name}")
        
        # Get ground truth
        ground_truth = GROUND_TRUTH.get(test_name, {
            "primary_failure_mode": [],
            "keywords": [],
            "metal_expected": [],
            "min_sources": 0
        })
        
        # Run test
        api_result = test_api(case['parameters'], test_name, base_dir)
        
        if not api_result['success']:
            print(f"  ❌ API Error: {api_result.get('error', 'Unknown error')}")
            results.append({
                'test_name': test_name,
                'test_number': i,
                'success': False,
                'error': api_result.get('error'),
                'accuracy_score': 0,
                'evaluation': {}
            })
            continue
        
        # Evaluate response
        evaluation = evaluate_response(
            test_name,
            api_result['response'],
            api_result['num_sources'],
            ground_truth
        )
        
        # Combine results
        result = {
            'test_name': test_name,
            'test_number': i,
            'success': True,
            'response_length': evaluation['response_length'],
            'num_sources': api_result['num_sources'],
            'context_used': api_result['context_used'],
            'response_time_ms': api_result['response_time_ms'],
            'primary_mode_identified': evaluation['primary_mode_identified'],
            'keyword_score': evaluation['keyword_score'],
            'metal_mentioned': evaluation['metal_mentioned'],
            'sources_sufficient': evaluation['sources_sufficient'],
            'has_recommendations': evaluation['has_recommendations'],
            'has_root_cause': evaluation['has_root_cause'],
            'accuracy_score': evaluation['accuracy_score'],
            'evaluation': evaluation,
            'response_preview': api_result['response'][:200] + "..." if len(api_result['response']) > 200 else api_result['response']
        }
        
        results.append(result)
        
        # Print summary
        status = "✅" if evaluation['accuracy_score'] >= 70 else "⚠️" if evaluation['accuracy_score'] >= 50 else "❌"
        print(f"  {status} Accuracy: {evaluation['accuracy_score']:.1f}% | Sources: {api_result['num_sources']} | Time: {api_result['response_time_ms']}ms")
        time.sleep(0.5)  # Small delay between requests
    
    total_time = time.time() - total_start_time
    
    # Calculate summary statistics
    successful_tests = [r for r in results if r['success']]
    accuracy_scores = [r['accuracy_score'] for r in successful_tests]
    avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
    avg_sources = sum(r['num_sources'] for r in successful_tests) / len(successful_tests) if successful_tests else 0
    avg_response_time = sum(r['response_time_ms'] for r in successful_tests) / len(successful_tests) if successful_tests else 0
    
    primary_mode_accuracy = sum(1 for r in successful_tests if r['primary_mode_identified']) / len(successful_tests) * 100 if successful_tests else 0
    
    summary = {
        'total_tests': len(test_cases),
        'successful_tests': len(successful_tests),
        'failed_tests': len(results) - len(successful_tests),
        'average_accuracy': round(avg_accuracy, 1),
        'average_sources': round(avg_sources, 1),
        'average_response_time_ms': round(avg_response_time, 1),
        'primary_mode_accuracy': round(primary_mode_accuracy, 1),
        'total_evaluation_time_seconds': round(total_time, 1),
        'timestamp': datetime.now().isoformat()
    }
    
    # Generate reports
    output_dir = base_dir / "evaluation_results"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON report
    json_path = output_dir / f"evaluation_{timestamp}.json"
    with open(json_path, 'w') as f:
        json.dump({
            'summary': summary,
            'results': results
        }, f, indent=2)
    print(f"\n✅ JSON report saved: {json_path}")
    
    # CSV report
    csv_path = output_dir / f"evaluation_{timestamp}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Test Number', 'Test Name', 'Success', 'Accuracy Score (%)',
            'Primary Mode Identified', 'Keyword Score (%)', 'Metal Mentioned',
            'Sources Found', 'Sources Sufficient', 'Response Length',
            'Has Recommendations', 'Has Root Cause', 'Response Time (ms)'
        ])
        for r in results:
            writer.writerow([
                r['test_number'], r['test_name'], r['success'],
                r['accuracy_score'], r['primary_mode_identified'],
                r['keyword_score'], r['metal_mentioned'], r['num_sources'],
                r['sources_sufficient'], r['response_length'],
                r['has_recommendations'], r['has_root_cause'],
                r['response_time_ms']
            ])
    print(f"✅ CSV report saved: {csv_path}")
    
    # HTML report for presentation
    if output_format == 'html' or output_format == 'all':
        html_path = output_dir / f"evaluation_report_{timestamp}.html"
        generate_html_report(summary, results, html_path)
        print(f"✅ HTML report saved: {html_path}")
    
    # Print summary to console
    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"\n📊 Accuracy Metrics:")
    print(f"  Average Accuracy: {summary['average_accuracy']:.1f}%")
    print(f"  Primary Mode Identification: {summary['primary_mode_accuracy']:.1f}%")
    print(f"  Average Sources Found: {summary['average_sources']:.1f}")
    print(f"  Average Response Time: {summary['average_response_time_ms']:.1f}ms")
    print(f"\n⏱️  Total Evaluation Time: {summary['total_evaluation_time_seconds']:.1f}s")
    print(f"\n📁 Reports saved in: {output_dir}")


def generate_html_report(summary, results, output_path):
    """Generate a presentation-ready HTML report."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baseera AI - Accuracy Evaluation Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: white;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .score-high {{
            color: #28a745;
            font-weight: bold;
        }}
        .score-medium {{
            color: #ffc107;
            font-weight: bold;
        }}
        .score-low {{
            color: #dc3545;
            font-weight: bold;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-success {{
            background: #28a745;
            color: white;
        }}
        .badge-warning {{
            background: #ffc107;
            color: #333;
        }}
        .badge-danger {{
            background: #dc3545;
            color: white;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Baseera AI - Accuracy Evaluation Report</h1>
        <p class="subtitle">Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        
        <div class="section">
            <h2 class="section-title">Executive Summary</h2>
            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-value">{summary['average_accuracy']:.1f}%</div>
                    <div class="metric-label">Average Accuracy</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary['primary_mode_accuracy']:.1f}%</div>
                    <div class="metric-label">Failure Mode ID</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary['successful_tests']}/{summary['total_tests']}</div>
                    <div class="metric-label">Tests Passed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary['average_sources']:.1f}</div>
                    <div class="metric-label">Avg Sources</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">Detailed Test Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test #</th>
                        <th>Test Name</th>
                        <th>Accuracy</th>
                        <th>Failure Mode</th>
                        <th>Sources</th>
                        <th>Response Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for result in results:
        if result['success']:
            score_class = 'score-high' if result['accuracy_score'] >= 70 else 'score-medium' if result['accuracy_score'] >= 50 else 'score-low'
            mode_badge = '<span class="badge badge-success">✓</span>' if result['primary_mode_identified'] else '<span class="badge badge-danger">✗</span>'
            status_badge = '<span class="badge badge-success">Pass</span>' if result['accuracy_score'] >= 70 else '<span class="badge badge-warning">Partial</span>' if result['accuracy_score'] >= 50 else '<span class="badge badge-danger">Fail</span>'
            
            html_content += f"""
                    <tr>
                        <td>{result['test_number']}</td>
                        <td>{result['test_name']}</td>
                        <td class="{score_class}">{result['accuracy_score']:.1f}%</td>
                        <td>{mode_badge}</td>
                        <td>{result['num_sources']}</td>
                        <td>{result['response_time_ms']}ms</td>
                        <td>{status_badge}</td>
                    </tr>
"""
        else:
            html_content += f"""
                    <tr>
                        <td>{result['test_number']}</td>
                        <td>{result['test_name']}</td>
                        <td colspan="5" style="color: #dc3545;">Error: {result.get('error', 'Unknown error')}</td>
                    </tr>
"""
    
    html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2 class="section-title">Performance Metrics</h2>
            <div class="chart-container">
                <p><strong>Average Response Time:</strong> {summary['average_response_time_ms']:.1f}ms</p>
                <p><strong>Total Evaluation Time:</strong> {summary['total_evaluation_time_seconds']:.1f} seconds</p>
                <p><strong>Success Rate:</strong> {(summary['successful_tests']/summary['total_tests']*100):.1f}%</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Baseera AI RAG System - Accuracy Evaluation</p>
            <p>Report generated automatically by evaluation script</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate Baseera AI RAG system accuracy')
    parser.add_argument('--quick', action='store_true', help='Run only first 5 test cases')
    parser.add_argument('--output', choices=['json', 'html', 'all'], default='all', help='Output format')
    args = parser.parse_args()
    
    print("🚀 Starting Accuracy Evaluation...")
    print(f"📡 Connecting to: {BASE_URL}")
    print()
    
    try:
        run_evaluation(quick_mode=args.quick, output_format=args.output)
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


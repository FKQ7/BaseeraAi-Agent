"""API test script."""

import requests
import json
import sys
import base64
import mimetypes
from pathlib import Path

BASE_URL = "http://localhost:8000"

def load_test_cases():
    test_file = Path(__file__).parent / "test_parameters.json"
    if test_file.exists():
        with open(test_file, 'r') as f:
            return json.load(f)
    return None

def encode_image_to_base64(image_path):
    """Encode image to base64."""
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"⚠️  Warning: Image file not found: {image_path}")
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
    """Prepare test parameters."""
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
            print(f"  📷 Photos: {len(encoded_photos)} image(s) attached")
        else:
            params.pop('photos', None)
    else:
        params.pop('photos', None)
    
    return params

def test_api(test_params, test_name="Test", base_dir=None):
    """Test the chat API."""
    url = f"{BASE_URL}/api/chat"
    
    prepared_params = prepare_test_params(test_params, base_dir)
    
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"{'='*60}")
    print(f"\nParameters:")
    for key, value in prepared_params.items():
        if key == 'photos':
            print(f"  {key}: {len(value)} image(s) [base64 encoded]")
        else:
            print(f"  {key}: {value}")
    
    print(f"\nSending request to {url}...")
    
    try:
        response = requests.post(
            url,
            json=prepared_params,
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Success!")
            print(f"\nResponse:")
            print(f"  Context Used: {data.get('context_used', 'N/A')}")
            print(f"  Sources Found: {data.get('num_sources', 0)}")
            print(f"\nAI Analysis:")
            print("-" * 60)
            print(data.get('response', 'No response')[:500] + "..." if len(data.get('response', '')) > 500 else data.get('response', ''))
            print("-" * 60)
            
            return True
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error message: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Could not connect to {BASE_URL}")
        print("Make sure Django server is running: python manage.py runserver")
        return False
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False

def main():
    base_dir = Path(__file__).parent
    test_cases = load_test_cases()
    
    if not test_cases:
        print("❌ Could not load test_parameters.json")
        print("Using default quick test...")
        quick_test = {
            "metal_type": "316L Stainless Steel",
            "service_time": "3 years",
            "environment": "High-chloride environment, coastal atmosphere",
            "temperature": "60-80°C",
            "mechanical_load": "Static with residual stress",
            "notes": "Cracks observed in weld heat-affected zone. Intergranular cracking pattern."
        }
        test_api(quick_test, "Quick Test - Stress Corrosion Cracking", base_dir)
        return
    
    test_arg = sys.argv[1] if len(sys.argv) > 1 else "quick"
    
    if test_arg == "quick":
        quick_test = test_cases.get('quick_test', {})
        if quick_test and 'parameters' in quick_test:
            test_api(quick_test['parameters'], quick_test.get('name', 'Quick Test'), base_dir)
        else:
            print("❌ Quick test not found in test_parameters.json")
    elif test_arg.isdigit():
        case_num = int(test_arg) - 1
        cases = test_cases.get('test_cases', [])
        if 0 <= case_num < len(cases):
            case = cases[case_num]
            test_api(case['parameters'], case['name'], base_dir)
        else:
            print(f"❌ Test case {test_arg} not found. Available: 1-{len(cases)}")
    elif test_arg == "all":
        cases = test_cases.get('test_cases', [])
        print(f"Running all {len(cases)} test cases...\n")
        results = []
        for i, case in enumerate(cases, 1):
            success = test_api(case['parameters'], f"{i}. {case['name']}", base_dir)
            results.append((case['name'], success))
            if i < len(cases):
                input("\nPress Enter to continue to next test...")
        
        print(f"\n{'='*60}")
        print("Test Summary")
        print(f"{'='*60}")
        passed = sum(1 for _, success in results if success)
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {name}")
        print(f"\nTotal: {passed}/{len(results)} passed")
    else:
        print(f"❌ Unknown test argument: {test_arg}")
        print("\nUsage:")
        print("  python test_api.py          # Quick test")
        print("  python test_api.py quick    # Quick test")
        print("  python test_api.py 1        # Test case 1")
        print("  python test_api.py all      # Run all tests")

if __name__ == "__main__":
    main()


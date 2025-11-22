# Test Images Directory

This directory contains sample test images used for failure analysis test cases.

## Available Images

- `scc_cracks.jpg` - Stress corrosion cracking visual
- `fatigue_beach_marks.jpg` - Fatigue failure with beach marks
- `pitting_corrosion.jpg` - Pitting corrosion pattern
- `creep_deformation.jpg` - High-temperature creep deformation
- `brittle_fracture.jpg` - Brittle fracture surface
- `erosion_wear.jpg` - Erosive wear pattern
- `hydrogen_embrittlement.jpg` - Hydrogen embrittlement failure
- `thermal_fatigue.jpg` - Thermal fatigue cracks

## Using Your Own Images

To use your own failure analysis images:

1. Place your image files in this directory
2. Update `test_parameters.json` to reference your images:
   ```json
   {
     "photos": ["test_images/your_image.jpg"]
   }
   ```
3. Run the test script: `python test_api.py`

## Image Requirements

- Format: JPEG, PNG, or GIF
- Size: Up to 10MB per image
- Multiple images: Up to 5 images per test case
- The test script automatically encodes images to base64 for API requests


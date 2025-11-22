# Test Cases for Baseera AI RAG System

Use these test parameters to verify the RAG system is working correctly. Each test case is designed to trigger different types of searches in the knowledge base.

## 📸 Test Images

All test cases now include sample images located in the `test_images/` directory. These images are automatically encoded to base64 and sent with the API request. The test script (`test_api.py`) handles image encoding automatically.

**Available Test Images:**
- `scc_cracks.jpg` - Stress corrosion cracking visual
- `fatigue_beach_marks.jpg` - Fatigue failure with beach marks
- `pitting_corrosion.jpg` - Pitting corrosion pattern
- `creep_deformation.jpg` - High-temperature creep deformation
- `brittle_fracture.jpg` - Brittle fracture surface
- `erosion_wear.jpg` - Erosive wear pattern
- `hydrogen_embrittlement.jpg` - Hydrogen embrittlement failure
- `thermal_fatigue.jpg` - Thermal fatigue cracks

**Note:** If you want to use your own images, place them in the `test_images/` directory and update the photo paths in `test_parameters.json`.

## Test Case 1: Stress Corrosion Cracking (SCC)
**Expected:** Should find matches in ASM Handbook on SCC, CSB reports on corrosion failures  
**Image:** `test_images/scc_cracks.jpg` - Visual of intergranular cracks in weld HAZ

```json
{
  "metal_type": "316L Stainless Steel",
  "service_time": "3 years",
  "environment": "High-chloride environment, coastal atmosphere",
  "temperature": "60-80°C",
  "mechanical_load": "Static with residual stress",
  "notes": "Cracks observed in weld heat-affected zone. Intergranular cracking pattern. Component exposed to salt spray.",
  "photos": ["test_images/1.jpg"]
}
```

## Test Case 2: Fatigue Failure
**Expected:** Should retrieve ASM Handbook chapters on fatigue, fatigue fracture appearances  
**Image:** `test_images/fatigue_beach_marks.jpg` - Visual of beach marks on fracture surface

```json
{
  "metal_type": "Carbon Steel A36",
  "service_time": "8 years",
  "environment": "Atmospheric, industrial",
  "temperature": "Ambient (20-30°C)",
  "mechanical_load": "Cyclic loading, high frequency vibrations",
  "notes": "Beach marks visible on fracture surface. Failure at stress concentration point (hole). Component subject to rotating machinery vibrations.",
  "photos": ["test_images/fatigue_beach_marks.jpg"]
}
```

## Test Case 3: High-Temperature Creep
**Expected:** Should find ASM Handbook on creep failures, high-temperature service  
**Image:** `test_images/creep_deformation.jpg` - Visual of grain boundary separation

```json
{
  "metal_type": "Inconel 625",
  "service_time": "12 years",
  "environment": "High-temperature flue gas, oxidizing atmosphere",
  "temperature": "800-900°C",
  "mechanical_load": "Constant tensile stress",
  "notes": "Gradual deformation over time. Grain boundary separation. Used in furnace application.",
  "photos": ["test_images/creep_deformation.jpg"]
}
```

## Test Case 4: Pitting Corrosion
**Expected:** Should match ASM Handbook on forms of corrosion, pitting corrosion  
**Image:** `test_images/pitting_corrosion.jpg` - Visual of localized pitting pattern

```json
{
  "metal_type": "304 Stainless Steel",
  "service_time": "2 years",
  "environment": "Chloride-containing water, stagnant conditions",
  "temperature": "40-50°C",
  "mechanical_load": "Low, primarily static",
  "notes": "Localized pitting observed. Deep pits with small surface openings. Component in water storage tank.",
  "photos": ["test_images/pitting_corrosion.jpg"]
}
```

## Test Case 5: Hydrogen Embrittlement
**Expected:** Should retrieve ASM Handbook on hydrogen damage, embrittlement failures  
**Image:** `test_images/hydrogen_embrittlement.jpg` - Visual of brittle fracture surface

```json
{
  "metal_type": "High-Strength Steel (AISI 4340)",
  "service_time": "5 years",
  "environment": "Acidic environment, hydrogen sulfide present",
  "temperature": "50-70°C",
  "mechanical_load": "High tensile stress",
  "notes": "Brittle fracture with no plastic deformation. Delayed failure after exposure. Used in sour gas service.",
  "photos": ["test_images/hydrogen_embrittlement.jpg"]
}
```

## Test Case 6: Erosive Wear
**Expected:** Should find ASM Handbook on erosive wear, wear failures  
**Image:** `test_images/erosion_wear.jpg` - Visual of material loss from particle impact

```json
{
  "metal_type": "Carbon Steel",
  "service_time": "6 years",
  "environment": "Abrasive particles in gas stream",
  "temperature": "200-300°C",
  "mechanical_load": "High velocity particle impact",
  "notes": "Material loss on exposed surfaces. Smooth, polished appearance. Used in cyclone separator.",
  "photos": ["test_images/erosion_wear.jpg"]
}
```

## Test Case 7: Intergranular Corrosion
**Expected:** Should match ASM Handbook on intergranular fracture, corrosion forms

```json
{
  "metal_type": "304 Stainless Steel",
  "service_time": "4 years",
  "environment": "Acidic environment, oxidizing conditions",
  "temperature": "400-600°C (sensitization temperature range)",
  "mechanical_load": "Low stress",
  "notes": "Grain boundary attack. Material appears sound but loses strength. Weldment area affected."
}
```

## Test Case 8: Thermal Fatigue
**Expected:** Should retrieve ASM Handbook on thermal cycling, fatigue failures  
**Image:** `test_images/thermal_fatigue.jpg` - Visual of thermal fatigue cracks

```json
{
  "metal_type": "Cast Iron",
  "service_time": "10 years",
  "environment": "Cyclic heating and cooling",
  "temperature": "20-500°C (cyclic)",
  "mechanical_load": "Thermal stress from expansion/contraction",
  "notes": "Cracks initiating from surface. Thermal cycling in furnace application. Multiple crack origins.",
  "photos": ["test_images/thermal_fatigue.jpg"]
}
```

## Test Case 9: Galvanic Corrosion
**Expected:** Should find ASM Handbook on forms of corrosion, galvanic effects

```json
{
  "metal_type": "Aluminum 6061",
  "service_time": "3 years",
  "environment": "Marine atmosphere, salt water exposure",
  "temperature": "Ambient",
  "mechanical_load": "Low",
  "notes": "Accelerated corrosion where aluminum contacts stainless steel fasteners. Localized attack at contact points."
}
```

## Test Case 10: Brittle Fracture
**Expected:** Should match ASM Handbook on brittle fracture, low-temperature failures  
**Image:** `test_images/brittle_fracture.jpg` - Visual of cleavage fracture surface

```json
{
  "metal_type": "Carbon Steel",
  "service_time": "15 years",
  "environment": "Low temperature service",
  "temperature": "-20°C",
  "mechanical_load": "Impact loading",
  "notes": "Cleavage fracture surface. No plastic deformation. Failure occurred during cold weather operation.",
  "photos": ["test_images/brittle_fracture.jpg"]
}
```

## Test Case 11: Fretting Wear
**Expected:** Should retrieve ASM Handbook on fretting wear failures

```json
{
  "metal_type": "Stainless Steel 316",
  "service_time": "7 years",
  "environment": "Atmospheric, with vibration",
  "temperature": "Ambient",
  "mechanical_load": "Small amplitude oscillatory motion",
  "notes": "Wear at contact interface between two components. Oxide debris present. Bolted joint application."
}
```

## Test Case 12: Stress-Corrosion Cracking (Chloride)
**Expected:** Should find extensive matches in ASM Handbook and CSB reports

```json
{
  "metal_type": "Duplex Stainless Steel 2205",
  "service_time": "4 years",
  "environment": "Chloride-containing process fluid",
  "temperature": "70-90°C",
  "mechanical_load": "Residual stress from welding",
  "notes": "Transgranular cracking. Branching cracks. Failure in heat exchanger tube."
}
```

## Test Case 13: Liquid Droplet Impingement Erosion
**Expected:** Should match ASM Handbook on liquid droplet erosion

```json
{
  "metal_type": "Titanium Grade 2",
  "service_time": "9 years",
  "environment": "High-velocity liquid droplets",
  "temperature": "100-150°C",
  "mechanical_load": "Erosive impact from droplets",
  "notes": "Material removal in specific pattern. Used in steam turbine application. Erosion at blade leading edges."
}
```

## Test Case 14: Oxidation at High Temperature
**Expected:** Should retrieve ASM Handbook on high-temperature oxidation

```json
{
  "metal_type": "Nickel-based Superalloy",
  "service_time": "6 years",
  "environment": "Oxidizing atmosphere at high temperature",
  "temperature": "1000-1100°C",
  "mechanical_load": "Thermal cycling",
  "notes": "Oxide scale formation. Spallation of oxide layer. Used in gas turbine application."
}
```

## Test Case 15: Low Context Test (Should show limited context)
**Expected:** Should still provide analysis but with limited knowledge base matches

```json
{
  "metal_type": "Unusual Alloy XYZ-123",
  "service_time": "1 month",
  "environment": "Unknown",
  "temperature": "Unknown",
  "mechanical_load": "Unknown",
  "notes": "Failure occurred but limited information available."
}
```

---

## Quick Test Checklist

### Basic Functionality Tests:
- [ ] Test Case 1: Verify SCC analysis with sources
- [ ] Test Case 2: Verify fatigue analysis with sources
- [ ] Test Case 15: Verify graceful handling with limited context

### RAG Verification:
- [ ] Check that "Knowledge Base: X sources found" badge appears
- [ ] Verify loading states show "Searching knowledge base..."
- [ ] Confirm AI response references specific documents/sources
- [ ] Verify knowledge base stats display in header

### Edge Cases:
- [ ] Empty fields (should still work)
- [ ] Very specific/rare failure modes
- [ ] Multiple failure mechanisms combined

---

## Expected RAG Behavior

### When RAG Works Well:
- **Response includes:** "Based on: [Document Name]" or similar citations
- **Badge shows:** "Knowledge Base: 3-5 sources found"
- **Analysis references:** Specific cases, handbooks, or reports
- **Loading shows:** Both steps complete successfully

### When RAG Has Limited Context:
- **Badge shows:** "Limited context available"
- **Response still provides:** General analysis based on principles
- **No errors:** System gracefully handles missing context

---

## Performance Benchmarks

- **Query Time:** 100-500ms for RAG search
- **Total Response:** 2-5 seconds (including AI generation)
- **Sources Found:** Typically 3-5 relevant chunks per query
- **Context Quality:** Should match failure type to relevant documents

---

## Running Tests

### Using the Test Script

The `test_api.py` script automatically handles image encoding and API testing:

```bash
# Quick test (with image)
python test_api.py

# Run specific test case
python test_api.py 1

# Run all test cases
python test_api.py all
```

### What the Script Does

1. **Loads test cases** from `test_parameters.json`
2. **Encodes images** to base64 format automatically
3. **Sends API requests** to `http://localhost:8000/api/chat`
4. **Displays results** including:
   - Context usage status
   - Number of sources found
   - AI response preview
   - Success/failure status

### Image Handling

- Images are automatically encoded to base64 before sending
- If an image file is missing, a warning is shown but the test continues
- Multiple images per test case are supported (up to 5)
- Image paths in `test_parameters.json` are relative to the project root

## Testing Tips

1. **Start with Test Case 1** - Most common failure type, should have many matches and includes an image
2. **Try Test Case 15** - Verifies system works even without perfect matches (no image)
3. **Check Admin Panel** - View QueryLog to see what was searched
4. **Monitor Console** - Check for any errors in browser console
5. **Compare Responses** - With vs without RAG (if you disable it temporarily)
6. **Test Image Analysis** - Verify that AI responses reference visual observations from images

---

## Notes

- All test cases are based on real failure analysis scenarios
- Metal types, environments, and failure modes are realistic
- Expected results assume knowledge base has been populated
- Adjust expectations if knowledge base is still being populated


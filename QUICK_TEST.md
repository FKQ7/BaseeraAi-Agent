# Quick Test Guide

## Fastest Test (Copy & Paste)

Use this single test case to quickly verify the RAG system is working:

### Test Parameters:
```
Metal Type: 316L Stainless Steel
Service Time: 3 years
Environment: High-chloride environment, coastal atmosphere
Temperature: 60-80°C
Mechanical Load: Static with residual stress
Engineer Notes: Cracks observed in weld heat-affected zone. Intergranular cracking pattern. Component exposed to salt spray.
```

### What to Look For:

✅ **Loading States:**
- Should show "Searching knowledge base..." first
- Then "Generating analysis..."

✅ **Response Badge:**
- Should show "Knowledge Base: X sources found" (typically 3-5)
- Badge should be blue with an icon

✅ **AI Response:**
- Should mention "stress corrosion cracking" or "SCC"
- Should reference ASM Handbook, CSB reports, or similar sources
- Should provide root cause analysis
- Should include recommendations

✅ **Knowledge Base Stats:**
- Header should show document/chunk counts (if documents are processed)

---

## Expected Response Elements:

1. **Root Cause:** Should identify stress corrosion cracking
2. **Correlations:** Should mention chloride + temperature + stainless steel
3. **Sources:** Should cite documents like "ASM Handbook" or "CSB Report"
4. **Recommendations:** Should provide actionable suggestions

---

## If Something's Wrong:

### No Sources Found:
- Check if documents are ingested: `python manage.py ingest_documents --limit 10`
- Verify ChromaDB is working
- Check browser console for errors

### Badge Shows "Limited Context":
- This is OK - means RAG searched but found few matches
- System still provides analysis based on general principles

### No Response:
- Check Django server logs
- Verify Gemini API key is working
- Check network tab in browser dev tools

---

## Full Test Suite:

See `TEST_CASES.md` for 15 comprehensive test cases covering different failure modes.


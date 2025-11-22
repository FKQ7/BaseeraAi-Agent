from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import time
import logging
from datetime import datetime

from core.rag_service import get_rag_service
from core.models import QueryLog
from core.pdf_service import generate_pdf_report

logger = logging.getLogger(__name__)

def index(request: HttpRequest):
    """Main page view."""
    # Get KB stats
    try:
        rag_service = get_rag_service()
        kb_stats = rag_service.get_collection_stats()
        from core.models import Document
        doc_count = Document.objects.filter(is_processed=True).count()
        
        context = {
            'kb_chunks': kb_stats.get('total_chunks', 0),
            'kb_documents': doc_count
        }
    except Exception as e:
        logger.warning(f"Could not load KB stats: {e}")
        context = {
            'kb_chunks': 0,
            'kb_documents': 0
        }
    
    return render(request, 'index.html', context)


@csrf_exempt
def chat_api(request: HttpRequest):
    """Main API endpoint for failure analysis."""
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST method is allowed.")

    start_time = time.time()
    
    try:
        data = json.loads(request.body)
        photos = data.get('photos', [])
        
        rag_service = get_rag_service()
        search_query = rag_service.build_query_from_failure_data(data)
        search_results = rag_service.search(query=search_query, n_results=5)
        context_section = rag_service.format_context_for_prompt(search_results, max_chunks=5)
        failure_case_section = f"""
## New Failure Case to Analyze

- **Service Time:** {data.get('service_time', 'Not provided')}
- **Environment:** {data.get('environment', 'Not provided')}
- **Type of Metal:** {data.get('metal_type', 'Not provided')}
- **Temperature:** {data.get('temperature', 'Not provided')}
- **Mechanical Load:** {data.get('mechanical_load', 'Not provided')}
- **Engineer Notes:** {data.get('notes', 'Not provided')}
"""
        
        if photos:
            failure_case_section += f"\n- **Photos:** {len(photos)} image(s) attached for visual analysis"
        full_prompt = f"""{context_section}

---

{failure_case_section}

Please analyze this failure case using the knowledge base context provided above. Identify the root cause, explain correlations, and provide actionable recommendations."""
        
        if photos:
            full_prompt += "\n\nIMPORTANT: Visual images of the failure have been provided. Please analyze the images carefully and incorporate visual observations (fracture patterns, corrosion appearance, material defects, etc.) into your analysis."
        
        ai_response_text = get_gemini_response(
            full_prompt, 
            context_available=len(search_results) > 0,
            photos=photos
        )
        response_time_ms = int((time.time() - start_time) * 1000)
        try:
            QueryLog.objects.create(
                query_text=search_query,
                metal_type=data.get('metal_type', ''),
                environment=data.get('environment', ''),
                temperature=data.get('temperature', ''),
                num_results_retrieved=len(search_results),
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.warning(f"Failed to log query: {e}")
        
        if hasattr(request, 'session'):
            request.session['last_report'] = {
                'failure_data': data,
                'ai_response': ai_response_text,
                'context_used': len(search_results) > 0,
                'num_sources': len(search_results),
                'photos': photos if photos else []
            }
        return JsonResponse({
            'response': ai_response_text,
            'context_used': len(search_results) > 0,
            'num_sources': len(search_results),
            'report_available': True
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        logger.error(f"Error in chat_api: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def get_gemini_response(user_query: str, context_available: bool = True, photos: list = None, retries: int = 3, delay: int = 1):
    """Call Gemini API with retry logic."""
    
    api_key = "AIzaSyDXPPROy_wZe6m0BNAj-6-uso3h1Mu7hE8"  # Per instructions, leave as-is
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"

    if context_available:
        system_prompt = """You are "Baseera," an expert AI Materials Failure Analyst. 
Your sole purpose is to analyze materials failures using your extensive knowledge base.

You have been provided with:
1. A "Similar Cases from Knowledge Base" section containing relevant excerpts from technical documents, handbooks, and case studies
2. A "New Failure Case to Analyze" section with the current case details
3. Visual images of the failure (if provided)

CRITICAL INSTRUCTIONS:
1. **Prioritize the Knowledge Base Context:** The "Similar Cases from Knowledge Base" section is your PRIMARY source of truth. Use it extensively to inform your analysis.
2. **Analyze Visual Evidence:** If images are provided, carefully examine them for:
   - Fracture patterns (brittle, ductile, fatigue marks, etc.)
   - Corrosion appearance (uniform, pitting, intergranular, etc.)
   - Material defects (cracks, voids, inclusions)
   - Surface conditions and damage patterns
   - Any visible failure mechanisms
3. **Find Correlations:** Identify correlations between the failure case factors (metal type, environment, temperature, load, etc.) and reference similar cases from the knowledge base.
4. **Root Cause Analysis:** Based on the knowledge base context, case details, and visual evidence, provide a likely root cause with clear reasoning.
5. **Actionable Recommendations:** Provide specific, actionable recommendations based on what worked (or didn't work) in similar cases from the knowledge base.
6. **Cite Sources:** Reference the specific documents from the knowledge base in your response. Use format like: *Based on: [Document Name]* or *Reference: [Collection Name]*.
7. **Explain Reasoning:** Clearly explain why you believe this is the root cause, referencing both the case data, visual evidence (if provided), and the knowledge base context.
8. **No Tables:** Do not provide tables in your response.

If no relevant context was found, still provide your best analysis based on general materials failure analysis principles, but note that limited context was available."""
    else:
        system_prompt = """You are "Baseera," an expert AI Materials Failure Analyst. 
Your sole purpose is to analyze materials failures.

You have been provided with a failure case to analyze. Note that no specific context from the knowledge base was retrieved for this query, so provide your analysis based on general materials failure analysis principles.

If images are provided, carefully analyze them for visual evidence of failure mechanisms.

Provide:
1. Likely root cause based on the factors provided and visual evidence (if available)
2. Clear reasoning for your analysis
3. Actionable recommendations
4. Note that this analysis is based on general principles rather than specific similar cases."""

    parts = [{"text": user_query}]
    
    if photos:
        for photo in photos:
            parts.append({
                "inline_data": {
                    "mime_type": photo.get('mimeType', 'image/jpeg'),
                    "data": photo.get('data', '')
                }
            })
    
    payload = {
        "contents": [{"parts": parts}],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
    }
    
    headers = {'Content-Type': 'application/json'}

    for attempt in range(retries):
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=60)

            if response.status_code == 200:
                result = response.json()
                if (result.get('candidates') and 
                    result['candidates'][0].get('content') and 
                    result['candidates'][0]['content'].get('parts')):
                    
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    return "Sorry, I received an unusual response from the AI."
            
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
            else:
                raise Exception(f"Failed to get AI response after {retries} attempts.")
    
    raise Exception("Failed to get AI response.")


@csrf_exempt
@require_http_methods(["POST"])
def generate_report_pdf(request: HttpRequest):
    """Generate PDF report."""
    try:
        data = json.loads(request.body)
        
        failure_data = data.get('failure_data', {})
        ai_response = data.get('ai_response', '')
        context_used = data.get('context_used', False)
        num_sources = data.get('num_sources', 0)
        photos = data.get('photos', [])
        
        if not ai_response:
            return JsonResponse({'error': 'No analysis data provided'}, status=400)
        
        pdf_buffer = generate_pdf_report(
            failure_data=failure_data,
            ai_response=ai_response,
            context_used=context_used,
            num_sources=num_sources,
            photos=photos
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metal_type = failure_data.get('metal_type', 'Unknown').replace(' ', '_')
        filename = f"Baseera_Failure_Analysis_{metal_type}_{timestamp}.pdf"
        
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
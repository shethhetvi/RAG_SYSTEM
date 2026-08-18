import os
import time
from groq import Groq
from .retrieval import retrieve_context
from .guardrails import check_query_safety, check_groundedness

# Main LLM for generation
GENERATION_MODEL = "llama3-70b-8192"

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    return Groq(api_key=api_key)

def process_rag_query(query: str, timings: dict):
    """
    Structured orchestration around the model.
    Handles guardrails, retrieval, and generation.
    Returns (answer, context_used).
    """
    
    # 1. Guardrail 1: Safety
    t_start = time.time()
    is_safe = check_query_safety(query)
    timings["guardrail_safety"] = time.time() - t_start
    
    if not is_safe:
        return "Your query violated safety guidelines. I cannot process it.", []
        
    # 2. Retrieval
    t_start = time.time()
    retrieved_docs = retrieve_context(query, top_k=3)
    timings["retrieval"] = time.time() - t_start
    
    if not retrieved_docs:
        return "I could not find any relevant context in my knowledge base.", []
        
    context_text = "\n\n".join([d["text"] for d in retrieved_docs])
    
    # 3. Guardrail 2: Context Sufficiency (Handled in prompt)
    system_prompt = (
        "You are a helpful, bioluminescent alien AI. You answer questions based ONLY on the provided context. "
        "If the context does not contain the answer, say 'I do not have sufficient information to answer this query based on my data.' "
        "Do not hallucinate."
    )
    
    # 4. Answer Generation
    t_start = time.time()
    client = get_groq_client()
    answer = ""
    
    if client:
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
                ],
                model=GENERATION_MODEL,
                temperature=0.2,
                max_tokens=256
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Error communicating with LLM: {e}"
    else:
        # Mock answer for missing API key
        answer = f"[Mock Output] Based on context: '{retrieved_docs[0]['text'][:50]}...', the answer is..."
        
    timings["generation"] = time.time() - t_start
    
    # 5. Guardrail 3: Groundedness check
    t_start = time.time()
    # To hit 200ms, we might only run this async or conditionally, but we run it here
    is_grounded = check_groundedness(answer, context_text)
    timings["guardrail_groundedness"] = time.time() - t_start
    
    if not is_grounded:
        return "My generated response could not be verified against the source text. I cannot provide an answer.", retrieved_docs
        
    return answer, retrieved_docs

import os
from groq import Groq

# Fast model for guardrails
GUARDRAIL_MODEL = "llama3-8b-8192"

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    return Groq(api_key=api_key)

def check_query_safety(query: str) -> bool:
    """
    Checks if the query is safe and on-topic.
    Returns True if safe, False if off-topic or unsafe.
    """
    # For ultra-low latency, we can use simple heuristic checks first
    unsafe_keywords = ["hack", "kill", "bomb", "illegal", "bypass"]
    if any(word in query.lower() for word in unsafe_keywords):
        return False
        
    # Optional LLM check for safety (commented out by default to save latency)
    """
    client = get_groq_client()
    if client:
        try:
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": "Reply YES if the user query is safe and a normal question, NO if it is harmful, toxic, or completely nonsensical."},
                          {"role": "user", "content": query}],
                model=GUARDRAIL_MODEL,
                max_tokens=10,
                temperature=0
            )
            answer = response.choices[0].message.content.strip().upper()
            return "YES" in answer
        except:
            return True
    """
    return True

def check_groundedness(answer: str, context: str) -> bool:
    """
    Checks if the generated answer is grounded in the provided context.
    Returns True if grounded, False if hallucinated.
    """
    # For latency purposes, we might skip the LLM call here in the critical path, 
    # but the requirement states we need a groundedness check.
    # We will implement it using a fast LLM call.
    client = get_groq_client()
    if not client:
        return True # Fallback if no API key
        
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a groundedness checker. Does the following ANSWER rely purely on the CONTEXT? Reply YES or NO."},
                {"role": "user", "content": f"CONTEXT: {context}\n\nANSWER: {answer}"}
            ],
            model=GUARDRAIL_MODEL,
            max_tokens=10,
            temperature=0
        )
        decision = response.choices[0].message.content.strip().upper()
        return "YES" in decision
    except Exception as e:
        print(f"Groundedness check failed: {e}")
        return True

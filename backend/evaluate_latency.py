import requests
import time
import numpy as np
import statistics

# Test configuration
NUM_QUERIES = 20
TEST_QUERIES = [
    "What is the capital of France?",
    "How does a quantum computer work?",
    "Explain the theory of relativity.",
    "What are the benefits of a Mediterranean diet?",
    "Who wrote 'To Kill a Mockingbird'?",
    "Describe the process of photosynthesis.",
    "What are the main causes of climate change?",
    "How to learn programming?",
    "What is the history of the Internet?",
    "Why is the sky blue?"
]

API_URL = "http://localhost:8000/query/text"

def run_evaluation():
    print(f"Running latency evaluation with {NUM_QUERIES} test queries...")
    latencies = []
    
    # Warmup query (not counted in metrics)
    print("Sending warmup query...")
    try:
        requests.post(API_URL, data={"query": "Hello"})
    except requests.exceptions.ConnectionError:
        print("Backend server is not running. Please start it with 'uvicorn backend.main:app --reload'")
        return
        
    for i in range(NUM_QUERIES):
        query = TEST_QUERIES[i % len(TEST_QUERIES)]
        start_time = time.time()
        
        try:
            response = requests.post(API_URL, data={"query": query})
            response.raise_for_status()
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            latencies.append(duration_ms)
            
            server_timings = response.json().get("timings", {})
            server_total_ms = server_timings.get("total", 0) * 1000
            
            print(f"Query {i+1}: Client Latency {duration_ms:.2f}ms, Server Latency {server_total_ms:.2f}ms")
            
        except Exception as e:
            print(f"Query {i+1} failed: {e}")
            
    if not latencies:
        print("No successful queries.")
        return
        
    # Calculate P50, P70, P100
    p50 = np.percentile(latencies, 50)
    p70 = np.percentile(latencies, 70)
    p100 = np.percentile(latencies, 100)
    avg = statistics.mean(latencies)
    
    print("\n" + "="*40)
    print("LATENCY ANALYTICS (Client-side, E2E)")
    print("="*40)
    print(f"Average Latency: {avg:.2f} ms")
    print(f"P50 Latency:     {p50:.2f} ms")
    print(f"P70 Latency:     {p70:.2f} ms")
    print(f"P100 Latency:    {p100:.2f} ms (Worst case)")
    print("="*40)
    
    if p50 <= 200:
        print("✅ P50 Target Met (< 200ms)")
    else:
        print("❌ P50 Target Missed (> 200ms)")

if __name__ == "__main__":
    run_evaluation()

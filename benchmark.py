import ollama
import time

def run_benchmark(model_name, prompt, runs=3):
    print(f"Testing model: {model_name}")
    print("-" * 50)
    
    total_time = 0
    total_tokens = 0
    
    for i in range(runs):
        print(f"Run {i+1}/{runs}...")
        
        start = time.time()
        
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        
        end = time.time()
        
        elapsed = end - start
        content = response['message']['content']
        tokens = len(content.split())
        tok_per_sec = tokens / elapsed
        
        total_time += elapsed
        total_tokens += tokens
        
        print(f"  Time: {elapsed:.1f}s | Tokens: {tokens} | Speed: {tok_per_sec:.1f} tok/s")
    
    avg_time = total_time / runs
    avg_tokens = total_tokens / runs
    avg_speed = avg_tokens / avg_time
    
    print()
    print(f"AVERAGE RESULT:")
    print(f"  Time:   {avg_time:.1f} seconds")
    print(f"  Tokens: {avg_tokens:.0f}")
    print(f"  Speed:  {avg_speed:.1f} tok/s")
    print("=" * 50)
    print()
    
    return avg_speed

# Test prompt
prompt = "Summarise this patient note in 3 sections: Patient is a 45 year old male with chest pain since 3 days. Pain radiates to left arm. History of high blood pressure."

print("=" * 50)
print("  LOCAL LLM BENCHMARK")
print("  Testing: llama3.2")
print("=" * 50)
print()

speed = run_benchmark("llama3.2", prompt, runs=3)

print("BENCHMARK COMPLETE!")
print(f"Your model speed: {speed:.1f} tok/s")
print()
print("Compare with standard results:")
print("  fp16  -> 8.2  tok/s")
print("  Q8_0  -> 11.4 tok/s")
print("  Q4_KM -> 18.7 tok/s")
print("  Q3_KS -> 24.1 tok/s")
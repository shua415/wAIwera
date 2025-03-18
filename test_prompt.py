import ollama
import json
import time

# List of models to test
models = ["mistral", "codellama", "gemma", "phi", "llama2"]

# Prompt for JSON generation
prompt = """Generate a JSON configuration for a geothermal simulation. 
The system has a reservoir of 16 km by 14 km by 5 km depth. 
The top boundary has constant pressure (1 bar) and temperature (25°C). 
The deep source inputs 100 kg/s, split into 70 kg/s at 1400 kJ/kg and 30 kg/s at 1100 kJ/kg.
Respond only with JSON format.
"""

# Dictionary to store results
results = {}

def run_model(model):
    """Runs the specified model and returns the response"""
    print(f"Testing model: {model}...")
    try:
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        output = response["message"].strip()
        
        # Validate if response is JSON
        try:
            json_output = json.loads(output)  # Convert to dict
            results[model] = json_output
            print(f"✅ {model} successfully generated JSON.")
        except json.JSONDecodeError:
            results[model] = {"error": "Invalid JSON format", "raw_output": output}
            print(f"❌ {model} failed JSON validation.")
        
    except Exception as e:
        results[model] = {"error": str(e)}
        print(f"❌ {model} encountered an error: {e}")

# Run all models
for model in models:
    run_model(model)
    time.sleep(2)  # Small delay to avoid overloading Ollama

# Save results to a JSON file
with open("ollama_model_comparison.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✅ All models tested! Results saved to 'ollama_model_comparison.json'.")

import json
import ollama
import jsonschema
import os

# Configuration
MODEL_NAME = "mistral"  # Change this if needed
CONTEXT_FILE = "Context.txt"
SCHEMA_FILE = "input_schema.json"  # Extracted from the test script

def load_context(file_path):
    """Load the markdown context from a .txt file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def generate_json(prompt, model=MODEL_NAME):
    """Generate a JSON response from the AI model."""
    context = load_context(CONTEXT_FILE)
    
    response = ollama.chat(model=model, messages=[
        {"role": "system", "content": "You are an expert in creating valid JSON files for the Waiwera simulation."},
        {"role": "user", "content": f"Here is the documentation on how to create a valid JSON file:\n\n{context}"},
        {"role": "user", "content": f"Now, generate a valid JSON file based on this prompt:\n{prompt}"}
    ])
    
    return response['message']['content']

def validate_json(json_str):
    """Validate the generated JSON against the extracted schema."""
    try:
        data = json.loads(json_str)
        with open(SCHEMA_FILE, "r", encoding="utf-8") as schema_file:
            schema = json.load(schema_file)
        jsonschema.validate(instance=data, schema=schema)
        print("✅ JSON is valid!")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print("❌ JSON validation failed:", e)
    except json.JSONDecodeError as e:
        print("❌ JSON parsing failed:", e)
    
    return False

def save_json(json_str, filename="generated.json"):
    """Save the JSON string to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json_str)
    print(f"✅ JSON saved to {filename}")

if __name__ == "__main__":
    user_prompt = input("Enter your JSON generation prompt: ")
    json_output = generate_json(user_prompt)

    print("\nGenerated JSON:\n", json_output)

    if validate_json(json_output):
        save_json(json_output)

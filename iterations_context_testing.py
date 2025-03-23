
import json
import ollama
import jsonschema
import os

# Configuration
MODEL_NAME = "mistral" 
CONTEXT_FILE = "Context.txt"
SCHEMA_FILE = "input_schema.json"
LOG_FILE = "validation_log.txt"  # Log file to store previous attempts

MAX_ITERATIONS = 2  # Maximum attempts before stopping

def load_context(file_path):
    """Load the markdown context from a .txt file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def read_previous_errors():
    """Read previous JSON outputs and validation errors from the log file."""
    if not os.path.exists(LOG_FILE):
        return ""
    
    with open(LOG_FILE, "r", encoding="utf-8") as file:
        return file.read()

def generate_json(prompt, model=MODEL_NAME, previous_errors=""):
    """Generate a JSON response from the AI model, incorporating previous errors."""
    context = load_context(CONTEXT_FILE)
    
    messages = [
        {"role": "system", "content": "You are an expert in creating valid JSON files for the Waiwera simulation. You are provided with a mesh file called 'placeholder.msh'. Do not include comments in JSON. One penalty for each error created. "},
        {"role": "user", "content": f"Here is the documentation on how to create a valid JSON file:\n\n{context}"},
    ]

    if previous_errors:
        messages.append({"role": "user", "content": f"Previous errors and invalid JSON:\n{previous_errors}"})
    
    messages.append({"role": "user", "content": f"Now, generate a valid JSON file based on this prompt:\n{prompt}"})

    response = ollama.chat(model=model, messages=messages)
    
    return response['message']['content']

def validate_json(json_str):
    """Validate the generated JSON against the schema and return errors."""
    try:
        data = json.loads(json_str)
        with open(SCHEMA_FILE, "r", encoding="utf-8") as schema_file:
            schema = json.load(schema_file)
        jsonschema.validate(instance=data, schema=schema)
        print("✅ JSON is valid!")
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        print("❌ JSON validation failed:", e)
        return False, str(e)
    except json.JSONDecodeError as e:
        print("❌ JSON parsing failed:", e)
        return False, str(e)

def save_json(json_str, filename="generated.json"):
    """Save the JSON string to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json_str)
    print(f"✅ JSON saved to {filename}")

def append_to_log(json_str, error_message):
    """Append the generated JSON and validation errors to the log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write("Generated JSON:\n")
        log_file.write(json_str + "\n\n")
        if error_message:
            log_file.write("Validation Error:\n")
            log_file.write(error_message + "\n\n")
        log_file.write("=" * 50 + "\n\n")

if __name__ == "__main__":
    user_prompt = input("Enter your JSON generation prompt: ")

    for attempt in range(1, MAX_ITERATIONS + 1):
        print(f"\n🔄 Attempt {attempt}/{MAX_ITERATIONS}")
        
        previous_errors = read_previous_errors()
        json_output = generate_json(user_prompt, previous_errors=previous_errors)

        print("\nGenerated JSON:\n", json_output)

        is_valid, error_message = validate_json(json_output)
        append_to_log(json_output, error_message)

        if is_valid:
            save_json(json_output)
            print("🎉 JSON generation successful!")
            break
    else:
        print("❌ Maximum attempts reached. JSON is still invalid.")

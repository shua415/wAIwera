import ollama
import json
import os
from docx import Document
from jsonschema import validate, ValidationError

# File paths
DOC_PATH = "context.docx"  # Your documentation file
SCHEMA_PATH = "input_schema.json"  # The updated schema file
OUTPUT_JSON = "generated.json"  # Output JSON file

def load_context_from_docx(doc_path):
    """Extracts text from a Word document."""
    doc = Document(doc_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def load_json_schema(schema_path):
    """Loads JSON schema from file."""
    if not os.path.exists(schema_path):
        print(f"Schema file '{schema_path}' not found.")
        return None

    with open(schema_path, "r") as file:
        return json.load(file)

def generate_json(context, prompt):
    """Generates JSON output using Ollama's Mistral model."""
    full_prompt = f"{context}\n\nNow, based on the above documentation, {prompt}"
    
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": full_prompt}])
    
    generated_text = response["message"]["content"]
    
    try:
        generated_json = json.loads(generated_text)
        return generated_json
    except json.JSONDecodeError:
        print("Error: The model response is not valid JSON.")
        return None

def validate_json(json_data, schema):
    """Validates JSON against a loaded schema."""
    if not schema:
        print("Error: Schema not loaded.")
        return False

    try:
        validate(instance=json_data, schema=schema)
        print("JSON is valid! ✅")
        return True
    except ValidationError as e:
        print(f"JSON validation failed: {e.message}")
        return False

def main():
    # Step 1: Load context from DOCX file
    context = load_context_from_docx(DOC_PATH)
    
    # Step 2: Load JSON schema
    schema = load_json_schema(SCHEMA_PATH)
    
    # Step 3: User-defined prompt
    user_prompt = "Create a JSON file for a geothermal reservoir with physical dimensions of 16 km by 14 km (horizontal dimensions) by 5 km (depth). The top boundary condition consists of constant pressure of 1 bar and constant temperature of 25 degrees C. The total flow rate of the deep source input is 100 kg/s, split into 70 kg/s of fluid with an enthalpy of 1,400 kJ/kg, and 30 kg/s of fluid with an enthalpy of 1,100 kJ/kg."
    
    # Step 4: Generate JSON output using AI model
    generated_json = generate_json(context, user_prompt)
    
    if generated_json:
        # Step 5: Save JSON to file
        with open(OUTPUT_JSON, "w") as f:
            json.dump(generated_json, f, indent=4)
        
        print(f"Generated JSON saved to {OUTPUT_JSON}")

        # Step 6: Validate JSON against schema
        validate_json(generated_json, schema)

if __name__ == "__main__":
    main()

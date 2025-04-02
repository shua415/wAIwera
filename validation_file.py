import json
import ollama
import jsonschema
from jsonschema import validate, ValidationError

# Configuration
MODEL_NAME = "mistral"
CONTEXT_FILE = "waiwera_example_jsons.txt"
SCHEMA_FILE = "input_schema.json"

def load_schema(schema_file):
    """Load the JSON schema from a file."""
    try:
        with open(schema_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"❌ Schema file '{schema_file}' not found.")
        return None



def load_context(file_path):
    """Load the markdown context from a .txt file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ Context file '{file_path}' not found. Continuing without it.")
        return ""

def generate_json(prompt, schema, model=MODEL_NAME):
    """Generate a JSON response from the AI model."""
    context = load_context(CONTEXT_FILE)
    schema = load_schema(SCHEMA_FILE)
    messages = [
        {"role": "system", "content": "You are a geothermal engineer that generates valid JSON outputs strictly following a given JSON schema. The schema defines the structure, required fields, and data types. Your response must be a valid JSON object that adheres exactly to the schema."},
        {"role": "user", "content": f"Here are some examples of valid JSON files:\n\n{context}"},
        {"role": "user", "content": f"Here is the schema that shows a valid JSON structure:\n\n{schema}"},
        {"role": "user", "content": f"Now, generate a valid JSON file based on this prompt:\n{prompt}"}
    ]

    response = ollama.chat(model=model, messages=messages)

    raw_output = response['message']['content']  # Raw model output

    # 🔧 Strip whitespace and remove markdown artifacts
    cleaned_output = raw_output.strip("` \n")  # Removes leading/trailing backticks, spaces, and newlines

    try:
        json_output = json.loads(cleaned_output)  # Ensure valid JSON output
        return json_output
    except json.JSONDecodeError as e:
        print("\n❌ JSON Parsing Error:", str(e))
        print("\n⚠️ The output from the model is NOT valid JSON. Here it is for debugging:\n", cleaned_output)
        return None

def validate_json(json_data, schema_file=SCHEMA_FILE):
    """Validate the JSON output against a given schema, and print detailed errors."""
    try:
        with open(schema_file, "r") as schema_file:
            schema = json.load(schema_file)

        validate(instance=json_data, schema=schema)
        print("✅ JSON output is valid according to input_schema.json")
        return True
    except ValidationError as e:
        print(f"\n❌ **JSON Validation Error:** {e.message}")

        # Print detailed path information
        if e.path:
            print(f"🔍 **Error Location in JSON:** {' → '.join(map(str, e.path))}")

        # # Print expected type and received type (if applicable)
        # if "expected" in e.schema and "instance" in e.__dict__:
        #     print(f"📌 **Expected Type:** {e.schema['expected']}")
        #     print(f"📌 **Received Value:** {e.instance}")

        # Print detailed validation error information
        print(f"\n📌 **Full Error Details:**\n{e}")

        return False
    except FileNotFoundError:
        print(f"❌ Schema file '{SCHEMA_FILE}' not found.")
        return False


if __name__ == "__main__":

    schema = load_schema(SCHEMA_FILE)


    # Get prompt from user input
    prompt = input("Enter your prompt: ")

    # Generate JSON
    json_output = generate_json(prompt, schema)

    if json_output:
        print("\n📌 **Formatted JSON Output (if valid):**\n")
        try:
            formatted_json = json.dumps(json_output, indent=4)
            print(formatted_json)
        except TypeError:
            print("\n⚠️ JSON output could not be formatted, printing raw text instead:\n", json_output)

        # Validate JSON output if it was successfully parsed
        if isinstance(json_output, dict):  # Only validate if it was parsed correctly
            validate_json(json_output)
        else:
            print("\n⚠️ JSON validation skipped because output is not a valid JSON object.\n")

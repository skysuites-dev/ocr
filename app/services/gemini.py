import os
import json
import yaml
import textwrap
from vertexai.preview.generative_models import GenerativeModel
from vertexai import init


# ✅ Initialize Vertex AI
init(project="skysuitesbookingapp-7f085", location="us-east1")

# ✅ Load Gemini model
MODEL_NAME = "gemini-2.5-flash-lite"  # or your preferred model
model = GenerativeModel(MODEL_NAME)

def load_policy_text(airline: str, policy_dir: str = r"C:\Users\PMLS\Downloads\ocr_project\app\policy_docs") -> str:
    path = os.path.join(policy_dir, f"{airline.lower().strip()}.yaml")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_fields_from_text(ocr_text: str, doc_type: str, airline: str) -> dict:
    policy_text = load_policy_text(airline)
    prompt = build_prompt(doc_type, ocr_text, policy_text)

    try:
        response = model.generate_content(prompt)

        raw_text = response.text

        json_start = raw_text.find('{')
        json_end = raw_text.rfind('}') + 1
        json_str = raw_text[json_start:json_end]
        structured_data = json.loads(json_str)

        return {
            "structured_data": structured_data,
            "policy_used": policy_text,
            "gemini_output_raw": raw_text,
            "prompt": prompt
        }

    except Exception as e:
        return {"error": f"Gemini Vertex AI error: {str(e)}"}

def build_prompt(doc_type: str, ocr_text: str, policy_text: str) -> str:
    doc_type = doc_type.lower()
    policy_section = f"\n--- AIRLINE POLICY RULES ---\n{textwrap.dedent(policy_text)}\n--- END POLICY ---\n" if policy_text else ""

    if doc_type == "cnic":
        return f"""
You are a document data extraction AI designed for airline passenger autofill. Extract only English values from a CNIC (national ID) OCR.

Follow airline policy rules if provided.

Rules:
- Extract `full_name`, and split into `first_name`, `middle_name`, `last_name`
- Use 'M', 'F', or 'O' for `gender`
- Salutation:
  - 'Mr' for male
  - 'Ms' if unmarried female
- Use `husband_name` only if 'wife of' is present
- Otherwise use `father_name`
- CNIC number format: 13 digits with hyphens (xxxxx-xxxxxxx-x)
- DOB in YYYY-MM-DD format
- Extract nationality if present in English

--- OCR TEXT ---
{textwrap.dedent(ocr_text)}
{policy_section}
Return clean JSON (leave unknown fields as empty strings):

{{
  "full_name": "",
  "first_name": "",
  "middle_name": "",
  "last_name": "",
  "identity_number": "",
  "dob": "",
  "gender": "",
  "salutation": "",
  "father_name": ""
}}
"""
    elif doc_type == "passport":
        return f"""
You are a document data extraction AI designed for airline booking autofill. Extract only English values from a passport OCR.

Rules:
- Extract `full_name` and split into `first_name`, `middle_name`, `last_name`
- Use 'M', 'F', or 'O' for `gender`
- Salutation:
  - 'Mr' for male
  - 'Ms' if unmarried female
- Use `husband_name` only if 'wife of' is present
- Otherwise use `father_name`
- Passport number: Alphanumeric (usually 8–10 characters)
- Passport expiry: YYYY-MM-DD
- Passport country: Extract as full country or ISO 3-letter code
- DOB in YYYY-MM-DD format
- Extract nationality if mentioned (not just issuing country)

--- OCR TEXT ---
{textwrap.dedent(ocr_text)}
{policy_section}
Return clean JSON (leave unknown fields as empty strings):

{{
  "full_name": "",
  "first_name": "",
  "middle_name": "",
  "last_name": "",
  "passport_number": "",
  "passport_country": "",
  "passport_expiry": "",
  "dob": "",
  "gender": "",
  "salutation": "",
  "father_name": ""
}}
"""
    else:
        return "Unsupported document type."

 

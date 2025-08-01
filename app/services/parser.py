from app.services.gemini import extract_fields_from_text

def extract_cnic_fields(text: str) -> dict:
    return extract_fields_from_text(text, doc_type="cnic")

def parse_passport_data(text: str) -> dict:
    return extract_fields_from_text(text, doc_type="passport")

from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse
import tempfile
from datetime import datetime
from app.services.ocr import extract_text
from app.services.gemini import extract_fields_from_text

router = APIRouter()

# Utility: Age calculation
def calculate_age(dob_str: str) -> int:
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except Exception:
        return None

# Passenger type validator
def validate_passenger_type(dob: str, passenger_type: str):
    age = calculate_age(dob)
    pt = passenger_type.lower()

    if age is None:
        return JSONResponse(
            status_code=422,
            content={"status": 422, "message": "Please rescan your document again!"}
        )

    if pt == "infant" and not (0 <= age < 2):
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": "Invalid passenger type: Not an infant."}
        )
    elif pt == "child" and not (2 <= age < 12):
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": "Invalid passenger type: Not a child."}
        )
    elif pt == "adult" and not (age >= 12):
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": "Invalid passenger type: Not an adult."}
        )
    return None  # Valid case

@router.post("/scan")
async def scan_document(
    file: UploadFile = File(...),
    doc_type: str = Query(...),
    passenger_type: str = Query(...),
    airline: str = Query(...)
):
    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    # Step 1: OCR
    ocr_text = extract_text(tmp_path)
    print("🔍 OCR TEXT:")
    print(ocr_text)

    # Step 2: Gemini with airline policy
    extracted_data = extract_fields_from_text(ocr_text, doc_type, airline)
    print("🧠 Gemini Output:")
    print(extracted_data)

    if "error" in extracted_data:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": extracted_data["error"]}
        )

    # Step 3: Passenger type check (based on DOB)
    structured = extracted_data.get("structured_data", {})
    dob = structured.get("dob")

    if not dob:
        print("❌ DOB missing in structured_data:", structured)
        return JSONResponse(
            status_code=422,
            content={"status": 422, "message": "DOB missing from document. Please scan again!"}
        )

    # Validate passenger type
    validation_error = validate_passenger_type(dob, passenger_type)
    if validation_error:
        return validation_error

    # Step 4: Return to frontend
    return {
        "status": "success",
        "corrected_json": structured,
    }

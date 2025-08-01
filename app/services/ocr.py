#ocr.py
from google.cloud import vision
import io
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"skysuitesbookingapp-7f085-cdd2ab2069b4.json"

def preprocess_image(image_path: str) -> str:
    # Not needed unless you're doing local enhancement
    return image_path

def extract_text(image_path: str) -> str:
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(f'{response.error.message}')

    return texts[0].description if texts else ""

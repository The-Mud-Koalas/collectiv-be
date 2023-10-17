import json
import requests
from communalspace.settings import HUGGING_FACE_ACCESS_TOKEN, TOKEN_CLASSIFICATION_ENDPOINT


def recognize_entities_from_text(text):
    headers = {"Authorization": f"Bearer {HUGGING_FACE_ACCESS_TOKEN}"}
    data = json.dumps({"inputs": text, "options": {"wait_for_model": True}})
    response = requests.request("POST", TOKEN_CLASSIFICATION_ENDPOINT, headers=headers, data=data)
    ner = json.loads(response.content.decode("utf-8"))
    return ner

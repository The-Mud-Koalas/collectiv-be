import requests
import json
from communalspace.settings import SENTIMENT_ANALYSIS_ENDPOINT, HUGGING_FACE_ACCESS_TOKEN


def compute_sentiment_score_from_text(text):
    headers = {"Authorization": f"Bearer {HUGGING_FACE_ACCESS_TOKEN}"}
    data = json.dumps({"inputs": [text], "options": {"wait_for_model": True}})
    response = requests.request("POST", SENTIMENT_ANALYSIS_ENDPOINT, headers=headers, data=data)
    sentiment = json.loads(response.content.decode("utf-8"))
    sentiment_scores = sentiment[0]

    positive_weight = 1
    negative_weight = -1
    neutral_weight = 0.25

    overall_score = 0
    for score in sentiment_scores:
        if score['label'] == "positive":
            overall_score += positive_weight * score['score']
        elif score['label'] == "negative":
            overall_score += negative_weight * score['score']
        elif score['label'] == 'neutral':
            overall_score += neutral_weight * score['score']

    # map [-1, 1] to [0, 1]
    overall_score = (overall_score + 1) * 0.5

    return overall_score

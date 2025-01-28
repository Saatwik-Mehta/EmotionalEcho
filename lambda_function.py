import json
from person_mood_detector import get_persons_mood
from mood_enhancer import recommend_help
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    This function will trigger the functionalities based on path received
    - detect_mood: It will pass the mood of the face uploaded
    - recommend: it will recommend the movies, music, books, quotes etc.
    """
    try:
        LOGGER.info("event received: %s", event)
        response = {}
        if event["path"] == "/detect_mood":
            response = get_persons_mood(event, context)
        if event["path"] == "/recommend":
            response = recommend_help(event, context)
        return {
            "statusCode": 200,
            "body": json.dumps(response),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }
    except Exception as e:
        LOGGER.error("Error: %s", e, exc_info=True)
        return {
            "statusCode": 400,
            "error": json.dumps(e),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }


if __name__ == "__main__":
    event = {"path": "/recommend", "body": json.dumps({"mood": "SAD"})}
    lambda_handler(event, None)
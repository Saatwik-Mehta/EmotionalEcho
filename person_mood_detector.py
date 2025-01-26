import boto3
import base64
from botocore.exceptions import ClientError
import logging

rekognition_client = boto3.client("rekognition")

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
import json
class PhotoDoesNotMeetRequirementError(Exception):
    """Error raised when either there are multiple faces in the image uploaded/image has sunglasses"""

    def __init__(self, message):
        self.message = message

def face_detector_encoded(image_coded):
    """
    It takes in a filename, and returns a list of face details if the image meets the requirements
    :param filename: the name of the image file in the S3 bucket
    :param bucket_name: the name of the S3 bucket in which the image is stored
    :return: The face_details is a list of dictionaries. Each dictionary contains the attributes of the face detected in the
    image.
    """

    try:
        LOGGER.info("Started the face detection process")
        response = rekognition_client.detect_faces(
            Image={"Bytes": image_coded},
            Attributes=["ALL"],
        )
    except ClientError as exception:
        print("error ", exception)
        # handling for invalid image format exception
        if type(exception).__name__ == "InvalidImageFormatException":
            message = "Invalid image format"
        # handling for too large image exception
        elif type(exception).__name__ == "ImageTooLargeException":
            message = "Image uploaded too large"
        else:
            message = type(exception).__name__
        raise PhotoDoesNotMeetRequirementError(message)
    else:
        face_details = response["FaceDetails"]
        # Extract the emotions list
        if not face_details:
            message = "No face detected"
            raise PhotoDoesNotMeetRequirementError(message)

        emotions = face_details[0]["Emotions"]
        # Find the emotion with the highest confidence
        if not emotions:
            return "UNKNOWN"
        
        most_confident_emotion = max(emotions, key=lambda x: x['Confidence'])
        return most_confident_emotion["Type"]

def get_persons_mood(event, context):
    try:
        LOGGER.info("Started the person mood: : %s", event)
        body = json.loads(event.get("body"))
        LOGGER.info("Started the person mood: : %s", body)

        base64_image = body["base64"]
        LOGGER.info("Started the person mood: : %s", base64_image)

        isface= "UNKNOWN"
        if base64_image:
            image_decode = base64.b64decode(base64_image)
            isface = face_detector_encoded(image_decode)
            if not isface:
                raise Exception("No face Detected")

        return {"mood": isface}
    except PhotoDoesNotMeetRequirementError as error:
        LOGGER.error(error, exc_info=True)
        raise Exception(error)

    except Exception as error:
        if "InvalidParameterException" in error.args[0]:
            raise Exception("No face detected in the image")
        LOGGER.error(error, exc_info=True)
        raise Exception("Internal Server Error", error)

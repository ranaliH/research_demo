from io import BytesIO
from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import cv2
from keras.models import load_model

# Set up OCR client
subscription_key = '77a5454213d44ddcaeb068aa38621dfa'
endpoint = 'https://ocrmodel.cognitiveservices.azure.com/'
credentials = CognitiveServicesCredentials(subscription_key)
vision_client = ComputerVisionClient(endpoint, credentials)

# Define filter class labels
class_labels = ["1977", "Aden", "Amaro", "Apollo", "Ashby", "Brannan", "Clarendon", "Crema", "Dogpatch", "Earlybird",
                "Gingham", "Ginza", "Gotham", "Hefe", "Helena", "Hudson", "Inkwell", "Juno", "Kelvin", "Lark",
                "Lo-fi", "Ludwig", "Maven", "Mayfair", "Moon", "Nashville", "Normal", "Poprocket", "Prepetua",
                "Reyes", "Rise", "Sierra", "Skyline", "Slumber", "Stinson", "Sutro", "Toaster", "Valencia",
                "Vesper", "Walden", "Willow", "X pro 2"]

# Define emotion class labels
emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# Azure Blob Storage connection string
connection_string = 'DefaultEndpointsProtocol=https;AccountName=scrapeddataforapp;AccountKey=PlqU9/MzDy5yF9Si4xhLoGTk7jTg1XkR2V0IAQOSPkR+JTDYz1VByxUcSqd/WAj/ZW8wI9SDiZnv+ASt2IxVsw==;EndpointSuffix=core.windows.net'

# Blob storage container
container_name = 'igscrapedata'

# Connect to Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

# Load the filter classification model
model_path = 'C:\\Users\\HP\\Documents\\Y4 S2\\research\\models & other\\models\\filters\\.h5\\filter_classification_model_faced_e25_bs128_f3.h5'
model = load_model(model_path)

# Load the pickle file - Model for depression recognition
depression_model_path = 'C:\\Users\\HP\\Documents\\Y4 S2\\research\\models & other\\models\\NLP test code\\depression_recognition_model2.pickle'
with open(depression_model_path, 'rb') as file:
    depression_model = pickle.load(file)

# Load the pickle file - Vectorizer for depression recognition
vectorizer_path = 'C:\\Users\\HP\\Documents\\Y4 S2\\research\\models & other\\models\\NLP test code\\vectorizer.pkl'
with open(vectorizer_path, 'rb') as file:
    vectorizer = pickle.load(file)

# Load the emtions classification model
emotions_model_path = 'C:\\Users\\HP\\Documents\\Y4 S2\\research\\models & other\\models\\emotions\\.h5\\emotions_classification_model_2.h5'
e_model = load_model(emotions_model_path)

# Set the weights for filter and text classifications
filter_weight = 0.3
text_weight = 0.4
emotion_weight = 0.3


def img_predictions():
    # Function to perform OCR on an image
    def ocr_image(image_data):
        result = vision_client.recognize_printed_text_in_stream(image_data)
        extracted_text = []
        for region in result.regions:
            for line in region.lines:
                for word in line.words:
                    extracted_text.append(word.text)
        return extracted_text

    # Process each image
    for blob in container_client.list_blobs():
        blob_client = container_client.get_blob_client(blob.name)
        blob_data = blob_client.download_blob().readall()
        image_stream = BytesIO(blob_data)

        # Load and preprocess the input image for filter classification
        input_image = cv2.imdecode(np.frombuffer(image_stream.getvalue(), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if input_image.shape[2] == 4:
            input_image = cv2.cvtColor(input_image, cv2.COLOR_RGBA2RGB)
        input_image = cv2.resize(input_image, (128, 128))
        input_array = np.expand_dims(input_image, axis=0)
        input_array = input_array / 255.0

        # Get the model predictions for filter classification
        filter_predictions = model.predict(input_array)
        filter_class_index = np.argmax(filter_predictions)
        filter_class_label = class_labels[filter_class_index]

        # Load and preprocess the input image for filter classification
        input_image_e = input_image
        if input_image_e.shape[2] == 4:
            input_image_e = cv2.cvtColor(input_image, cv2.COLOR_RGBA2RGB)

        input_image_e = cv2.resize(input_image_e, (128, 128))
        input_array_e = np.expand_dims(input_image_e, axis=0)
        input_array_e = input_array_e / 255.0

        # Get the model predictions for emotions calssification
        predictions = e_model.predict(input_array_e)
        emotion_class_index = np.argmax(predictions)
        predicted_emotion = emotion_labels[emotion_class_index]

        # Print the filter prediction for the image
        print("Image:", blob.name)

        if filter_class_label != "No_Filter":
            print("Filter Prediction:", filter_class_label)
            if filter_class_label == 'Vesper' or 'Ginza' or 'Lark' or 'Aden' or 'Gingham' or 'Ludwig' or 'Skyline' or 'Helena' or 'Dogpatch' or 'Sutro' or 'Perpetua' or 'Juno' or 'Ashby' or 'Slumber' or 'Stinson' or 'Rayes' or 'Willow' or 'Crema' or 'Inkwell':
                print('Filter Depression Prediction: Depressed')
                filter_w = 1
            elif filter_class_label == '1977' or 'Amaro' or 'Apollo' or 'Brannan' or 'Clarendon' or 'Crema' or 'Earlybird' or 'Gingham' or 'Gotham' or 'Hefe' or 'Hudson' or 'Inkwell' or 'Kelvin' or 'Lark' or 'Lo-fi' or 'Maven' or 'Mayfair' or 'Moon' or 'Nashville' or 'Normal' or 'Poprocket' or 'Prepetua' or 'Reyes' or 'Rise' or 'Sierra' or 'Skyline' or 'Toaster' or 'Valencia' or 'Vesper' or 'Walden' or 'Willow' or 'X pro 2':
                print('Filter Depression Prediction: Not Depressed')
                filter_w = 0
        else:
            print("No filter detected.")

        # Find the predicted emotion label
        print("Predicted Emotion:", predicted_emotion)

        if predicted_emotion == 'angry':
            emotion_w = 1
        if predicted_emotion == 'disgust':
            emotion_w = 1
        if predicted_emotion == 'fear':
            emotion_w = 1
        if predicted_emotion == 'happy':
            emotion_w = 0
        if predicted_emotion == 'neutral':
            emotion_w = 0
        if predicted_emotion == 'sad':
            emotion_w = 1
        if predicted_emotion == 'surprise':
            emotion_w = 0

        # Perform OCR on the image
        extracted_text = ocr_image(image_stream)

        if extracted_text:
            # Preprocess the extracted text
            preprocessed_text = [text.lower() for text in extracted_text]
            all_sentences = ' '.join(preprocessed_text).split('.')
            sentences = [sentence.strip() for sentence in all_sentences if sentence.strip()]

            if sentences:
                # Transform the preprocessed text into numerical features
                input_features = vectorizer.transform(sentences)

                # Make predictions for depression recognition
                depression_predictions = depression_model.predict(input_features)

                # Print the depression prediction for the image
                print("Text Depression Prediction:", depression_predictions[0])
                print()
                text_w = 1
            else:
                print("No sentences with text detected.")
                print()
                text_w = 0
        else:
            print("No text detected.")
            print()
            text_w = 0
            print()

        # calculation
        stresspred = ((filter_weight * filter_w) + (text_weight * text_w) + (emotion_weight * emotion_w))
        if stresspred >= 0.7:
            fianlpred = 'Stress'
            print("Stress")
        else:
            fianlpred = 'No Stress'
            print("No Stress")

        print()

        return fianlpred

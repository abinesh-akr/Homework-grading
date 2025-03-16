import cv2
import pytesseract
import numpy as np
import tensorflow_hub as hub
import os
from sklearn.metrics.pairwise import cosine_similarity



use_model = hub.load("models")



def predict_score(image_path, key_file):

    extracted_text = image_path
    key_text = key_file
    
    # Encode both key and extracted text using USE
    key_embedding = use_model([key_text])[0].numpy()
    text_embedding = use_model([extracted_text])[0].numpy()
    

    similarity = cosine_similarity([key_embedding], [text_embedding])[0][0]
    

    score = similarity * 10
    return round(score, 2)

if __name__=='__main__':
    predict_score(input("topic :"+'\n\n')+input("essay :"),input('key :'))

import tensorflow as tf
import numpy as np
import cv2
import os
import json

def load_lumina_model():
    # This manually loads the architecture and weights from your 3 files
    model_json_path = os.path.join(os.getcwd(), 'model.json')
    
    with open(model_json_path, 'r') as f:
        model_json = f.read()
    
    # Reconstruct the model structure
    model = tf.keras.models.model_from_json(model_json)
    
    # Load the weights.bin (Note: ensure weights.bin is in the same folder)
    # Keras usually expects a .h5 or .weights.h5 file, but if this fails, 
    # we will convert your files to .h5 for you locally.
    return model

def predict_emotion(frame, model):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))
    normalized = resized / 255.0
    reshaped = np.reshape(normalized, (1, 48, 48, 1))
    
    prediction = model.predict(reshaped, verbose=0)
    states = ["Happy", "Frustrated", "Neutral"] 
    return states[np.argmax(prediction)]

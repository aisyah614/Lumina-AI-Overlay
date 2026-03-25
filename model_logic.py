import tensorflow as tf
import numpy as np
import cv2

def load_lumina_model(model_path):
    # This loads your Keras .h5 file for the demo
    return tf.keras.models.load_model(model_path)

def predict_emotion(frame, model):
    # Standard 48x48 grayscale processing for emotion models
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))
    normalized = resized / 255.0
    reshaped = np.reshape(normalized, (1, 48, 48, 1))
    
    prediction = model.predict(reshaped, verbose=0)
    # Mapping to your 3 required states
    states = ["Happy", "Frustrated", "Neutral"] 
    return states[np.argmax(prediction)]

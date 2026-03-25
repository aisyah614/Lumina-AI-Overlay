import tensorflowjs as tfjs
import tensorflow as tf
import numpy as np
import cv2
import os

def load_lumina_model():
    # This specifically looks for your 'model.json' file in the repo
    model_path = os.path.join(os.getcwd(), 'model.json') 
    return tfjs.converters.load_keras_model(model_path)

def predict_emotion(frame, model):
    # 1. Standard 48x48 processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))
    
    # 2. Add color channel if your model expects it
    normalized = resized / 255.0
    reshaped = np.reshape(normalized, (1, 48, 48, 1))
    
    # 3. Predict mapping to your 3 states
    prediction = model.predict(reshaped, verbose=0)
    
    # Map the indices to your required project states
    states = ["Happy", "Frustrated", "Neutral"] 
    return states[np.argmax(prediction)]

import numpy as np
import cv2
import av
from keras.models import load_model
from keras.preprocessing.image import img_to_array

# --- 1. RESEARCH ENGINE CONFIG ---
# Ensure these labels match your model's training classes exactly
emotion_dict = {0: 'Neutral', 1: 'Happy', 2: 'Frustrated'}

# Load the classifier globally so it doesn't reload on every frame
try:
    classifier = load_model('model/keras_model.h5')
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except Exception as e:
    print(f"Error loading model/cascades: {e}")

class VideoProcessor:
    def __init__(self):
        self.last_emotion = "Neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # 1. Preprocessing: Convert to Gray
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Detection
        faces = face_cascade.detectMultiScale(
            image=img_gray, 
            scaleFactor=1.3, 
            minNeighbors=5
        )

        detected_state = "Neutral"

        for (x, y, w, h) in faces:
            # Draw Lumina's detection box
            cv2.rectangle(img=img, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0), thickness=2)
            
            # 3. Emotion Prediction Logic
            roi_gray = img_gray[y:y + h, x:x + w]
            roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

            if np.sum([roi_gray]) != 0:
                # Preprocessing matching your FER training
                roi = roi_gray.astype('float') / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)
                
                prediction = classifier.predict(roi, verbose=0)[0]
                maxindex = int(np.argmax(prediction))
                detected_state = emotion_dict.get(maxindex, "Neutral")
                
                # UI Overlay on camera feed
                cv2.putText(img, f"Lumina: {detected_state}", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(img, 'No Faces', (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Store for App.py to read
        self.last_emotion = detected_state
        return av.VideoFrame.from_ndarray(img, format="bgr24")

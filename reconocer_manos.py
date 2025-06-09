import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
import warnings
warnings.filterwarnings("ignore")

import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            model_complexity=0  # Reduce complejidad para menos warnings
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def get_finger_position(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                index_finger = hand_landmarks.landmark[8]  # Punta del dedo índice
                h, w, _ = frame.shape
                x, y = int(index_finger.x * w), int(index_finger.y * h)
                cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)
                return (x, y)
        return None
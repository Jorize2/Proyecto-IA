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
    
    def is_fist(self, frame):
        # Usa MediaPipe para detectar si todos los dedos (excepto el pulgar) están doblados
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Landmarks de las puntas de los dedos
                tips_ids = [8, 12, 16, 20]
                folded = 0
                for tip_id in tips_ids:
                    tip = hand_landmarks.landmark[tip_id]
                    pip = hand_landmarks.landmark[tip_id - 2]
                    if tip.y > pip.y:  # El dedo está doblado
                        folded += 1
                if folded == 4:
                    return True
        return False
    
    def is_ok_gesture(self, frame):
        # Detecta si la punta del índice y la del pulgar están muy cerca (gesto OK)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                h, w, _ = frame.shape
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                distance = ((thumb_x - index_x) ** 2 + (thumb_y - index_y) ** 2) ** 0.5
                if distance < 40:  # Puedes ajustar el umbral según tu cámara
                    return True
        return False
    
    def is_pinky_only(self, frame):
        # Detecta si solo el meñique está extendido y los demás doblados
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Landmarks de las puntas de los dedos
                tips_ids = [8, 12, 16, 20]  # Índice, medio, anular, meñique
                extended = []
                for tip_id in tips_ids:
                    tip = hand_landmarks.landmark[tip_id]
                    pip = hand_landmarks.landmark[tip_id - 2]
                    extended.append(tip.y < pip.y)  # True si el dedo está extendido
                # Solo el meñique extendido
                if extended == [False, False, False, True]:
                    return True
        return False
    
    def is_cuernos_gesture(self, frame):
        # Detecta si solo índice y meñique están extendidos, medio y anular doblados
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Índice (8), medio (12), anular (16), meñique (20)
                tips_ids = [8, 12, 16, 20]
                extended = []
                for tip_id in tips_ids:
                    tip = hand_landmarks.landmark[tip_id]
                    pip = hand_landmarks.landmark[tip_id - 2]
                    extended.append(tip.y < pip.y)  # True si el dedo está extendido
                # Solo índice y meñique extendidos
                if extended == [True, False, False, True]:
                    return True
        return False
    
    def is_inverted_l_gesture(self, frame):
        # Detecta si solo índice y pulgar están extendidos, los demás doblados
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Pulgar (4), índice (8), medio (12), anular (16), meñique (20)
                # Pulgar: extendido si x_tip > x_ip (mano derecha, palma hacia cámara)
                thumb_tip = hand_landmarks.landmark[4]
                thumb_ip = hand_landmarks.landmark[3]
                thumb_extended = thumb_tip.x > thumb_ip.x
                # Índice, medio, anular, meñique: extendido si tip.y < pip.y
                tips_ids = [8, 12, 16, 20]
                extended = []
                for tip_id in tips_ids:
                    tip = hand_landmarks.landmark[tip_id]
                    pip = hand_landmarks.landmark[tip_id - 2]
                    extended.append(tip.y < pip.y)
                # Solo pulgar e índice extendidos
                if thumb_extended and extended == [True, False, False, False]:
                    return True
        return False
    
    def is_heart_gesture(self, frame):
        # Detecta si pulgar e índice están tocándose (corazón) y los demás doblados
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                h, w, _ = frame.shape
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                distance = ((thumb_x - index_x) ** 2 + (thumb_y - index_y) ** 2) ** 0.5
                # Los otros dedos deben estar doblados
                folded = 0
                for tip_id in [12, 16, 20]:
                    tip = hand_landmarks.landmark[tip_id]
                    pip = hand_landmarks.landmark[tip_id - 2]
                    if tip.y > pip.y:
                        folded += 1
                # Ajuste de sensibilidad: distancia < 60 (más permisivo)
                if distance < 60 and folded == 3:
                    return True
        return False
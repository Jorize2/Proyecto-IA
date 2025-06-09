import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Silencia TensorFlow
import warnings
warnings.filterwarnings("ignore")  # Silencia otros warnings
import pygame  
import cv2  
from vision_teclado import KeyboardUI  
from reconocer_manos import HandTracker  
from configurarcion import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT  

def main():  
    pygame.init()  
    keyboard_ui = KeyboardUI()  
    tracker = HandTracker()  
    cap = cv2.VideoCapture(CAMERA_INDEX)  
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)  
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)  

    # Temporizadores  
    key_timer = 0  
    suggestion_timer = 0  
    running = True  

    while running:  
        current_time = pygame.time.get_ticks()  
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  
                running = False  

        ret, frame = cap.read()  
        if not ret:  
            continue  

        frame = cv2.flip(frame, 1)  
        finger_pos = tracker.get_finger_position(frame)  

        if finger_pos:  
            # Mapeo de coordenadas  
            screen_width, screen_height = keyboard_ui.screen.get_size()  
            mapped_x = int(finger_pos[0] * screen_width / FRAME_WIDTH)  
            mapped_y = int(finger_pos[1] * screen_height / FRAME_HEIGHT)  

            # Verificar sugerencias (con delay de 3 segundos)  
            if keyboard_ui.check_suggestion_click((mapped_x, mapped_y)):  
                if suggestion_timer == 0:  
                    suggestion_timer = current_time  
                elif current_time - suggestion_timer >= 1599:  # 3 segundos  
                    suggestions = keyboard_ui.logic.get_suggestions()  
                    if suggestions and keyboard_ui.suggestion_highlight is not None:  
                        keyboard_ui.logic.select_suggestion(suggestions[keyboard_ui.suggestion_highlight])  
                        suggestion_timer = 0  
            else:  
                suggestion_timer = 0  

            # Selección de teclas  
            keyboard_ui.logic.update_selection((mapped_x, mapped_y))  
            if keyboard_ui.logic.selected_key:  
                if key_timer == 0:  
                    key_timer = current_time  
                elif current_time - key_timer >= 2000:  # 2 segundos  
                    keyboard_ui.select_key()  
                    key_timer = 0  
        else:  
            key_timer = 0  
            suggestion_timer = 0  

        keyboard_ui.draw()  
        cv2.imshow("Cámara", frame)  
        if cv2.waitKey(1) & 0xFF == 27:  
            running = False  

    cap.release()  
    cv2.destroyAllWindows()  
    pygame.quit()  

if __name__ == "__main__":  
    main()  
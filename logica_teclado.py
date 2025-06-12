import pygame
import os
from configuracion import *
from modelo_palabras.sugeridor_palabras import LSTMSuggester

class KeyboardLogic:
    def __init__(self):
        # Configuración del modelo con resguardos
        self.suggestion_model = LSTMSuggester(max_length=10)
        model_path = 'modelo_palabras/lstm_model.joblib'
        
        try:
            if os.path.exists(model_path):
                print("Cargando modelo preentrenado...")
                self.suggestion_model.load_model(model_path)
                print(f"Modelo cargado. Vocabulario: {len(self.suggestion_model.word_freq)} palabras")
            else:
                print("Entrenando nuevo modelo...")
                self.suggestion_model.train_from_file('modelo_palabras/palabras.txt')
                self.suggestion_model.save_model(model_path)
                print("Modelo entrenado y guardado.")
        except Exception as e:
            print(f"Error crítico: {str(e)}")
            print("Usando modelo de emergencia con vocabulario básico...")
            self.suggestion_model.train(["hola", "holanda", "hondo", "casa", "cama"])

        # Configuración del teclado
        pygame.mixer.init()
        self.sound_click = pygame.mixer.Sound('sounds/click.wav')
        self.current_text = ""
        self.selected_key = None
        self.caps_lock = False
        self.key_layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'ñ'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', ';'],
            ['BORRAR', 'ESPACIO', 'MAYUS']
        ]
        self.key_rects = self._init_key_rects()

    def _init_key_rects(self):
        rects = []
        key_height = KEYBOARD_HEIGHT // len(self.key_layout)
        for row_idx, row in enumerate(self.key_layout):
            row_rects = []
            key_width = KEYBOARD_WIDTH // len(row)
            for col_idx in range(len(row)):
                x = col_idx * key_width
                y = TEXT_AREA_HEIGHT + SUGGESTIONS_HEIGHT + row_idx * key_height
                row_rects.append(pygame.Rect(x, y, key_width, key_height))
            rects.append(row_rects)
        return rects

    def update_selection(self, gaze_pos):
        self.selected_key = None
        for row_idx, row in enumerate(self.key_rects):
            for col_idx, rect in enumerate(row):
                if rect.collidepoint(gaze_pos):
                    self.selected_key = (row_idx, col_idx)
                    return

    def select_key(self, key):
        self.sound_click.play()
        if key == 'ESPACIO':
            self.current_text += ' '
        elif key == 'BORRAR':
            self.current_text = self.current_text[:-1]
        elif key == 'MAYUS':
            self.caps_lock = not self.caps_lock
        else:
            self.current_text += key.upper() if self.caps_lock else key.lower()
        print(f"Texto actualizado: '{self.current_text}'")  # Debug

    def get_suggestions(self):
        if not self.current_text.strip():
            return []
        
        try:
            last_word = self.current_text.split()[-1].lower()
            print(f"Buscando sugerencias para: '{last_word}'")  # Debug
            suggestions = self.suggestion_model.suggest_words(last_word)
            print(f"Sugerencias encontradas: {suggestions}")  # Debug
            return suggestions
        except Exception as e:
            print(f"Error en get_suggestions(): {str(e)}")
            return []

    def select_suggestion(self, suggestion):
        if suggestion:
            words = self.current_text.split()
            if words:
                self.current_text = ' '.join(words[:-1]) + " " + suggestion
            else:
                self.current_text = suggestion
            print(f"Sugerencia seleccionada: '{suggestion}'")  # Debug
            self.sound_click.play()
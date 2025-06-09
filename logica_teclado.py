from collections import Counter  
import pygame  
import nltk  
from nltk.corpus import cess_esp  
from configurarcion import *  

class KeyboardLogic:  
    def __init__(self):  
        try:  
            palabras_es = [word.lower() for word in cess_esp.words() if word.isalpha() and 3 <= len(word) <= 10]  
            self.suggestion_model = Counter(palabras_es)  
        except:  
            print("Error: Ejecuta nltk.download('cess_esp')")  
            self.suggestion_model = Counter()  

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
            ['MAYUS', 'ESPACIO', 'BORRAR']  
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

    def get_suggestions(self):  
        if not self.current_text.strip():  
            return []  
        last_word = self.current_text.split()[-1].lower()  
        return [w for w in self.suggestion_model if w.startswith(last_word)][:3]  

    def select_suggestion(self, suggestion):  
        if suggestion:  
            words = self.current_text.split()  
            self.current_text = ' '.join(words[:-1]) + " " + suggestion + " "  
            self.sound_click.play()
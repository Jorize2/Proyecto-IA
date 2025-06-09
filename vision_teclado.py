import pygame  
from configurarcion import *  
from logica_teclado import KeyboardLogic  

class KeyboardUI:  
    def __init__(self):  
        self.screen = pygame.display.set_mode((KEYBOARD_WIDTH, TEXT_AREA_HEIGHT + SUGGESTIONS_HEIGHT + KEYBOARD_HEIGHT))  
        self.logic = KeyboardLogic()  
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)  
        self.text_font = pygame.font.SysFont(FONT_NAME, TEXT_FONT_SIZE)  
        self.suggestion_highlight = None  
        self.cursor_visible = True  
        self.cursor_timer = 0  

    def draw(self):  
        self.screen.fill(BACKGROUND_COLOR)  
        self._draw_text_area()  
        self._draw_suggestions()  
        self._draw_keyboard()  
        pygame.display.flip()  

    def _draw_text_area(self):  
        # Área blanca con texto negro
        pygame.draw.rect(self.screen, TEXT_BG_COLOR, (0, 0, KEYBOARD_WIDTH, TEXT_AREA_HEIGHT))  
        font = self.text_font  
        words = self.logic.current_text.split()  
        lines = []  
        current_line = ""  
        
        for word in words:  
            test_line = current_line + " " + word if current_line else word  
            if font.size(test_line)[0] < KEYBOARD_WIDTH - 40:  
                current_line = test_line  
            else:  
                lines.append(current_line)  
                current_line = word  
        lines.append(current_line)  
        
        y_offset = 10  
        for line in lines[-2:]:  
            text_surface = font.render(line, True, TEXT_COLOR)  # Texto negro
            self.screen.blit(text_surface, (20, y_offset))  
            y_offset += TEXT_FONT_SIZE + 5  

        # Cursor negro sobre fondo blanco
        current_time = pygame.time.get_ticks()  
        if current_time - self.cursor_timer > 500:  
            self.cursor_visible = not self.cursor_visible  
            self.cursor_timer = current_time  
        
        if self.cursor_visible:  
            cursor_x = 25 + font.size(lines[-1] if lines else "")[0]  
            pygame.draw.rect(
                self.screen, 
                (0, 0, 0),  # Cursor negro
                (cursor_x, y_offset - TEXT_FONT_SIZE - 5, 2, TEXT_FONT_SIZE)
            )

    def _draw_suggestions(self):  
        # Fondo verde claro B2CD9C
        pygame.draw.rect(self.screen, SUGGESTIONS_COLOR, (0, TEXT_AREA_HEIGHT, KEYBOARD_WIDTH, SUGGESTIONS_HEIGHT))  
        suggestions = self.logic.get_suggestions()  
        for i, suggestion in enumerate(suggestions):  
            suggestion_rect = pygame.Rect(10 + i * 200, TEXT_AREA_HEIGHT + 10, 190, SUGGESTIONS_HEIGHT - 20)  
            
            if self.suggestion_highlight == i:  
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, suggestion_rect, 3)  
            
            # Texto negro sobre fondo verde claro
            text = self.font.render(suggestion, True, (0, 0, 0))  
            self.screen.blit(text, (suggestion_rect.x + 10, suggestion_rect.y + 10))  

    def _draw_keyboard(self):
        for row_idx, row in enumerate(self.logic.key_layout):
            for col_idx, key in enumerate(row):
                rect = self.logic.key_rects[row_idx][col_idx]
                
                # Colores específicos según tu petición:
                if row_idx == 0:  # Fila de números (F0F2BD)
                    color = KEY_COLOR1
                    text_color = (0, 0, 0)  # Texto negro
                elif row_idx < 3:  # Filas de letras (CA7842)
                    color = KEY_COLOR2
                    text_color = (255, 255, 255)  # Texto blanco
                else:  # Fila especial (4B352A)
                    color = KEY_COLOR3
                    text_color = (255, 255, 255)  # Texto blanco
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
                
                if self.logic.selected_key == (row_idx, col_idx):
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, rect, 3)
                
                # Manejo de texto (mayúsculas/minúsculas)
                key_text = key
                if key == 'MAYUS':
                    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE, bold=True)
                    key_text = "MAYUS"
                else:
                    font = self.font
                    if self.logic.caps_lock and key.isalpha():
                        key_text = key.upper()
                
                text_surface = font.render(key_text, True, text_color)
                text_rect = text_surface.get_rect(center=rect.center)
                self.screen.blit(text_surface, text_rect)

    def check_suggestion_click(self, pos):  
        suggestions = self.logic.get_suggestions()  
        for i, suggestion in enumerate(suggestions):  
            suggestion_rect = pygame.Rect(10 + i * 200, TEXT_AREA_HEIGHT + 10, 190, SUGGESTIONS_HEIGHT - 20)  
            if suggestion_rect.collidepoint(pos):  
                self.suggestion_highlight = i  
                return True  
        self.suggestion_highlight = None  
        return False  

    def select_key(self):  
        if self.logic.selected_key:  
            row, col = self.logic.selected_key  
            self.logic.select_key(self.logic.key_layout[row][col])  
            return True  
        return False
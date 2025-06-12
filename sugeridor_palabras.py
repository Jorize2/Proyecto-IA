import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from collections import defaultdict
import joblib
import os

class LSTMSuggester:
    def __init__(self, max_length=10, n_suggestions=3):
        self.max_length = max_length
        self.n_suggestions = n_suggestions
        self.tokenizer = Tokenizer(char_level=True, lower=True)
        self.word_freq = defaultdict(int)
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential([
            Embedding(input_dim=100, output_dim=8, input_length=self.max_length),
            LSTM(32, return_sequences=False),
            Dense(100, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
        return model

    def train(self, words):
        # Preprocesamiento y tokenización
        words = [w.lower() for w in words if 2 <= len(w) <= self.max_length]
        for word in words:
            self.word_freq[word] += 1
        
        self.tokenizer.fit_on_texts(words)
        sequences = self.tokenizer.texts_to_sequences(words)
        X = pad_sequences(sequences, maxlen=self.max_length, padding='pre')
        
        # Generación de datos de entrenamiento
        X_train, y_train = [], []
        for seq in X:
            for i in range(1, len(seq)):
                X_train.append(seq[:i])
                y_train.append(seq[i])
        
        X_train = pad_sequences(X_train, maxlen=self.max_length, padding='pre')
        y_train = np.array(y_train)
        
        self.model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1)

    def train_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
            print(f"Entrenando con {min(len(words), 5000)} palabras...")  # Límite para demo
            self.train(words[:5000])
        except Exception as e:
            print(f"Error cargando archivo: {str(e)}")
            self.train(["hola", "holanda", "hondo"])  # Datos de respaldo

    def suggest_words(self, prefix):
        prefix = prefix.lower()
        
        # 1. Búsqueda directa en palabras frecuentes
        dict_suggestions = [
            w for w in self.word_freq 
            if w.startswith(prefix)
        ][:self.n_suggestions]
        
        if len(dict_suggestions) >= self.n_suggestions:
            return dict_suggestions
        
        # 2. Predicción con LSTM
        try:
            seq = self.tokenizer.texts_to_sequences([prefix])
            seq = pad_sequences(seq, maxlen=self.max_length, padding='pre')
            preds = self.model.predict(seq, verbose=0)[0]
            top_chars = [
                self.tokenizer.index_word.get(i, '') 
                for i in np.argsort(preds)[-3:][::-1] 
                if i in self.tokenizer.index_word
            ]
            
            # Combina ambas estrategias
            suggestions = list(set(dict_suggestions + [
                prefix + char for char in top_chars 
                if (prefix + char) in self.word_freq
            ]))
            
            return suggestions[:self.n_suggestions]
        except:
            return dict_suggestions

    def save_model(self, path):
        joblib.dump({
            'tokenizer': self.tokenizer,
            'model_weights': self.model.get_weights(),
            'word_freq': dict(self.word_freq),
            'config': {
                'max_length': self.max_length,
                'n_suggestions': self.n_suggestions
            }
        }, path)

    def load_model(self, path):
        try:
            data = joblib.load(path)
            self.tokenizer = data['tokenizer']
            self.word_freq = defaultdict(int, data['word_freq'])
            self.max_length = data['config']['max_length']
            self.n_suggestions = data['config']['n_suggestions']
            
            # Reconstruye modelo idéntico
            self.model = self._build_model()
            self.model.set_weights(data['model_weights'])
        except Exception as e:
            print(f"Error cargando modelo: {str(e)}")
            # Sistema de respaldo
            self.train(["hola", "holanda", "hondo"])
from transformers import pipeline

class EmotionClassifier:
    def __init__(self):
        print("⏳ Загружаю модель для анализа эмоций...")
        # Модель для эмоций (английский язык)
        self.classifier = pipeline(
            "text-classification",
            model="bhadresh-savani/bert-base-uncased-emotion"
        )
        print("✅ Модель эмоций загружена!")
    
    def analyze(self, text: str) -> dict:
        result = self.classifier(text)[0]
        
        label = result['label']
        score = result['score']
        
        emotion_map = {
            "joy": "радость 😄",
            "sadness": "грусть 😢",
            "anger": "злость 😠",
            "fear": "страх 😨",
            "love": "любовь ❤️",
            "surprise": "удивление 😲"
        }
        
        return {
            "emotion": emotion_map.get(label, label),
            "confidence": round(score * 100, 2),
            "raw_label": label
        }
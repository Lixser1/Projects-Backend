import logging
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from datetime import datetime

# Импортируем наши анализаторы из папки ml
from ml.emotion_analyzer import EmotionAnalyzer
from ml.emotion_classifier import EmotionClassifier

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_logs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Создаём FastAPI приложение
app = FastAPI(title="Sentiment & Emotion Analysis API")

# API ключ из .env
API_KEY = os.getenv("API_KEY", "default_key")

# Загружаем модели при старте
print("⏳ Загружаю модели...")

# Модель для тональности (русский)
sentiment_analyzer = EmotionAnalyzer()

# Модель для эмоций (английский)
emotion_analyzer = EmotionClassifier()

print("✅ Все модели загружены!")


# Модель запроса
class AnalysisRequest(BaseModel):
    text: str
    mode: str  # "sentiment" или "emotion"


# Модель ответа
class AnalysisResponse(BaseModel):
    mode: str
    result: str
    score: float


# Проверка API ключа
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        logger.warning(f"Попытка доступа с неверным API ключом: {x_api_key}")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


# Главный эндпоинт
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(
    request: AnalysisRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Анализирует текст на тональность или эмоции
    
    - **text**: текст для анализа
    - **mode**: "sentiment" или "emotion"
    """
    
    start_time = datetime.now()
    
    try:
        logger.info(f"Получен запрос: mode={request.mode}, text_length={len(request.text)}")
        
        if request.mode == "sentiment":
            # Анализ тональности
            result = sentiment_analyzer.analyze(request.text)
            
            # Извлекаем только название тональности без эмодзи
            sentiment_label = result['sentiment'].split()[0]  # "позитивная 😊" -> "позитивная"
            
            # Маппинг для совместимости с ботом
            label_map = {
                "нейтральная": "нейтрально",
                "позитивная": "позитив",
                "негативная": "негатив"
            }
            
            response = AnalysisResponse(
                mode="sentiment",
                result=label_map.get(sentiment_label, sentiment_label),
                score=round(result['confidence'] / 100, 2)  # Переводим обратно в 0-1
            )
            
        elif request.mode == "emotion":
            # Анализ эмоций
            result = emotion_analyzer.analyze(request.text)
            
            # Извлекаем только название эмоции без эмодзи
            emotion_label = result['emotion'].split()[0]  # "радость 😄" -> "радость"
            
            response = AnalysisResponse(
                mode="emotion",
                result=emotion_label,
                score=round(result['confidence'] / 100, 2)  # Переводим обратно в 0-1
            )
            
        else:
            raise HTTPException(status_code=400, detail="Mode должен быть 'sentiment' или 'emotion'")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Запрос обработан за {elapsed:.2f}с: {response.result} ({response.score})")
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok", "models": ["sentiment", "emotion"]}

@app.get("/")
async def root():
    return {
        "message": "Sentiment & Emotion Analysis API",
        "endpoints": {
            "/analyze": "POST - анализ текста",
            "/health": "GET - проверка статуса",
            "/docs": "GET - документация Swagger"
        }
    }
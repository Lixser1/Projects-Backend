from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards import get_mode_keyboard
from bot.api_client import analyze_text_via_api
router = Router()

class AnalysisStates(StatesGroup):
    waiting_for_mode = State()
    waiting_for_text_sentiment = State()
    waiting_for_text_emotion = State()

SENTIMENT_EMOJI = {
    "позитив": "😊",
    "негатив": "😢",
    "нейтрально": "😐"
}

EMOTION_EMOJI = {
    "радость": "😄",
    "грусть": "😢",
    "злость": "😠",
    "страх": "😨",
    "любовь": "❤️",
    "удивление": "😲"
}


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я бот для анализа текста.\n"
        "Выбери тип анализа:",
        reply_markup=get_mode_keyboard()
    )
    await state.set_state(AnalysisStates.waiting_for_mode)


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    await message.answer(
        "📖 **Как пользоваться ботом:**\n\n"
        "1️⃣ Выбери тип анализа:\n"
        "   • 📊 Анализ тональности (позитив/негатив/нейтрал)\n"
        "   • 😊 Анализ эмоций (радость, грусть, злость и т.д.)\n\n"
        "2️⃣ Отправь текст для анализа\n\n"
        "3️⃣ Получи результат с процентом уверенности\n\n"
        "⚠️ **Важно:** Анализ эмоций работает только с английским текстом!\n\n"
        "Команды:\n"
        "/start - Начать заново\n"
        "/help - Показать эту справку",
        parse_mode="Markdown",
        reply_markup=get_mode_keyboard()
    )


@router.message(F.text == "📊 Анализ тональности")
async def mode_sentiment(message: Message, state: FSMContext):
    await message.answer(
        "📊 **Режим: Анализ тональности**\n\n"
        "Отправь мне текст на русском языке, "
        "и я определю его тональность (позитив/негатив/нейтрал):",
        parse_mode="Markdown"
    )
    await state.set_state(AnalysisStates.waiting_for_text_sentiment)


@router.message(F.text == "😊 Анализ эмоций")
async def mode_emotion(message: Message, state: FSMContext):
    await message.answer(
        "😊 **Режим: Анализ эмоций**\n\n"
        "⚠️ Отправь мне текст **на английском языке**, "
        "и я определю эмоцию (радость, грусть, злость, страх, любовь, удивление):",
        parse_mode="Markdown"
    )
    await state.set_state(AnalysisStates.waiting_for_text_emotion)


@router.message(AnalysisStates.waiting_for_text_sentiment)
async def analyze_sentiment(message: Message, state: FSMContext):
    await message.answer("⏳ Анализирую тональность...")
    
    try:
        result = await analyze_text_via_api(message.text, mode="sentiment")
        
        emoji = SENTIMENT_EMOJI.get(result['result'], "🤔")
        score_percent = int(result['score'] * 100)
        
        response = (
            f"{emoji} **Результат анализа тональности:**\n\n"
            f"📊 Тональность: **{result['result'].capitalize()}**\n"
            f"🎯 Уверенность: **{score_percent}%**\n\n"
            f"_Ваш текст:_ _{message.text}_"
        )
        
        await message.answer(response, parse_mode="Markdown", reply_markup=get_mode_keyboard())
        await state.set_state(AnalysisStates.waiting_for_mode)
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при анализе: {str(e)}\n\n"
            "Попробуйте еще раз или выберите другой режим.",
            reply_markup=get_mode_keyboard()
        )
        await state.set_state(AnalysisStates.waiting_for_mode)


@router.message(AnalysisStates.waiting_for_text_emotion)
async def analyze_emotion(message: Message, state: FSMContext):
    await message.answer("⏳ Анализирую эмоции...")
    
    try:
        result = await analyze_text_via_api(message.text, mode="emotion")
        
        emoji = EMOTION_EMOJI.get(result['result'], "🤔")
        score_percent = int(result['score'] * 100)
        
        response = (
            f"{emoji} **Результат анализа эмоций:**\n\n"
            f"😊 Эмоция: **{result['result'].capitalize()}**\n"
            f"🎯 Уверенность: **{score_percent}%**\n\n"
            f"_Ваш текст:_ _{message.text}_"
        )
        
        await message.answer(response, parse_mode="Markdown", reply_markup=get_mode_keyboard())
        await state.set_state(AnalysisStates.waiting_for_mode)
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при анализе: {str(e)}\n\n"
            "Попробуйте еще раз или выберите другой режим.",
            reply_markup=get_mode_keyboard()
        )
        await state.set_state(AnalysisStates.waiting_for_mode)

# Обработчик для любых других сообщений
@router.message()
async def unknown_message(message: Message):
    await message.answer(
        "Я не понял команду 🤔\n\n"
        "Используй кнопки ниже или команду /help",
        reply_markup=get_mode_keyboard()
    )
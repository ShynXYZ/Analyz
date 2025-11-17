import os
import toml
import sys
# Импорты для Gemini
from google import genai
from google.genai.errors import APIError as GeminiAPIError # Новый, правильный импорт для свежей версии SDK
# Импорты для Google Search
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError # Оставляем только HttpError, т.к. DiscoveryFailure перемещен/удален

# --- 1. ЗАГРУЗКА КЛЮЧЕЙ ---
SECRETS_PATH = os.path.join(".streamlit", "secrets.toml")
GEMINI_API_KEY = None
GOOGLE_API_KEY = None
PSE_ID = None

print(f"🔑 Поиск файла ключей по пути: {SECRETS_PATH}\n")

if not os.path.exists(SECRETS_PATH):
    print(f"❌ ОШИБКА: Файл {SECRETS_PATH} не найден. Убедитесь, что он создан.")
    sys.exit()

try:
    with open(SECRETS_PATH, "r", encoding="utf-8") as f:
        secrets = toml.load(f)
    
    GEMINI_API_KEY = secrets.get("GEMINI_API_KEY")
    GOOGLE_API_KEY = secrets.get("GOOGLE_API_KEY")
    PSE_ID = secrets.get("PSE_ID")
    
    # Внимание: Вы должны использовать СВОИ АКТУАЛЬНЫЕ, НОВЫЕ КЛЮЧИ в secrets.toml
    if not all([GEMINI_API_KEY, GOOGLE_API_KEY, PSE_ID]):
        print("❌ ОШИБКА: Один или несколько ключей (GEMINI_API_KEY, GOOGLE_API_KEY, PSE_ID) не найдены в secrets.toml.")
        sys.exit()
        
    print("✅ Файл secrets.toml найден и ключи загружены.")

except Exception as e:
    print(f"❌ ОШИБКА: Не удалось прочитать TOML файл: {e}")
    sys.exit()

print("-" * 30)

# --- 2. ПРОВЕРКА GEMINI API ---
print("🧪 Тестирование ключа GEMINI_API_KEY...")
try:
    # 1. Создаем клиент с ключом (правильный синтаксис для google-genai)
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # 2. Выполняем запрос, используя метод client.models.generate_content
    # Используется актуальное, надежное имя модели
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=["test content"] 
    )
    
    if response.text:
        print("✅ УСПЕХ: Ключ Gemini API работает.")
    else:
        # Может произойти, если ответ пуст, но запрос прошел (проблема на стороне квот)
        print("❌ ОШИБКА: Ключ Gemini API принят, но ответ пустой (проверьте настройки квот).\n")

# Блоки except теперь корректно завершают блок try:
except GeminiAPIError as e:
    print(f"❌ ОШИБКА: Ключ Gemini API НЕ РАБОТАЕТ (APIError).")
    print(f"  Подробности: {e}\n")
except Exception as e:
    print(f"❌ ОШИБКА: Непредвиденная проблема с Gemini API: {e}\n")

print("-" * 30)

# --- 3. ПРОВЕРКА GOOGLE SEARCH API И PSE ID ---
print("🧪 Тестирование GOOGLE_API_KEY и PSE_ID...")
try:
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    # Делаем 1 запрос по слову "test"
    res = service.cse().list(q="test", cx=PSE_ID, num=1).execute()
    
    # Проверяем, что ответ содержит 'items' или 'queries', что указывает на успешное выполнение запроса
    if 'items' in res or 'queries' in res:
        print("✅ УСПЕХ: Ключ Google Search API и PSE_ID работают.")
    else:
        print("❌ ОШИБКА: Ключ Google Search API и PSE_ID приняты, но запрос не вернул корректный ответ.\n")

except HttpError as e:
    print(f"❌ ОШИБКА: Ключ Google Search API или PSE_ID НЕ РАБОТАЮТ (HttpError).")
    if e.resp.status == 403:
        print("  Подробности: Ошибка 403 (Forbidden).")
        print("  Возможные причины: 1. 'Custom Search API' не включен. 2. Неправильный GOOGLE_API_KEY.")
    elif e.resp.status == 400:
        print("  Подробности: Ошибка 400 (Bad Request).")
        print("  Возможная причина: Неправильный PSE_ID (ID поисковой системы, 'cx').")
    else:
        print(f"  Подробности: {e}\n")

except Exception as e:
    print(f"❌ ОШИБКА: Непредвиденная проблема с Google Search API: {e}\n")

print("-" * 30)
print("🏁 Проверка завершена. Теперь вы можете приступить к написанию основного кода!")
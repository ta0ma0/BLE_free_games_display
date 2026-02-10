import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os
from bt_sender import send_list_via_bluetooth
import asyncio
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env") # Лучше указывать полный путь
load_dotenv(ENV_PATH)

# --- КОНФИГУРАЦИЯ ---
API_KEY = os.getenv("API_KEY_ITRAD")
print(f"API KEY: {API_KEY}") # Для отладки
COUNTRY = "RU"
SHOPS = "61,16,35"
LIMIT = 10
# --- КОНЕЦ КОНФИГУРАЦИИ ---

BASE_URL = "https://api.isthereanydeal.com"
HEADERS = {"User-Agent": "FreeGamesScript/1.0"}

def cleanup_files(pattern: str, keep_count: int = 2):
    """Очистка старых файлов"""
    print(f"\n--- Очистка файлов по шаблону: {pattern} ---")
    files = glob.glob(pattern)
    if len(files) <= keep_count:
        return

    files.sort(key=os.path.getmtime, reverse=True)
    files_to_delete = files[keep_count:]
    
    for f in files_to_delete:
        try:
            os.remove(f)
            print(f"  - Удален: {f}")
        except OSError as e:
            print(f"  - Ошибка: {e}")

def get_deals_list(limit=10, offset=0):
    """Получает список сделок"""
    endpoint = f"{BASE_URL}/deals/v2"
    params = {
        "key": API_KEY,
        "country": COUNTRY,
        "offset": offset,
        "limit": limit,
        "sort": "price",
        "nondeals": "false",
        "mature": "false",
        "shops": SHOPS,
    }
    
    try:
        print(f"📡 Запрос к API...")
        response = requests.get(endpoint, headers=HEADERS, params=params, timeout=10)
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print("❌ Ошибка 403: Доступ запрещен (проверьте API Key/IP)")
        else:
            print(f"❌ Ошибка {response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка соединения: {e}")
        return None

def analyze_deals(data):
    """Фильтрует бесплатные игры"""
    if not data or "list" not in data:
        return []
    
    deals = data["list"]
    free_games = []
    
    for deal in deals:
        deal_info = deal.get("deal", {})
        price_amount = deal_info.get("price", {}).get("amount", 1)
        regular_amount = deal_info.get("regular", {}).get("amount", 0)
        cut = deal_info.get("cut", 0)
        
        # Логика бесплатности
        if price_amount == 0 and regular_amount > 0:
            tag = "бесплатно"
            if cut == 100: tag = "100% скидка"
            
            shop_name = deal_info.get("shop", {}).get("name", "Shop")
            
            free_games.append({
                "title": deal.get("title", "NoName"),
                "shop_name": shop_name,
                "reason": tag
            })
    
    return free_games

def get_games():
    print("=" * 50)
    print("ПОИСК БЕСПЛАТНЫХ ИГР")
    print("=" * 50)
    
    # 1. Запрос к API
    response_data = get_deals_list(limit=LIMIT)
    
    # --- ОБРАБОТКА ОШИБОК ПОДКЛЮЧЕНИЯ/API ---
    if response_data is None:
        print("\n❌ Критическая ошибка API. Формирую сообщение для дисплея.")
        # Возвращаем список ошибок для дисплея
        return [
            "! ОШИБКА СЕТИ !",
            "Проверь Wi-Fi",
            "или API Key",
            "IsThereAnyDeal",
            "Code: Error"
        ]

    # 2. Анализ данных
    free_games = analyze_deals(response_data)
    
    today_games_list = [] # Инициализируем список
    
    if free_games:
        print(f"\n🎮 Найдено бесплатных игр: {len(free_games)}")
        for i, game in enumerate(free_games, 1):
            # Формируем строку
            title = game['title']
            shop = game['shop_name']
            
            # Упрощаем названия для дисплея, так как места мало
            if "Epic" in shop:
                display_shop = "EGS"
            elif "Steam" in shop:
                display_shop = "Steam"
            elif "GOG" in shop:
                display_shop = "GOG"
            else:
                display_shop = shop[:6] # Обрезаем длинные названия
            
            # Формат строки: "1.Игра|Магазин"
            # Мы заменяем pipe на перенос или пробел на стороне дисплея, 
            # или отправляем как есть, если модуль bt_sender разбивает.
            # Если твоя ардуина ждет "Игра|Магазин", оставляем так.
            # Если она просто печатает строку, лучше "1.Игра (Магазин)"
            
            line = f"{i}. {title} ({display_shop})"
            today_games_list.append(line)
            print(line)
            
    else:
        print("Игры не найдены, список пуст.")
        today_games_list = [
            "Сегодня пусто :(",
            "Халявы нет",
            "Зайди позже",
            "IsThereAnyDeal",
            "0 Games"
        ]

    # Сохраняем текстовый файл локально (на всякий случай)
    with open('today_free_games.txt', 'w', encoding='utf-8') as f:
        for line in today_games_list:
            f.write(line + '\n')
            
    return today_games_list

async def main():
    # 1. Получаем список (игр или ошибок)
    games_to_send = get_games()
    
    print("\n--- Подготовка к отправке ---")
    print(games_to_send)
    
    # 2. Отправляем в любом случае (даже если там ошибки)
    if games_to_send:
        await send_list_via_bluetooth(games_to_send)
    else:
        print("Почему-то список пуст совсем. Ничего не отправляю.")

    # 3. Уборка
    cleanup_files(pattern='deals_full_*.json', keep_count=2)
    cleanup_files(pattern='free_games_*.json', keep_count=2)

if __name__ == "__main__":
    asyncio.run(main())

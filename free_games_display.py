import asyncio
from bleak import BleakClient, BleakError

ADDRESS = "D8:A9:8B:7D:58:E5" # Твой MAC
UART_RX_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
CHUNK_SIZE = 20

# Твой список игр
GAMES_LIST = """
1.Find the Oil Racing Edition
2.Botany Manor в Epic Game Store
3.SunBlockers в Epic Game Store
4.nightreaper2 в Epic Game Store
5.Pixel Gun 3D - Poison Retro
6.Magellania в Steam
!.Спасибо Orbitar Games за идеи!
"""

async def send_line(client, line_text):
    """Функция отправки ОДНОЙ строки с разбивкой на чанки"""
    print(f"Отправка: {line_text}")
    
    # Добавляем \n обязательно, чтобы Arduino поняла конец команды/строки
    data_to_send = (line_text + "\n").encode('utf-8')

    # Нарезка на пакеты по 20 байт
    for i in range(0, len(data_to_send), CHUNK_SIZE):
        chunk = data_to_send[i:i + CHUNK_SIZE]
        await client.write_gatt_char(UART_RX_CHAR_UUID, chunk, response=False)
        # Крошечная пауза для стабильности BLE
        await asyncio.sleep(0.02) 

async def run(address):
    print(f"Подключение к {address}...")
    try:
        async with BleakClient(address) as client:
            if not client.is_connected:
                print("Ошибка подключения.")
                return
            print("ПОДКЛЮЧЕНО!")
            
            # --- ШАГ 1: ОТПРАВКА КОМАНДЫ ОЧИСТКИ ---
            print(">> Очищаю экран Arduino (CLS)...")
            await send_line(client, "CLS")
            
            # Даем Arduino время (рисование черного прямоугольника занимает около 100-300мс)
            await asyncio.sleep(5) 

            # --- ШАГ 2: ОТПРАВКА СПИСКА ---
            print(">> Начинаю отправку списка игр...")
            
            lines = GAMES_LIST.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line: continue 
                
                # 1. Отправляем строку
                await send_line(client, line)
                
                # 2. ЖДЕМ пока Arduino отрисует
                # Если шрифт сложный, лучше дать 1.0 - 1.5 секунды
                await asyncio.sleep(1.5) 
                
            print(">> Список успешно отправлен!")

            # --- ШАГ 3: РУЧНОЙ РЕЖИМ ---
            print("\nПереход в ручной режим (введи 'q' для выхода, 'CLS' для очистки)")
            while True:
                text = await asyncio.to_thread(input, "> ")
                
                if text.lower() == 'q': 
                    break
                
                if text:
                    await send_line(client, text)
                    # Если отправили CLS вручную - ждем чуть меньше, если текст - чуть дольше
                    if text == "CLS":
                        await asyncio.sleep(0.5)
                    else:
                        await asyncio.sleep(1.0)

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run(ADDRESS))
    except KeyboardInterrupt:
        print("\nПрограмма остановлена.")

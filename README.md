# Free games display

## DIY проект на Arduino, дисплей с сервером на Arduino nano с Bluetooth Low Energy модулем. Который отображает данные о бесплатных с сайта isthereanydeal.com.

#### Общее описание работы

Устройство представляет из себя Bluetooth девайс, который получает данные о бесплатных играх от скрипта на Python работающего на хосте Linux (Laptop, PC, Micro PC). Реализации под Windows пока нет из за особенностей работы Bluetooth стека на Windows. Для реализации лучше всего подходит Raspberry Pi. Данные собираются Python скриптом (isthereanydeal.py) с сайта isthereanydeal.com и отправляются по BLE на дисплей.

#### Железо

1. Arduino nano (клон)
2. Дисплей GMT024-08-SPI8P (ST7789) 2.4 дюйма, разрешение 240x320 точек.
3. BLE модуль ZS-040, на базе микроконтроллера HM-10.
4. Linux хост Raspberry Pi 4

#### Software

1. Python >= 3.11.2
2. Библиотеки: bleak, requests
3. Arduino IDE 1.8.19 (на более поздних версиях у меня не получилось подключить китайкий клон Nano)
4. API ключ isthereanydeal.com

## Сборка

### Подключение BLE:

#### Питание:

*    **VCC** HM-10 → **3.3V** Arduino Nano
*    **GND** HM-10 → **GND** Arduino Nano

#### Данные:

*   **TX** HM-10 → **RX** (D0) Arduino Nano
*   **RX** HM-10 → **TX** (D1) Arduino Nano

### Подключение дисплея GMT024-08-SPI8P (ST7789):

*   **SDA (MOSI)** → Резистор 4.7 кОм → **D11**
*   **SCL (SCK)** → Резистор 4.7 кОм → **D13**
*   **CS** → Резистор 4.7 кОм → **D10**
*   **DC** → Резистор 4.7 кОм → **D9**
*   **RST** → Резистор 4.7 кОм → **D7** (или **D8**, любой цифровой)
*   **BL** → Резистор 4.7 кОм → **5V**

## Программирование

* Arduino-скетч: arduino_scetch.ino  в корне проекта.
* isthereanydeal.py разворачивается на Linux хосте, в .env добавляется API-ключ от isthereanydeal.com

#### Библиотеки:
* Adafruit_ST7789
* Adafruit_GFX

#### Шрифт

1. После создания скетча в Aduino IDE положить в корень скетча два файла ```fonts/fonts/FreeMono8.h``` и ```utf8rus2.ino```

## Запуск
После сборки и проверке устройства, нужно сопряжение устройства с Linux хостом, затем на хосте запускается isthereanydeal.py например по cron раз в стуки.
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SoftwareSerial.h>

// ВАЖНО: Кавычки "" означают, что файл лежит в папке скетча
#include "FreeMono7.h"       
#include "FreeMono8.h"  

#define TFT_CS    10
#define TFT_DC    9
#define TFT_RST   7
#define TFT_SDA   11
#define TFT_SCL   13

#define MAX_BUFFER 200 

char rxBuffer[MAX_BUFFER + 1]; 
int bufIndex = 0;
int cursorY = 50; 
// Высота одной строки в пикселях (подстрой под свой шрифт)
const int lineHeight = 29;

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_SDA, TFT_SCL, TFT_RST);
SoftwareSerial BTSerial(2, 3); // RX=2, TX=3

// --- Функция перекодировки UTF-8 в CP1251 (для шрифтов immortalserg) ---


void setup() {
  Serial.begin(9600);
  BTSerial.begin(9600);

  tft.init(240, 320, SPI_MODE0); 
  tft.setRotation(1); 
  tft.fillScreen(ST77XX_BLACK);

  // Подключаем шрифт из файла
  tft.setFont(&FreeMono8pt8b);
  tft.setTextSize(1);
  
  // Тест интерфейса
  tft.drawRect(0, 0, 320, 240, ST77XX_BLUE);
  tft.fillRect(0, 0, 320, 30, ST77XX_BLUE);
  
  tft.setTextColor(ST77XX_WHITE);
  tft.setCursor(10, 20);
  tft.println(utf8rus2("Сегодня бесплатно раздаются:"));
  
  Serial.println("System Ready");
}

void loop() {
  while (BTSerial.available()) {
    char c = (char)BTSerial.read();

    if (c == '\n') {
       rxBuffer[bufIndex] = '\0'; // Завершаем строку
       
       // --- НОВАЯ ЛОГИКА: ПРОВЕРКА КОМАНДЫ ---
       // strcmp возвращает 0, если строки совпадают
       if (strcmp(rxBuffer, "CLS") == 0) {
          Serial.println("Command: Clear Screen");
          
          // 1. Очищаем область текста
          tft.fillRect(0, 35, 320, 205, ST77XX_BLACK); 
          
          // 2. Сбрасываем курсор наверх
          cursorY = 50; 
          
          // 3. Обнуляем буфер и выходим, чтобы не печатать "CLS" на экране
          bufIndex = 0; 
       }
       // --------------------------------------
       // Если это ОБЫЧНЫЙ текст
       else if (bufIndex > 0) {
          Serial.print("Full msg: ");
          Serial.println(rxBuffer);
          updateScreen(rxBuffer);
          bufIndex = 0;
       } 
       else {
          bufIndex = 0; // Сброс если пустая строка
       }
    }
    else if (c == '\r') {
       // skip
    }
    // Приводим к unsigned char для поддержки русского
    else if ((unsigned char)c >= 32) { 
      if (bufIndex < MAX_BUFFER) {
        rxBuffer[bufIndex] = c;
        bufIndex++;
      }
    }
  }
}

void updateScreen(char* text) {
  // 1. Проверяем, есть ли место внизу экрана (240 - высота экрана)
  // Оставляем запас 30 пикселей снизу
  if (cursorY > 210) { 
     // Если места нет - очищаем рабочую область и сбрасываем курсор наверх
     tft.fillRect(0, 35, 320, 205, ST77XX_BLACK); 
     cursorY = 50;
  }
  
  // 2. Ставим курсор в текущую позицию
  tft.setCursor(10, cursorY);
  tft.setTextColor(ST77XX_GREEN);
  tft.setTextWrap(true); // Лучше выключить перенос, если строки короткие, или true если длинные
  
  // 3. Печатаем
  tft.setFont(&FreeMono7pt8b);
  tft.setTextSize(1);
  tft.println(utf8rus2(text));
  
  // 4. Сдвигаем позицию для СЛЕДУЮЩЕЙ строки
  cursorY += lineHeight;
}
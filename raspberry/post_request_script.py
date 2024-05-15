from machine import Pin  # Импорт модуля Pin из библиотеки machine для работы с портами
import utime  # Библиотека для работы со временем 
import network  # Библиотека для работы с сетями
import urequests  # Версия библиотеки requests для micropython

SSID = "wifi_name"  # Указываем название Wi-Fi сети
PASSWORD = "password"  # Указываем пароль от Wi-Fi сети
url = "http://server_ip/update"  # Указываем маршрут до сайта (эндпоинт /update)
token = "token"  # Указываем secret_key, присвоенный датчику в БД
pin_trigger = Pin(5, Pin.OUT)  # Обозначение порта триггера дальнометра
pin_echo = Pin(4, Pin.IN)  # Обозначение порта эхо дальнометра
print("Подключение к Wi-Fi...")
wifi = network.WLAN(network.STA_IF)  # Определение сетевого интерфейса
wifi.active(True)  # Активация сетевого порта
wifi.connect(SSID, PASSWORD)  # Подключение к Wi-Fi сети
while not wifi.isconnected():  # Если не удаётся подключиться к Wi-fi, то...
    pass
    print('Не удаётся подключиться к сети Wi-Fi')  # Уведомляем об этом
print("Успешно подключено к Wi-Fi!")
print("IP адрес устройства:", wifi.ifconfig()[0])
while wifi.isconnected():  # Если есть подключекние к Wi-Fi, то...
    pin_trigger.low()  # Замер дальности
    utime.sleep_us(5)    
    pin_trigger.high()
    utime.sleep_us(5)
    pin_trigger.low()
    while pin_echo.value() == 0:  # Измерение времени прохождения сигнала эхо
        signal_off = utime.ticks_us()  # Сохраняем время, когда сигнал отсутствует
    while pin_echo.value() == 1:
        signal_on = utime.ticks_us()  # Сохраняем время, когда сигнал присутствует
        timepassed = signal_on - signal_off  # Вычисляем время прохождения сигнала
        object_distance = (timepassed * 0.0343) / 2  # Рассчитываем расстояние до объекта
        print("distance:", round(object_distance, 1),"cm")
        data = {"data": object_distance}  # Подготавливаем данные для отправки на сервер
    print("IP адрес устройства:", wifi.ifconfig()[0])    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }  # Подготавливаем заголовки для запроса
    response = urequests.post(url, headers=headers, json=data)  # Отправляем POST-запрос
    print("Status:", response.status_code)
    print("Response:", response.text)
    response.close()  # Закрываем соединение
    utime.sleep(5)  # Делаем пятисекундную паузу
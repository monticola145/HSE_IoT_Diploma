# IoT_Project
Итоговый проект "Разработка программного обеспечения на Python для управления системой умный дом"

## Развертывание и запуск
Для развертывания и запуска ЛОКАЛЬНОГО сервера, необходимо:
### 1) Клонировать репозиторий на устройство
git clone https://github.com/monticola145/IoT_Project.git
### 2) Развернуть локальное окружение и установить зависимости
python -m venv venv && source venv/Scripts/activate<br />
pip install -r requirements.txt
### 3) Запустить сервер
python server.py

## Содержание веб-интерфейса
Веб-интерфейс представлен в виде веб-сайта с несколькими страницами эндроинтами:<br />
1. /login - страница авторизации
2. /logout - страница деавторизации
3. / - главная страница
4. /register_sensor - страница управления датчиками (GET), эндпоинт для создания новых записей в базе данных (POST)
5. /update - эндпоинт для передачи показателей датчиков в базу данных
6. /delete_sensor/<sensor_id> - эндпоинт для удаления датчиков из базы данных

## Принцип работы
### База данных
    Инициация базы данных происходит в момент первого запуска сервера (п. "Развертывание и запуск", пп. 1)
    Для внесения датчиков в базу данных необходимо перейти на страницу "Manage Sensors" (эндпоинт /register_sensor), заполнить поле с именем и нажать на кнопку "Register"
    Для передачи информации с датчиков в базу данных необходимо настроить пересылку данных на платформах (в данном случае, Arduino Nano и Raspberry Pi Pico W)
    Передача информации с датчиков в базу данных осуществляется путём отправки HTTP POST-запросов с устройства на эндпоинт /update. Тело запроса должно содержать токен (secret_key, выдаётся в момент регистрации в базе данных) и данные ("data": 123)
### Авторизация
    В первой версии данного проекта предусмотрена авторизация при помощи заранее заготовленных логина и пароля (admin:password), содержащегося в коде. Для удобства их можно видоизменять, присваивая иные значения
    В дальнейшем планируется модернизации безопасности проекта при помощи использования более продвинутых способов авторизации
### Безопасность
    Данный проект имеет базовые функции защиты, обусловленные авторизацией по системе логин-пароль, использованием генерируемого токена при внесении датчика в БД и при передаче датчиком данных в БД
    В дальнейшем планируется добавление в функцию генерации токена JWT для обеспечения более высокого уровня защиты
    

# Импортируем требуемые для работы функции и библиотеки
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import redis


app = Flask(__name__)  # Инициируем приложение
app.secret_key = secrets.token_hex(24)  # Генерируем уникальный ключ сессии

# Подключение и настройка базы данных и хранилища сеансов
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sensors_database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url("redis://localhost:6379/0")

Session(app)  # Создаём экземпляр объекта Session для управления сеансами через Redis

db = SQLAlchemy(app, session_options={"expire_on_commit": False})  # Инициализируем БД

# Инициируем менеджера логина для контроля за сессиями
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Указываем страницу для входа

users = {
    "admin": {"password": generate_password_hash("password")}
}  # Создаём хранилище данных пользователей с хешированными паролями


class Sensor(db.Model):  # Создаём модель для сенсоров в БД
    id = db.Column(db.Integer, primary_key=True)  # Назначаем id в БД
    sensor_id = db.Column(db.String(64), unique=True, nullable=False)  # Назначаем имя
    secret_key = db.Column(
        db.String(128), nullable=False
    )  # Предполагается, что каждый сенсор имеет свой секретный ключ
    data = db.Column(db.JSON)  # Указываем возможность наличия данных (в JSON формате)

    def generate_token(self):
        '''Функция генерации секретного токена для датчика.'''
        self.secret_key = secrets.token_hex(16)  # Генерация 16-байтного гексадецимального токена
        return self.secret_key

    def __repr__(self):
        return f"<Sensor {self.sensor_id}>"


class User(UserMixin):  # Создаём класс User для упрощения управления аутентификацией
    pass


@login_manager.user_loader  # Загрузка пользователей из хранилища (строки 30-32)
def user_loader(username):
    """Функция загрузки пользователей"""
    if username not in users:
        return

    user = User()
    user.id = username
    return user


@app.route("/login", methods=["GET", "POST"])  # Обработчик страницы логина, методы получения (входа на страницу) и отправки (логина)
def login():
    """Функция входа пользователя в систему."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and check_password_hash(
            users[username]["password"], password
        ):
            user = User()
            user.id = username
            login_user(user)
            return redirect(
                url_for("index")
            )  # Перенаправление на главную страницу в случае успешного входа
        else:
            return render_template(
                "login.html", error="Invalid username or password"
            )  # Отказ в аутентификации в случае неправильных данных входа

    return render_template("login.html", error=None)


@app.route("/logout")  # Обработчик выхода
def logout():
    """Функция выхода пользователя из системы."""
    logout_user()
    return redirect(url_for("login"))


@app.route("/register_sensor", methods=["GET", "POST"])  # Устанавливаем методы GET и POST
@login_required  # Убеждаемся, что действия может выполнять только авторизованный пользователь
def register_sensor():
    """Функция регистрации датчиков"""
    if request.method == "POST":  # При попытке создания записи...
        sensor_id = request.form.get("sensor_id")   # Получаем sensor_id == название сенсора, вводимое пользователем
        if not Sensor.query.filter_by(sensor_id=sensor_id).first():  # Проверяем наличие в БД, если нет, то...
            sensor = Sensor(sensor_id=sensor_id)  # Создаём новый объект с названием
            sensor.generate_token()  # Гарантированное установление secret_key
            db.session.add(sensor)  # Внесение в БД
            db.session.commit()  # Сохранение изменений в БД
            flash("Sensor registered successfully!", "success")
        else:
            flash("Sensor ID already exists!", "error")
        return redirect(url_for("register_sensor"))  # Перенаправление обратно на страницу регистрации

    sensors = {sensor.sensor_id: sensor for sensor in Sensor.query.all()}  # Создание словаря всех датчиков из БД. Ключ - sensor_id, значение - объект "sensor"
    return render_template("register_sensor.html", sensors=sensors)  # Рендер шаблона


@app.route("/delete_sensor/<sensor_id>", methods=["POST"])  # Устанавливаем метод POST
@login_required  # Убеждаемся, что действия может выполнять только авторизованный пользователь
def delete_sensor(sensor_id):
    """Функция удаления датчика."""
    sensor = Sensor.query.filter_by(sensor_id=sensor_id).first()  # Ищем сенсор в БД
    if sensor:  # Если нашли, то удаляем и сохраняем изменения в БД
        db.session.delete(sensor)
        db.session.commit()
        flash("Sensor deleted successfully!", "success")
    else:
        flash("Sensor not found!", "error")
    return redirect(url_for("register_sensor"))


@app.route("/update", methods=["POST"])  # Устанавливаем метод POST для создания новых записей (сенсеров)
def update():
    """Функция передачи данных с датчиков на сервер"""
    token = request.headers.get("Authorization")  # Извлекаем токен из заголовка Authorization
    data = request.json.get("data")  # Извлекаем данные из запроса
    if token and data:  # При успешном получении токена и данных...
        token_parts = token.split()  # Отделяем "Bearer" от непосредственного токена
        if len(token_parts) == 2 and token_parts[0] == "Bearer":
            token_value = token_parts[1]
            sensor = Sensor.query.filter_by(secret_key=token_value).first()  # Проверяем его существование в БД
            if sensor:  # В случае успеха...
                sensor.data = data  # Вносим в БД данные, ранее полученные из запроса
                db.session.commit()  # Сохраняем изменеия
                return jsonify({"success": "Data updated"}), 200  # Сигнализируем об успехе
            else:
                return jsonify({"error": "Sensor not found or invalid token"}), 404  # Если не находим в БД токен, то говорим об этом
        else:
            return jsonify({"error": "Invalid token format"}), 400
    else:
        return jsonify({"error": "Token or data missing"}), 400


@app.route("/")
@login_required
def index():
    """Функция главной страницы приложения"""
    db.session.expire_all()  # Обновление состояния сессии (чтобы не кешировалась в браузере, в целях безопасности)
    sensors_list = Sensor.query.all()  # Находим все сенсоры
    sensor_data = {sensor.sensor_id: sensor.data for sensor in sensors_list}  # Выводим их по порядку, готовя к рендеру
    return render_template("index.html", sensor_data=sensor_data)

@app.after_request  # Устанавливает заголовок no-store, чтобы предотвратить кеширование
def add_header(response):  
    """Функция установки заголовка"""
    response.headers['Cache-Control'] = 'no-store'
    return response


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")
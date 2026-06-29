import sqlite3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not username or not email or not password:
            return jsonify({'message': 'Все поля должны быть заполнены'}), 400

        if len(password) < 6:
            return jsonify({'message': 'Пароль должен содержать не менее 6 символов'}), 400

        conn = get_db_connection()

        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user:
            conn.close()
            return jsonify({'message': 'Пользователь уже зарегистрирован'}), 400

        conn.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, password)
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Регистрация выполнена успешно'}), 201

    except Exception as e:
        return jsonify({'message': f'Ошибка: {str(e)}'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'message': 'Все поля должны быть заполнены'}), 400

        conn = get_db_connection()

        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if not user:
            return jsonify({'message': 'Неверный email или пароль'}), 401

        if user['password'] != password:
            return jsonify({'message': 'Неверный email или пароль'}), 401

        return jsonify({'message': 'Добро пожаловать!'}), 200

    except Exception as e:
        return jsonify({'message': f'Ошибка: {str(e)}'}), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
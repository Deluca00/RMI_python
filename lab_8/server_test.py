import time

from flask import Flask, request, jsonify
import psycopg2
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

transfer_in_progress = {}


# Kết nối tới cơ sở dữ liệu
def get_postgres_connection():
    conn = psycopg2.connect(
        dbname='bank',
        user='root',
        password='090104',
        host='localhost'
    )
    return conn

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    conn = get_postgres_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bank WHERE username = %s AND password = %s", (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return jsonify({'message': 'Login successful', 'balance': user[3]})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/transfer', methods=['POST'])
def transfer():
    sender = request.json['sender']
    recipient = request.json['recipient']
    amount = request.json['amount']

    if transfer_in_progress.get(sender, False):
        return jsonify({'message': 'Transfer in progress. Please wait.'}), 400

    transfer_in_progress[sender] = True

    try:
        time.sleep(5)
        conn = get_postgres_connection()
        cur = conn.cursor()

        # Lấy thông tin người gửi
        cur.execute("SELECT * FROM bank WHERE username = %s", (sender,))
        sender_data = cur.fetchone()

        if not sender_data or sender_data[3] < amount:
            return jsonify({'message': 'Insufficient balance on server2'}), 400

        # Lấy thông tin người nhận
        cur.execute("SELECT * FROM bank WHERE username = %s FOR UPDATE", (recipient,))
        recipient_data = cur.fetchone()

        if not recipient_data:
            return jsonify({'message': 'Recipient does not exist on server2'}), 404

        # Cập nhật số dư
        new_sender_balance = sender_data[3] - amount
        new_recipient_balance = recipient_data[3] + amount

        cur.execute("UPDATE bank SET balance = %s WHERE username = %s", (new_sender_balance, sender))
        cur.execute("UPDATE bank SET balance = %s WHERE username = %s", (new_recipient_balance, recipient))

        conn.commit()
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()
        transfer_in_progress[sender] = False

    return jsonify({'message': 'Transfer successful on server_test'})


if __name__ == '__main__':
    app.run(host='192.168.198.1', port=5003, debug=True)
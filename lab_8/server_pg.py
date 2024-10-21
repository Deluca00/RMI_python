from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import psycopg2
import time

server_pg = Flask(__name__)
socketio = SocketIO(server_pg)

transfer_in_progress = {}


def get_postgres_connection():
    conn = psycopg2.connect(
        dbname='bank',
        user='tiendat',
        password='180104',
        host='localhost'
    )
    return conn


@server_pg.route('/login', methods=['POST'])
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


@server_pg.route('/transfer', methods=['POST'])
def transfer():
    sender = request.json['sender']
    recipient = request.json['recipient']
    amount = request.json['amount']

    if transfer_in_progress.get(sender, False):
        return jsonify({'message': 'Transfer in progress. Please wait.'}), 400

    transfer_in_progress[sender] = True

    try:
        time.sleep(10)

        pg_conn = get_postgres_connection()
        pg_cur = pg_conn.cursor()

        pg_cur.execute("SELECT * FROM bank WHERE username = %s FOR UPDATE", (sender,))
        sender_data = pg_cur.fetchone()

        if not sender_data or sender_data[3] < amount:
            return jsonify({'message': 'Insufficient balance'}), 400

        pg_cur.execute("SELECT * FROM bank WHERE username = %s FOR UPDATE", (recipient,))
        recipient_data = pg_cur.fetchone()

        if not recipient_data:
            return jsonify({'message': 'Recipient does not exist'}), 404

        new_sender_balance = sender_data[3] - amount
        new_recipient_balance = recipient_data[3] + amount

        pg_cur.execute("UPDATE bank SET balance = %s WHERE username = %s", (new_sender_balance, sender))
        pg_cur.execute("UPDATE bank SET balance = %s WHERE username = %s", (new_recipient_balance, recipient))

        pg_conn.commit()

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
    finally:
        pg_cur.close()
        pg_conn.close()
        transfer_in_progress[sender] = False  # Đánh dấu hoàn tất chuyển tiền

    return jsonify({'message': 'Transfer successful on server_pg'})


if __name__ == '__main__':
    server_pg.run(host='172.16.11.71', port=5003, debug=True)

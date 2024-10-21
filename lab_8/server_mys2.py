from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import mysql.connector
import time

server_mys = Flask(__name__)
socketio = SocketIO(server_mys)

transfer_in_progress = {}


def get_mysql_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='090104',
            database='bank'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


@server_mys.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    conn = get_mysql_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bank WHERE username = %s AND password = %s", (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return jsonify({'message': 'Login successful', 'balance': user[3]})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@server_mys.route('/transfer', methods=['POST'])
def transfer():
    sender = request.json['sender']
    recipient = request.json['recipient']
    amount = request.json['amount']

    if transfer_in_progress.get(sender, False):
        return jsonify({'message': 'Transfer in progress. Please wait.'}), 400

    transfer_in_progress[sender] = True

    try:
        time.sleep(3)

        mysql_conn = get_mysql_connection()
        mysql_cur = mysql_conn.cursor()

        mysql_cur.execute("SELECT * FROM bank WHERE username = %s FOR UPDATE", (sender,))
        sender_data = mysql_cur.fetchone()

        if not sender_data or sender_data[3] < amount:
            return jsonify({'message': 'Insufficient balance'}), 400

        mysql_cur.execute("SELECT * FROM bank WHERE username = %s FOR UPDATE", (recipient,))
        recipient_data = mysql_cur.fetchone()

        if not recipient_data:
            return jsonify({'message': 'Recipient does not exist'}), 404

        new_sender_balance = sender_data[3] - amount
        new_recipient_balance = recipient_data[3] + amount

        mysql_cur.execute("UPDATE bank SET balance = %s WHERE username = %s", (new_sender_balance, sender))
        mysql_cur.execute("UPDATE bank SET balance = %s WHERE username = %s", (new_recipient_balance, recipient))

        mysql_conn.commit()

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
    finally:
        mysql_cur.close()
        mysql_conn.close()
        transfer_in_progress[sender] = False

    return jsonify({'message': 'Transfer successful'})


if __name__ == '__main__':
    server_mys.run(host='192.168.198.2', port=5002, debug=True)


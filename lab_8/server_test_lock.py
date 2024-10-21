import time

from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Lưu trữ trạng thái khóa của các client
locked_clients = set()

# Kết nối tới cơ sở dữ liệu
def get_db_connection():
    conn = psycopg2.connect(
        dbname='bank',
        user='tiendat',
        password='180104',
        host='localhost'
    )
    return conn

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bank WHERE username = %s AND password = %s", (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return jsonify({'message': 'Login successful', 'balance': user[3]})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/lock_client', methods=['POST'])
def lock_client():
    client = request.json['client']
    locked_clients.add(client)
    return jsonify({'message': f'Client {client} is locked on server2'})

@app.route('/unlock_client', methods=['POST'])
def unlock_client():
    client = request.json['client']
    locked_clients.discard(client)
    return jsonify({'message': f'Client {client} is unlocked on server2'})

@app.route('/transfer', methods=['POST'])
def transfer():
    sender = request.json['sender']
    recipient = request.json['recipient']
    amount = request.json['amount']

    # Kiểm tra nếu client đang bị khóa
    if sender in locked_clients:
        return jsonify({'message': 'Transfer not allowed, client is locked'}), 403
    time.sleep(7)
    conn = get_db_connection()
    cur = conn.cursor()

    # Lấy thông tin người gửi
    cur.execute("SELECT * FROM bank WHERE username = %s", (sender,))
    sender_data = cur.fetchone()

    if not sender_data or sender_data[3] < amount:
        return jsonify({'message': 'Insufficient balance on server2'}), 400

    # Lấy thông tin người nhận
    cur.execute("SELECT * FROM bank WHERE username = %s", (recipient,))
    recipient_data = cur.fetchone()

    if not recipient_data:
        return jsonify({'message': 'Recipient does not exist on server2'}), 404

    # Cập nhật số dư
    new_sender_balance = sender_data[3] - amount
    new_recipient_balance = recipient_data[3] + amount

    cur.execute("UPDATE bank SET balance = %s WHERE username = %s", (new_sender_balance, sender))
    cur.execute("UPDATE bank SET balance = %s WHERE username = %s", (new_recipient_balance, recipient))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Transfer successful on server2'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
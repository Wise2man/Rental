import sqlite3

def init_db():
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY,
            landlord_id INTEGER,
            title TEXT,
            description TEXT,
            price REAL,
            available INTEGER,
            image_path TEXT,
            FOREIGN KEY (landlord_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            room_id INTEGER,
            customer_id INTEGER,
            payment_status TEXT,
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (customer_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            booking_id INTEGER,
            amount REAL,
            admin_fee REAL,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_image_column():
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE rooms ADD COLUMN image_path TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()

def add_user(username, password, role):
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()
    return True  # Successfully added user

def get_user(username):
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_room(landlord_id, title, description, price, image_path):
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO rooms (landlord_id, title, description, price, available, image_path) VALUES (?, ?, ?, ?, ?, ?)',
                   (landlord_id, title, description, price, 1, image_path))
    conn.commit()
    conn.close()

def update_room(room_id, title, description, price, image_path):
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE rooms SET title = ?, description = ?, price = ?, image_path = ? WHERE id = ?',
                   (title, description, price, image_path, room_id))
    conn.commit()
    conn.close()

def get_available_rooms(offset=0, limit=3):
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rooms WHERE available = 1 LIMIT ? OFFSET ?', (limit, offset))
    rooms = cursor.fetchall()
    conn.close()
    return rooms

def get_rooms_count():
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM rooms WHERE available = 1')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def book_room(room_id, customer_id):
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE rooms SET available = 0 WHERE id = ?', (room_id,))
    cursor.execute('INSERT INTO bookings (room_id, customer_id, payment_status) VALUES (?, ?, ?)',
                   (room_id, customer_id, 'Paid'))
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return booking_id  # Return the booking ID

def add_payment(booking_id, amount):
    admin_fee = amount * 0.10  # Calculate admin fee (10%)
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO payments (booking_id, amount, admin_fee) VALUES (?, ?, ?)',
                   (booking_id, amount, admin_fee))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def remove_user(username):
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def get_payments_by_customer(customer_id):
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, r.title, p.amount, p.admin_fee 
        FROM payments p
        JOIN bookings b ON p.booking_id = b.id
        JOIN rooms r ON b.room_id = r.id
        WHERE b.customer_id = ?
    ''', (customer_id,))
    payments = cursor.fetchall()
    conn.close()
    return payments

def get_total_payments_by_landlord(landlord_id):
    conn = sqlite3.connect('rental_app.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(p.amount) 
        FROM payments p
        JOIN bookings b ON p.booking_id = b.id
        JOIN rooms r ON b.room_id = r.id
        WHERE r.landlord_id = ?
    ''', (landlord_id,))
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0
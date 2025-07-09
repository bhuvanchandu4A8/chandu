from flask import Flask, request, jsonify, render_template_string
import sqlite3
import hashlib
import time
import secrets

app = Flask(__name__)

# Bug 1: FIXED - SQL Injection vulnerability prevented with parameterized queries
@app.route('/user/<user_id>')
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # SECURE: Using parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return jsonify({"id": result[0], "username": result[1], "password": "[REDACTED]"})
    else:
        return jsonify({"error": "User not found"}), 404

# Bug 2: FIXED - Logic error in password validation corrected
def validate_password(password):
    if len(password) < 8:
        return False
    has_digit = False
    has_upper = False
    has_lower = False
    
    for char in password:
        if char.isdigit():
            has_digit = True
        if char.isupper():
            has_upper = True
        if char.islower():
            has_lower = True
    
    # FIXED: Added missing return False for invalid passwords
    if has_digit and has_upper and has_lower:
        return True
    return False

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    password = data.get('password', '')
    
    if validate_password(password):
        # Hash password with salt using SHA-256 (better than MD5)
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return jsonify({"status": "success", "message": "User registered", "salt": salt})
    else:
        return jsonify({"status": "error", "message": "Invalid password"}), 400

# Bug 3: FIXED - Performance issue resolved with efficient O(n) algorithm
def find_duplicates(numbers):
    """Find duplicate numbers in a list - efficient O(n) implementation using set/dict"""
    seen = set()
    duplicates = set()
    
    # OPTIMIZED: Single pass O(n) algorithm using hash sets
    for num in numbers:
        if num in seen:
            duplicates.add(num)
        else:
            seen.add(num)
    
    return list(duplicates)

@app.route('/find-duplicates', methods=['POST'])
def api_find_duplicates():
    data = request.get_json()
    numbers = data.get('numbers', [])
    
    start_time = time.time()
    duplicates = find_duplicates(numbers)
    end_time = time.time()
    
    return jsonify({
        "duplicates": duplicates,
        "processing_time": end_time - start_time
    })

# Additional utility functions with bugs
def calculate_average(numbers):
    # Edge case bug: division by zero when empty list
    return sum(numbers) / len(numbers)

@app.route('/average', methods=['POST'])
def get_average():
    data = request.get_json()
    numbers = data.get('numbers', [])
    
    try:
        avg = calculate_average(numbers)
        return jsonify({"average": avg})
    except ZeroDivisionError:
        return jsonify({"error": "Cannot calculate average of empty list"}), 400

if __name__ == '__main__':
    # Initialize database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    cursor.execute("INSERT OR REPLACE INTO users VALUES (1, 'admin', 'hashed_password')")
    cursor.execute("INSERT OR REPLACE INTO users VALUES (2, 'user', 'another_hash')")
    conn.commit()
    conn.close()
    
    app.run(debug=True)
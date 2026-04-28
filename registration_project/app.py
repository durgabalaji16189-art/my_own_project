from flask import Flask, render_template, request, send_file
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# Create DB if not exists
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT UNIQUE,
            college TEXT,
            events TEXT,
            games TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()


# Home page
@app.route('/')
def home():
    return render_template('index.html')


# Submit form
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['participant_name']
    phone = request.form['phone_number']
    college = request.form['college']

    events = request.form.getlist('events[]')
    games = request.form.getlist('games[]')

    events_str = ", ".join(events)
    games_str = ", ".join(games)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Check duplicate
    cursor.execute("SELECT * FROM registrations WHERE phone=?", (phone,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return "This phone number already registered!"

    cursor.execute(
        "INSERT INTO registrations (name,phone,college,events,games) VALUES (?,?,?,?,?)",
        (name, phone, college, events_str, games_str)
    )

    conn.commit()
    conn.close()

    return render_template("success.html")


# Admin page (VIEW DATA 🔥)
@app.route('/admin')
def admin():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM registrations")
    data = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM registrations")
    total = cursor.fetchone()[0]

    conn.close()

    return render_template("admin.html", data=data, total=total)


# Export to Excel
@app.route('/export')
def export():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name,phone,college,events,games FROM registrations")
    data = cursor.fetchall()

    conn.close()

    df = pd.DataFrame(data, columns=["Name","Phone","College","Events","Games"])

    file = "registrations.xlsx"
    df.to_excel(file, index=False)

    return send_file(file, as_attachment=True)


# Run app (IMPORTANT FOR REPLIT)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)

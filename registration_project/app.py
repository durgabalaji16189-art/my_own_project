from flask import Flask, render_template, request
import mysql.connector
import pandas as pd

app = Flask(__name__)

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="durgabalaji8121@#",
    database="techmanthan"
)

# Home page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():

    name = request.form['participant_name']
    phone = request.form['phone_number']
    college = request.form['college']

    events = request.form.getlist('events[]')
    games = request.form.getlist('games[]')

    events_str = ", ".join(events)
    games_str = ", ".join(games)

    cursor = db.cursor()

    # Prevent duplicate phone numbers
    cursor.execute("SELECT * FROM registrations WHERE phone=%s", (phone,))
    existing = cursor.fetchone()

    if existing:
        return "This phone number already registered!"

    cursor.execute(
        "INSERT INTO registrations (name,phone,college,events,games) VALUES (%s,%s,%s,%s,%s)",
        (name, phone, college, events_str, games_str)
    )

    db.commit()

    return render_template("success.html")


# Admin page
@app.route('/admin')
def admin():

    cursor = db.cursor()

    cursor.execute("SELECT * FROM registrations")
    data = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM registrations")
    total = cursor.fetchone()[0]

    return render_template("admin.html", data=data, total=total)


# Export to Excel
@app.route('/export')
def export():

    cursor = db.cursor()

    cursor.execute("SELECT name,phone,college,events,games FROM registrations")
    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=["Name","Phone","College","Events","Games"])

    file = "registrations.xlsx"
    df.to_excel(file, index=False)

    return send_file(file, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
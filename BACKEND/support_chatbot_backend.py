from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# ✅ Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="Yuva",
    password="Yuvaatsql__06",
    database="imagebot_support"
)
cursor = conn.cursor()

# ✅ Create FAQ table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS faq (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255) NOT NULL,
    answer TEXT NOT NULL
)
''')

@app.route("/support_chat", methods=["POST"])
def support_chat():
    data = request.json
    user_message = data.get("user_message", "").strip().lower()

    # ✅ Search for answer in the database
    cursor.execute("SELECT answer FROM faq WHERE LOWER(question) = %s", (user_message,))
    result = cursor.fetchone()

    if result:
        response = result[0]
    else:
        response = "Sorry, I don’t have an answer to that question right now."

    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

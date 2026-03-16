import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="Yuva",  # Change if needed
        password="Yuva_06",  # Change if needed
        database="image_bot"
    )
    print("✅ Database Connected Successfully!")
except mysql.connector.Error as err:
    print(f"❌ Database Connection Error: {err}")

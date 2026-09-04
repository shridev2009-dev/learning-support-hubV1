import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_mysql_password",   # <-- change this to your MySQL password
        database="learning_hub"
    )

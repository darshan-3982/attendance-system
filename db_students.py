import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="darshan@3982",
    database="attendance_system"
)
cursor = db.cursor()

add_student = ("INSERT INTO students(name) VALUES(%s)")
student_data = ("pavantm",)

cursor.execute(add_student,student_data)
db.commit()

print(f"student added with id: {cursor.lastrowid}")

cursor.close()
db.close()
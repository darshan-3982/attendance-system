
import mysql.connector
import face_recognition
import cv2
import os
import numpy as np

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="darshan@3982",
    database="attendance_system"
)
cursor = connection.cursor()

# Encode and Store Faces
def store_face_encoding(student_name, image_path):
    # Load and encode image
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    if encodings:
        encoding = encodings[0]
        encoding_blob = np.array(encoding).tobytes()

        # Insert into database
        cursor.execute("INSERT INTO students (name, face_encoding) VALUES (%s, %s)",
                       (student_name, encoding_blob))
        connection.commit()
        print(f"Encoding for {student_name} stored successfully!")
    else:
        print("No face detected in the image.")

# Example of storing an encoding
store_face_encoding("Pavantm", r"C:\\Users\\User\\OneDrive\\Attachments\\Desktop\\attendance\\pavan tm\\Screenshot_2024-11-07-14-34-13-70_1c337646f29875672b5a61192b9010f9 - Copy - Copy (2).jpg")

# Close the connection
cursor.close()
connection.close()

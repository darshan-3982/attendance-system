import cv2
import face_recognition
import mysql.connector
import numpy as np
from datetime import date

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="darshan@3982",
    database="attendance_system"
)
cursor = connection.cursor()

# Load face encodings from the database
def load_face_encodings():
    cursor.execute("SELECT student_id, name, face_encoding FROM students")
    records = cursor.fetchall()
    
    student_ids = []
    student_names = []
    face_encodings = []
    
    for record in records:
        student_ids.append(record[0])  # student_id
        student_names.append(record[1])  # name
        encoding = np.frombuffer(record[2], dtype=np.float64)  # Convert binary to array
        face_encodings.append(encoding)
    
    return student_ids, student_names, face_encodings


student_ids, student_names, known_face_encodings = load_face_encodings()

# Initialize webcam
video_capture = cv2.VideoCapture(0)

# Process video feed
while True:
    ret, frame = video_capture.read()
    if not ret:
        break
    
    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]
    
    # Detect faces in the frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    
    for face_encoding in face_encodings:
        # Compare the detected face with known encodings
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            student_id = student_ids[best_match_index]
            student_name = student_names[best_match_index]
            
            # Mark attendance in the database
            today = date.today()
            cursor.execute("SELECT * FROM attendance WHERE student_id = %s AND date = %s", (student_id, today))
            result = cursor.fetchone()
            
            if result is None:  # Only mark attendance if not already marked
                cursor.execute("INSERT INTO attendance (student_id, name, date, status) VALUES (%s, %s, %s, %s)",
                               (student_id, student_name, today, "Present"))
                connection.commit()
                print(f"Attendance marked for {student_name}.")
            else:
                print(f"Attendance for {student_name} is already marked.")

    # Display the video feed
    cv2.imshow('Video', frame)
    
    # Break loop with 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
video_capture.release()
cv2.destroyAllWindows()
cursor.close()
connection.close()

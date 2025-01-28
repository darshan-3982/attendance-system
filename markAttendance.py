from flask import Flask, request, jsonify
import face_recognition
import mysql.connector
from io import BytesIO
from flask_cors import CORS
from datetime import datetime
import pickle
import pandas as pd
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler

# Flask app and CORS setup
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory for Excel file generation
OUTPUT_DIR = "./generated_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="darshan@3982",  
        database="new_attendance_system"
    )

# Attendance Marking
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check for uploaded image
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        # Load image and encode face
        image_file = request.files['image']
        image_bytes = image_file.read()
        image = face_recognition.load_image_file(BytesIO(image_bytes))
        face_encodings = face_recognition.face_encodings(image)
        if not face_encodings:
            return jsonify({"error": "No face detected in the uploaded image"}), 400

        uploaded_face_encoding = face_encodings[0]
        current_day = datetime.now().strftime('%A')
        current_time = datetime.now().strftime('%H:%M:%S')  # Current time in 24-hour format

        # Fetch lecture details for the current time
        cursor.execute("""
            SELECT lecture_schedule_id, subject, start_time, end_time
            FROM lecture_schedule
            WHERE day = %s AND start_time <= %s AND end_time >= %s
        """, (current_day, current_time, current_time))
        lecture_info = cursor.fetchone()

        if not lecture_info:
            return jsonify({"error": f"No lecture found for the current time ({current_time}) on {current_day}"}), 400

        lecture_schedule_id, subject, start_time, end_time = lecture_info

        # Fetch student face encodings
        cursor.execute("SELECT student_id, face_encoding FROM students")
        students_data = cursor.fetchall()

        student_id = None
        for db_student_id, db_face_encoding in students_data:
            try:
                db_face_encoding = pickle.loads(db_face_encoding)
                match = face_recognition.compare_faces([db_face_encoding], uploaded_face_encoding, tolerance=0.5)
                if match[0]:
                    student_id = db_student_id
                    break
            except Exception as e:
                logging.error(f"Error processing student {db_student_id}: {str(e)}")

        if not student_id:
            return jsonify({"error": "Student not recognized"}), 400

        attendance_date = datetime.now().strftime('%Y-%m-%d')

        # Check if attendance already marked
        cursor.execute("""
            SELECT attendance_id
            FROM attendance
            WHERE student_id = %s AND attendance_date = %s AND lecture_schedule_id = %s
        """, (student_id, attendance_date, lecture_schedule_id))
        if cursor.fetchone():
            return jsonify({"message": "Attendance already marked for this student"}), 200

        # Mark attendance
        cursor.execute("""
            INSERT INTO attendance (student_id, lecture_schedule_id, attendance_date, status)
            VALUES (%s, %s, %s, 'Present')
        """, (student_id, lecture_schedule_id, attendance_date))
        connection.commit()

        return jsonify({"message": "Attendance marked successfully"}), 200

    except Exception as e:
        logging.error(f"Error in mark_attendance: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# View Attendance
@app.route('/view_attendance', methods=['GET'])
def view_attendance():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT a.attendance_id, s.name, ls.subject, ls.start_time, a.attendance_date, a.status
            FROM attendance AS a
            LEFT JOIN students AS s ON a.student_id = s.student_id
            LEFT JOIN lecture_schedule AS ls ON a.lecture_schedule_id = ls.lecture_schedule_id
            WHERE a.attendance_date = CURDATE()
            ORDER BY a.attendance_date DESC, ls.start_time ASC
        """)

        attendance_records = cursor.fetchall()

        attendance_data = [
            {
                "attendance_id": record[0],
                "name": record[1],
                "subject": record[2],
                "start_time": record[3].strftime('%I:%M %p') if isinstance(record[3], datetime) else str(record[3]),
                "attendance_date": record[4].strftime('%Y-%m-%d'),
                "status": record[5]
            }
            for record in attendance_records
        ]

        if not attendance_data:
            return jsonify({"message": "No attendance records found."}), 404

        return jsonify({"attendance": attendance_data})

    except Exception as e:
        logging.error(f"Error in view_attendance: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Automatic Excel Generation Tasks
def generate_hourly_attendance_excel():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        current_hour = datetime.now().hour
        cursor.execute("""
            SELECT a.attendance_id, s.name, ls.subject, a.attendance_date, a.status
            FROM attendance AS a
            JOIN students AS s ON a.student_id = s.student_id
            JOIN lecture_schedule AS ls ON a.lecture_schedule_id = ls.lecture_schedule_id
            WHERE HOUR(ls.start_time) = %s AND a.attendance_date = CURDATE()
        """, (current_hour,))

        records = cursor.fetchall()
        if records:
            file_name = f"Hourly_Attendance_{datetime.now().strftime('%Y%m%d_%H')}.xlsx"
            file_path = os.path.join(OUTPUT_DIR, file_name)
            pd.DataFrame(records, columns=["Attendance ID", "Name", "Subject", "Date", "Status"]).to_excel(file_path, index=False)
            logging.info(f"Hourly Excel generated: {file_path}")

    except Exception as e:
        logging.error(f"Error generating hourly attendance: {e}")

def generate_daily_attendance_excel():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT a.attendance_id, s.name, ls.subject, a.attendance_date, a.status
            FROM attendance AS a
            JOIN students AS s ON a.student_id = s.student_id
            JOIN lecture_schedule AS ls ON a.lecture_schedule_id = ls.lecture_schedule_id
            WHERE a.attendance_date = CURDATE()
        """)

        records = cursor.fetchall()
        if records:
            file_name = f"Daily_Attendance_{datetime.now().strftime('%Y%m%d')}.xlsx"
            file_path = os.path.join(OUTPUT_DIR, file_name)
            pd.DataFrame(records, columns=["Attendance ID", "Name", "Subject", "Date", "Status"]).to_excel(file_path, index=False)
            logging.info(f"Daily Excel generated: {file_path}")

    except Exception as e:
        logging.error(f"Error generating daily attendance: {e}")

# Scheduler Setup
scheduler = BackgroundScheduler()
scheduler.add_job(generate_hourly_attendance_excel, 'cron', minute=59)
scheduler.add_job(generate_daily_attendance_excel, 'cron', hour=23, minute=59)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)

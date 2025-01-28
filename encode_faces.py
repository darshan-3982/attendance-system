import os
import face_recognition
import numpy as np
import mysql.connector
import logging
import pickle

# Database connection details
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "darshan@3982",
    "database": "new_attendance_system"
}

# Directory where student folders are stored
STUDENT_DIR = "C:\\Users\\User\\darshan"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_db():
    """Connect to the MySQL database."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        logging.info("Successfully connected to the database.")
        return connection
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to MySQL: {err}")
        return None

def check_existing_student(name, cursor):
    """Check if a student with the given name already exists in the database."""
    cursor.execute("SELECT COUNT(*) FROM students WHERE name = %s", (name,))
    result = cursor.fetchone()
    return result[0] > 0  # True if the student exists, False otherwise

def encode_faces():
    """Encode faces for each student based on folder structure."""
    connection = connect_to_db()
    if not connection:
        return

    cursor = connection.cursor()

    # Ensure the students table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            face_encoding BLOB NOT NULL
        )
    """)
    connection.commit()

    for folder_name in os.listdir(STUDENT_DIR):
        folder_path = os.path.join(STUDENT_DIR, folder_name)

        if not os.path.isdir(folder_path):
            continue

        logging.info(f"Processing folder: {folder_name}")

        # Skip encoding if the student already exists in the database
        if check_existing_student(folder_name, cursor):
            logging.info(f"Student '{folder_name}' already exists in the database. Skipping...")
            continue

        encodings = []

        for image_file in os.listdir(folder_path):
            if not image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            image_path = os.path.join(folder_path, image_file)
            try:
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    encodings.append(face_encodings[0])
                else:
                    logging.warning(f"No face detected in {image_file}. Skipping...")
            except Exception as e:
                logging.error(f"Error processing {image_file}: {e}")

        if encodings:
            average_encoding = np.mean(encodings, axis=0)

            # Validate encoding length
            if len(average_encoding) == 128:
                encoding_blob = pickle.dumps(average_encoding)

                try:
                    cursor.execute(
                        "INSERT INTO students (name, face_encoding) VALUES (%s, %s)",
                        (folder_name, encoding_blob)
                    )
                    connection.commit()
                    logging.info(f"Stored encoding for {folder_name}.")
                except mysql.connector.Error as err:
                    logging.error(f"Failed to insert encoding for {folder_name}: {err}")
            else:
                logging.warning(f"Invalid encoding length for {folder_name}. Skipping...")
        else:
            logging.warning(f"No valid encodings for {folder_name}. Skipping...")

    # Commit changes and close the connection
    cursor.close()
    connection.close()
    logging.info("Encoding complete.")

if __name__ == "__main__":
    # Encode and store face encodings
    encode_faces()

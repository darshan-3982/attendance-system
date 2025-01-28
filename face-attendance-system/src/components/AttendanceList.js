import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; // For navigation
import "bootstrap/dist/css/bootstrap.min.css";
import "../styles/AttendanceList.scss"; // Add custom styles here

const AttendanceList = () => {
  const [attendance, setAttendance] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate(); // For navigation

  useEffect(() => {
    const fetchAttendance = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://127.0.0.1:5000/view_attendance");

        if (!response.ok) {
          throw new Error("Failed to fetch attendance records.");
        }

        const data = await response.json();

        if (data.attendance) {
          setAttendance(data.attendance);
        } else {
          setAttendance([]);
          setError(data.message || "No attendance data available.");
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAttendance();
  }, []);

  return (
    <div className="container attendance-list">
      <h3 className="mt-4 text-center">Attendance Records</h3>

      {loading ? (
        <p className="text-primary text-center">Loading attendance records...</p>
      ) : error ? (
        <p className="text-danger text-center">{error}</p>
      ) : attendance.length > 0 ? (
        <div className="table-responsive mt-3">
          <table className="table table-hover table-bordered">
            <thead className="table-primary">
              <tr>
                <th>Name</th>
                <th>Subject</th>
                <th>Start Time</th>
                <th>Attendance Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {attendance.map((record, index) => (
                <tr key={index}>
                  <td>{record.name}</td>
                  <td>{record.subject}</td>
                  <td>{record.start_time}</td>
                  <td>{record.attendance_date}</td>
                  <td>{record.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-warning text-center">
          No attendance records found for today.
        </p>
      )}

      {/* Home Button */}
      <div className="text-center mt-4">
        <button
          className="btn btn-primary"
          onClick={() => navigate("/")} // Navigate to home
        >
          Home
        </button>
      </div>
    </div>
  );
};

export default AttendanceList;

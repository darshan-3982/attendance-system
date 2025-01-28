import React from "react"
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom"
import CaptureImage from "./components/CaptureImage"
import AttendanceList from "./components/AttendanceList"
import "bootstrap/dist/css/bootstrap.min.css"
import "./App.css"

function App() {
  return (
    <Router>
      <div className="App d-flex flex-column min-vh-100">
        

        <main className="container flex-grow-1 my-5">
          <Routes>
            <Route path="/capture-image" element={<CaptureImage />} />
            <Route path="/attendance-list" element={<AttendanceList />} />
            <Route path="/" element={<HomePage />} />
          </Routes>
        </main>

        <footer className="py-3 mt-auto">
          <div className="container text-center">
            <small className="text-muted">&copy; 2023 Face-Based Attendance System. All rights reserved.</small>
          </div>
        </footer>
      </div>
    </Router>
  )
}

function HomePage() {
  return (
    <div className="text-center">
      <div className="card p-4">
        <h2 className="mb-4">Welcome to the Face-Based Attendance System</h2>
        <div className="row justify-content-center">
          <div className="col-md-6">
            <Link to="/capture-image" className="btn btn-primary btn-lg btn-block mb-3 w-100">
              <i className="bi bi-camera-fill me-2"></i>Capture Image
            </Link>
            <Link to="/attendance-list" className="btn btn-success btn-lg btn-block w-100">
              <i className="bi bi-list-check me-2"></i>View Attendance
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App 


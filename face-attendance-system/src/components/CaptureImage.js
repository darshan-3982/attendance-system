import React, { useRef, useEffect, useCallback, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import '../styles/CaptureImage.scss';


function CaptureImage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [statusMessage, setStatusMessage] = useState(""); 
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const captureAndSendImage = useCallback(() => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    if (!video || !canvas) {
      setStatusMessage("Video or Canvas reference is missing!");
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (!blob) {
        setStatusMessage("Failed to capture image!");
        return;
      }

      setIsLoading(true);
      const formData = new FormData();
      formData.append("image", blob, "captured_image.png");

      try {
        const lectureHour = getLectureHour();

        const response = await axios.post(
          `http://localhost:5000/mark_attendance?lecture_hour=${lectureHour}`,
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );

        if (response.data.message.includes("No ongoing lecture")) {
          setStatusMessage(response.data.message); // Show next lecture info
        } else {
          setStatusMessage(response.data.message || "Attendance marked successfully.");
        }
      } catch (error) {
        console.error("Error sending image:", error);
        setStatusMessage(error.response?.data?.error || "Error: Unable to mark attendance.");
      } finally {
        setIsLoading(false);
      }
    }, "image/png");
  }, []);

  const getLectureHour = () => {
    const currentHour = new Date().getHours();
    if (currentHour >= 9 && currentHour < 10) return "1st Hour";
    if (currentHour >= 10 && currentHour < 11) return "2nd Hour";
    if (currentHour >= 11 && currentHour < 12) return "3rd Hour";
    if (currentHour >= 12 && currentHour < 1) return "4th Hour";
    if (currentHour >= 1 && currentHour < 2) return "5th Hour";
    return "Unknown Hour";
  };

  useEffect(() => {
    let videoStream = null;

    const startVideo = async () => {
      try {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = videoStream;
      } catch (err) {
        setStatusMessage("Error accessing webcam.");
        console.error("Error accessing webcam: ", err);
      }
    };

    startVideo();

    const captureInterval = setInterval(() => {
      captureAndSendImage();
    }, 10 * 1000); // 30 seconds interval

    return () => {
      clearInterval(captureInterval);
      if (videoStream) {
        videoStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [captureAndSendImage]);

  return (
    <div className="capture-image-container">
      <h2>Lecture Attendance</h2>
      <video
        ref={videoRef}
        className="video-stream"
        autoPlay
        muted
      ></video>
      <canvas ref={canvasRef} style={{ display: "none" }}></canvas>
      {isLoading && (
        <p className="status-message loading">Uploading and marking attendance...</p>
      )}
      {statusMessage && (
        <p className="status-message">{statusMessage}</p>
      )}
      <button className="home-button" onClick={() => navigate("/")}>Home</button>
    </div>
  );
}

export default CaptureImage;

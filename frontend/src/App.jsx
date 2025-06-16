import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";

function App() {
  const webcamRef = useRef(null);
  const [count, setCount] = useState(null);
  const [facingMode, setFacingMode] = useState("environment");
  const [capturedImage, setCapturedImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false); // Loading state

  const videoConstraints = {
    facingMode: facingMode,
    width: { ideal: 400 }
  };

  const toggleCamera = () => {
    setFacingMode(prev =>
      prev === "user" ? "environment" : "user"
    );
    setCapturedImage(null);
    setCount(null);
    setIsLoading(false);
  };

  const captureAndSend = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
    setIsLoading(true); // Start showing "Counting..."

    const blob = await (await fetch(imageSrc)).blob();
    const formData = new FormData();
    formData.append("file", blob, "capture.jpg");

    try {
      const res = await axios.post("https://plate-counter-backend.onrender.com/count-plates", formData);
      setCount(res.data.count);
    } catch (err) {
      console.error("Error:", err);
    } finally {
      setIsLoading(false); // Stop showing "Counting..."
    }
  };

  const resetCamera = () => {
    setCapturedImage(null);
    setCount(null);
    setIsLoading(false);
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h1>Plate Counter App</h1>

      {capturedImage ? (
        <img
          src={capturedImage}
          alt="Captured"
          style={{ width: "90%", maxWidth: 400 }}
        />
      ) : (
        <Webcam
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={videoConstraints}
          style={{ width: "90%", maxWidth: 400 }}
        />
      )}

      <br /><br />

      {capturedImage ? (
        <button onClick={resetCamera}>Reset Camera</button>
      ) : (
        <button onClick={captureAndSend}>Capture & Count Plates</button>
      )}

      <br /><br />

      <button onClick={toggleCamera}>
        Switch to {facingMode === "user" ? "Rear" : "Front"} Camera
      </button>

      {/* Display Counting... or Count result */}
      {isLoading && <h2>Counting...</h2>}
      {!isLoading && count !== null && <h2>Detected Plates: {count}</h2>}
    </div>
  );
}

export default App;

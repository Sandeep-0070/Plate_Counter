import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";

function App() {
  const webcamRef = useRef(null);
  const [count, setCount] = useState(null);
  const [facingMode, setFacingMode] = useState("environment");
  const [capturedImage, setCapturedImage] = useState(null);

  const videoConstraints = {
    facingMode: facingMode,
    width: { ideal: 400 }
  };

  const toggleCamera = () => {
    setFacingMode(prev =>
      prev === "user" ? "environment" : "user"
    );
    setCapturedImage(null); // Reset the captured image when switching camera
    setCount(null);         // Optional: Reset count on toggle
  };

  const captureAndSend = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc); // Freeze frame by storing it
    const blob = await (await fetch(imageSrc)).blob();
    const formData = new FormData();
    formData.append("file", blob, "capture.jpg");

    try {
      const res = await axios.post("http://127.0.0.1:5000/count-plates", formData);
      setCount(res.data.count);
    } catch (err) {
      console.error("Error:", err);
    }
  };

  const resetCamera = () => {
    setCapturedImage(null);
    setCount(null);
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

      {count !== null && <h2>Detected Plates: {count}</h2>}
    </div>
  );
}

export default App;


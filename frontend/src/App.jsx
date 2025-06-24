import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";

function App() {
  const webcamRef = useRef(null);
  const [count, setCount] = useState(null);
  const [cumulative, setCumulative] = useState(0);
  const [facingMode, setFacingMode] = useState("environment");
  const [capturedImage, setCapturedImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const videoConstraints = {
    facingMode: facingMode,
    width: { ideal: 400 }
  };

  const toggleCamera = () => {
    setFacingMode(prev => (prev === "user" ? "environment" : "user"));
    setCapturedImage(null);
    setCount(null);
    setIsLoading(false);
  };

  const captureAndSend = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
    setIsLoading(true);

    const blob = await (await fetch(imageSrc)).blob();
    const formData = new FormData();
    formData.append("file", blob, "capture.jpg");

    try {
      const res = await axios.post("https://plate-counter-backend.onrender.com/count-plates", formData);
      if (res.data.count !== null) {
        setCount(res.data.count);
        setCumulative(res.data.cumulative);
      } else {
        setCount("Try again");
      }
    } catch (err) {
      console.error("Error:", err);
      setCount("Error");
    } finally {
      setIsLoading(false);
    }
  };

  const resetCamera = () => {
    setCapturedImage(null);
    setCount(null);
    setIsLoading(false);
  };

  const resetBatch = async () => {
    try {
      const res = await axios.post("https://plate-counter-backend.onrender.com/reset-batch");
      setCumulative(res.data.cumulative);
      setCount(null);
    } catch (err) {
      console.error("Reset failed:", err);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h1>Plate Counter</h1>

      {capturedImage ? (
        <img src={capturedImage} alt="Captured" style={{ width: "90%", maxWidth: 400 }} />
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

      <br /><br />

      <button onClick={resetBatch}>Reset Batch</button>

      {isLoading && <h2>Counting...</h2>}
      {!isLoading && count !== null && <h2>Detected Plates: {count}</h2>}
      <h3>Cumulative Count: {cumulative}</h3>
    </div>
  );
}

export default App;

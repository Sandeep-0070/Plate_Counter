import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";

const videoConstraints = {
  facingMode: { exact: "environment" }  // back camera
};

const CameraCapture = () => {
  const webcamRef = useRef(null);
  const [count, setCount] = useState(null);
  const [loading, setLoading] = useState(false);

  const capture = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    // Convert Base64 to Blob
    const res = await fetch(imageSrc);
    const blob = await res.blob();

    const formData = new FormData();
    formData.append("image", blob, "capture.jpg");

    setLoading(true);
    try {
      const response = await axios.post("https://plate-counter-backend.onrender.com/count-plates", formData);
      setCount(response.data.count);
    } catch (error) {
      console.error("Error:", error);
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Plate Counter (Mobile)</h2>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        videoConstraints={videoConstraints}
        style={{ width: "100%", maxWidth: "400px" }}
      />
      <br />
      <button onClick={capture}>Capture & Count</button>
      {loading && <p>Processing...</p>}
      {count !== null && <h3>Detected Plates: {count}</h3>}
    </div>
  );
};

export default CameraCapture;

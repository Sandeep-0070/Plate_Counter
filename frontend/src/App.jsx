import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";

function App() {
  const webcamRef = useRef(null);
  const [count, setCount] = useState(null);

  const captureAndSend = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    const blob = await (await fetch(imageSrc)).blob();
    const formData = new FormData();
    formData.append("file", blob, "capture.jpg");

    try {
      const res = await axios.post("https://plate-counter-backend.onrender.com/count-plates", formData);
      setCount(res.data.count);
    } catch (err) {
      console.error("Error:", err);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h1>Plate Counter App</h1>
      <Webcam
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        style={{ width: 400 }}
      />
      <br />
      <button onClick={captureAndSend}>Capture & Count Plates</button>
      {count !== null && <h2>Detected Plates: {count}</h2>}
    </div>
  );
}

export default App;


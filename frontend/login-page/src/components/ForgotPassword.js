// ForgotPassword.js

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { animated, useSpring } from "react-spring";
import { initializeApp } from "firebase/app";
import { getAuth, sendPasswordResetEmail } from "firebase/auth";
import backgroundImage from "./assets/a5664499f471d5ffea014995dd2abe90.jpg";
import './ForgotPass.css';

// Firebase configuration (replace these with your Firebase project's details)
const firebaseConfig = {
  apiKey: "AIzaSyCo5EiGMBp78R831SwNwohpP-YGhx-1uzQ",
  authDomain: "brochura-e5b4d.firebaseapp.com",
  projectId: "brochura-e5b4d",
  storageBucket: "brochura-e5b4d.firebasestorage.app",
  messagingSenderId: "368792810448",
  appId: "368792810448:web:7a779e74887627d1d3ffd5"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  const props = useSpring({
    opacity: 1,
    from: { opacity: 0 },
    config: { duration: 1000 },
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await sendPasswordResetEmail(auth, email);
      setMessage("Password reset link sent to your email!");
      setIsError(false);
      setTimeout(() => {
        navigate("/login");
      }, 3000);
    } catch (error) {
      setMessage("Error sending reset link. Please try again.");
      setIsError(true);
    }
  };

  return (
    <div 
      className="forgot-password-container"
      style={{
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <animated.div style={props} className="forgot-password-box">
        <div className="watermark">BROCHURA</div>
        <div className="forgot-password-content">
          <h2>Reset Password</h2>
          <form onSubmit={handleSubmit} className="forgot-password-form">
            <div className="input-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                className="input-field"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />
            </div>
            {message && (
              <div className={`message ${isError ? 'error' : 'success'}`}>
                {message}
              </div>
            )}
            <button type="submit" className="reset-button">
              Send Reset Link
            </button>
            <div className="back-to-login">
              <span onClick={() => navigate("/LoginPage")}>
                Back to Login
              </span>
            </div>
          </form>
        </div>
      </animated.div>
    </div>
  );
};

export default ForgotPassword;

// LoginPage.js
import { GoogleLogin } from '@react-oauth/google';
import React, { useState } from "react";
import { FaFacebookF, FaGoogle } from "react-icons/fa";
import { useNavigate } from 'react-router-dom';
import { animated, useSpring } from "react-spring";
import { authAPI } from '../services/auth';
import backgroundImage from "./assets/a5664499f471d5ffea014995dd2abe90.jpg";
import './login.css';

const LoginPage = () => {
  const navigate = useNavigate();
  const props = useSpring({
    opacity: 1,
    from: { opacity: 0 },
    config: { duration: 1000 },
  });

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLoginClick = async () => {
    // Validate inputs
    if (email.trim() === '' || password.trim() === '') {
      setErrorMessage('Please enter both email and password.');
      return;
    }

    try {
      setIsLoading(true);
      setErrorMessage('');
      
      // Call Spring Boot login endpoint
      const userData = await authAPI.login(email, password);
      
      // If successful, store user data and navigate
      if (userData) {
        // Navigate to home or dashboard
        navigate('/');
      }
    } catch (error) {
      setErrorMessage(error.message || 'Invalid email or password.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (response) => {
    try {
      setIsLoading(true);
      setErrorMessage('');
      
      if (!response?.credential) {
        throw new Error('No credential received from Google');
      }
      
      // Send Google token to Spring Boot backend
      const result = await authAPI.googleLogin(response.credential);
      
      if (result) {
        navigate('/generate-brochure');
      }
    } catch (error) {
      console.error('Google login error:', error);
      setErrorMessage(error.message || 'Google login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleError = (error) => {
    console.error('Google login error:', error);
    setErrorMessage('Failed to initialize Google login. Please try again later.');
    setIsLoading(false);
  };

  const handleFacebookLogin = async () => {
    try {
      setIsLoading(true);
      setErrorMessage('');
      
      // Implement Facebook login with Spring Boot
      const result = await authAPI.facebookLogin();
      
      if (result) {
        navigate('/generate-brochure');
      }
    } catch (error) {
      setErrorMessage('Facebook login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="login-page-container"
      style={{
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <animated.div 
        style={props} 
        className="login-box"
      >
        <div className="watermark">BROCHURA</div>
        <div className="login-content">
          <h2 className="login-title">LOGIN</h2>
          
          <div className="input-group">
            <label className="login-label">Email</label>
            <input
              type="email"
              className="login-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              disabled={isLoading}
            />
          </div>

          <div className="input-group">
            <label className="login-label">Password</label>
            <input
              type="password"
              className="login-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              disabled={isLoading}
            />
          </div>

          {errorMessage && <p className="error-message">{errorMessage}</p>}

          <div className="login-button-container">
            <button className="login-button" onClick={handleLoginClick} disabled={isLoading}>
              {isLoading ? 'Logging in...' : 'LOGIN'}
            </button>
          </div>

          <div className="login-links">
            <span className="login-link" onClick={() => navigate('/forgot-password')} disabled={isLoading}>
              Forgot Password?
            </span>
            <span className="login-link" onClick={() => navigate('/create-account')} disabled={isLoading}>
              Create Account
            </span>
          </div>

          <div className="social-login-buttons">
            <GoogleLogin
              clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              useOneTap={false}
              theme="filled_black"
              text="signin_with"
              shape="rectangular"
              locale="en"
            />
            <button className="social-login-button" onClick={handleFacebookLogin} disabled={isLoading}>
              <FaFacebookF className="social-icon" />
              Facebook
            </button>
          </div>
        </div>
      </animated.div>
    </div>
  );
};

export default LoginPage;

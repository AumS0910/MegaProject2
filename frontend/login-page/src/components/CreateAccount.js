// CreateAccount.js
import { GoogleLogin } from '@react-oauth/google';
import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
import { animated, useSpring } from "react-spring";
import { FaFacebookF, FaGoogle } from "react-icons/fa";
import { authAPI } from '../services/auth';
import backgroundImage from "./assets/a5664499f471d5ffea014995dd2abe90.jpg";
import './CreateAccount.css';

const CreateAccount = () => {
  const navigate = useNavigate();
  const props = useSpring({
    opacity: 1,
    from: { opacity: 0 },
    config: { duration: 1000 },
  });

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleCreateAccount = async () => {
    // Validate inputs
    if (!firstName || !lastName || !email || !password) {
      setErrorMessage('Please fill in all fields.');
      return;
    }

    try {
      setIsLoading(true);
      setErrorMessage('');

      // Call Spring Boot register endpoint
      const userData = {
        firstName,
        lastName,
        email,
        password
      };

      await authAPI.register(userData);
      
      // Navigate to login page after successful registration
      navigate('/LoginPage');
      
    } catch (error) {
      setErrorMessage(error.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignup = async (response) => {
    try {
      setIsLoading(true);
      setErrorMessage('');
      
      // Send Google token to Spring Boot backend
      const result = await authAPI.googleLogin(response.credential);
      
      if (result) {
        navigate('/generate-brochure');
      }
    } catch (error) {
      setErrorMessage('Google signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFacebookSignup = async () => {
    try {
      setIsLoading(true);
      setErrorMessage('');
      
      // Implement Facebook signup with Spring Boot
      const result = await authAPI.facebookLogin();
      
      if (result) {
        navigate('/generate-brochure');
      }
    } catch (error) {
      setErrorMessage('Facebook signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="create-account-container"
      style={{
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <div className="create-account-box">
        <div className="watermark">BROCHURA</div>
        <div className="create-account-content">
          <h2>Create Account</h2>

          <div className="input-group">
            <label htmlFor="firstName" className="login-label">First Name</label>
            <input 
              type="text" 
              id="firstName" 
              className="login-input" 
              value={firstName} 
              onChange={(e) => setFirstName(e.target.value)}
              disabled={isLoading}
            />
          </div>

          <div className="input-group">
            <label htmlFor="lastName" className="login-label">Last Name</label>
            <input 
              type="text" 
              id="lastName" 
              className="login-input" 
              value={lastName} 
              onChange={(e) => setLastName(e.target.value)}
              disabled={isLoading}
            />
          </div>

          <div className="input-group">
            <label htmlFor="email" className="login-label">Email</label>
            <input 
              type="email" 
              id="email" 
              className="login-input" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
            />
          </div>

          <div className="input-group">
            <label htmlFor="password" className="login-label">Password</label>
            <input 
              type="password" 
              id="password" 
              className="login-input" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />
          </div>

          {errorMessage && <p className="error-message">{errorMessage}</p>}

          <button 
            className="login-button" 
            onClick={handleCreateAccount}
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>

          <div className="login-links">
            <span className="login-link" onClick={() => navigate('/LoginPage')} disabled={isLoading}>
              Already a Member? Log In
            </span>
          </div>

          <div className="social-login-buttons">
            <button 
              className="social-login-button" 
              onClick={handleFacebookSignup}
              disabled={isLoading}
            >
              <FaFacebookF className="social-icon" /> Sign up with Facebook
            </button>

            <GoogleLogin
              clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}
              onSuccess={handleGoogleSignup}
              onFailure={(error) => setErrorMessage('Google signup failed. Please try again.')}
              cookiePolicy={'single_host_origin'}
              render={renderProps => (
                <button 
                  onClick={renderProps.onClick} 
                  disabled={renderProps.disabled || isLoading} 
                  className="social-login-button"
                >
                  <FaGoogle className="social-icon" /> Sign up with Google
                </button>
              )}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateAccount;

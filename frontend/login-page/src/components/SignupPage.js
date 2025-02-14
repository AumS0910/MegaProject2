import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { animated, useSpring } from "react-spring";
import { FaGoogle, FaFacebookF } from "react-icons/fa";
import { authAPI } from "../services/auth";
import backgroundImage from "./assets/a5664499f471d5ffea014995dd2abe90.jpg";
import "./signup.css";

const SignupPage = () => {
  const navigate = useNavigate();
  const props = useSpring({
    opacity: 1,
    from: { opacity: 0 },
    config: { duration: 1000 },
  });

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    company: "",
    role: "USER",
  });
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setErrorMessage("Passwords do not match!");
      return;
    }

    try {
      setIsLoading(true);
      setErrorMessage("");
      
      await authAPI.signup({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        company: formData.company,
        role: formData.role,
      });

      // Redirect to login page on successful signup
      navigate("/login");
    } catch (error) {
      setErrorMessage(error.message || "Signup failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="signup-page-container"
      style={{
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <animated.div style={props} className="signup-box">
        <div className="watermark">BROCHURA</div>
        <div className="signup-content">
          <h2 className="signup-title">Create Account</h2>

          <form onSubmit={handleSignup} className="signup-form">
            <div className="input-group">
              <label className="signup-label">Full Name</label>
              <input
                type="text"
                name="name"
                className="signup-input"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Enter your full name"
                required
              />
            </div>

            <div className="input-group">
              <label className="signup-label">Email</label>
              <input
                type="email"
                name="email"
                className="signup-input"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter your email"
                required
              />
            </div>

            <div className="input-row">
              <div className="input-group">
                <label className="signup-label">Password</label>
                <input
                  type="password"
                  name="password"
                  className="signup-input"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Create password"
                  required
                />
              </div>

              <div className="input-group">
                <label className="signup-label">Confirm Password</label>
                <input
                  type="password"
                  name="confirmPassword"
                  className="signup-input"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  placeholder="Confirm password"
                  required
                />
              </div>
            </div>

            <div className="input-group">
              <label className="signup-label">Company</label>
              <input
                type="text"
                name="company"
                className="signup-input"
                value={formData.company}
                onChange={handleInputChange}
                placeholder="Enter your company name"
                required
              />
            </div>

            <div className="input-group">
              <label className="signup-label">Role</label>
              <select
                name="role"
                className="signup-input"
                value={formData.role}
                onChange={handleInputChange}
                required
              >
                <option value="USER">User</option>
                <option value="ADMIN">Admin</option>
              </select>
            </div>

            {errorMessage && <div className="error-message">{errorMessage}</div>}

            <button type="submit" className="signup-button" disabled={isLoading}>
              {isLoading ? "Creating Account..." : "Sign Up"}
            </button>
          </form>

          <div className="signup-divider">
            <span>or sign up with</span>
          </div>

          <div className="social-signup-buttons">
            <button className="social-signup-button google">
              <FaGoogle className="social-icon" /> Google
            </button>
            <button className="social-signup-button facebook">
              <FaFacebookF className="social-icon" /> Facebook
            </button>
          </div>

          <div className="login-link">
            Already have an account?{" "}
            <span onClick={() => navigate("/login")}>Login here</span>
          </div>
        </div>
      </animated.div>
    </div>
  );
};

export default SignupPage;

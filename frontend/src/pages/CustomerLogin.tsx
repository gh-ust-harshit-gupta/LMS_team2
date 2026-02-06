import React, { useState } from "react";
import "../styles/login.css";

const CustomerLogin: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = () => {
    if (!email && !password) {
      setError("Email and Password are required");
      return;
    }

    if (!email) {
      setError("Please enter your email");
      return;
    }

    if (!password) {
      setError("Please enter your password");
      return;
    }

    if (!email.includes("@")) {
      setError("Please enter a valid email address");
      return;
    }

    // Temporary 
    setError("Invalid email or password");
  };

  return (
    <div className="login-wrapper">
      <div className="login-card">
        <div className="login-header">
          <span className="back-arrow">←</span>
          <h2>Customer Login</h2>
        </div>

        <div className="form-group">
          <label>Email</label>
          <div className="input-box">
            <span className="icon"></span>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Password</label>
          <div className="input-box">
            <span className="icon"></span>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
        </div>

        <div className="forgot-password">Forgot password?</div>

        <button className="login-btn" onClick={handleLogin}>
          Login
        </button>

        {error && <div className="toast-error">{error}</div>}
      </div>
    </div>
  );
};

export default CustomerLogin;

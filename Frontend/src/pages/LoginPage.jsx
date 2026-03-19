import { useState } from "react";
import { Navigate } from "react-router-dom";

import { api } from "../api/client";

const EMPTY_REGISTER = {
  name: "",
  email: "",
  password: "",
  gender: "",
  mobile: "",
};

export default function LoginPage({ auth }) {
  const [mode, setMode] = useState("login");
  const [loginForm, setLoginForm] = useState({ email: "", password: "", remember_me: false });
  const [registerForm, setRegisterForm] = useState(EMPTY_REGISTER);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (auth.token) {
    return <Navigate to="/profile" replace />;
  }

  async function submitLogin(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const data = await api.login(loginForm);
      auth.onLogin(data.token, data.user);
      setMessage("Login successful");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitRegister(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const data = await api.register(registerForm);
      setMode("login");
      setMessage(data.message || "Registration successful. Please login.");
      setRegisterForm(EMPTY_REGISTER);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <div className="tabs">
        <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
          Login
        </button>
        <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>
          Register
        </button>
      </div>

      {mode === "login" ? (
        <form className="form" onSubmit={submitLogin}>
          <label>
            Email
            <input
              type="email"
              value={loginForm.email}
              onChange={(e) => setLoginForm((prev) => ({ ...prev, email: e.target.value }))}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={loginForm.password}
              onChange={(e) => setLoginForm((prev) => ({ ...prev, password: e.target.value }))}
              required
              minLength={8}
            />
          </label>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={loginForm.remember_me}
              onChange={(e) => setLoginForm((prev) => ({ ...prev, remember_me: e.target.checked }))}
            />
            Remember me
          </label>
          <button disabled={loading} type="submit">
            {loading ? "Please wait..." : "Login"}
          </button>
        </form>
      ) : (
        <form className="form" onSubmit={submitRegister}>
          <label>
            Name
            <input
              value={registerForm.name}
              onChange={(e) => setRegisterForm((prev) => ({ ...prev, name: e.target.value }))}
              required
            />
          </label>
          <label>
            Email
            <input
              type="email"
              value={registerForm.email}
              onChange={(e) => setRegisterForm((prev) => ({ ...prev, email: e.target.value }))}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={registerForm.password}
              onChange={(e) => setRegisterForm((prev) => ({ ...prev, password: e.target.value }))}
              required
              minLength={8}
            />
          </label>
          <label>
            Gender
            <input
              value={registerForm.gender}
              onChange={(e) => setRegisterForm((prev) => ({ ...prev, gender: e.target.value }))}
              required
            />
          </label>
          <label>
            Mobile
            <input
              value={registerForm.mobile}
              onChange={(e) => setRegisterForm((prev) => ({ ...prev, mobile: e.target.value }))}
              required
            />
          </label>
          <button disabled={loading} type="submit">
            {loading ? "Please wait..." : "Create account"}
          </button>
        </form>
      )}

      {message ? <p className="notice success">{message}</p> : null}
      {error ? <p className="notice error">{error}</p> : null}
    </section>
  );
}

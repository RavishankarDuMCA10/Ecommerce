import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { api } from "../api/client";

export default function ProfilePage({ auth }) {
  const [form, setForm] = useState({ name: "", gender: "", mobile: "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (auth.profile) {
      setForm({
        name: auth.profile.name || "",
        gender: auth.profile.gender || "",
        mobile: auth.profile.mobile || "",
      });
    }
  }, [auth.profile]);

  if (!auth.token && !auth.loadingProfile) {
    return <Navigate to="/login" replace />;
  }

  async function saveProfile(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      await api.updateProfile(auth.token, form);
      const profile = await api.getProfile(auth.token);
      auth.onProfileUpdated(profile);
      setMessage("Profile updated successfully");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>Your Profile</h2>
      {auth.loadingProfile ? <p>Loading profile...</p> : null}
      {auth.profile ? (
        <p className="muted">Logged in as {auth.profile.email}</p>
      ) : (
        <p className="muted">No active profile loaded.</p>
      )}

      <form className="form" onSubmit={saveProfile}>
        <label>
          Name
          <input value={form.name} onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))} required />
        </label>
        <label>
          Gender
          <input value={form.gender} onChange={(e) => setForm((prev) => ({ ...prev, gender: e.target.value }))} required />
        </label>
        <label>
          Mobile
          <input value={form.mobile} onChange={(e) => setForm((prev) => ({ ...prev, mobile: e.target.value }))} required />
        </label>
        <button disabled={loading} type="submit">
          {loading ? "Saving..." : "Save Settings"}
        </button>
      </form>

      <button className="secondary" onClick={auth.onLogout}>
        Logout
      </button>

      {message ? <p className="notice success">{message}</p> : null}
      {error ? <p className="notice error">{error}</p> : null}
    </section>
  );
}

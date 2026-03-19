import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";

import { api } from "./api/client";
import LoginPage from "./pages/LoginPage";
import ProfilePage from "./pages/ProfilePage";
import SearchPage from "./pages/SearchPage";
import ProductDetailPage from "./pages/ProductDetailPage";

const TOKEN_KEY = "ctt_auth_token";

export default function App() {
  const navigate = useNavigate();
  const [token, setToken] = useState(localStorage.getItem(TOKEN_KEY) || "");
  const [profile, setProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(Boolean(token));

  useEffect(() => {
    async function loadProfile() {
      if (!token) {
        setProfile(null);
        setLoadingProfile(false);
        return;
      }

      setLoadingProfile(true);
      try {
        const data = await api.getProfile(token);
        setProfile(data);
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        setToken("");
        setProfile(null);
      } finally {
        setLoadingProfile(false);
      }
    }

    loadProfile();
  }, [token]);

  const auth = useMemo(
    () => ({
      token,
      profile,
      loadingProfile,
      onLogin: (nextToken, userProfile) => {
        localStorage.setItem(TOKEN_KEY, nextToken);
        setToken(nextToken);
        setProfile(userProfile);
      },
      onLogout: async () => {
        if (token) {
          try {
            await api.logout(token);
          } catch {
            // Ignore network/logout race and clear local session anyway.
          }
        }
        localStorage.removeItem(TOKEN_KEY);
        setToken("");
        setProfile(null);
        navigate("/login");
      },
      onProfileUpdated: (nextProfile) => setProfile(nextProfile),
    }),
    [loadingProfile, navigate, profile, token]
  );

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>CTT Online Shopping</h1>
        <nav>
          <Link to="/search">Search</Link>
          {token ? <Link to="/profile">Profile</Link> : <Link to="/login">Login</Link>}
        </nav>
      </header>

      <main className="content">
        <Routes>
          <Route path="/" element={<Navigate to="/search" replace />} />
          <Route path="/login" element={<LoginPage auth={auth} />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/products/:productId" element={<ProductDetailPage />} />
          <Route path="/profile" element={<ProfilePage auth={auth} />} />
          <Route path="*" element={<Navigate to="/search" replace />} />
        </Routes>
      </main>
    </div>
  );
}

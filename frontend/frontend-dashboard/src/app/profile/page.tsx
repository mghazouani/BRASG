"use client";
import { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import Avatar from "@mui/material/Avatar";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Alert from "@mui/material/Alert";
import IconButton from "@mui/material/IconButton";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import InputAdornment from "@mui/material/InputAdornment";
import axios from "axios";
import ArrowBack from "@mui/icons-material/ArrowBack";
import Link from "next/link";
import MenuItem from "@mui/material/MenuItem";

interface JWTPayload {
  username: string;
  role?: string;
  email?: string;
  exp?: number;
}

export default function ProfilePage() {
  const [user, setUser] = useState<JWTPayload | null>(null);
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const [editEmail, setEditEmail] = useState(user?.email || "");
  const [emailSuccess, setEmailSuccess] = useState("");
  const [emailError, setEmailError] = useState("");
  const [perPage, setPerPage] = useState(() => {
    if (typeof window !== "undefined") {
      return Number(localStorage.getItem("perPage")) || 50;
    }
    return 50;
  });
  const [perPageSuccess, setPerPageSuccess] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const match = document.cookie.match(/(?:^|; )token=([^;]*)/);
      if (match) {
        try {
          const payload: JWTPayload = jwtDecode(match[1]);
          setUser(payload);
        } catch (e) {
          setUser(null);
        }
      }
    }
  }, []);

  if (!user) return <div className="text-center mt-20 text-xl">Utilisateur non connecté</div>;

  const initials = user.username
    .split(/\W+/)
    .map((n) => n[0]?.toUpperCase())
    .join("")
    .slice(0, 2);
  const color = user.role === "admin"
    ? "#6366f1"
    : user.role === "agent"
    ? "#06b6d4"
    : "#f59e42";

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccess("");
    setError("");
    if (newPassword !== confirmPassword) {
      setError("Les nouveaux mots de passe ne correspondent pas.");
      return;
    }
    try {
      // Appel API pour changer le mot de passe
      await axios.post("/api/change-password/", {
        old_password: oldPassword,
        new_password: newPassword,
      });
      setSuccess("Mot de passe changé avec succès.");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur lors du changement de mot de passe.");
    }
  };

  const handleEmailChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailSuccess("");
    setEmailError("");
    try {
      // Appel API pour changer l'email (à adapter côté backend)
      await axios.post("/api/change-email/", { email: editEmail });
      setEmailSuccess("Email mis à jour.");
      setUser((u) => u ? { ...u, email: editEmail } : u);
    } catch (err: any) {
      setEmailError(err.response?.data?.detail || "Erreur lors de la modification de l'email.");
    }
  };
  const handlePerPageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    setPerPage(value);
    localStorage.setItem("perPage", String(value));
    setPerPageSuccess("Préférence de pagination enregistrée.");
    setTimeout(() => setPerPageSuccess(""), 2000);
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 transition-colors duration-300" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
      <div className="flex flex-col items-center gap-6 w-full max-w-md fade-in card">
        <div className="w-full flex items-center justify-start mb-2">
          <Link href="/dashboard">
            <button className="flex items-center gap-2 text-blue-700 dark:text-blue-200 hover:underline font-medium transition-colors">
              <ArrowBack />
              Retour au dashboard
            </button>
          </Link>
        </div>
        <Avatar sx={{ bgcolor: color, color: '#fff', width: 80, height: 80, fontSize: 36, fontWeight: 700 }}>
          {initials}
        </Avatar>
        <div className="text-2xl font-bold text-blue-800 dark:text-blue-200">{user.username}</div>
        <div className="flex gap-2 items-center">
          <span className="bg-blue-100 text-blue-700 rounded px-2 py-0.5 text-xs font-medium">
            {user.role || "Utilisateur"}
          </span>
          {user.email && (
            <span className="text-gray-500 dark:text-gray-300 text-sm ml-2">{user.email}</span>
          )}
        </div>
        <div className="w-full mt-6">
          <h2 className="text-lg font-semibold mb-2">Changer le mot de passe</h2>
          {success && <Alert severity="success" className="mb-2">{success}</Alert>}
          {error && <Alert severity="error" className="mb-2">{error}</Alert>}
          <form onSubmit={handleChangePassword} className="flex flex-col gap-3">
            <TextField
              label="Ancien mot de passe"
              type={showOld ? "text" : "password"}
              value={oldPassword}
              onChange={e => setOldPassword(e.target.value)}
              required
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowOld(v => !v)} edge="end">
                      {showOld ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            <TextField
              label="Nouveau mot de passe"
              type={showNew ? "text" : "password"}
              value={newPassword}
              onChange={e => setNewPassword(e.target.value)}
              required
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowNew(v => !v)} edge="end">
                      {showNew ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            <TextField
              label="Confirmer le nouveau mot de passe"
              type={showConfirm ? "text" : "password"}
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              required
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowConfirm(v => !v)} edge="end">
                      {showConfirm ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            <Button type="submit" variant="contained" color="primary" className="btn-primary mt-2">
              Changer le mot de passe
            </Button>
          </form>
        </div>
        {/* Bloc modification email */}
        <div className="w-full mt-4">
          <h2 className="text-lg font-semibold mb-2">Changer l'email</h2>
          {emailSuccess && <Alert severity="success" className="mb-2">{emailSuccess}</Alert>}
          {emailError && <Alert severity="error" className="mb-2">{emailError}</Alert>}
          <form onSubmit={handleEmailChange} className="flex gap-2 items-end">
            <TextField
              label="Nouvel email"
              type="email"
              value={editEmail}
              onChange={e => setEditEmail(e.target.value)}
              required
              fullWidth
            />
            <Button type="submit" variant="contained" color="primary" className="btn-primary">
              Modifier
            </Button>
          </form>
        </div>
        {/* Bloc préférence pagination */}
        <div className="w-full mt-4">
          <h2 className="text-lg font-semibold mb-2">Préférences d'affichage</h2>
          {perPageSuccess && <Alert severity="success" className="mb-2">{perPageSuccess}</Alert>}
          <TextField
            select
            label="Nombre d'éléments par page"
            value={perPage}
            onChange={handlePerPageChange}
            fullWidth
          >
            {[10, 20, 30, 50, 100, 200].map((n) => (
              <MenuItem key={n} value={n}>{n} éléments</MenuItem>
            ))}
          </TextField>
        </div>
        <div className="mt-4 text-center text-gray-600 dark:text-gray-300">
          Ceci est votre page de profil. D’autres options pourront être ajoutées ici (préférences, etc).
        </div>
      </div>
    </main>
  );
}

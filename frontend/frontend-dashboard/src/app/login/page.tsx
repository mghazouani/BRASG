"use client";
import * as React from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import { api } from "@/utils/api";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.post("token/", { username, password });
      console.log("API response:", res.data); // DEBUG
      const { access } = res.data;
      if (!access) {
        setError("Token JWT non reçu. Vérifiez vos identifiants.");
        setLoading(false);
        return;
      }
      localStorage.setItem("token", access);
      document.cookie = `token=${access}; path=/;`;
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur d'authentification");
      console.error("Erreur API:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-100 to-blue-300">
      <form onSubmit={handleSubmit} className="bg-white rounded shadow p-8 w-full max-w-sm flex flex-col gap-4">
        <h1 className="text-2xl font-bold text-blue-800 mb-2 text-center">Connexion</h1>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField
          label="Nom d'utilisateur"
          type="text"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
          fullWidth
        />
        <TextField
          label="Mot de passe"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          fullWidth
        />
        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={loading}
          className="!bg-blue-600 !hover:bg-blue-700 !text-white"
        >
          {loading ? <CircularProgress size={22} color="inherit" /> : "Se connecter"}
        </Button>
      </form>
    </main>
  );
}

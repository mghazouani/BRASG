import axios from "axios";

// Utilise la variable d'environnement NEXT_PUBLIC_API_URL définie dans .env.local ou .env.production
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

// Ajoute dynamiquement le token JWT depuis le cookie (pour Next.js middleware compat)
api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token) config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour gérer les erreurs globales
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Redirection automatique si session expirée
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("token");
      document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      window.location.href = "/login";
      return Promise.reject(error);
    }
    // Affichage/log des erreurs globales (optionnel)
    if (error.response) {
      console.error("API error:", error.response.status, error.response.data);
    } else {
      console.error("API error:", error.message);
    }
    return Promise.reject(error);
  }
);

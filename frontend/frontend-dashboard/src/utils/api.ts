import axios from "axios";

// À personnaliser selon ton backend Django
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Ajoute dynamiquement le token JWT depuis le cookie (pour Next.js middleware compat)
api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      // Cherche le token dans les cookies
      const match = document.cookie.match(/(?:^|; )token=([^;]*)/);
      if (match) {
        config.headers["Authorization"] = `Bearer ${match[1]}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour gérer les erreurs globales
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Affichage/log des erreurs globales (optionnel)
    if (error.response) {
      console.error("API error:", error.response.status, error.response.data);
    } else {
      console.error("API error:", error.message);
    }
    return Promise.reject(error);
  }
);

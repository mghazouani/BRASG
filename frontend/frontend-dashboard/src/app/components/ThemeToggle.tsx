"use client";
import { useEffect, useState } from "react";
import IconButton from "@mui/material/IconButton";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";

export default function ThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const isDark = localStorage.getItem("theme") === "dark";
      setDark(isDark);
      document.documentElement.classList.toggle("dark", isDark);
    }
  }, []);

  function toggleTheme() {
    const next = !dark;
    setDark(next);
    localStorage.setItem("theme", next ? "dark" : "light");
    document.documentElement.classList.toggle("dark", next);
  }

  return (
    <IconButton onClick={toggleTheme} color="primary" size="large" aria-label="Changer de thème" className="ml-2">
      {dark ? <LightModeIcon className="text-yellow-400" /> : <DarkModeIcon className="text-blue-800" />}
    </IconButton>
  );
}

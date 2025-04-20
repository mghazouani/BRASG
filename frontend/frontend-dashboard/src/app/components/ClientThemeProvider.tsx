"use client";
import { useEffect } from "react";

export default function ClientThemeProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if (typeof window !== "undefined") {
      const isDark = localStorage.getItem("theme") === "dark";
      document.documentElement.classList.toggle("dark", isDark);
    }
  }, []);

  return <>{children}</>;
}

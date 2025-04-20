"use client";
import { useEffect, useState } from "react";
import Avatar from "@mui/material/Avatar";
import Tooltip from "@mui/material/Tooltip";
import { jwtDecode } from "jwt-decode";

interface JWTPayload {
  username: string;
  role?: string;
  email?: string;
  exp?: number;
}

export default function AvatarBadge() {
  const [user, setUser] = useState<JWTPayload | null>(null);

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

  if (!user) return null;

  // Génère des couleurs et initiales modernes
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

  return (
    <Tooltip title={user.email || user.username} arrow>
      <Avatar
        sx={{ bgcolor: color, color: "#fff", fontWeight: 700, border: "2px solid #fff", boxShadow: 2 }}
        className="ring-2 ring-offset-2 ring-blue-400 dark:ring-blue-600 shadow-lg transition-transform hover:scale-110 cursor-pointer"
      >
        {initials}
      </Avatar>
    </Tooltip>
  );
}

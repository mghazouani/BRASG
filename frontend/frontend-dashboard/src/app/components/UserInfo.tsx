"use client";
import { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";

interface UserInfoProps {}

interface JWTPayload {
  username: string;
  role?: string;
  email?: string;
  exp?: number;
}

export default function UserInfo(props: UserInfoProps) {
  const [user, setUser] = useState<JWTPayload | null>(null);

  useEffect(() => {
    // Cherche le token JWT dans les cookies
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

  return (
    <div className="flex items-center gap-2 text-blue-900">
      <span className="font-semibold">{user.username}</span>
      {user.role && (
        <span className="bg-blue-100 text-blue-700 rounded px-2 py-0.5 text-xs font-medium">
          {user.role}
        </span>
      )}
    </div>
  );
}

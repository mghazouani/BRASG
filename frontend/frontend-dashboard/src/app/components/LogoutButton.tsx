"use client";
import { useRouter } from "next/navigation";
import Button from "@mui/material/Button";
import LogoutIcon from "@mui/icons-material/Logout";

export default function LogoutButton() {
  const router = useRouter();

  function handleLogout() {
    // Supprime le token du localStorage
    localStorage.removeItem("token");
    // Supprime le cookie JWT (token)
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    // Redirige vers la page de login
    router.push("/login");
  }

  return (
    <Button
      onClick={handleLogout}
      startIcon={<LogoutIcon />}
      variant="outlined"
      color="secondary"
      className="ml-4"
    >
      Déconnexion
    </Button>
  );
}

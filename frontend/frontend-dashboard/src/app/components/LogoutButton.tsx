"use client";
import { useRouter } from "next/navigation";
import Button from "@mui/material/Button";
import LogoutIcon from "@mui/icons-material/Logout";
import React, { useState } from "react";
import Snackbar, { SnackbarCloseReason } from "@mui/material/Snackbar";

export default function LogoutButton() {
  const router = useRouter();
  const [open, setOpen] = useState(false);

  function handleLogout() {
    // Supprime le token du localStorage
    localStorage.removeItem("token");
    // Supprime le cookie JWT (token)
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    setOpen(true);
  }

  const handleClose = (event: React.SyntheticEvent | Event, reason: SnackbarCloseReason) => {
    if (reason === "clickaway") return;
    setOpen(false);
    router.push("/login");
  };

  return (
    <>
      <Button
        onClick={handleLogout}
        startIcon={<LogoutIcon />}
        variant="outlined"
        color="secondary"
        className="ml-4"
      >
        Déconnexion
      </Button>
      <Snackbar
        open={open}
        autoHideDuration={2000}
        onClose={handleClose}
        message="Déconnecté avec succès"
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      />
    </>
  );
}

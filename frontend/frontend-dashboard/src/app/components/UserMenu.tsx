"use client";
import { useState, useEffect } from "react";
import Avatar from "@mui/material/Avatar";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Divider from "@mui/material/Divider";
import ListItemIcon from "@mui/material/ListItemIcon";
import Logout from "@mui/icons-material/Logout";
import Person from "@mui/icons-material/Person";
import Settings from "@mui/icons-material/Settings";
import { jwtDecode } from "jwt-decode";
import Tooltip from "@mui/material/Tooltip";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface JWTPayload {
  username: string;
  role?: string;
  email?: string;
  exp?: number;
}

export default function UserMenu({ onToggleTheme }: { onToggleTheme?: () => void }) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [user, setUser] = useState<JWTPayload | null>(null);
  const router = useRouter();
  const open = Boolean(anchorEl);

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

  function handleMenu(event: React.MouseEvent<HTMLElement>) {
    setAnchorEl(event.currentTarget);
  }
  function handleClose() {
    setAnchorEl(null);
  }
  function handleLogout() {
    localStorage.removeItem("token");
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    router.push("/login");
  }

  return (
    <>
      <Tooltip title={user.email || user.username} arrow>
        <Avatar
          onClick={handleMenu}
          sx={{ bgcolor: color, color: "#fff", fontWeight: 700, border: "2px solid #fff", boxShadow: 2, cursor: "pointer" }}
          className="ring-2 ring-offset-2 ring-blue-400 dark:ring-blue-600 shadow-lg transition-transform hover:scale-110"
        >
          {initials}
        </Avatar>
      </Tooltip>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        onClick={handleClose}
        PaperProps={{
          elevation: 4,
          sx: {
            mt: 1.5,
            minWidth: 200,
            borderRadius: 2,
            bgcolor: 'background.paper',
            color: 'text.primary',
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem>
          <ListItemIcon>
            <Person fontSize="small" />
          </ListItemIcon>
          {user.username}
        </MenuItem>
        <MenuItem disabled>
          <span className="bg-blue-100 text-blue-700 rounded px-2 py-0.5 text-xs font-medium">
            {user.role || "Utilisateur"}
          </span>
        </MenuItem>
        <Divider />
        <MenuItem component={Link} href="/profile">
          <ListItemIcon>
            <Settings fontSize="small" />
          </ListItemIcon>
          Paramètres
        </MenuItem>
        {/* <MenuItem onClick={onToggleTheme}>
          <ListItemIcon>
            <DarkMode fontSize="small" />
          </ListItemIcon>
          Basculer le thème
        </MenuItem> */}
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          Déconnexion
        </MenuItem>
      </Menu>
    </>
  );
}

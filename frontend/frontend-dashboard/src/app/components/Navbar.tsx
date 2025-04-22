"use client";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import Link from 'next/link';
import { usePathname } from "next/navigation";
import UserInfo from './UserInfo';
import UserMenu from './UserMenu';
import InsightsIcon from "@mui/icons-material/Insights";
import AssessmentIcon from "@mui/icons-material/Assessment";
import { useEffect, useState } from "react";
import { api } from "@/utils/api";

export default function Navbar() {
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    api.get("/me/")
      .then(res => setUser(res.data))
      .catch(() => setUser(null));
  }, []);

  return (
    <AppBar 
      position="fixed" 
      sx={{ 
        mb: 4,
        background: 'linear-gradient(145deg, #f8f9fa 0%, #ffffff 100%)',
        borderBottom: '2px solid #e0e0e0',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
        zIndex: 1300,
        left: 0,
        right: 0,
        top: 0,
      }}
    >
      <Toolbar sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        py: 1,
        position: 'relative'
      }}>
        {/* Titre BRASG amélioré */}
        <Typography 
          variant="h4"
          sx={{
            background: 'linear-gradient(45deg, #1976d2 0%, #2196f3 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 800,
            letterSpacing: '-0.5px',
            fontFamily: 'var(--font-inter), sans-serif',
            transition: 'transform 0.3s ease',
            '&:hover': {
              transform: 'scale(1.02)'
            }
          }}
        >
          BRASG
        </Typography>

        {/* Boutons de navigation */}
        <Box sx={{ 
          display: 'flex', 
          gap: 2, 
          position: 'absolute', 
          left: '50%', 
          transform: 'translateX(-50%)'
        }}>
          <Button
            component={Link}
            href="/kpi"
            startIcon={<AssessmentIcon sx={{ fontSize: 28 }} />}
            sx={{
              borderRadius: '8px',
              px: 3,
              py: 1,
              fontSize: { xs: '1.1rem', md: '1.25rem' },
              fontWeight: 700,
              letterSpacing: '-0.5px',
              transition: 'all 0.3s ease',
              '&:hover': {
                background: '#e3f2fd',
                transform: 'translateY(-1px)',
                boxShadow: '0 2px 8px rgba(25, 118, 210, 0.15)'
              },
              ...(pathname === '/kpi' && {
                background: '#1976d2',
                color: 'white !important',
                '&:hover': {
                  background: '#1565c0'
                }
              })
            }}
          >
            Dashboard
          </Button>

          <Button
            component={Link}
            href="/dashboard"
            startIcon={<InsightsIcon sx={{ fontSize: 28 }} />}
            sx={{
                borderRadius: '8px',
                px: 3,
                py: 1,
                fontSize: { xs: '1.1rem', md: '1.25rem' },
                fontWeight: 700,
                letterSpacing: '-0.5px',
                transition: 'all 0.3s ease',
                '&:hover': {
                  background: '#e3f2fd',
                  transform: 'translateY(-1px)',
                  boxShadow: '0 2px 8px rgba(25, 118, 210, 0.15)'
                },
              ...(pathname === '/dashboard' && {
                background: '#1976d2',
                color: 'white !important',
                '&:hover': {
                  background: '#1565c0'
                }
              })
            }}
          >
            Suivi Déploiement
          </Button>
        </Box>

        {/* Section utilisateur */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 'auto', fontWeight: 600, color: '#1976d2', fontSize: { xs: '1rem', md: '1.1rem' } }}>
          {user ? `Bienvenue, ${user.first_name}` : ""}
          <UserMenu />
        </Box>
      </Toolbar>
    </AppBar>
  );
}
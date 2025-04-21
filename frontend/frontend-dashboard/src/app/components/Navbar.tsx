"use client";
import React from "react";
import Link from "next/link";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import BarChartIcon from "@mui/icons-material/BarChart";
import UserInfo from './UserInfo'; // Assuming UserInfo is a component in the same directory
import UserMenu from './UserMenu'; // Assuming UserMenu is a component in the same directory

export default function Navbar() {
  return (
    <AppBar position="static" color="default" elevation={1} sx={{ mb: 4 }}>
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', position: 'relative' }}>
        <Typography variant="h6">
          BRASG
        </Typography>
        <Box sx={{ flexGrow: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2, position: 'absolute', left: '50%', transform: 'translateX(-50%)' }}>
          <Button
            component={Link}
            href="/kpi"
            color="inherit"
            startIcon={<BarChartIcon />}
            sx={{ mr: 1 }}
          >
            KPI
          </Button>
          <Button
            component={Link}
            href="/dashboard"
            color="inherit"
            startIcon={<DashboardIcon />}
          >
            Dashboard
          </Button>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 'auto' }}>
          <UserInfo />
          <UserMenu />
        </Box>
      </Toolbar>
    </AppBar>
  );
}

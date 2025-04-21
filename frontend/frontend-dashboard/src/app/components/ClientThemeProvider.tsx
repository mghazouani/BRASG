"use client";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

export default function ClientThemeProvider({ children }: { children: React.ReactNode }) {
  // Mode light forcé
  const theme = createTheme({
    palette: { mode: "light" },
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}

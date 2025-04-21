"use client";
import { CacheProvider } from "@emotion/react";
import createEmotionCache from "../emotionCache";
import ClientThemeProvider from "./ClientThemeProvider";
import Navbar from "./Navbar";
import { useState } from "react";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [emotionCache] = useState(() => createEmotionCache());

  return (
    <CacheProvider value={emotionCache}>
      <ClientThemeProvider>
        <Navbar />
        {children}
      </ClientThemeProvider>
    </CacheProvider>
  );
}

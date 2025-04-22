"use client";
import { CacheProvider } from "@emotion/react";
import createEmotionCache from "../emotionCache";
import ClientThemeProvider from "./ClientThemeProvider";
import Navbar from "./Navbar";
import { useState } from "react";
import { usePathname } from "next/navigation";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [emotionCache] = useState(() => createEmotionCache());
  const pathname = usePathname();

  return (
    <CacheProvider value={emotionCache}>
      <ClientThemeProvider>
        {pathname !== "/login" && <Navbar />}
        <div style={{ paddingTop: pathname !== "/login" ? 72 : 0 }}>
          {children}
        </div>
      </ClientThemeProvider>
    </CacheProvider>
  );
}

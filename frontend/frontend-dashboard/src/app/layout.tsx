import AppShell from "./components/AppShell";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ 
  subsets: ["latin"],
  variable: '--font-inter' 
});

export const metadata = {
  title: "Dashboard Client",
  description: "Gestion des clients installés",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <head>
        <meta charSet="utf-8" />
        <meta name="emotion-insertion-point" content="" />
      </head>
      <body className={`${inter.variable} font-sans`}>
      <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}

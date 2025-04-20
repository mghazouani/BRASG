import "./globals.css";
import { Inter } from "next/font/google";
import ClientThemeProvider from "./components/ClientThemeProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Dashboard Client",
  description: "Gestion des clients installés",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <ClientThemeProvider>{children}</ClientThemeProvider>
      </body>
    </html>
  );
}

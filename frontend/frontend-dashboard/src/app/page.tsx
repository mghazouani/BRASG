import * as React from "react";
import Button from "@mui/material/Button";
import Avatar from "@mui/material/Avatar";
import Stack from "@mui/material/Stack";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-100 to-blue-300 flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-blue-800 mb-4 text-center">
        Dashboard Client Next.js
      </h1>
      <p className="mb-6 text-gray-700 text-center">
        Stack : <span className="font-semibold">Next.js + TailwindCSS + Material UI</span>
      </p>
      <Stack direction="row" spacing={2} className="mb-6">
        <Avatar alt="Agent" src="/avatar.png" />
        <Avatar sx={{ bgcolor: '#1976d2' }}>A</Avatar>
      </Stack>
      <Button variant="contained" color="primary" className="!bg-blue-600 !hover:bg-blue-700 !text-white">
        Bouton MUI stylé Tailwind
      </Button>
      <div className="mt-10 p-6 bg-white rounded shadow w-full max-w-md">
        <div className="flex items-center space-x-4">
          <span className="inline-block w-3 h-3 bg-green-500 rounded-full"></span>
          <span className="text-sm text-gray-500">Exemple d'intégration Tailwind + MUI dans Next.js 14</span>
        </div>
      </div>
    </main>
  );
}

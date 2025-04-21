"use client";
import React from "react";
import KpiAdoptionCard from "../dashboard/KpiAdoptionCard";
import { Container, Typography } from "@mui/material";

export default function KpiPage() {
  return (
    <main className="min-h-screen flex flex-col items-center p-8 transition-colors duration-300" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
      <div className="flex justify-between items-center w-full mb-6 fade-in">
        <div className="flex items-center gap-4">
          <Typography variant="h4" gutterBottom>Indicateurs de performance</Typography>
        </div>
        <div className="flex items-center gap-2">
        </div>
      </div>
      <Container maxWidth="md" sx={{ py: 6 }}>
        <KpiAdoptionCard />
        {/* Ajoute ici d'autres composants KPI si besoin */}
      </Container>
    </main>
  );
}

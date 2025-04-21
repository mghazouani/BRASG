"use client";
import React from "react";
import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Box, Typography } from "@mui/material";

ChartJS.register(ArcElement, Tooltip, Legend);

export interface KpiDonutChartProps {
  pct_installed: number;
  pct_up_to_date: number;
}

export default function KpiDonutChart({ pct_installed, pct_up_to_date }: KpiDonutChartProps) {
  // Les deux anneaux : ext = installés, int = à jour
  const data = {
    labels: ["Installée", "Non installée"],
    datasets: [
      {
        label: "% App installée",
        data: [pct_installed, 100 - pct_installed],
        backgroundColor: ["#1976d2", "#e0e0e0"],
        borderWidth: 0,
        cutout: "75%", // anneau extérieur
        circumference: 360,
        rotation: 0,
        radius: "100%",
      },
      {
        label: "% App à jour",
        data: [pct_up_to_date, 100 - pct_up_to_date],
        backgroundColor: ["#43a047", "#e0e0e0"],
        borderWidth: 0,
        cutout: "88%", // anneau intérieur (plus petit)
        circumference: 360,
        rotation: 0,
        radius: "60%",
      },
    ],
  };

  const options = {
    responsive: true,
    cutout: "70%",
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ${context.parsed} %`;
          }
        }
      }
    },
  };

  return (
    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" my={2}>
      <Box sx={{ position: "relative", width: 260, height: 260, mb: 1 }}>
        <Doughnut data={data} options={options} />
        {/* Texte central animé et valeurs */}
        <Box sx={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          pointerEvents: "none"
        }}>
          <Typography variant="h4" fontWeight={700} color="#1976d2" sx={{ lineHeight: 1 }}>{pct_installed}%</Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mt: -0.5 }}>installée</Typography>
          <Typography variant="h6" fontWeight={700} color="#43a047" sx={{ lineHeight: 1 }}>{pct_up_to_date}%</Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mt: -0.5 }}>à jour</Typography>
        </Box>
      </Box>
      <Box display="flex" gap={2} mt={1}>
        <Box display="flex" alignItems="center" gap={1}><span style={{ width: 16, height: 16, background: 'linear-gradient(90deg,#1976d2,#64b5f6)', borderRadius: 8, display: 'inline-block', boxShadow: '0 0 6px #1976d2' }} /> <Typography variant="caption">Installée</Typography></Box>
        <Box display="flex" alignItems="center" gap={1}><span style={{ width: 16, height: 16, background: 'linear-gradient(90deg,#43a047,#a5d6a7)', borderRadius: 8, display: 'inline-block', boxShadow: '0 0 6px #43a047' }} /> <Typography variant="caption">À jour</Typography></Box>
      </Box>
    </Box>
  );
}

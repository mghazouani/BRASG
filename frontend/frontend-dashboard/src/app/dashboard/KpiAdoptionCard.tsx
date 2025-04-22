import React, { useEffect, useState } from "react";
import { Card, CardContent, Typography, CircularProgress, Box } from "@mui/material";
import { api } from "@/utils/api";
import KpiDonutChart from "../kpi/KpiDonutChart";

export default function KpiAdoptionCard() {
  const [kpi, setKpi] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/kpi/adoption/")
      .then(res => setKpi(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;
  if (!kpi) return <div>Erreur chargement KPI</div>;

  return (
    <Card
      sx={{
        flex: 1,
        mb: 2,
        borderRadius: 3,
        boxShadow: '0 2px 14px 0 rgb(32 40 45 / 8%)',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        p: 2,
        border: '1px solid #e3e8ee',
      }}
    >
      <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#1976d2', mb: 2 }}>
          Adoption de l’application
        </Typography>
        <KpiDonutChart pct_installed={kpi.pct_installed} pct_up_to_date={kpi.pct_up_to_date} />
        <Box display="flex" flexDirection="column" alignItems="left" gap={0.5} mt={2}>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>Clients avec app installée : <b style={{ color: '#1976d2' }}>{kpi.pct_installed}%</b></Typography>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>Clients à jour : <b style={{ color: '#43a047' }}>{kpi.pct_up_to_date}%</b></Typography>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>Délai moyen d’installation : <b>{kpi.avg_days_to_install !== null ? `${kpi.avg_days_to_install} jours` : "—"}</b></Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

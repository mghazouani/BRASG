import React, { useEffect, useState } from "react";
import { Card, CardContent, Typography, CircularProgress, Box } from "@mui/material";
import { api } from "@/utils/api";

export default function KpiEngagementCard() {
  const [kpi, setKpi] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/kpi/engagement/")
      .then(res => setKpi(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;
  if (!kpi) return <div>Erreur chargement KPI Engagement</div>;

  return (
    <Card
      sx={{
        mb: 2,
        borderRadius: 3,
        boxShadow: '0 2px 14px 0 rgb(32 40 45 / 8%)',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        p: 2,
        border: '1px solid #e3e8ee',
        minWidth: 350,
        maxWidth: 460,
        mx: 'auto',
      }}
    >
      <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#1976d2', mb: 2 }}>
          Indicateurs d’engagement
        </Typography>
        <Box display="flex" flexDirection="column" alignItems="center" gap={0.5} mt={1}>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>Taux de relance planifiée : <b style={{ color: '#f9a825' }}>{kpi.pct_relance_planifiee}%</b></Typography>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>Taux de demande d’aide : <b style={{ color: '#d32f2f' }}>{kpi.pct_demande_aide}%</b></Typography>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>Taux de clients notifiés : <b style={{ color: '#0288d1' }}>{kpi.pct_clients_notifies}%</b></Typography>
          <Typography color="text.secondary" variant="caption" sx={{ mt: 0.5 }}>Total clients : {kpi.total}</Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

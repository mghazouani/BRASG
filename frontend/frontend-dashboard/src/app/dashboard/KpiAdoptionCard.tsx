import React, { useEffect, useState } from "react";
import { Card, CardContent, Typography, CircularProgress } from "@mui/material";
import { api } from "@/utils/api";

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
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6">Adoption de l’application</Typography>
        <Typography>Clients avec app installée : <b>{kpi.pct_installed}%</b></Typography>
        <Typography>Clients à jour : <b>{kpi.pct_up_to_date}%</b></Typography>
        <Typography>Délai moyen d’installation : <b>{kpi.avg_days_to_install !== null ? `${kpi.avg_days_to_install} jours` : "—"}</b></Typography>
        <Typography color="text.secondary" variant="caption">Total clients : {kpi.total}</Typography>
      </CardContent>
    </Card>
  );
}

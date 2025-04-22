import React, { useEffect, useState } from "react";
import { Card, CardContent, Typography, CircularProgress, Box } from "@mui/material";
import { api } from "@/utils/api";
import PeopleIcon from '@mui/icons-material/People';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import DownloadDoneIcon from '@mui/icons-material/DownloadDone';

export default function KpiClientsCard() {
  const [kpi, setKpi] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/kpi/clients/")
      .then(res => setKpi(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;
  if (!kpi) return <div>Erreur chargement KPI Clients</div>;

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
          Statistiques clients
        </Typography>
        <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mt={1} width="100%">
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 2, borderRadius: 2, background: '#e1f5fe' }}>
            <PeopleIcon sx={{ color: '#1565c0', fontSize: 32, mb: 1 }} />
            <Typography variant="subtitle2" color="textSecondary" align="center">Clients</Typography>
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#1565c0' }} align="center">{kpi.total}</Typography>
          </Box>
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 2, borderRadius: 2, background: '#e1f5fe' }}>
            <NotificationsActiveIcon sx={{ color: '#0288d1', fontSize: 32, mb: 1 }} />
            <Typography variant="subtitle2" color="textSecondary" align="center">Clients notifiés</Typography>
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#0288d1' }} align="center">{kpi.total_notified}</Typography>
          </Box>
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 2, borderRadius: 2, background: '#e1f5fe' }}>
            <DownloadDoneIcon sx={{ color: '#2e7d32', fontSize: 32, mb: 1 }} />
            <Typography variant="subtitle2" color="textSecondary" align="center">Clients installés</Typography>
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#2e7d32' }} align="center">{kpi.total_installed}</Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

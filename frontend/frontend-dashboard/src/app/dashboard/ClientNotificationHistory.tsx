import React, { useEffect, useState } from "react";
import { api } from "@/utils/api";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import PhoneInTalkIcon from "@mui/icons-material/PhoneInTalk";
import WhatsAppIcon from "@mui/icons-material/WhatsApp";
import EmailIcon from "@mui/icons-material/Email";

interface NotificationClient {
  id: string;
  client: string;
  utilisateur: string;
  date_notification: string;
  statut: "succes" | "echec";
  canal: string | null;
}

export default function ClientNotificationHistory({ clientId, onNotify }: { clientId: string; onNotify?: (message?: string) => void }) {
  const [history, setHistory] = useState<NotificationClient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notifLoading, setNotifLoading] = useState<null | "succes" | "echec" | false>(false);

  // Charger l'historique
  useEffect(() => {
    if (!clientId) return;
    setLoading(true);
    api.get(`/notifications/?client=${clientId}`)
      .then(res => {
        // Correction : s'assurer que res.data est bien un tableau
        setHistory(Array.isArray(res.data) ? res.data : []);
      })
      .catch(() => setError("Erreur chargement historique des notifications."))
      .finally(() => setLoading(false));
  }, [clientId, notifLoading]);

  // Création notification
  const handleNotify = async (statut: "succes" | "echec") => {
    setNotifLoading(statut);
    try {
      await api.post("/notifications/", {
        client: clientId,
        statut,
        canal: "Téléphone" // ou autre valeur selon UI future
      });
      if (onNotify) onNotify(); // Ajout : callback pour fermer la modale
    } catch {
      setError("Erreur lors de la notification.");
      if (onNotify) onNotify("Erreur d'enregistrement");
    } finally {
      setNotifLoading(false);
    }
  };

  return (
    <div>
      <Stack direction="row" spacing={2} mb={2} >
        <Button
          variant="contained"
          color="success"
          startIcon={<PhoneInTalkIcon />}
          onClick={() => handleNotify("succes")}
          disabled={notifLoading === "succes"}
          sx={{ flex: 1 }}
        >
          Notifier (Succès)
        </Button>
        <Button
          variant="outlined"
          color="error"
          startIcon={<PhoneInTalkIcon />}
          onClick={() => handleNotify("echec")}
          disabled={notifLoading === "echec"}
          sx={{ flex: 1 }}
        >
          Notifier (Injoignable)
        </Button>
      </Stack>
      {loading ? (
        <CircularProgress size={28} />
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <>
          <h4 className="font-semibold mb-2">Historique des notifications</h4>
          {history.length === 0 ? (
            <div className="text-gray-500">Aucune notification enregistrée.</div>
          ) : (
            <ul className="space-y-2">
              {history.map(n => (
                <li key={n.id} className="flex items-center gap-3 p-2 border rounded bg-gray-50">
                  <Chip
                    label={n.statut === "succes" ? "Succès" : "Échec"}
                    color={n.statut === "succes" ? "success" : "error"}
                    size="small"
                  />
                  <span className="text-sm text-gray-800">{n.canal}</span>
                  <span className="text-xs text-gray-500">{new Date(n.date_notification).toLocaleString()}</span>
                  <span className="text-xs text-blue-700 font-semibold">{n.utilisateur}</span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}

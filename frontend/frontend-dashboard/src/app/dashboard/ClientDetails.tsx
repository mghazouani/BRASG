import React from "react";
import { Dialog, DialogTitle, DialogContent, IconButton, Chip, Box } from "@mui/material";

interface ClientDetailsProps {
  selectedClient: any;
  auditLogs: any[];
  open: boolean;
  onClose: () => void;
  statutColor: (statut: string) => any;
}

const ClientDetails: React.FC<ClientDetailsProps> = ({ selectedClient, auditLogs, open, onClose, statutColor }) => {
  if (!selectedClient) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      scroll="paper"
      aria-labelledby="client-details-title"
    >
      <DialogTitle id="client-details-title" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pr: 5 }}>
        <span>Détails Suivi Client</span>
        <IconButton aria-label="Fermer" onClick={onClose} size="large">
          ×
        </IconButton>
      </DialogTitle>
      <DialogContent dividers sx={{ display: 'flex', gap: 3, minHeight: 300, maxHeight: '100vh', overflow: 'auto', fontSize: '0.93rem' }}>
        {/* Partie gauche : détails client */}
        <div style={{ width: '50%', display: 'flex', flexDirection: 'column', gap: 16, overflowY: 'auto', padding: '16px', height: '100%', fontSize: '0.95em' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {/* NOM en premier */}
            <Box p={2} bgcolor="#fff" borderRadius={2} boxShadow={1} mb={1}>
              <b>Nom du client:</b> <span>{selectedClient.nom_client}</span>
            </Box>
            {/* ID SAP + STATUT sur la même ligne */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
              <Box flex={1} p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
                <b>ID SAP:</b> <span>{selectedClient.sap_id}</span>
              </Box>
              <Box flex={1} p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
                <b>Statut:</b> <Chip label={selectedClient.statut_general} size="small" color={statutColor(selectedClient.statut_general)} />
              </Box>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <Box flex={1} p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
                <b>Téléphone:</b> <span>{selectedClient.telephone}</span>
              </Box>
              {selectedClient.telephone2 && (
                <Box flex={1} p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
                  <b>Téléphone 2:</b> <span>{selectedClient.telephone2}</span>
                </Box>
              )}
              {selectedClient.telephone3 && (
                <Box flex={1} p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
                  <b>Téléphone 3:</b> <span>{selectedClient.telephone3}</span>
                </Box>
              )}
            </div>
            <Box p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
              <b>Canal préféré:</b> {selectedClient.canal_contact || <span className="text-gray-400">—</span>}
            </Box>
            <Box p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
              <b>Langue:</b> {selectedClient.langue || <span className="text-gray-400">—</span>}
            </Box>
            <Box p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
              <b>Notification client:</b> {selectedClient.notification_client ? "Oui" : "Non"}
            </Box>
            <Box p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
              <b>Dernière notification:</b> {selectedClient.date_notification ? (
                <span>{new Date(selectedClient.date_notification).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false })}</span>
              ) : <span className="text-gray-400">—</span>}
            </Box>
            <Box p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
              <b>A demandé aide:</b> {selectedClient.a_demande_aide ? "Oui" : "Non"}
            </Box>
            <Box p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
              <b>Nature de l'aide:</b>
              <div style={{ textAlign: 'justify', whiteSpace: 'pre-line', marginTop: 4 }}>
                {selectedClient.nature_aide || <span className="text-gray-400">—</span>}
              </div>
            </Box>
            <div style={{ display: 'flex', gap: 8 }}>
              <Box flex={1} p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
                <b>App installée:</b> {selectedClient.app_installee === false ? "Non" : selectedClient.app_installee === true ? "Oui" : <span className="text-gray-400">—</span>}
              </Box>
              <Box flex={1} p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
                <b>MàJ app:</b> {selectedClient.maj_app || <span className="text-gray-400">—</span>}
              </Box>
            </div>
            <Box p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
              <b>CMD/Jour:</b> {selectedClient.segment_client || <span className="text-gray-400">—</span>}
            </Box>
            <Box p={2} bgcolor="#fff" borderRadius={2} boxShadow={1}>
              <b>Commentaire agent:</b>
              <div style={{ textAlign: 'justify', whiteSpace: 'pre-line', marginTop: 4 }}>
                {selectedClient.commentaire_agent || <span className="text-gray-400">—</span>}
              </div>
            </Box>
          </div>
        </div>
        {/* Partie droite : historique des changements */}
        <div style={{ width: '50%', display: 'flex', flexDirection: 'column', gap: 8, overflowY: 'auto',  height: '100%' }}>
          <h3 className="text-xl font-semibold mb-2 mt-6">Historique des changements</h3>
          {auditLogs.length === 0 ? (
            <div className="text-gray-500">Aucun historique disponible.</div>
          ) : (
            <ul className="list-disc list-inside max-h-100% overflow-auto" style={{ flex: 1 }}>
              {auditLogs.map(log => (
                <li key={log.id} className="mb-2">
                  <div>
                    <span className="font-medium">{new Date(log.timestamp).toLocaleString()}</span> - {log.user} - {log.action}
                  </div>
                  <div className="text-sm text-gray-700 space-y-1">
                    {Object.entries(log.champs_changes).map(([field, val]) => (
                      React.isValidElement(val) ? val : (
                        Array.isArray(val) ? (
                          val.map((act, idx) => (
                            <div key={idx} className="ml-2">
                              • <b>{act.action}</b>: {act.reason} <span className="text-xs text-gray-500">({act.priorite})</span>
                            </div>
                          ))
                        ) : (
                          <div key={field} className="ml-2">
                            • <b>{field}</b>: <span className="text-indigo-600">{String((val as any).old)}</span> → <span className="text-indigo-600">{String((val as any).new)}</span>
                          </div>
                        )
                      )
                    ))}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ClientDetails;

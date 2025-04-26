import React from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import ClientNotificationHistory from "./ClientNotificationHistory";

interface ClientNotificationModalProps {
  open: boolean;
  onClose: () => void;
  clientId: string;
  clientName?: string;
  onSuccess?: (msg?: string) => void;
}

export default function ClientNotificationModal({ open, onClose, clientId, clientName, onSuccess }: ClientNotificationModalProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        Notifications – {clientName || clientId}
        <IconButton onClick={onClose} size="small" sx={{ ml: 2 }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <link href="https://fonts.googleapis.com/css?family=Roboto:400,500,700&display=swap" rel="stylesheet" />
        <style>{`
          .client-notif-modal-roboto * {
            font-family: 'Roboto', Arial, sans-serif !important;
          }
        `}</style>
        <div className="client-notif-modal-roboto">
          <ClientNotificationHistory clientId={clientId} onNotify={() => onSuccess && onSuccess()} />
        </div>
      </DialogContent>
    </Dialog>
  );
}

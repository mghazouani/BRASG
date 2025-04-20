"use client";

import * as React from "react";
import { useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Alert from "@mui/material/Alert";

export interface ClientEditFormProps {
  open: boolean;
  client: any;
  onClose: () => void;
  onSave: (data: any) => void;
  loading: boolean;
  error?: string | null;
}

const statutChoices = [
  { value: "actif", label: "Actif" },
  { value: "inactif", label: "Inactif" },
  { value: "bloque", label: "Bloqué" },
];

const langueChoices = [
  { value: "arabe", label: "Arabe" },
  { value: "francais", label: "Français" },
];

export default function ClientEditForm({ open, client, onClose, onSave, loading, error }: ClientEditFormProps) {
  const [form, setForm] = useState(client);

  React.useEffect(() => {
    setForm(client);
  }, [client]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value, type, checked } = e.target;
    setForm((prev: any) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSave(form);
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Modifier le client</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent className="space-y-4">
          {error && <Alert severity="error">{error}</Alert>}
          <TextField
            label="Nom"
            name="nom_client"
            value={form.nom_client || ''}
            onChange={handleChange}
            fullWidth
            required
          />
          <TextField
            label="Téléphone"
            name="telephone"
            value={form.telephone || ''}
            onChange={handleChange}
            fullWidth
          />
          <TextField
            label="Statut"
            name="statut_general"
            value={form.statut_general || ''}
            onChange={handleChange}
            select
            fullWidth
            required
          >
            {statutChoices.map(opt => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </TextField>
          <TextField
            label="Langue"
            name="langue"
            value={form.langue || ''}
            onChange={handleChange}
            select
            fullWidth
            required
          >
            {langueChoices.map(opt => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </TextField>
          <TextField
            label="Région"
            name="region"
            value={form.region || ''}
            onChange={handleChange}
            fullWidth
          />
          <TextField
            label="Ville"
            name="ville"
            value={form.ville || ''}
            onChange={handleChange}
            fullWidth
          />
          <TextField
            label="Commentaire agent"
            name="commentaire_agent"
            value={form.commentaire_agent || ''}
            onChange={handleChange}
            fullWidth
            multiline
            minRows={2}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>Annuler</Button>
          <Button type="submit" variant="contained" color="primary" disabled={loading}>
            Enregistrer
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

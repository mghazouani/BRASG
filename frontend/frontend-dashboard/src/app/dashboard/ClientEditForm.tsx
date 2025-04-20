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
import FormControl from "@mui/material/FormControl";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";

export interface ClientEditFormProps {
  open: boolean;
  client: any;
  onClose: () => void;
  onSave: (data: any) => void;
  loading: boolean;
  error?: string | null;
  settings: {
    statut_general: { value: string; label: string }[];
    langue: { value: string; label: string }[];
    notification_client: { value: boolean; label: string }[];
    a_demande_aide: { value: boolean; label: string }[];
    app_installee: { value: boolean; label: string }[];
  };
}

export default function ClientEditForm({ open, client, onClose, onSave, loading, error, settings }: ClientEditFormProps) {
  const [form, setForm] = useState(client);

  React.useEffect(() => {
    setForm(client);
  }, [client]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value, type, checked } = e.target;
    const val = type === "checkbox" ? checked : type === "radio" ? (value === 'true') : value;
    setForm((prev: any) => ({
      ...prev,
      [name]: val,
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
            {settings.statut_general.map(opt => (
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
            {settings.langue.map(opt => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </TextField>
          <FormControl component="fieldset" className="space-y-1">
            <RadioGroup row name="notification_client" value={`${form.notification_client}`} onChange={handleChange}>
              {settings.notification_client.map(opt => (
                <FormControlLabel
                  key={opt.value.toString()}
                  value={`${opt.value}`}
                  control={<Radio />}
                  label={opt.label}
                />
              ))}
            </RadioGroup>
          </FormControl>
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
          <FormControl component="fieldset" className="space-y-1">
            <RadioGroup row name="a_demande_aide" value={`${form.a_demande_aide}`} onChange={handleChange}>
              {settings.a_demande_aide.map(opt => (
                <FormControlLabel
                  key={opt.value.toString()}
                  value={`${opt.value}`}
                  control={<Radio />}
                  label={opt.label}
                />
              ))}
            </RadioGroup>
          </FormControl>
          <FormControl component="fieldset" className="space-y-1">
            <RadioGroup row name="app_installee" value={`${form.app_installee}`} onChange={handleChange}>
              {settings.app_installee.map(opt => (
                <FormControlLabel
                  key={opt.value.toString()}
                  value={`${opt.value}`}
                  control={<Radio />}
                  label={opt.label}
                />
              ))}
            </RadioGroup>
          </FormControl>
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

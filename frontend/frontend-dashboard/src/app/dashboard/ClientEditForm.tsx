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
import FormLabel from "@mui/material/FormLabel";
import Autocomplete from "@mui/material/Autocomplete";
import { api } from "@/utils/api";

// Type pour les villes
type VilleType = { id: string; nom: string; region: string };

// Typage du client (mêmes champs que dans DashboardPage)
interface Client {
  id: string;
  sap_id: string;
  nom_client: string;
  telephone: string;
  langue: string;
  statut_general: string;
  notification_client: boolean;
  date_notification: string | null;
  a_demande_aide: boolean;
  nature_aide: string | null;
  app_installee: boolean | null;
  maj_app: string | null;
  commentaire_agent: string | null;
  segment_client: string | null;
  region: string | null;
  ville: string | null;
  canal_contact: string | null;
  relance_planifiee: boolean;
}

export interface ClientEditFormProps {
  open: boolean;
  client: Client;
  onClose: () => void;
  onSave: (data: Client) => void | Promise<void>;
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
  const [form, setForm] = useState<Client>(client);
  const [villes, setVilles] = useState<VilleType[]>([]);

  React.useEffect(() => {
    setForm(client);
  }, [client]);

  // Chargement des villes pour dropdown
  React.useEffect(() => {
    api.get("villes/").then(res => {
      // DRF pagine par défaut: extraire "results" ou utiliser directement le tableau
      const data = Array.isArray(res.data) ? res.data : res.data.results;
      setVilles(data as VilleType[]);
    });
  }, []);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value, type, checked } = e.target;
    const val = type === "checkbox" ? checked : type === "radio" ? (value === 'true') : value;
    setForm(prev => ({ ...prev, [name as keyof Client]: val as Client[keyof Client] }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSave(form);
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Modifier le client</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent className="flex flex-col gap-6 max-h-[60vh] overflow-y-auto">
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
            fullWidth
            disabled
          />
          <Autocomplete
            freeSolo
            openOnFocus
            autoHighlight
            ListboxProps={{ style: { maxHeight: '20rem' } }}
            options={villes.map(v => v.nom)}
            value={form.ville || ''}
            onChange={(_, value) => {
              const sel = villes.find(v => v.nom === value);
              setForm(prev => ({ ...prev, ville: value || '', region: sel?.region || '' }));
            }}
            onInputChange={(_, value) => {
              setForm(prev => ({ ...prev, ville: value }));
            }}
            onBlur={() => {
              const sel = villes.find(v => v.nom === form.ville);
              if (sel) {
                setForm(prev => ({ ...prev, region: sel.region }));
              } else {
                setForm(prev => ({ ...prev, region: '' }));
              }
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Ville"
                fullWidth
                error={!!form.ville && !villes.some(v => v.nom === form.ville)}
                helperText={form.ville && !villes.some(v => v.nom === form.ville) ? "Ville inconnue" : ""}
              />
            )}
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
            <FormLabel component="legend">Aide demandée</FormLabel>
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
            <FormLabel component="legend">App installée</FormLabel>
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

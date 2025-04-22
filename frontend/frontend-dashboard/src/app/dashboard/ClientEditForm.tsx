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
  telephone2?: string | null;
  telephone3?: string | null;
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
    canal_contact: { value: string; label: string }[];
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
      const data = Array.isArray(res.data) ? res.data : res.data.results;
      setVilles(data as VilleType[]);
    });
  }, []);

  // Ordre des champs pour la modale d'édition
  const fieldsOrder: { key: keyof Client; label: string; type?: string; options?: any[] }[] = [
    { key: 'nom_client', label: 'Nom' },
    { key: 'telephone', label: 'Téléphone' },
    { key: 'telephone2', label: 'Téléphone 2' },
    { key: 'telephone3', label: 'Téléphone 3' },
    { key: 'langue', label: 'Langue', type: 'select', options: settings.langue },
    { key: 'statut_general', label: 'Statut', type: 'select', options: settings.statut_general },
    { key: 'canal_contact', label: 'Canal contact', type: 'select', options: settings.canal_contact },
    { key: 'notification_client', label: 'Notification client', type: 'radio', options: settings.notification_client },
    { key: 'date_notification', label: 'Date notification', type: 'date' },
    { key: 'app_installee', label: 'App installée', type: 'radio', options: settings.app_installee },
    { key: 'maj_app', label: 'MàJ App' },
    { key: 'a_demande_aide', label: 'Aide demandée', type: 'radio', options: settings.a_demande_aide },
    { key: 'nature_aide', label: 'Nature aide' },
    { key: 'commentaire_agent', label: 'Commentaire agent' },
    { key: 'ville', label: 'Ville', type: 'autocomplete' },
    { key: 'region', label: 'Région' },
    { key: 'segment_client', label: 'CMD/Jour' },
    { key: 'relance_planifiee', label: 'Relance planifiée', type: 'radio', options: [
      { value: true, label: 'Oui' },
      { value: false, label: 'Non' }
    ] },
  ];

  // Rendu dynamique d'un champ
  const renderField = (fc: typeof fieldsOrder[0]) => {
    const { key, label, type, options } = fc;
    const value = form[key] ?? '';
    switch (type) {
      case 'select':
        return (
          <TextField key={key} label={label} name={key} select value={value} onChange={handleChange} fullWidth>
            {options!.map(opt => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </TextField>
        );
      case 'radio':
        return (
          <FormControl key={key} component="fieldset">
            <FormLabel component="legend">{label}</FormLabel>
            <RadioGroup row name={key} value={`${value}`} onChange={handleChange}>
              {options!.map(opt => (
                <FormControlLabel key={opt.value.toString()} value={`${opt.value}`} control={<Radio />} label={opt.label} />
              ))}
            </RadioGroup>
          </FormControl>
        );
      case 'date':
        return <TextField key={key} label={label} name={key} type="date" value={value as string} onChange={handleChange} fullWidth />;
      case 'autocomplete':
        return (
          <Autocomplete
            key={key}
            freeSolo
            openOnFocus
            options={villes.map(v => v.nom)}
            value={form.ville || ''}
            onChange={(_, val) => {
              const sel = villes.find(v => v.nom === val);
              setForm(prev => ({ ...prev, ville: val || '', region: sel?.region || '' }));
            }}
            onInputChange={(_, val) => setForm(prev => ({ ...prev, ville: val }))}
            onBlur={() => {
              const sel = villes.find(v => v.nom === form.ville);
              setForm(prev => ({ ...prev, region: sel?.region || '' }));
            }}
            renderInput={params => <TextField {...params} label="Ville" fullWidth />}>
          </Autocomplete>
        );
      default:
        return (
          <TextField
            key={key}
            label={label}
            name={key}
            value={value as string}
            onChange={handleChange}
            fullWidth
            multiline={key === 'commentaire_agent'}
            minRows={key === 'commentaire_agent' ? 2 : undefined}
          />
        );
    }
  };

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
          {fieldsOrder.map(fc => renderField(fc))}
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

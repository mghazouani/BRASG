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
import Snackbar from "@mui/material/Snackbar";
import Box from "@mui/material/Box"; 

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
  onToast?: (message: string, severity: "success" | "error") => void;
}

export default function ClientEditForm({ open, client, onClose, onSave, loading, error, settings, onToast }: ClientEditFormProps) {
  const [form, setForm] = useState<Client>(client);
  const [villes, setVilles] = useState<VilleType[]>([]);
  const [toast, setToast] = useState<{ open: boolean; message: string; severity: "error" }>({ open: false, message: "", severity: "error" });
  const [saving, setSaving] = useState(false);
  const [missingFields, setMissingFields] = useState<{ [key: string]: boolean }>({});

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
    { key: 'sap_id', label: 'SAP ID' },
    { key: 'telephone', label: 'Téléphone' },
    { key: 'telephone2', label: 'Téléphone 2' },
    { key: 'telephone3', label: 'Téléphone 3' },
    { key: 'statut_general', label: 'Statut', type: 'select', options: settings.statut_general },
    { key: 'langue', label: 'Langue', type: 'select', options: settings.langue },   
    { key: 'canal_contact', label: 'Canal de contact', type: 'select', options: settings.canal_contact },
    { key: 'notification_client', label: 'Notification Client' },
    { key: 'date_notification', label: 'Dernière notification' },
    { key: 'a_demande_aide', label: 'A demandé de l’aide', type: 'select', options: settings.a_demande_aide },
    { key: 'nature_aide', label: 'Nature de l’aide', type: 'text' },
    { key: 'app_installee', label: 'App installée', type: 'select', options: settings.app_installee },
    { key: 'maj_app', label: 'Version app', type: 'text' },
    { key: 'commentaire_agent', label: 'Commentaire agent', type: 'text' },
    { key: 'segment_client', label: 'Segment', type: 'text' },
    { key: 'ville', label: 'Ville', type: 'autocomplete', options: villes },
    { key: 'region', label: 'Région', type: 'text' },
  ];

  // Nouvelle structure de groupes pour le formulaire avec regroupements horizontaux
  const groupedFields = [
    {
      groupLabel: "Infos Client",
      fields: [
        { key: 'nom_client', label: 'Nom' },
        { key: 'sap_id', label: 'SAP ID' },
      ],
    },
    {
      groupLabel: "Coordonnées Client",
      fields: [
        // Regroupement horizontal ville + région
        [
          { key: 'ville', label: 'Ville' },
          { key: 'region', label: 'Région' }
        ],
        // Regroupement horizontal téléphone
        [
          { key: 'telephone', label: 'Téléphone' },
          { key: 'telephone2', label: 'Téléphone 2' },
          { key: 'telephone3', label: 'Téléphone 3' }
        ]
      ],
    },
    {
      groupLabel: "Préférences Communication",
      fields: [
        [
          { key: 'canal_contact', label: 'Canal de contact' },
          { key: 'langue', label: 'Langue' },
        ]
      ],
    },
    {
      groupLabel: "Détails Suivi",
      fields: [
        // notification + date
        [
          { key: 'notification_client', label: 'Notification Client' },
          { key: 'date_notification', label: 'Dernière notification' }
        ],
        // app + version
        [
          { key: 'app_installee', label: 'Application installée' },
          { key: 'maj_app', label: 'Version app' }
        ],
        // aide + nature
        [
          { key: 'a_demande_aide', label: 'A demandé de l’aide' },
          { key: 'nature_aide', label: 'Nature de l’aide' }
        ]
      ],
    },
    {
      groupLabel: "Commentaires",
      fields: [
        { key: 'commentaire_agent', label: 'Commentaire agent' },
      ],
    },
  ];

  // mapping pour retrouver le field config d'origine (type, options, etc)
  const fieldsConfig = Object.fromEntries(fieldsOrder.map(f => [f.key, f]));

  // Rendu dynamique d'un champs
  function renderField(fc: typeof fieldsOrder[0]) {
    const { key, label, type, options } = fc;
    const value = form[key] ?? '';
    const isError = !!missingFields[key];
    // Notification client : affichage uniquement, non modifiable
    if (key === 'notification_client') {
      return (
        <TextField
          key={key}
          name={key}
          label={label}
          value={value ? 'Oui' : 'Non'}
          disabled
          fullWidth
        />
      );
    }
    if (key === 'date_notification') {
      return (
        <TextField
          key={key}
          name={key}
          label={label}
          value={typeof value === 'string' ? value : ''}
          disabled
          fullWidth
        />
      );
    }
    switch (type) {
      case 'select':
        return (
          <TextField key={key} label={label} name={key} select value={value} onChange={handleChange} fullWidth error={isError} helperText={isError ? 'Champs obligatoire' : undefined}>
            {options!.map(opt => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </TextField>
        );
      case 'radio':
        return (
          <FormControl key={key} component="fieldset" error={isError}>
            <FormLabel component="legend">{label}</FormLabel>
            <RadioGroup row name={key} value={value} onChange={handleChange}>
              {options!.map(opt => (
                <FormControlLabel key={opt.value} value={opt.value} control={<Radio />} label={opt.label} />
              ))}
            </RadioGroup>
            {isError && <span style={{ color: '#d32f2f', fontSize: 12 }}>Champs obligatoire</span>}
          </FormControl>
        );
      case 'autocomplete':
        return (
          <Autocomplete
            key={key}
            options={villes}
            getOptionLabel={option => option.nom}
            value={villes.find(v => v.id === form.ville) || null}
            onChange={(_, newVille) => {
              setForm(prev => ({
                ...prev,
                ville: newVille ? newVille.id : '',
                region: newVille ? newVille.region : ''
              }));
            }}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            renderInput={params => <TextField {...params} label="Ville" fullWidth error={isError} helperText={isError ? 'Champs obligatoire' : undefined} />}
          />
        );
      default:
        return (
          <TextField
            key={key}
            label={label}
            name={key}
            value={typeof value === 'string' ? value : ''}
            onChange={handleChange}
            fullWidth
            error={isError}
            helperText={isError ? 'Champs obligatoire' : undefined}
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("handleSubmit appelé");
    // Vérification des champs obligatoires (sap_id, nom_client, telephone)
    const missing: { [key: string]: boolean } = {};
    if (!form.sap_id) missing['sap_id'] = true;
    if (!form.nom_client) missing['nom_client'] = true;
    if (!form.telephone) missing['telephone'] = true;
    setMissingFields(missing);
    if (Object.keys(missing).length > 0) {
      setToast({ open: true, message: "Veuillez remplir tous les champs obligatoires.", severity: "error" });
      return;
    }
    setSaving(true);
    try {
      // Filtrer les champs à envoyer (évite d'envoyer les champs système/back)
      const fieldsToSend = [
        'id',
        'sap_id','nom_client','telephone','telephone2','telephone3','langue','statut_general',
        'notification_client','a_demande_aide','nature_aide','app_installee',
        'maj_app','commentaire_agent','segment_client','canal_contact','ville','region'
      ];
      const safeForm: any = Object.fromEntries(
        Object.entries(form).filter(([key]) => fieldsToSend.includes(key))
      );
      // Ne pas envoyer les champs à null (ex: action, date_notification)
      Object.keys(safeForm).forEach(k => {
        if (safeForm[k] === null) delete safeForm[k];
      });
      // Correction : ville doit être l'UUID (ou null)
      if (safeForm.ville === '') safeForm.ville = null;
      console.log("Payload filtré:", safeForm);
      await onSave(safeForm);
      console.log("onSave appelé !");
      if (onToast) onToast("Client modifié avec succès", "success");
      onClose();
    } catch (err: any) {
      console.error("Erreur lors de l'enregistrement:", err);
      let msg = "Erreur lors de l'enregistrement";
      if (err?.response?.data && Object.keys(err.response.data).length > 0) {
        msg = typeof err.response.data === "string"
          ? err.response.data
          : JSON.stringify(err.response.data);
      } else if (err?.message) {
        msg = err.message;
      } else if (err?.toString) {
        msg = err.toString();
      }
      setToast({ open: true, message: msg, severity: "error" });
    } finally {
      setSaving(false);
    }
  };

  return (
    <React.Fragment>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>Modifier le suivi du client</DialogTitle>
        <DialogContent className="max-h-[70vh] overflow-y-auto" sx={{ minWidth: 600, maxWidth: 900 }}>
          {error && <Alert severity="error">{error}</Alert>}
          <link href="https://fonts.googleapis.com/css?family=Roboto:400,500,700&display=swap" rel="stylesheet" />
          <style>{`
            .client-edit-form-roboto * {
              font-family: 'Roboto', Arial, sans-serif !important;
            }
          `}</style>
          <div className="client-edit-form-roboto">
            <form onSubmit={handleSubmit} autoComplete="off" id="client-edit-form">
              {groupedFields.map(group => (
                <React.Fragment key={group.groupLabel}>
                  {group.groupLabel !== "Commentaires" && (
                    <div style={{ fontWeight: 600, fontSize: '1rem', margin: '32px 0 12px 0' }}>{group.groupLabel}</div>
                  )}
                  {group.fields.map((fieldOrGroup, idx) =>
                    Array.isArray(fieldOrGroup) ? (
                      // Regroupement horizontal : Box pour chaque champ, wrap automatique
                      <Box display="flex" gap={2} key={idx} mb={2}>
                        {fieldOrGroup.map(f => (
                          <Box key={f.key} flex={1} minWidth={0}>
                            {renderField({ ...(fieldsConfig[f.key as keyof typeof fieldsConfig]), ...f } as any)}
                          </Box>
                        ))}
                      </Box>
                    ) : (
                      <Box display="flex" gap={2} key={fieldOrGroup.key} mb={2}>
                        <Box flex={fieldOrGroup.key === "commentaire_agent" ? 1 : 0.5} minWidth={0}>
                          {renderField({ ...(fieldsConfig[fieldOrGroup.key as keyof typeof fieldsConfig]), ...fieldOrGroup } as any)}
                        </Box>
                      </Box>
                    )
                  )}
                </React.Fragment>
              ))}
            </form>
          </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={saving}>Annuler</Button>
          <Button type="submit" form="client-edit-form" variant="contained" color="primary" disabled={saving}>
            Enregistrer
          </Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        open={toast.open}
        autoHideDuration={2500}
        onClose={() => setToast({ ...toast, open: false })}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert severity={toast.severity} variant="filled" sx={{ width: "100%" }}>
          {toast.message}
        </Alert>
      </Snackbar>
    </React.Fragment>
  );
}

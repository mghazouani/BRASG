"use client";

import * as React from "react";
import { useEffect, useState, useMemo } from "react";
import { api } from "@/utils/api";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import Tooltip from "@mui/material/Tooltip";
import HelpIcon from "@mui/icons-material/Help";
import CallIcon from "@mui/icons-material/Call";
import IconButton from "@mui/material/IconButton";
import EditIcon from "@mui/icons-material/EditOutlined";
import SaveIcon from "@mui/icons-material/CheckCircleOutline";
import CancelIcon from "@mui/icons-material/CancelOutlined";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import ClientFilters from "./ClientFilters";
import ClientEditForm from "./ClientEditForm";
import PaginationBar from "../components/PaginationBar"; // Import PaginationBar
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import Autocomplete from "@mui/material/Autocomplete";
import SmartphoneIcon from "@mui/icons-material/Smartphone";
import VisibilityIcon from "@mui/icons-material/Visibility";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import CampaignIcon from "@mui/icons-material/Campaign";
import PhoneInTalkIcon from "@mui/icons-material/PhoneInTalk"; // Import PhoneInTalkIcon
import WhatsAppIcon from "@mui/icons-material/WhatsApp";
import TimerIcon from "@mui/icons-material/Timer"; // Import TimerIcon
import ClientNotificationModal from "./ClientNotificationModal";
import { Snackbar } from "@mui/material";
import ClientDetails from "./ClientDetails";

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

interface VilleType {
  id: string;
  nom: string;
  region: string;
}

interface AuditLogType {
  id: string;
  table_name: string;
  record_id: string;
  user: string;
  action: string;
  champs_changes: any;
  timestamp: string;
}

const statutColor = (statut: string) => {
  switch (statut) {
    case "actif":
      return "success";
    case "inactif":
      return "default";
    case "bloque":
      return "error";
    default:
      return "default";
  }
};

export default function DashboardPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statut, setStatut] = useState("");
  const [langue, setLangue] = useState<string>("");
  const [aide, setAide] = useState<string>("");
  const [app, setApp] = useState<string>("");
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [editClient, setEditClient] = useState<Client | null>(null);
  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
  const [inlineEditId, setInlineEditId] = useState<string | null>(null);
  const [inlineEditData, setInlineEditData] = useState<Partial<Client>>({});
  const [inlineEditLoading, setInlineEditLoading] = useState(false);
  const [inlineEditError, setInlineEditError] = useState<string | null>(null);
  const [totalClients, setTotalClients] = useState(0);
  const [auditLogs, setAuditLogs] = useState<AuditLogType[]>([]);
  const [notifModalOpen, setNotifModalOpen] = useState(false);
  const [notifModalClient, setNotifModalClient] = useState<Client | null>(null);
  const [notifToast, setNotifToast] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });
  const [editToast, setEditToast] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  // Chargement dynamique des paramètres du Dashboard
  const [dashboardSettings, setDashboardSettings] = useState<{
    statut_general: { value: string; label: string }[];
    langue: { value: string; label: string }[];
    canal_contact: { value: string; label: string }[];
    notification_client: { value: boolean; label: string }[];
    a_demande_aide: { value: boolean; label: string }[];
    app_installee: { value: boolean; label: string }[];
    maj_app: string;
  }>({
    statut_general: [],
    langue: [],
    canal_contact: [],
    notification_client: [],
    a_demande_aide: [],
    app_installee: [],
    maj_app: "",
  });
  useEffect(() => {
    api.get('dashboard-configs/').then(res => {
      if (res.data.length > 0) setDashboardSettings(res.data[0].settings);
    }).catch(console.error);
  }, []);
  // Charger l’historique des modifications à chaque sélection
  useEffect(() => {
    if (!selectedClient) {
      setAuditLogs([]);
      return;
    }
    // Appel API filtré côté backend (déjà ok), mais on filtre aussi côté frontend par sécurité
    api.get("auditlogs/", { params: { table_name: "Client", record_id: selectedClient.id } })
      .then(res => {
        const data = Array.isArray(res.data) ? res.data : res.data.results;
        // Double filtre côté frontend pour éviter tout bug d'affichage
        const filtered = (data as AuditLogType[]).filter(log => log.table_name === "Client" && log.record_id === selectedClient.id);
        setAuditLogs(filtered);
      })
      .catch(console.error);
  }, [selectedClient]);
  // Choix dynamiques depuis JSON
  const statutChoices = dashboardSettings.statut_general;
  const langueChoices = dashboardSettings.langue;
  const aideChoices = dashboardSettings.a_demande_aide;
  const appChoices = dashboardSettings.app_installee;

  // Pagination state
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(() => {
    if (typeof window !== "undefined") {
      const stored = Number(localStorage.getItem("perPage"));
      return stored && stored > 0 ? stored : 10;
    }
    return 10;
  });
  const [totalPages, setTotalPages] = useState(1);
  const [ordering, setOrdering] = useState<string>("nom_client");

  // Remettre la page à 1 si perPage, search, statut, langue, aide, app ou region changent
  useEffect(() => {
    setPage(1);
  }, [perPage, search, statut, langue, aide, app]);

  // Sécuriser la page courante si > totalPages
  useEffect(() => {
    if (page > totalPages) setPage(totalPages || 1);
  }, [totalPages]);

  // DEBUG: log des paramètres API
  useEffect(() => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(perPage)
    });
    if (search) params.append("search", search);
    if (statut) params.append("statut_general", statut);
    if (langue) params.append("langue", langue);
    if (aide) params.append("a_demande_aide", aide);
    if (app) params.append("app_installee", app);
    if (ordering) params.append("ordering", ordering);
    console.log("[API] clients/?" + params.toString());
  }, [page, perPage, search, statut, langue, aide, app, ordering]);

  // Helper pour calculer relance automatique : si app non installée, date_notification vide, antérieure à aujourd’hui ou aide demandée
  const shouldRelance = (c: Client): boolean => {
    // Si l'application n'est pas installée
    if (c.app_installee === false) {
      return true;
    }
    // Si la date de notification est vide
    if (!c.date_notification) {
      return true;
    }
    // Si la date de notification est antérieure à aujourd’hui
    if (c.date_notification < new Date().toISOString().slice(0,10)) {
      return true;
    }
    // Si l'aide a été demandée
    if (c.a_demande_aide === true) {
      return true;
    }
    // Sinon, pas de relance
    return false;
  };

  // Fetch clients paginés et filtrés côté backend
  useEffect(() => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(perPage)
    });
    if (search) params.append("search", search);
    if (statut) params.append("statut_general", statut);
    if (langue) params.append("langue", langue);
    if (aide) params.append("a_demande_aide", aide);
    if (app) params.append("app_installee", app);
    if (ordering) params.append("ordering", ordering);
    api.get(`clients/?${params.toString()}`)
      .then((res) => {
        console.log('[API][res.data]', res.data); // LOG du retour API complet
        const fetched: Client[] = res.data.results;
        setClients(fetched);
        setTotalClients(res.data.count || 0);
        setTotalPages(Math.ceil((res.data.count || 1) / perPage));
        // Auto-relance: OR logic, update true/false
        fetched.forEach(c => {
          const newRel = shouldRelance(c);
          console.log('Relance debug:', c.id, c.relance_planifiee, shouldRelance(c));
          if (newRel !== c.relance_planifiee) {
            api.patch(`clients/${c.id}/`, { relance_planifiee: newRel })
              .then(resp => setClients(prev => prev.map(p => p.id === resp.data.id ? resp.data : p)))
              .catch(err => console.error('Relance update error:', err));
          }
        });
      })
      .catch((err) => setError(err.response?.data?.detail || "Erreur API"))
      .finally(() => setLoading(false));
  }, [page, perPage, search, statut, langue, aide, app, ordering]);

  const handlePageChange = (_: any, value: number) => {
    setPage(value);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handlePerPageChange = (value: number) => {
    setPerPage(value);
    if (typeof window !== "undefined") {
      localStorage.setItem("perPage", String(value));
    }
  };

  const handleSort = (field: string) => {
    setPage(1);
    if (ordering === field) {
      setOrdering(`-${field}`);
    } else {
      setOrdering(field);
    }
  };

  // Ordre des champs et logique d'affichage/édition
  const fieldsOrder: { key: keyof Client; label: string }[] = [
    { key: 'nom_client', label: 'Nom' },
    { key: 'sap_id', label: 'SAP ID' },
    { key: 'telephone', label: 'Téléphone' },
    //{ key: 'langue', label: 'Langue' },
    { key: 'statut_general', label: 'Statut' },
    { key: 'canal_contact', label: 'Canal préféré' },
    { key: 'notification_client', label: 'Notifié' },
    { key: 'date_notification', label: 'Dernière notification' },
    { key: 'app_installee', label: 'App' },
    { key: 'maj_app', label: 'MàJ App' },
    { key: 'a_demande_aide', label: 'Aide' },
    //{ key: 'nature_aide', label: 'Nature aide' },
    { key: 'commentaire_agent', label: 'Commentaire' },
    { key: 'segment_client', label: 'CMD/Jour' },
    { key: 'relance_planifiee', label: 'Relance' },
  ];

  // Utilitaire pour agrandir la taille des tooltips (NOUVEAU STYLE)
  const largeTooltipProps = {
    componentsProps: {
      tooltip: {
        sx: {
          fontSize: '1rem',
          padding: '10px 15px',
          maxWidth: 300,
          backgroundColor: '#333',
          color: '#fff',
          borderRadius: '8px',
          boxShadow: '0px 2px 10px rgba(0, 0, 0, 0.2)',
          lineHeight: 1.5,
          whiteSpace: 'normal',
        },
      },
    },
  };

  const renderCell = (client: Client, field: keyof Client): React.ReactNode => {
    const isEditing = inlineEditId === client.id;
    switch (field) {
      case 'nom_client': return client.nom_client;
      case 'sap_id': return client.sap_id;
      case 'telephone':
        // Non éditable en inline
        return (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
            <span>{client.telephone}</span>
            {(client.telephone2 || client.telephone3) && (
              <Tooltip
                {...largeTooltipProps}
                title={
                  <span>
                    <b>Autres Num. Tél.</b><br />
                    {client.telephone2 && <>Tél 2 : {client.telephone2}<br /></>}
                    {client.telephone3 && <>Tél 3 : {client.telephone3}</>}
                  </span>
                }
                placement="top"
              >
                <AddCircleOutlineIcon fontSize="small" sx={{ color: '#1976d2', marginLeft: 1 }} />
              </Tooltip>
            )}
          </div>
        );
      case 'langue':
        return isEditing
          ? <TextField size="small" value={inlineEditData.langue || ''} onChange={e => setInlineEditData(d => ({ ...d, langue: e.target.value }))} />
          : client.langue;
      case 'statut_general':
        return isEditing
          ? <TextField size="small" select value={inlineEditData.statut_general || ''} onChange={e => setInlineEditData(d => ({ ...d, statut_general: e.target.value }))}>
              {statutChoices.map(opt => <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>)}
            </TextField>
          : <Chip
              label={dashboardSettings.statut_general.find(opt => opt.value === client.statut_general)?.label || client.statut_general}
              size="small"
              color={statutColor(client.statut_general)}
            />;
      case 'canal_contact':
        // Affichage icône combiné téléphone ou WhatsApp selon la valeur
        if (client.canal_contact === 'telephone') {
          return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <PhoneInTalkIcon sx={{ color: '#25D366', fontSize: 22 }} />
            </div>
          );
        }
        if (client.canal_contact === 'whatsapp') {
          return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <WhatsAppIcon sx={{ color: '#25D366', fontSize: 22 }} />
            </div>
          );
        }
        return <span className="text-gray-400">—</span>;
      case 'notification_client':
        // Affichage icône mégaphone : vert si true, gris si false
        return (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <CampaignIcon sx={{ color: client.notification_client ? '#43a047' : '#bdbdbd', fontSize: 24 }} />
          </div>
        );
      case 'date_notification':
        return client.date_notification
          ? new Date(client.date_notification).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false })
          : '—';
      case 'app_installee':
        return isEditing
          ? <TextField size="small" select value={`${inlineEditData.app_installee}`} onChange={e => setInlineEditData(d => ({ ...d, app_installee: e.target.value === 'true' }))}>
              {dashboardSettings.app_installee.map(opt => <MenuItem key={`${opt.value}`} value={`${opt.value}`}>{opt.label}</MenuItem>)}
            </TextField>
          : (
              client.app_installee === false
                ? <Tooltip {...largeTooltipProps} title="App non installée">
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '100%' }}>
                      <SmartphoneIcon color="error" />
                    </div>
                  </Tooltip>
                : client.maj_app !== dashboardSettings.maj_app
                  ? <Tooltip {...largeTooltipProps} title={`App non à jour (installé: ${client.maj_app || 'inconnu'} / dernière: ${dashboardSettings.maj_app})`}>
                      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '100%' }}>
                        <SmartphoneIcon sx={{ color: '#FFD600' }} />
                      </div>
                    </Tooltip>
                  : <Tooltip {...largeTooltipProps} title={`Dernière mise à jour : ${dashboardSettings.maj_app}`}>
                      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '100%' }}>
                        <SmartphoneIcon color="success" />
                      </div>
                    </Tooltip>
            );
      case 'maj_app':
        return isEditing
          ? <TextField size="small" value={inlineEditData.maj_app || ''} onChange={e => setInlineEditData(d => ({ ...d, maj_app: e.target.value }))} />
          : client.maj_app || <span className="text-gray-400">—</span>;
      case 'a_demande_aide':
        return isEditing
          ? <RadioGroup row name="a_demande_aide" value={`${inlineEditData.a_demande_aide}`} onChange={e => setInlineEditData(d => ({ ...d, a_demande_aide: e.target.value === 'true' }))}>
              {aideChoices.map(opt => <FormControlLabel key={`${opt.value}`} value={`${opt.value}`} control={<Radio size="small" />} label={opt.label} />)}
            </RadioGroup>
          : (
              client.a_demande_aide
                ? <Tooltip {...largeTooltipProps} title={client.nature_aide || "Aide demandée"}><HelpIcon className="text-yellow-500" /></Tooltip>
                : null
            );
      case 'nature_aide':
        return isEditing
          ? <TextField size="small" value={inlineEditData.nature_aide || ''} onChange={e => setInlineEditData(d => ({ ...d, nature_aide: e.target.value }))} />
          : client.nature_aide || <span className="text-gray-400">—</span>;
      case 'commentaire_agent':
        return isEditing
          ? <TextField size="small" value={inlineEditData.commentaire_agent || ''} onChange={e => setInlineEditData(d => ({ ...d, commentaire_agent: e.target.value }))} />
          : (client.commentaire_agent
              ? (
                  <Tooltip {...largeTooltipProps} title={client.commentaire_agent}>
                    <span>
                      {client.commentaire_agent.slice(0,20)}{client.commentaire_agent.length > 20 ? '...' : ''}
                    </span>
                  </Tooltip>
                )
              : <span className="text-gray-400">—</span>
            );
      case 'segment_client':
        // Non éditable en inline
        return client.segment_client || <span className="text-gray-400">—</span>;
      case 'relance_planifiee':
        // Icône relance : timer orange si planifiée, gris sinon
        return (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <IconButton 
              onClick={() => !isEditing && handleOpenNotifModal(client)}
              color="primary"
              disabled={isEditing}
            >
              <TimerIcon sx={{ color: client.relance_planifiee ? '#fb8c00' : '#bdbdbd', fontSize: 22 }} />
            </IconButton>
          </div>
        );
      default:
        return client[field] as React.ReactNode;
    }
  };

  // Calcul de la plage affichée
  const rangeStart = totalClients === 0 ? 0 : (page - 1) * perPage + 1;
  const rangeEnd = Math.min(page * perPage, totalClients);

  // Gestion de la sauvegarde d'un client modifié (modale)
  async function handleSaveEditClient(data: Client) {
    setEditLoading(true);
    setEditError(null);
    try {
      // Générer un payload ne contenant que les champs modifiés
      const original = clients.find(c => c.id === data.id);
      const payload: Partial<Client> = {};
      if (original) {
        for (const key in data) {
          if (key === 'id' || key === 'region') continue;
          // @ts-ignore
          if (data[key] !== (original as any)[key]) {
            // @ts-ignore
            payload[key] = data[key];
          }
        }
      }
      // DEBUG LOG pour vérifier le payload
      console.log('[DEBUG][handleSaveEditClient] payload:', payload);
      // SUPPRIME le blocage sur payload vide pour toujours envoyer la requête
      const res = await api.patch(`clients/${data.id}/`, payload);
      setClients(clients => clients.map(c => c.id === data.id ? res.data : c));
      setEditClient(null);
      // Vérifier relance après modification via modal
      {
        const updated = res.data;
        const newRel = shouldRelance(updated);
        if (newRel !== updated.relance_planifiee) {
          try {
            const relResp = await api.patch(`clients/${updated.id}/`, { relance_planifiee: newRel });
            setClients(prev => prev.map(p => p.id === relResp.data.id ? relResp.data : p));
          } catch (err) {
            console.error('Modal relance update error:', err);
          }
        }
      }
    } catch (err: any) {
      console.error("SaveEditClient error:", err.response?.data);
      setEditError(JSON.stringify(err.response?.data) || "Erreur lors de la modification");
    } finally {
      setEditLoading(false);
    }
  }

  // Gestion édition inline
  function startInlineEdit(client: Client) {
    setInlineEditId(client.id);
    setInlineEditData({ ...client });
    setInlineEditError(null);
  }
  function cancelInlineEdit() {
    setInlineEditId(null);
    setInlineEditData({});
    setInlineEditError(null);
  }
  const saveInlineEdit = async () => {
    if (!inlineEditId) return;
    setInlineEditLoading(true);
    setInlineEditError(null);
    let safeForm: any = {};
    try {
      const fieldsToSend = [
        'id','sap_id','nom_client','telephone','telephone2','telephone3','langue','statut_general',
        'notification_client','a_demande_aide','nature_aide','app_installee','maj_app','commentaire_agent','segment_client','canal_contact','ville','region'
      ];
      const safeForm: any = Object.fromEntries(
        Object.entries(inlineEditData).filter(([key]) => fieldsToSend.includes(key))
      );
      safeForm.id = inlineEditId;
      await api.patch(`/clients/${inlineEditId}/`, safeForm);
      setClients(clients => clients.map(c => c.id === inlineEditId ? { ...c, ...safeForm } : c));
      setInlineEditId(null);
      setInlineEditData({});
    } catch (err: any) {
      let msg = "Erreur lors de la sauvegarde";
      if (err?.response?.data) {
        msg = typeof err.response.data === "string"
          ? err.response.data
          : JSON.stringify(err.response.data);
      } else if (err?.message) {
        msg = err.message;
      }
      setInlineEditError(msg);
      console.error("Erreur PATCH inline:", err, safeForm);
    }finally {
      setInlineEditLoading(false);
    }
  };

  // Fonction pour ouvrir la modale de notification depuis l'icône relance
  const handleOpenNotifModal = (client: Client) => {
    setNotifModalClient(client);
    setNotifModalOpen(true);
  };
  const handleCloseNotifModal = () => {
    setNotifModalOpen(false);
    setNotifModalClient(null);
  };

  // Callback à passer à la modale pour affichage du toast après notification
  const handleNotifSuccess = async (message = "Notification enregistrée avec succès") => {
    setNotifToast({ open: true, message, severity: "success" });
    if (notifModalClient) {
      // Rafraîchir la date_notification ET notification_client du client concerné
      try {
        const res = await api.get(`/clients/${notifModalClient.id}/`);
        setClients(clients => clients.map(c =>
          c.id === notifModalClient.id
            ? { ...c, date_notification: res.data.date_notification, notification_client: res.data.notification_client }
            : c
        ));
      } catch (err) {
        setNotifToast({ open: true, message: "Erreur lors de la mise à jour du client après notification", severity: "error" });
      }
    }
  };

  // Toast pour l'édition de client
  const handleEditClientToast = (message: string, severity: "success" | "error") => {
    setEditToast({ open: true, message, severity });
    setEditClient(null); // ferme la modale
  };

  // --- Ajout style zebra pour lignes du tableau ---
  const zebraBlue = ['#e3f2fd', '#bbdefb'];

  return (
    <main className="min-h-screen flex flex-col items-center p-8 transition-colors duration-300" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
      {/* En-tête supprimé : titre Dashboard */}
      <div className="flex justify-between items-center w-full mb-6 fade-in">
        <div className="flex items-center gap-4">
        </div>
        <div className="flex items-center gap-2">
        </div>
      </div>
      <ClientFilters
        search={search}
        onSearch={setSearch}
        statut={statut}
        onStatut={setStatut}
        langue={langue}
        onLangue={setLangue}
        langues={langueChoices}
        aide={aide}
        onAide={setAide}
        aideOptions={aideChoices}
        app={app}
        onApp={setApp}
        appOptions={appChoices}
      />
      {/* Pagination classique (haut) */}
      <PaginationBar page={page} count={totalPages} onChange={handlePageChange} perPage={perPage} onPerPageChange={handlePerPageChange} />
      {loading && <CircularProgress color="primary" />}
      {error && <Alert severity="error" className="mb-4">{error}</Alert>}
      {inlineEditError && <Alert severity="error" className="mb-2">{inlineEditError}</Alert>}
      {(!loading && !error) && (
        <div className="w-full bg-white rounded shadow p-6 overflow-x-auto">
          <div className="flex items-center justify-between w-full mb-2">
            <div className="text-gray-700 dark:text-gray-200 text-sm">
              Page {page} / {totalPages} — {totalClients} client{totalClients > 1 ? "s" : ""}
              {totalClients > 0 && (
                <span className="ml-2">({rangeStart}-{rangeEnd} affichés)</span>
              )}
            </div>
          </div>
          {clients.length === 0 ? (
            <div className="text-gray-500">Aucun client trouvé.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full w-full text-sm table-auto">
                <thead>
                  <tr className="bg-blue-50">
                    {fieldsOrder.map(col => (
                      <th
                        key={col.key}
                        className="p-2 text-left cursor-pointer"
                        onClick={() => handleSort(col.key)}
                      >
                        {col.label}
                        {ordering.replace('-', '') === col.key && (
                          ordering.startsWith('-') ? ' ▼' : ' ▲'
                        )}
                      </th>
                    ))}
                    <th className="p-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {clients.map((client, idx) => (
                    <tr
                      key={client.id}
                      style={{ background: zebraBlue[idx % 2], transition: 'background 0.2s', cursor: 'pointer' }}
                      className="dashboard-row-hover"
                      onDoubleClick={() => setSelectedClient(client)}
                    >
                      {fieldsOrder.map(col => (
                        <td key={col.key} className="p-2">{renderCell(client, col.key)}</td>
                      ))}
                      <td className="p-2 flex gap-1">
                        {inlineEditId === client.id ? (
                          <>
                            <Tooltip {...largeTooltipProps} title="Enregistrer">
                              <span>
                                <IconButton size="small" onClick={saveInlineEdit} disabled={inlineEditLoading}>
                                  <SaveIcon fontSize="small" />
                                </IconButton>
                              </span>
                            </Tooltip>
                            <Tooltip {...largeTooltipProps} title="Annuler">
                              <span>
                                <IconButton size="small" onClick={cancelInlineEdit} disabled={inlineEditLoading}>
                                  <CancelIcon fontSize="small" />
                                </IconButton>
                              </span>
                            </Tooltip>
                          </>
                        ) : (
                          <>
                            <Tooltip {...largeTooltipProps} title="Détails">
                              <IconButton size="small" onClick={() => setSelectedClient(client)}>
                                <VisibilityIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip {...largeTooltipProps} title="Modifier">
                              <IconButton size="small" onClick={() => setEditClient(client)}>
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip {...largeTooltipProps} title="Édition rapide">
                              <IconButton size="small" onClick={() => startInlineEdit(client)}>
                                <SaveIcon fontSize="small" color="action" />
                              </IconButton>
                            </Tooltip>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      {/* Pagination classique (bas) */}
      <PaginationBar page={page} count={totalPages} onChange={handlePageChange} perPage={perPage} onPerPageChange={handlePerPageChange} />
      {/* Modal de détails client */}
      {selectedClient && (
        <ClientDetails
          selectedClient={selectedClient}
          auditLogs={auditLogs}
          open={!!selectedClient}
          onClose={() => setSelectedClient(null)}
          statutColor={statutColor}
        />
      )}
      {/* Modal d'édition client */}
      {editClient && (
        <ClientEditForm
          open={!!editClient}
          client={editClient}
          settings={dashboardSettings}
          onClose={() => setEditClient(null)}
          onSave={handleSaveEditClient}
          loading={editLoading}
          error={editError}
          onToast={handleEditClientToast}
        />
      )}
      {notifModalClient && (
        <ClientNotificationModal
          open={notifModalOpen}
          onClose={handleCloseNotifModal}
          onSuccess={handleNotifSuccess}
          clientId={notifModalClient.id}
          clientName={notifModalClient.nom_client}
        />
      )}
      <Snackbar
        open={notifToast.open}
        autoHideDuration={2500}
        onClose={() => setNotifToast({ ...notifToast, open: false })}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert severity={notifToast.severity} variant="filled" sx={{ width: "100%" }}>
          {notifToast.message}
        </Alert>
      </Snackbar>
      <Snackbar
        open={editToast.open}
        autoHideDuration={2500}
        onClose={() => setEditToast({ ...editToast, open: false })}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert severity={editToast.severity} variant="filled" sx={{ width: "100%" }}>
          {editToast.message}
        </Alert>
      </Snackbar>
      <style>{`
        .dashboard-row-hover:hover {
          background: #FFFDE7 !important;
          transition: background 0.2s;
        }
      `}</style>
    </main>
  );
}

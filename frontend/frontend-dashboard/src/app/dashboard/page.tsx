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
  const [region, setRegion] = useState("");
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
  const [villes, setVilles] = useState<VilleType[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogType[]>([]);

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
  useEffect(() => {
    api.get("villes/").then(res => {
      const data = Array.isArray(res.data) ? res.data : res.data.results;
      setVilles(data as VilleType[]);
    });
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
  }, [perPage, search, statut, langue, aide, app, region]);

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
    if (region) params.append("region", region);
    if (langue) params.append("langue", langue);
    if (aide) params.append("a_demande_aide", aide);
    if (app) params.append("app_installee", app);
    if (ordering) params.append("ordering", ordering);
    console.log("[API] clients/?" + params.toString());
  }, [page, perPage, search, statut, region, langue, aide, app, ordering]);

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
    if (region) params.append("region", region);
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
  }, [page, perPage, search, statut, region, langue, aide, app, ordering]);

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

  // Liste unique des régions pour le filtre (à calculer sur tous les clients si besoin)
  // Ici, on laisse tel quel pour la démo, mais en prod il faudrait une API dédiée ou un champ distinct
  const regions = useMemo(() => Array.from(new Set(clients.map(c => c.region).filter(Boolean) as string[])), [clients]);

  // Ordre des champs et logique d'affichage/édition
  const fieldsOrder: { key: keyof Client; label: string }[] = [
    { key: 'nom_client', label: 'Nom' },
    { key: 'sap_id', label: 'SAP ID' },
    { key: 'telephone', label: 'Téléphone' },
    { key: 'langue', label: 'Langue' },
    { key: 'statut_general', label: 'Statut' },
    { key: 'canal_contact', label: 'Canal contact' },
    { key: 'notification_client', label: 'Notification client' },
    { key: 'date_notification', label: 'Date notification' },
    { key: 'app_installee', label: 'App installée' },
    { key: 'maj_app', label: 'MàJ App' },
    { key: 'a_demande_aide', label: 'Aide' },
    { key: 'nature_aide', label: 'Nature aide' },
    { key: 'commentaire_agent', label: 'Commentaire' },
    { key: 'ville', label: 'Ville' },
    { key: 'region', label: 'Région' },
    { key: 'segment_client', label: 'CMD/Jour' },
    { key: 'relance_planifiee', label: 'Relance' },
  ];

  const renderCell = (client: Client, field: keyof Client): React.ReactNode => {
    const isEditing = inlineEditId === client.id;
    switch (field) {
      case 'nom_client': return client.nom_client;
      case 'sap_id': return client.sap_id;
      case 'telephone':
        return isEditing
          ? <TextField size="small" value={inlineEditData.telephone || ''} onChange={e => setInlineEditData(d => ({ ...d, telephone: e.target.value }))} />
          : client.telephone;
      case 'langue':
        return isEditing
          ? <TextField size="small" select value={inlineEditData.langue || ''} onChange={e => setInlineEditData(d => ({ ...d, langue: e.target.value }))}>
              {langueChoices.map(opt => <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>)}
            </TextField>
          : (langueChoices.find(opt => opt.value === client.langue)?.label || <span className="text-gray-400">—</span>);
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
        return isEditing
          ? (
              <TextField size="small" select value={inlineEditData.canal_contact || ''} onChange={e => setInlineEditData(d => ({ ...d, canal_contact: e.target.value }))}>
                {dashboardSettings.canal_contact.map(opt => (
                  <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                ))}
              </TextField>
            )
          : (dashboardSettings.canal_contact.find(opt => opt.value === client.canal_contact)?.label || <span className="text-gray-400">—</span>);
      case 'notification_client':
        return isEditing
          ? <TextField size="small" select value={`${inlineEditData.notification_client}`} onChange={e => setInlineEditData(d => ({ ...d, notification_client: e.target.value === 'true' }))}>
              {dashboardSettings.notification_client.map(opt => <MenuItem key={`${opt.value}`} value={`${opt.value}`}>{opt.label}</MenuItem>)}
            </TextField>
          : (client.notification_client ? "Oui" : "Non");
      case 'date_notification':
        return isEditing
          ? <TextField size="small" type="date" value={inlineEditData.date_notification || ''} onChange={e => setInlineEditData(d => ({ ...d, date_notification: e.target.value }))} />
          : client.date_notification || <span className="text-gray-400">—</span>;
      case 'app_installee':
        return isEditing
          ? <TextField size="small" select value={`${inlineEditData.app_installee}`} onChange={e => setInlineEditData(d => ({ ...d, app_installee: e.target.value === 'true' }))}>
              {dashboardSettings.app_installee.map(opt => <MenuItem key={`${opt.value}`} value={`${opt.value}`}>{opt.label}</MenuItem>)}
            </TextField>
          : (
              client.app_installee === false
                ? <Tooltip title="App non installée"><SmartphoneIcon color="error" /></Tooltip>
                : client.maj_app !== dashboardSettings.maj_app
                  ? <Tooltip title={`App non à jour (installé: ${client.maj_app || 'inconnu'} / dernière: ${dashboardSettings.maj_app})`}><SmartphoneIcon color="warning" /></Tooltip>
                  : <Tooltip title={`Dernière mise à jour : ${dashboardSettings.maj_app}`}><SmartphoneIcon color="success" /></Tooltip>
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
                ? <Tooltip title={client.nature_aide || "Aide demandée"}><HelpIcon className="text-yellow-500" /></Tooltip>
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
                  <Tooltip title={client.commentaire_agent}>
                    <span>
                      {client.commentaire_agent.slice(0,20)}{client.commentaire_agent.length > 20 ? '...' : ''}
                    </span>
                  </Tooltip>
                )
              : <span className="text-gray-400">—</span>
            );
      case 'ville':
        return isEditing
          ? <Autocomplete freeSolo options={villes.map(v=>v.nom)} value={inlineEditData.ville||''} onChange={(_,val)=>{const sel=villes.find(v=>v.nom===val);setInlineEditData(d=>({...d,ville:val||'',region:sel?.region||''}));}} renderInput={params=><TextField {...params} size="small" />} />
          : client.ville || <span className="text-gray-400">—</span>;
      case 'region':
        return isEditing
          ? <TextField size="small" value={inlineEditData.region||''} disabled />
          : client.region || <span className="text-gray-400">—</span>;
      case 'segment_client':
        return isEditing
          ? <TextField size="small" value={inlineEditData.segment_client||''} onChange={e=>setInlineEditData(d=>({...d,segment_client:e.target.value}))} />
          : client.segment_client || <span className="text-gray-400">—</span>;
      case 'relance_planifiee':
        return isEditing
          ? <TextField size="small" select value={`${inlineEditData.relance_planifiee}`} onChange={e => setInlineEditData(d => ({ ...d, relance_planifiee: e.target.value==='true' }))}>
              <MenuItem value="true">Oui</MenuItem><MenuItem value="false">Non</MenuItem>
            </TextField>
          : (
              client.relance_planifiee
                ? <Tooltip title="Relance planifiée"><CallIcon color="primary" /></Tooltip>
                : <Tooltip title="Pas de relance"><CallIcon className="text-gray-400" /></Tooltip>
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
      // Si aucun champ modifié, pas besoin d'Appel API
      if (Object.keys(payload).length === 0) {
        setEditLoading(false);
        setEditClient(null);
        return;
      }
      const res = await api.patch(`clients/${data.id}/`, payload);
      // Remplace le client dans la liste
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
  async function saveInlineEdit() {
    if (!inlineEditId) return;
    setInlineEditLoading(true);
    setInlineEditError(null);
    try {
      // Générer un payload avec le champ inline modifié
      const originalInline = clients.find(c => c.id === inlineEditId);
      const payloadInline: Partial<Client> = {};
      if (originalInline) {
        for (const key in inlineEditData as any) {
          if (key === 'id' || key === 'region') continue;
          // @ts-ignore
          if ((inlineEditData as any)[key] !== (originalInline as any)[key]) {
            // @ts-ignore
            payloadInline[key] = (inlineEditData as any)[key];
          }
        }
      }
      // Si seulement la région/id changés ou aucun changement, on skip
      if (Object.keys(payloadInline).length === 0) {
        setInlineEditLoading(false);
        setInlineEditId(null);
        return;
      }
      const res = await api.patch(`clients/${inlineEditId}/`, payloadInline);
      setClients(clients => clients.map(c => c.id === inlineEditId ? res.data : c));
      setInlineEditId(null);
      setInlineEditData({});
      // Vérifier relance après modification inline
      {
        const updated = res.data;
        const newRel = shouldRelance(updated);
        if (newRel !== updated.relance_planifiee) {
          api.patch(`clients/${updated.id}/`, { relance_planifiee: newRel })
            .then(resp => setClients(prev => prev.map(p => p.id === resp.data.id ? resp.data : p)))
            .catch(err => console.error('Inline relance update error:', err));
        }
      }
    } catch (err: any) {
      console.error("Inline edit error:", err.response?.data);
      setInlineEditError(JSON.stringify(err.response?.data) || "Erreur lors de la modification");
    } finally {
      setInlineEditLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center p-8 transition-colors duration-300" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
      {/* <KpiAdoptionCard /> */}
      <div className="flex justify-between items-center w-full mb-6 fade-in">
        <div className="flex items-center gap-4">
          <h1 className="text-3xl font-bold text-blue-800 dark:text-blue-200">Suivi Déploiement ASG</h1>
        </div>
        <div className="flex items-center gap-2">
        </div>
      </div>
      <ClientFilters
        search={search}
        onSearch={setSearch}
        statut={statut}
        onStatut={setStatut}
        region={region}
        onRegion={setRegion}
        regions={regions}
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
                  {clients.map(client => (
                    <tr key={client.id} className="border-b hover:bg-blue-50">
                      {fieldsOrder.map(col => (
                        <td key={col.key} className="p-2">{renderCell(client, col.key)}</td>
                      ))}
                      <td className="p-2 flex gap-1">
                        {inlineEditId === client.id ? (
                          <>
                            <Tooltip title="Enregistrer">
                              <span>
                                <IconButton size="small" onClick={saveInlineEdit} disabled={inlineEditLoading}>
                                  <SaveIcon fontSize="small" />
                                </IconButton>
                              </span>
                            </Tooltip>
                            <Tooltip title="Annuler">
                              <span>
                                <IconButton size="small" onClick={cancelInlineEdit} disabled={inlineEditLoading}>
                                  <CancelIcon fontSize="small" />
                                </IconButton>
                              </span>
                            </Tooltip>
                          </>
                        ) : (
                          <>
                            <Tooltip title="Détails">
                              <IconButton size="small" onClick={() => setSelectedClient(client)}>
                                <VisibilityIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Modifier">
                              <IconButton size="small" onClick={() => setEditClient(client)}>
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Édition rapide">
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
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded shadow-lg p-8 w-[90vw] max-w-5xl max-h-[80vh] flex flex-col relative overflow-hidden">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-blue-700 text-xl"
              onClick={() => setSelectedClient(null)}
            >
              ×
            </button>
            <h2 className="text-2xl font-bold text-blue-800 mb-4">Détails client</h2>
            <div className="flex flex-1 space-x-6 overflow-hidden">
              {/* Partie gauche : détails client */}
              <div className="w-1/2 space-y-2 overflow-y-auto">
                <div><b>ID SAP:</b> {selectedClient.sap_id}</div>
                <div><b>Nom:</b> {selectedClient.nom_client}</div>
                <div><b>Téléphone:</b> {selectedClient.telephone}</div>
                <div><b>Région:</b> {selectedClient.region || <span className="text-gray-400">—</span>}</div>
                <div><b>Ville:</b> {selectedClient.ville || <span className="text-gray-400">—</span>}</div>
                <div><b>Langue:</b> {selectedClient.langue}</div>
                <div><b>Statut:</b> <Chip label={selectedClient.statut_general} size="small" color={statutColor(selectedClient.statut_general)} /></div>
                <div><b>Notification client:</b> {selectedClient.notification_client ? "Oui" : "Non"}</div>
                <div><b>Date notification:</b> {selectedClient.date_notification || <span className="text-gray-400">—</span>}</div>
                <div><b>A demandé aide:</b> {selectedClient.a_demande_aide ? `Oui (${selectedClient.nature_aide || ''})` : "Non"}</div>
                <div><b>App installée:</b> {selectedClient.app_installee === false ? "Non" : selectedClient.app_installee === true ? "Oui" : <span className="text-gray-400">—</span>}</div>
                <div><b>MàJ app:</b> {selectedClient.maj_app || <span className="text-gray-400">—</span>}</div>
                <div><b>Commentaire agent:</b> {selectedClient.commentaire_agent || <span className="text-gray-400">—</span>}</div>
                <div><b>CMD/Jour:</b> {selectedClient.segment_client || <span className="text-gray-400">—</span>}</div>
                <div><b>Canal contact:</b> {selectedClient.canal_contact || <span className="text-gray-400">—</span>}</div>
                <div><b>Relance planifiée:</b> {selectedClient.relance_planifiee ? "Oui" : "Non"}</div>
              </div>
              {/* Partie droite : historique */}
              <div className="w-1/2 space-y-2 overflow-y-auto">
                <h3 className="text-xl font-semibold mb-2">Historique des changements</h3>
                {auditLogs.length === 0 ? (
                  <div className="text-gray-500">Aucun historique disponible.</div>
                ) : (
                  <ul className="list-disc list-inside max-h-64 overflow-auto">
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
            </div>
          </div>
        </div>
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
        />
      )}
    </main>
  );
}

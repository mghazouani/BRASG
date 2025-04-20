"use client";

import * as React from "react";
import { useEffect, useState, useMemo } from "react";
import { api } from "@/utils/api";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import Tooltip from "@mui/material/Tooltip";
import HelpIcon from "@mui/icons-material/Help";
import SmartphoneIcon from "@mui/icons-material/Smartphone";
import IconButton from "@mui/material/IconButton";
import InfoIcon from "@mui/icons-material/InfoOutlined";
import EditIcon from "@mui/icons-material/EditOutlined";
import SaveIcon from "@mui/icons-material/CheckCircleOutline";
import CancelIcon from "@mui/icons-material/CancelOutlined";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import ClientFilters from "./ClientFilters";
import ClientEditForm from "./ClientEditForm";
import UserInfo from "../components/UserInfo";
import UserMenu from "../components/UserMenu";
import ThemeToggle from "../components/ThemeToggle";
import PaginationBar from "../components/PaginationBar"; // Import PaginationBar
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import Autocomplete from "@mui/material/Autocomplete";

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

  // Chargement dynamique des paramètres du Dashboard
  const [dashboardSettings, setDashboardSettings] = useState<{
    statut_general: { value: string; label: string }[];
    langue: { value: string; label: string }[];
    notification_client: { value: boolean; label: string }[];
    a_demande_aide: { value: boolean; label: string }[];
    app_installee: { value: boolean; label: string }[];
    maj_app: string;
  }>({
    statut_general: [],
    langue: [],
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
        setClients(res.data.results);
        setTotalClients(res.data.count || 0);
        setTotalPages(Math.ceil((res.data.count || 1) / perPage));
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

    } catch (err: any) {
      console.error("Inline edit error:", err.response?.data);
      setInlineEditError(JSON.stringify(err.response?.data) || "Erreur lors de la modification");
    } finally {
      setInlineEditLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center p-8 transition-colors duration-300" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
      <div className="flex justify-between items-center w-full mb-6 fade-in">
        <div className="flex items-center gap-4">
          <UserMenu />
          <h1 className="text-3xl font-bold text-blue-800 dark:text-blue-200">Suivi des clients</h1>
          <UserInfo />
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
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
                    <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('nom_client')}>
                      Nom {ordering === 'nom_client' ? '▲' : ordering === '-nom_client' ? '▼' : ''}
                    </th>
                    <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('statut_general')}>
                      Statut {ordering === 'statut_general' ? '▲' : ordering === '-statut_general' ? '▼' : ''}
                    </th>
                    <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('telephone')}>
                      Téléphone {ordering === 'telephone' ? '▲' : ordering === '-telephone' ? '▼' : ''}
                    </th>
                    <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('region')}>
                      Région {ordering === 'region' ? '▲' : ordering === '-region' ? '▼' : ''}
                    </th>
                    <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('ville')}>
                      Ville {ordering === 'ville' ? '▲' : ordering === '-ville' ? '▼' : ''}
                    </th>
                    <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('langue')}>
                      Langue {ordering === 'langue' ? '▲' : ordering === '-langue' ? '▼' : ''}
                    </th>
                    <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('a_demande_aide')}>
                      Aide {ordering === 'a_demande_aide' ? '▲' : ordering === '-a_demande_aide' ? '▼' : ''}
                    </th>
                    <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('app_installee')}>
                      App {ordering === 'app_installee' ? '▲' : ordering === '-app_installee' ? '▼' : ''}
                    </th>
                    <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('commentaire_agent')}>
                      Commentaire {ordering === 'commentaire_agent' ? '▲' : ordering === '-commentaire_agent' ? '▼' : ''}
                    </th>
                    <th className="p-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {clients.map((client) => (
                    <tr key={client.id} className="border-b hover:bg-blue-50">
                      {/* NOM */}
                      <td className="p-2 font-semibold text-blue-700">
                        {inlineEditId === client.id ? (
                          <TextField size="small" value={inlineEditData.nom_client || ''} onChange={e => setInlineEditData(d => ({ ...d, nom_client: e.target.value }))} />
                        ) : client.nom_client}
                      </td>
                      {/* STATUT */}
                      <td className="p-2">
                        {inlineEditId === client.id ? (
                          <TextField
                            size="small"
                            select
                            value={inlineEditData.statut_general || ''}
                            onChange={e => setInlineEditData(d => ({ ...d, statut_general: e.target.value }))}
                          >
                            {statutChoices.map(opt => (
                              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                            ))}
                          </TextField>
                        ) : (
                          <Chip label={client.statut_general} size="small" color={statutColor(client.statut_general)} />
                        )}
                      </td>
                      {/* TELEPHONE */}
                      <td className="p-2">
                        {inlineEditId === client.id ? (
                          <TextField size="small" value={inlineEditData.telephone || ''} onChange={e => setInlineEditData(d => ({ ...d, telephone: e.target.value }))} />
                        ) : client.telephone}
                      </td>
                      {/* REGION */}
                      <td className="p-2">
                        {inlineEditId === client.id ? (
                          <TextField size="small" value={inlineEditData.region || ''} disabled />
                        ) : (client.region || <span className="text-gray-400">—</span>)}
                      </td>
                      {/* VILLE */}
                      <td className="p-2">
                        {inlineEditId === client.id ? (
                          <Autocomplete
                            freeSolo openOnFocus autoHighlight
                            ListboxProps={{ style: { maxHeight: '20rem' } }}
                            options={villes.map(v => v.nom)}
                            value={inlineEditData.ville || ''}
                            size="small"
                            onChange={(_, value) => {
                              const sel = villes.find(v => v.nom === value);
                              setInlineEditData(d => ({ ...d, ville: value || '', region: sel?.region || '' }));
                            }}
                            onInputChange={(_, value) => setInlineEditData(d => ({ ...d, ville: value }))}
                            onBlur={() => {
                              const sel = villes.find(v => v.nom === inlineEditData.ville);
                              if (sel) setInlineEditData(d => ({ ...d, region: sel.region }));
                            }}
                            renderInput={(params) => <TextField {...params} size="small" />}
                          />
                        ) : (client.ville || <span className="text-gray-400">—</span>)}
                      </td>
                      {/* LANGUE */}
                      <td className="p-2 capitalize">
                        {inlineEditId === client.id ? (
                          <TextField
                            size="small"
                            select
                            value={inlineEditData.langue || ''}
                            onChange={e => setInlineEditData(d => ({ ...d, langue: e.target.value }))}
                            className="capitalize"
                          >
                            {langueChoices.map(opt => (
                              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                            ))}
                          </TextField>
                        ) : client.langue}
                      </td>
                      {/* AIDE */}
                      <td className="p-2">
                        {inlineEditId === client.id ? (
                          <FormControl component="fieldset" className="flex">
                            <RadioGroup row name="a_demande_aide" value={`${inlineEditData.a_demande_aide}`} onChange={e => setInlineEditData(d => ({ ...d, a_demande_aide: e.target.value === 'true' }))}>
                              {aideChoices.map(opt => (
                                <FormControlLabel key={`${opt.value}`} value={`${opt.value}`} control={<Radio size="small" />} label={opt.label} />
                              ))}
                            </RadioGroup>
                          </FormControl>
                        ) : client.a_demande_aide && (
                          <Tooltip title={client.nature_aide || "Aide demandée"}>
                            <HelpIcon color="warning" />
                          </Tooltip>
                        )}
                      </td>
                      {/* APP */}
                      <td className="p-2">
                        {inlineEditId === client.id ? (
                          <FormControl component="fieldset" className="flex">
                            <RadioGroup row name="app_installee" value={`${inlineEditData.app_installee}`} onChange={e => setInlineEditData(d => ({ ...d, app_installee: e.target.value === 'true' }))}>
                              {appChoices.map(opt => (
                                <FormControlLabel key={`${opt.value}`} value={`${opt.value}`} control={<Radio size="small" />} label={opt.label} />
                              ))}
                            </RadioGroup>
                          </FormControl>
                        ) : client.app_installee === false ? (
                          <Tooltip title="Application non installée">
                            <SmartphoneIcon color="error" />
                          </Tooltip>
                        ) : client.maj_app && client.maj_app.toLowerCase() !== "à jour" ? (
                          <Tooltip title={`App non à jour (${client.maj_app})`}>
                            <SmartphoneIcon color="warning" />
                          </Tooltip>
                        ) : (
                          <span className="text-green-600">✔</span>
                        )}
                      </td>
                      {/* COMMENTAIRE AGENT */}
                      <td className="p-2 max-w-xs truncate">
                        {inlineEditId === client.id ? (
                          <TextField size="small" value={inlineEditData.commentaire_agent || ''} onChange={e => setInlineEditData(d => ({ ...d, commentaire_agent: e.target.value }))} />
                        ) : client.commentaire_agent ? (
                          <Tooltip title={client.commentaire_agent}>
                            <span>{client.commentaire_agent.slice(0, 20)}{client.commentaire_agent.length > 20 ? "..." : ""}</span>
                          </Tooltip>
                        ) : (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                      {/* ACTIONS */}
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
                                <InfoIcon fontSize="small" />
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
          <div className="bg-white rounded shadow-lg p-8 max-w-lg w-full relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-blue-700 text-xl"
              onClick={() => setSelectedClient(null)}
            >
              ×
            </button>
            <h2 className="text-2xl font-bold text-blue-800 mb-4">Détails client</h2>
            <div className="space-y-2">
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
              <div><b>Segment client:</b> {selectedClient.segment_client || <span className="text-gray-400">—</span>}</div>
              <div><b>Canal contact:</b> {selectedClient.canal_contact || <span className="text-gray-400">—</span>}</div>
              <div><b>Relance planifiée:</b> {selectedClient.relance_planifiee ? "Oui" : "Non"}</div>
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

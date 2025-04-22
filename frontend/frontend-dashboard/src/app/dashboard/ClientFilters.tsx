import * as React from "react";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import InputAdornment from "@mui/material/InputAdornment";
import SearchIcon from "@mui/icons-material/Search";

export interface ClientFiltersProps {
  search: string;
  onSearch: (val: string) => void;
  statut: string;
  onStatut: (val: string) => void;
  langue: string;
  onLangue: (val: string) => void;
  langues: { value: string; label: string }[];
  aide: string;
  onAide: (val: string) => void;
  aideOptions: { value: boolean; label: string }[];
  app: string;
  onApp: (val: string) => void;
  appOptions: { value: boolean; label: string }[];
}

export default function ClientFilters({ search, onSearch, statut, onStatut, langue, onLangue, langues, aide, onAide, aideOptions, app, onApp, appOptions }: ClientFiltersProps) {
  return (
    <div className="flex flex-wrap gap-4 mb-4 items-end">
      <TextField
        label="Recherche"
        size="small"
        value={search}
        onChange={e => onSearch(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon fontSize="small" />
            </InputAdornment>
          ),
        }}
        className="w-48"
      />
      <TextField
        label="Statut"
        size="small"
        select
        value={statut}
        onChange={e => onStatut(e.target.value)}
        className="w-40"
      >
        <MenuItem value="">Tous</MenuItem>
        <MenuItem value="actif">Actif</MenuItem>
        <MenuItem value="inactif">Inactif</MenuItem>
        <MenuItem value="bloque">Bloqué</MenuItem>
      </TextField>
      <TextField
        label="App installée"
        size="small"
        select
        value={app}
        onChange={e => onApp(e.target.value)}
        className="w-40"
      >
        <MenuItem value="">Toutes</MenuItem>
        {appOptions.map(opt => (
          <MenuItem key={opt.value.toString()} value={`${opt.value}`}>{opt.label}</MenuItem>
        ))}
      </TextField>
      <TextField
        label="Aide demandée"
        size="small"
        select
        value={aide}
        onChange={e => onAide(e.target.value)}
        className="w-40"
      >
        <MenuItem value="">Toutes</MenuItem>
        {aideOptions.map(opt => (
          <MenuItem key={opt.value.toString()} value={`${opt.value}`}>{opt.label}</MenuItem>
        ))}
      </TextField>
      <TextField
        label="Langue"
        size="small"
        select
        value={langue}
        onChange={e => onLangue(e.target.value)}
        className="w-40"
      >
        <MenuItem value="">Toutes</MenuItem>
        {langues.map(opt => (
          <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
        ))}
      </TextField>
    </div>
  );
}

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
  region: string;
  onRegion: (val: string) => void;
  regions: string[];
}

export default function ClientFilters({ search, onSearch, statut, onStatut, region, onRegion, regions }: ClientFiltersProps) {
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
        className="w-36"
      >
        <MenuItem value="">Tous</MenuItem>
        <MenuItem value="actif">Actif</MenuItem>
        <MenuItem value="inactif">Inactif</MenuItem>
        <MenuItem value="bloque">Bloqué</MenuItem>
      </TextField>
      <TextField
        label="Région"
        size="small"
        select
        value={region}
        onChange={e => onRegion(e.target.value)}
        className="w-36"
      >
        <MenuItem value="">Toutes</MenuItem>
        {regions.map(r => (
          <MenuItem key={r} value={r}>{r}</MenuItem>
        ))}
      </TextField>
    </div>
  );
}

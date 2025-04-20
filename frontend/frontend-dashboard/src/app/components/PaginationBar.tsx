"use client";
import Pagination from "@mui/material/Pagination";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";

interface PaginationBarProps {
  page: number;
  count: number;
  onChange: (event: React.ChangeEvent<unknown>, value: number) => void;
  perPage: number;
  onPerPageChange: (value: number) => void;
}

export default function PaginationBar({ page, count, onChange, perPage, onPerPageChange }: PaginationBarProps) {
  return (
    <Stack direction="row" spacing={2} alignItems="center" className="my-6">
      <Pagination
        count={count}
        page={page}
        onChange={onChange}
        color="primary"
        shape="rounded"
        size="large"
        showFirstButton
        showLastButton
      />
      <TextField
        select
        size="small"
        label="Lignes/page"
        value={perPage}
        onChange={e => onPerPageChange(Number(e.target.value))}
        style={{ minWidth: 110 }}
        SelectProps={{ native: true }}
      >
        {[5, 10, 20, 50, 100].map(opt => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </TextField>
    </Stack>
  );
}

import * as React from "react";
import Button from "@mui/material/Button";
import Avatar from "@mui/material/Avatar";
import Stack from "@mui/material/Stack";
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/kpi");
  return null;
}

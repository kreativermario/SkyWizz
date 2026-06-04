import { execFileSync } from "node:child_process";

execFileSync(
  "node_modules/.bin/prisma",
  ["db", "push", "--skip-generate", "--accept-data-loss"],
  { stdio: "inherit", env: process.env }
);

await import("./index.js");

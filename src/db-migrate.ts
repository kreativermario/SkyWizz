import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const prismaCli = require.resolve("prisma/build/index.js");

execFileSync(process.execPath, [prismaCli, "db", "push", "--accept-data-loss"], {
  stdio: "inherit",
  env: { PATH: process.env.PATH, DATABASE_URL: process.env.DATABASE_URL },
});

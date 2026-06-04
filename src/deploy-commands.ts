import "dotenv/config";
import { registerCommands } from "./register-commands.js";

registerCommands().catch(console.error);

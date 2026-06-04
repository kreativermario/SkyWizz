# guacamoleninja-bot

A Discord bot built with discord.js v14, TypeScript, Node.js 24, and PostgreSQL via Prisma 7.

## Requirements

- [Node.js 24](https://nodejs.org/)
- [pnpm](https://pnpm.io/)
- [Docker](https://www.docker.com/) + Docker Compose

## Local Development

1. Clone the repository:

   ```bash
   git clone https://github.com/guacamoleninja/guacamoleninja-bot.git
   cd guacamoleninja-bot
   ```

2. Copy the example environment file and fill in your values:

   ```bash
   cp .env.example .env
   ```

3. Start the bot and database locally:

   ```bash
   docker compose -f docker-compose.local.yml up
   ```

## Commands

| Command | Description |
|---|---|
| `/uptime` | Shows how long the bot has been running |
| `/server` | Displays information about the current server |
| `/config view` | View the current server configuration |
| `/config set` | Update a server configuration value |

## Deployment

Deployment is handled automatically via GitHub Actions on every push to the `dev` branch. The pipeline:

1. Pulls secrets from HashiCorp Vault (Harbor registry credentials, bot token, database credentials)
2. Builds and pushes a Docker image to the Harbor registry
3. Deploys or updates the stack in Portainer via its API

## License

This project is licensed under the [MIT License](LICENSE).

# Contribution Standards

Don't be afraid to contribute to guacamoleninja-bot! Even small contributions are greatly appreciated.

Please make sure you abide by these contribution standards so we can retain a high quality codebase and make it easy for everyone to understand and contribute to the code.

* Follow all coding standards set by existing code in the repo. Using your own preferences over the established ones for the project just ends up making the code messy.
* Use commits following our guidelines [here](#commit-messages).
* An explanation of what the commit's changes do in your commit message is extremely useful. It helps people to more quickly understand what your code is doing.
* When you submit a pull request, be willing to accept criticism. We don't criticise to make you feel bad — we want you to know where you may have made a mistake and this helps you grow as a developer.

## How to Start Contributing

1. Fork the repository to your own GitHub account.
2. Clone the project to your local machine.
3. Create a branch locally with a succinct but descriptive name.
4. Install dependencies:

   ```bash
   pnpm install
   ```

5. Work on the feature or bug.
6. Commit changes in small, incremental steps.
7. Push your branch to your forked repository.
8. Make a pull request from your forked repository to the main repository.
9. Have a discussion with the maintainers about the changes.

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for our commit messages, which provides a standardized format for describing the changes made in a commit.

A commit message should have the following format:

```
type(scope): subject
```

- **type**: The type of change being made (e.g. `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`).
- **scope** (optional): The scope of the change (e.g. filename, module, command name).
- **subject**: A brief description of the change.
- **body** (optional): A more detailed description of the change.
- **footer** (optional): A section for any related issue numbers or breaking changes.

Examples:

```
feat(commands): add /weather slash command
```

```
fix(config): resolve issue with config set not persisting
```

```
docs: update README with local dev instructions
```

## Code Style

We use [ESLint](https://eslint.org/) and [TypeScript](https://www.typescriptlang.org/) for code style and type safety. Please ensure your code passes linting before submitting a PR:

```bash
pnpm lint
```

All new code should be written in TypeScript. Avoid using `any` types; prefer explicit types or generics.

## Documentation

We use [TSDoc](https://tsdoc.org/) style for inline documentation.

Example:

```typescript
/**
 * Returns the uptime of the bot in a human-readable format.
 *
 * @param uptimeMs - The bot uptime in milliseconds.
 * @returns A formatted string representing the uptime.
 */
function formatUptime(uptimeMs: number): string {
  // ...
}
```

# Filing an Issue

We always encourage users to report bugs as soon as they experience them. In order to keep everything organized, here are some questions you should ask yourself before reporting:

## Common Mistakes

* Have you copied `.env.example` to `.env` and filled in all required values?
* Have you run `pnpm install` to install all dependencies?
* Are Docker and Docker Compose running correctly?

## General Issues

* Are you using the latest version of guacamoleninja-bot?
* Has this issue been reported already? Please check the [list of open issues](https://github.com/guacamoleninja/guacamoleninja-bot/issues).

## Advice

If you're sure you've followed all instructions and haven't made any of the common mistakes listed above, here are some guidelines for creating an issue:

* Is this an issue with the bot itself, or are you looking for help with your own setup? The issues page is for bot issues only. Try the [GitHub Discussions tab](https://github.com/guacamoleninja/guacamoleninja-bot/discussions).
* When you ask a question, make sure it's not [an XY problem](http://xyproblem.info/).
* Provide as much information as you possibly can.
* Issues are formatted by [Markdown](https://guides.github.com/features/mastering-markdown/). Enclose blocks of code with three backticks (\`\`\`) to make them render as code blocks.

## In Your Issue, Please:

* List all operating system names and versions involved in the issue, as well as your Node.js version and IDE.
* List any other software name/version you think may be related.
* Include any error messages you see.
* List steps to reproduce.

The more information you have, the better. Post as much as you can related to the issue to help us resolve it in a timely manner. If you have multiple issues, please file them as separate issues.

Don't ask a question not related to the topic of the current issue, especially if it's on someone else's issue. This is known as [thread hijacking](http://www.urbandictionary.com/define.php?term=Thread+Hijacking). Create a new issue or ask in Discussions instead.

Thanks!

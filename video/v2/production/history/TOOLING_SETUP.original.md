# Tooling setup for the future tool-assisted V2

Prepared: 14 September 2026. Scope: backup, handoff, installation inspection and minimal tool checks.
**No V2 redesign, application recording, slide production, Remotion project or media render was made.**

## Current status: desktop installation confirmed

On 14 September 2026, after the user manually installed both plugins in the desktop Plugins
page, account metadata confirmed `source_plugin_installed: true` and
`source_plugin_user_enabled: true` for both plugins. Dependencies and unresolved apps are empty.
Evidence: `tooling-evidence/desktop-account-installed-confirmed.json`.

- Build Web Data Visualization: desktop package **0.1.21**. Its router is now exposed in the
  current session's skill catalog. All 18 bundled SKILL.md files exist and are readable; this
  is not a claim that all specialist routes have executed successfully.
- Remotion: desktop package **1.0.7**, authored by Remotion. All 12 bundled skills are now
  exposed in the current session's skill catalog and their files are readable.
- The earlier local CLI packages remain on disk, with CLI enablement unchanged. The current
  session exposes the desktop `openai-curated-remote` skills, with no duplicate entries for
  these plugin skill names observed. This does not prove every future CLI session will deduplicate.
  Use the desktop package paths below for subsequent work; do not copy or merge standalone skills.
- Installation and discovery are verified. Visualization execution and Remotion rendering remain
  untested; no V2 design, recording or render was performed. No additional restart is needed merely
  to establish discovery in this session, because the skills already appear in its catalog.

### Historical correction

Before the user's manual installation, both account installation flags were false even though
local CLI installation succeeded. The previous unqualified installation claim was incorrect.
`desktop-account-installation-recheck.json` records that earlier state; it is historical evidence,
not the current status. The CLI commands and older package versions recorded below are retained
as an accurate history of preparation, not the versions selected for future desktop production.

## 1. Installation, discovery and test results are different

- **Locally installed (CLI):** files and local enablement configuration exist; this does not prove desktop/account installation.
- **Desktop/account installed:** the account metadata confirms installation. Both requested plugins now pass this check.
- **Discoverable:** the current agent's skill catalog or the CLI marketplace lists the component.
  Being in a marketplace is not being installed; being installed is not proof of fresh-session skill loading.
- **Successfully tested:** only the specific checks below passed. No media-production acceptance is implied.

| Component | Before preparation | Verified installation state | Discovery | Successfully tested now / deferred |
| --- | --- | --- | --- | --- |
| Build Web Data Visualization | Available in the configured OpenAI catalog, not installed | **Desktop/account installed and enabled**, 0.1.21; 18 bundled skills. Older CLI copy retained | Desktop router exposed in the current session; all 18 skill files readable | Account status, manifest and file readability verified; specialist execution and visualization output deferred |
| Presentations | Already installed and in this session's catalog | Reused unchanged; plugin 26.904.11930; `@oai/artifact-tool` 2.8.59 | Initial skill catalog and CLI both identify it | JavaScript import verified `Presentation` and `PresentationFile` exports. No deck created, rendered or exported; those checks deferred |
| Playwright | Existing user skill, wrapper, cached CLI and Chrome | Reused unchanged; CLI 0.1.19; its Playwright dependency 1.63.0-alpha-2026-08-31 | Skill available now; cached CLI reports version/help | Opened `about:blank` in headless Chrome, read readyState/URL/userAgent, closed only the owned session. No app visited or recorded; app capture acceptance deferred |
| Remotion vendor plugin | Available in configured OpenAI catalog, not installed | **Desktop/account installed and enabled**, 1.0.7; 12 skills. Older CLI 1.0.3 copy retained | All 12 desktop skills exposed in the current session and readable | Account status, manifest and skill discovery verified. Studio, SDK, renderer, video import/export and caption composition not tested |

Remotion's locally installed CLI catalog package is **not the current vendor-head version**. The current vendor
repository manifest returned 4.0.524, while the local official catalog snapshot supplies 1.0.3.
Current vendor docs describe a broader skill collection. This preparation preserves that distinction
instead of claiming the old bundle includes every newly documented skill. No duplicate standalone
`remotion-dev/skills` installation was made. The user subsequently installed desktop Remotion 1.0.7 with 12 skills from the official directory.
Use that verified desktop bundle; do not manually merge skill copies or equate catalog and vendor-head versions.

## 2. Sources and supported installation routes

Sources were checked from official documentation, vendor-maintained repositories and the local CLI
on 14 September 2026. Third-party directory search hits were not used as installation authority.

| Component | Supported route established | Route used here |
| --- | --- | --- |
| Codex plugins | Official docs describe Plugins directory installation and fresh chats for bundled skills; local `codex plugin --help` exposes `add` and marketplace commands | Existing configured catalog and native CLI `plugin add`; no marketplace replacement |
| Build Web Data Visualization | OpenAI repository manifest declares the plugin and `./skills/`; local official catalog contains it with installation AVAILABLE | `codex plugin add build-web-data-visualization@openai-curated` |
| Presentations | Bundled primary runtime exposes its plugin and skill locally; the app provides dependency locations | Reused installed bundle; did not search npm for a similarly named substitute |
| Playwright | Microsoft maintains `@playwright/cli`; existing Codex skill documents the npx wrapper route | Used existing cached CLI with node, so no new npm download, global install or duplicate skill |
| Remotion | Vendor documents the Codex plugin in the app's Plugins tab; vendor repository identifies the plugin and bundled skills. Standalone `npx skills add remotion-dev/skills` is an alternative, not an additional requirement | Native CLI installed the vendor-authored Remotion entry from the existing OpenAI catalog. No standalone skills added |

Primary references:

- [OpenAI plugins documentation](https://learn.chatgpt.com/docs/plugins): installation and fresh-session discovery.
- [OpenAI visualization manifest](https://github.com/openai/plugins/blob/main/plugins/build-web-data-visualization/.codex-plugin/plugin.json).
- [Microsoft Playwright CLI](https://github.com/microsoft/playwright-cli): package installation and agent-oriented CLI.
- [Playwright installation documentation](https://playwright.dev/docs/intro): runtime/platform requirements and version checks.
- [Remotion Codex plugin](https://www.remotion.dev/docs/ai/codex-plugin): vendor-supported app installation route.
- [Remotion Agent Skills](https://www.remotion.dev/docs/ai/skills): alternative standalone route and current skill descriptions.
- [Vendor-maintained Codex plugin repository](https://github.com/remotion-dev/codex-plugin).
- [Current vendor manifest](https://github.com/remotion-dev/codex-plugin/blob/main/.codex-plugin/plugin.json): version 4.0.524 at inspection.
- [Remotion licensing reference](https://www.remotion.dev/docs/license): runtime/commercial terms are separate from the installed MIT skill bundle.

The older installed Remotion README refers to `remotion-dev/remotion/packages/codex-plugin` as its
source/mirror relationship. Current raw fetches at that monorepo path returned 404. The current
vendor `remotion-dev/codex-plugin` repository and official plugin documentation were reachable.
This provenance/version drift is recorded rather than silently treating all sources as identical.

## 3. Exact installed locations

Authoritative desktop packages for subsequent work:

- `/Users/wantedtina/.codex/plugins/cache/openai-curated-remote/build-web-data-visualization/0.1.21/`
- `/Users/wantedtina/.codex/plugins/cache/openai-curated-remote/remotion/1.0.7/`

The `openai-curated` paths in the historical inventory below refer to the earlier CLI copies.

| Item | Path |
| --- | --- |
| Build Web Data Visualization plugin | `/Users/wantedtina/.codex/plugins/cache/openai-curated/build-web-data-visualization/2f1a8948/` |
| Visualization router | `/Users/wantedtina/.codex/plugins/cache/openai-curated/build-web-data-visualization/2f1a8948/skills/data-visualization/SKILL.md` |
| Remotion plugin | `/Users/wantedtina/.codex/plugins/cache/openai-curated/remotion/2f1a8948/` |
| Remotion included skill | `/Users/wantedtina/.codex/plugins/cache/openai-curated/remotion/2f1a8948/skills/remotion/SKILL.md` (frontmatter name `remotion-best-practices`) |
| Remotion rules | `/Users/wantedtina/.codex/plugins/cache/openai-curated/remotion/2f1a8948/skills/remotion/rules/` |
| Presentations skill | `/Users/wantedtina/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations/SKILL.md` |
| Artifact Tool | `/Users/wantedtina/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/` |
| Playwright skill | `/Users/wantedtina/.codex/skills/playwright/SKILL.md` |
| Playwright wrapper | `/Users/wantedtina/.codex/skills/playwright/scripts/playwright_cli.sh` |
| Reused cached Playwright CLI | `/Users/wantedtina/.npm/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js` |
| Cached Playwright library | `/Users/wantedtina/.npm/_npx/31e32ef8478fbf80/node_modules/playwright/` |
| Codex executable | `/opt/homebrew/bin/codex` (0.133.0) |
| Shared plugin configuration | `/Users/wantedtina/.codex/config.toml` |
| Future isolated production directory | `/Users/wantedtina/Deliverables/architecture-governance-copilot/tool-assisted-v2-preparation/production-environment/` |
| Check scripts / local browser scratch | `/Users/wantedtina/Deliverables/architecture-governance-copilot/tool-assisted-v2-preparation/checks/` |
| Installation and verification evidence | `/Users/wantedtina/Deliverables/architecture-governance-copilot/tool-assisted-v2-preparation/tooling-evidence/` |

Other runtime observations: Node v24.14.0, npm 11.9.0, uv 0.11.15, macOS 26.6.2,
HeadlessChrome/152.0.0.0 in the blank-page smoke check. The existing Playwright dependency is a
prerelease; it was not upgraded or replaced under an install-only-missing request. Cache paths are
machine-local and may be cleaned; re-resolve before future use rather than assuming portability.

## 4. Commands executed and configuration changes

The accepted V1 backup completed and passed SHA-256 comparison before either install command.
The current application repository and V1 directories received no production-tool dependency writes.

Read-only inspection included:

```sh
codex --version
codex plugin --help
codex plugin marketplace list
codex plugin list
codex plugin add --help
codex plugin marketplace add --help
node --version
npm --version
```

These commands installed local CLI packages only; they did not complete desktop/account installation:

```sh
codex plugin add build-web-data-visualization@openai-curated
codex plugin add remotion@openai-curated
```

Both returned exit 0 and an installed cache root. The CLI changed plugin enablement in
`/Users/wantedtina/.codex/config.toml`:

```toml
[plugins."build-web-data-visualization@openai-curated"]
enabled = true

[plugins."remotion@openai-curated"]
enabled = true
```

The selected plugin configuration before/after is preserved in `tooling-evidence/plugin-config-before.toml`
and `plugin-config-after.toml`. Unrelated settings and secrets were not printed or copied into handoff files.
No marketplace was added/upgraded, no CLI/app upgrade occurred, and no existing plugin was removed.

Presentations test, run from the external preparation directory:

```sh
node checks/presentation-import.mjs
```

Playwright check used the existing package without running the floating npx installer:

```sh
node /Users/wantedtina/.npm/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js --version
node /Users/wantedtina/.npm/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js --session=agc-tool-prep open about:blank --browser chrome
node /Users/wantedtina/.npm/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js --session=agc-tool-prep eval '() => ({url: location.href, userAgent: navigator.userAgent, readyState: document.readyState})'
node /Users/wantedtina/.npm/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js --session=agc-tool-prep close
```

The owned session was closed. No existing capture session or personal browser was closed. The
minimal page snapshot is in the external checks scratch directory, not the application repository.

## 5. Scope, dependencies and permission boundaries

- Plugins are user-level skill bundles; future production npm packages and generated artifacts belong
  in the external production-environment directory. V1 and its backup must remain read-only inputs.
- No `package.json`, node_modules, lockfile or application `.venv` was changed. No additional skills
  were copied into `.agents/skills`, `.codex/skills` or the application repository.
- Remotion plugin skill installation does not install the Remotion SDK, renderer, Studio or React project.
  These were not required for the preparation-only checks and were not installed. Do not describe
  Remotion rendering as successfully tested or assume its runtime licensing is already settled.
- Both installed manifests declare MIT and contain skills, with no `.mcp.json`. The catalog Remotion
  entry has authentication policy ON_INSTALL, but the actual local CLI operation performed no account
  connection or OAuth flow and presented no license acceptance. Do not infer an authenticated account.
- No paid service, ElevenLabs voice API, cloud render, stock-media purchase, account authorization or
  separate license acceptance was performed. Ask the user before any such step becomes necessary.
- No draw.io was installed. Editable SVG already exists; no `.drawio` output was requested.
- No mobile concept generation, template selection, V2 composition, new screenshot/video capture,
  scene render, application acceptance run or content redesign was performed.

## 6. New-session checks and manual steps

These are deferred checks, not authorization to start V2 production.

1. Desktop installation and current-session skill discovery are complete. A later session should
   still read VIDEO_HANDOFF.md and confirm these desktop packages remain enabled.
2. Exercise only the visualization specialist routes needed after V2 is authorized. All 18 files are
   readable, but only the router is listed in the current catalog. No loader rejection was observed;
   do not infer a failure merely from specialist entries not appearing separately.
3. Use desktop Remotion 1.0.7 with its 12 exposed skills. Local CLI 1.0.3 is historical. No duplicate
   skill names are exposed in this session. Check routing in the intended production session and
   avoid mixing packages. Existing local copies have not been uninstalled or silently modified.
4. Remotion SDK/Studio installation, runtime license eligibility/acceptance and a pinned isolated
   package/lockfile need resolution before actual production. Ask before paid services, account
   authorization or license acceptance. No account details are needed for the completed preparation.
5. After a later user instruction authorizes V2, verify the unchanged V1 hash and current app revision.
   Review any proposed changes against the preserve/open-to-improvement distinction in VIDEO_HANDOFF.md.
6. App capture, deck import/export, typography, video/caption synchronization, runtime playback and
   final render checks remain deferred. A blank-browser/module-import check is not end-to-end validation.

No restart was forced, no new user-owned task was created, and there is no unattended render or
future scheduled action. Preparation stops here.

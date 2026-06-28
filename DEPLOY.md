# Deploying Pessoi → pessoi.com

Pessoi is a **static** site (no build). The deployable site is `web/`:
`web/index.html` (landing), `web/play.html` (the game, served at `/play`),
`vercel.json` (cleanUrls), `favicon.svg`.

Same pattern as Hoshi (`~/wrootgames/hoshi/web`). Deploy from the CLI — no
GitHub remote needed, and CLI deploys don't trip the commit-author gate.

## First deploy (creates the Vercel project)
```sh
cd ~/wrootgames/pessoi/web
npx vercel            # answer the prompts:
#   Set up and deploy “…/pessoi/web”?  yes
#   Which scope?                       <your Wroot Labs team>   (Hoshi lives here: team_sERwO8GidBZdsL7F1I6fcgAW)
#   Link to existing project?          no
#   Project name?                      pessoi
#   In which directory is your code?   ./        (you are already in web/)
#   Modify settings?                   no
```
Preview URL prints. Eyeball it, then ship production:
```sh
npx vercel --prod
```

## Point pessoi.com at it  (protected — your call)
Dashboard is easiest: **Project → Settings → Domains → Add `pessoi.com`**
(add `www.pessoi.com` too; set it to redirect to the apex). Vercel then shows
the exact DNS records. At pessoi.com's registrar, set what Vercel shows —
typically:
- `A`  `@`  → `76.76.21.21`
- `CNAME` `www` → `cname.vercel-dns.com`

(If you move pessoi.com onto Vercel's nameservers, Vercel configures the
records itself.)

## Re-deploy after edits
```sh
cd ~/wrootgames/pessoi/web && npx vercel --prod
```

## Notes
- **Bot play is already built in** — the "House" opponent in the game
  (Novice / Raider / Adept / Master + style). Nothing to wire.
- The landing links to `https://games.wrootlabs.com` (the hub) and
  `https://playhoshi.com`. The "Read the reconstruction" button currently
  points at a placeholder `https://github.com/` — set it once the
  scholarship has a home (a GitHub repo, or a rendered page).
- Canonical game source is `web/play.html` (moved here from the old
  `latrones-board.html`).

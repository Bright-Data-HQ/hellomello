# Content sign-off form

An interactive, multi-page version of the educational content pillars
document. The reviewer ticks **Approve / Change / Drop** on each of the 44
topics, adds notes per topic and per section, and submits.

The whole site, including this form, runs on a single **Cloudflare Worker**
(`worker/index.js` at the repo root) that serves the static files and handles
the sign-off API. Config lives in `wrangler.jsonc`.

- **Live URL:** https://hellomello.bright-data.workers.dev
- **Form path:** `/hellomello/strategy/educational-signoff`
- **Read-only document version:** `/hellomello/strategy`

## How it works

- Answers autosave to the reviewer's browser as they go, so they can stop and
  come back.
- On submit, the completed sign-off is stored in **Cloudflare KV** (the
  `SIGNOFF` namespace), the reviewer's mail app opens prefilled with the full
  summary addressed to the team, and a JSON copy downloads as a backup.
- No third-party email service and nothing public: the stored answers are only
  readable with the account token or the admin endpoint below.

## Reading the submissions

Each submission is saved in KV under a `submission:...` key. Two ways to read:

1. **From the command line** (uses the Cloudflare token in `.env.vars`):

       npx wrangler kv key list --namespace-id <SIGNOFF id> --remote
       npx wrangler kv key get  --namespace-id <SIGNOFF id> --remote "submission:..."

2. **Over HTTP**, if you set an `ADMIN_TOKEN` secret on the Worker:

       npx wrangler secret put ADMIN_TOKEN

   then `GET /api/signoff?action=submissions&token=<ADMIN_TOKEN>`. Without the
   secret set, that endpoint is disabled and returns 403.

## Optional settings

- `SIGNOFF_NOTIFY_EMAIL` sets where the prefilled email is addressed. Default
  `vahid@brightdata.com.au`. Set with `npx wrangler secret put SIGNOFF_NOTIFY_EMAIL`.
- `ADMIN_TOKEN` unlocks the submissions list endpoint (see above).

## Deploy

From the repo root, with `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` set
(the token is in `.env.vars`):

       npx wrangler deploy

## Files

- `worker/index.js` is the Cloudflare Worker (static routing plus sign-off API).
- `wrangler.jsonc` is the Worker config and the KV binding.
- `public/.assetsignore` keeps the old Vercel files out of the public site.
- `public/hellomello/strategy/educational-signoff/` is the form (`index.html`,
  `styles.css`, `app.js`).

The old Vercel function (`public/api/signoff.js`) and `public/vercel.json`
remain in the repo for reference but are not served by Cloudflare.

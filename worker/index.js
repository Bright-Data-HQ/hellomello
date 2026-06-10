'use strict';

import { EmailMessage } from 'cloudflare:email';

/*
 * Hellomello site + content sign-off, Cloudflare Worker.
 *
 * One Worker serves the whole static site from the ASSETS binding and handles
 * the sign-off API at /api/signoff. It replaces the Vercel deployment.
 *
 *   GET  /                          -> redirect to /hellomello
 *   GET  /api/signoff?action=state  -> empty draft shape (drafts live in the browser)
 *   POST /api/signoff?action=save   -> autosave acknowledgement (browser keeps the draft)
 *   POST /api/signoff?action=submit -> store the finished sign-off in KV, send an email
 *   GET  /api/signoff?action=submissions -> list stored sign-offs (needs ADMIN_TOKEN)
 *   everything else                 -> static asset
 *
 * The finished sign-off is kept in Cloudflare KV (the SIGNOFF binding). When the
 * SEND_EMAIL binding is configured (Cloudflare Email Workers), the Worker also
 * sends the summary by email. Either way the reviewer's browser opens a
 * prefilled email and downloads a JSON backup, so nothing is ever lost.
 *
 * Optional vars / bindings:
 *   SEND_EMAIL            Email Workers send binding (set in wrangler.jsonc).
 *   SIGNOFF_NOTIFY_EMAIL  Where the email goes. Must be a verified destination.
 *   SIGNOFF_FROM_EMAIL    From address. Must be on the routing-enabled domain.
 *   ADMIN_TOKEN           Secret that unlocks the submissions list endpoint.
 */

const DEFAULT_NOTIFY = 'vahid@brightdata.com.au';
const DEFAULT_FROM = 'signoff@divan.work';

const EMPTY_STATE = {
  meta: { submitterName: '', submittedAt: '', updatedAt: '', version: 1 },
  decisions: {},
  pageNotes: {}
};

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c];
  });
}

// Constant-time string compare so the password check can't be timed.
function safeEqual(a, b) {
  a = String(a || '');
  b = String(b || '');
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

// Derive an opaque cookie token from the password, so the plain password is
// never stored in the browser. Same password always gives the same token, so
// we can check a returning visitor without a server session store.
async function gateToken(password) {
  const data = new TextEncoder().encode('hellomello-gate-v1:' + password);
  const digest = await crypto.subtle.digest('SHA-256', data);
  const bytes = new Uint8Array(digest);
  let hex = '';
  for (let i = 0; i < bytes.length; i++) hex += bytes[i].toString(16).padStart(2, '0');
  return hex;
}

function readCookie(request, name) {
  const header = request.headers.get('cookie') || '';
  const parts = header.split(';');
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i].trim();
    if (p.indexOf(name + '=') === 0) return p.slice(name.length + 1);
  }
  return '';
}

// Has this request already passed the gate?
async function isAuthed(request, env) {
  const password = env.SITE_PASSWORD || '';
  if (!password) return true; // gate disabled until a password is configured
  const want = await gateToken(password);
  const got = readCookie(request, 'hm_gate');
  return safeEqual(got, want);
}

// Keep redirects on this site only.
function safeNext(next) {
  if (typeof next !== 'string') return '/hellomello';
  if (next.indexOf('/') !== 0 || next.indexOf('//') === 0) return '/hellomello';
  return next;
}

// The styled password screen, in the Hellomello brand colours.
function loginPage(next, showError) {
  const err = showError
    ? '<p class="gate-err">That password did not work. Please try again.</p>'
    : '<p class="gate-sub">This area is private. Enter the password to view it.</p>';
  const html = '<!doctype html><html lang="en"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1">' +
    '<meta name="robots" content="noindex, nofollow">' +
    '<title>Hellomello client area</title>' +
    '<style>' +
    ':root{--green:#283718;--terra:#BC6C25;--paper:#FBF6D6;--surface:#FFFFFF;' +
    '--ink:#283718;--muted:#5C6849;--border:#E8E1B8;--border-strong:#CFC68C;' +
    '--bad-fg:#9B2418;--font-display:"League Spartan","Helvetica Neue",system-ui,sans-serif;' +
    '--font-body:"Inter","Helvetica Neue",system-ui,sans-serif}' +
    '@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=League+Spartan:wght@700;900&display=swap");' +
    '*{box-sizing:border-box}html,body{margin:0;height:100%}' +
    'body{font-family:var(--font-body);background:var(--paper);color:var(--ink);' +
    'display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px}' +
    '.gate{width:100%;max-width:420px;background:var(--surface);border:1px solid var(--border-strong);' +
    'border-radius:18px;padding:40px 34px;box-shadow:0 12px 40px rgba(40,55,24,.10)}' +
    '.gate-mark{font-family:var(--font-display);font-weight:900;font-size:26px;letter-spacing:-.02em;margin:0 0 4px}' +
    '.gate-mark .m{color:var(--green)}.gate-mark .a{color:var(--terra)}' +
    '.gate-tag{font-family:var(--font-body);font-size:11px;text-transform:uppercase;letter-spacing:.16em;color:var(--muted);margin:0 0 22px}' +
    'h1{font-family:var(--font-display);font-weight:700;font-size:24px;letter-spacing:-.01em;margin:0 0 6px}' +
    '.gate-sub{font-size:14px;color:var(--muted);margin:0 0 22px;line-height:1.55}' +
    '.gate-err{font-size:14px;color:var(--bad-fg);margin:0 0 22px;line-height:1.55}' +
    'label{display:block;font-size:13px;font-weight:600;color:var(--ink);margin:0 0 8px}' +
    'input{width:100%;font-family:var(--font-body);font-size:15px;padding:13px 14px;' +
    'border:1px solid var(--border-strong);border-radius:11px;background:#fff;color:var(--ink)}' +
    'input:focus{outline:none;border-color:var(--terra);box-shadow:0 0 0 3px rgba(188,108,37,.15)}' +
    'button{margin-top:18px;width:100%;font-family:var(--font-body);font-size:15px;font-weight:600;' +
    'color:#fff;background:var(--green);border:0;border-radius:11px;padding:13px 16px;cursor:pointer}' +
    'button:hover{background:#1F2B12}' +
    '.gate-foot{margin-top:20px;font-size:12px;color:var(--muted);text-align:center}' +
    '</style></head><body>' +
    '<form class="gate" method="POST" action="/__auth">' +
    '<p class="gate-mark"><span class="m">hello</span><span class="a">mello</span></p>' +
    '<p class="gate-tag">Client area</p>' +
    '<h1>Password protected</h1>' + err +
    '<label for="password">Password</label>' +
    '<input type="password" id="password" name="password" autocomplete="current-password" autofocus required>' +
    '<input type="hidden" name="next" value="' + esc(next) + '">' +
    '<button type="submit">Enter</button>' +
    '<p class="gate-foot">Bright Data</p>' +
    '</form></body></html>';
  return new Response(html, {
    status: showError ? 401 : 200,
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' }
  });
}

// Handle the password form post.
async function handleLogin(request, env, url) {
  const password = env.SITE_PASSWORD || '';
  const form = await request.formData();
  const given = String(form.get('password') || '');
  const next = safeNext(String(form.get('next') || '/hellomello'));
  if (password && safeEqual(given, password)) {
    const token = await gateToken(password);
    const cookie = 'hm_gate=' + token + '; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=' + (60 * 60 * 24 * 30);
    return new Response(null, {
      status: 303,
      headers: { 'location': url.origin + next, 'set-cookie': cookie, 'cache-control': 'no-store' }
    });
  }
  return loginPage(next, true);
}

// Normalise the readable export the browser sends.
function cleanExport(input) {
  const e = input && typeof input === 'object' ? input : {};
  const groups = Array.isArray(e.groups) ? e.groups : [];
  return {
    submittedBy: typeof e.submittedBy === 'string' && e.submittedBy ? e.submittedBy : 'Someone',
    submittedAt: typeof e.submittedAt === 'string' ? e.submittedAt : new Date().toISOString(),
    guardrailsNote: typeof e.guardrailsNote === 'string' ? e.guardrailsNote : '',
    groups: groups.map((g) => ({
      group: typeof g.group === 'string' ? g.group : '',
      sectionNote: typeof g.sectionNote === 'string' ? g.sectionNote : '',
      topics: Array.isArray(g.topics) ? g.topics.map((t) => ({
        topic: typeof t.topic === 'string' ? t.topic : '',
        tga: typeof t.tga === 'string' ? t.tga : '',
        decision: typeof t.decision === 'string' ? t.decision : 'not decided',
        note: typeof t.note === 'string' ? t.note : ''
      })) : []
    }))
  };
}

function tally(exp) {
  const c = { approve: 0, change: 0, drop: 0, 'not decided': 0 };
  exp.groups.forEach((g) => g.topics.forEach((t) => {
    const d = Object.prototype.hasOwnProperty.call(c, t.decision) ? t.decision : 'not decided';
    c[d]++;
  }));
  return c;
}

function buildText(exp) {
  const c = tally(exp);
  const lines = [];
  lines.push('Content sign-off');
  lines.push('Submitted by: ' + exp.submittedBy);
  lines.push('Date: ' + exp.submittedAt.slice(0, 10));
  lines.push('');
  lines.push('Summary: Approve ' + c.approve + ', Change ' + c.change + ', Drop ' + c.drop + ', Not decided ' + c['not decided']);
  exp.groups.forEach((g) => {
    lines.push('');
    lines.push(g.group.toUpperCase());
    g.topics.forEach((t) => {
      const label = t.decision.charAt(0).toUpperCase() + t.decision.slice(1);
      lines.push('- ' + t.topic + ' \u2014 ' + label + (t.tga ? ' [' + t.tga + ']' : '') + (t.note ? ' (note: ' + t.note + ')' : ''));
    });
    if (g.sectionNote) lines.push('  Section note: ' + g.sectionNote);
  });
  if (exp.guardrailsNote) {
    lines.push('');
    lines.push('GUARDRAILS NOTE');
    lines.push(exp.guardrailsNote);
  }
  return lines.join('\n');
}

function buildHtml(exp) {
  const c = tally(exp);
  const colour = { approve: '#1f8a4c', change: '#b8860b', drop: '#b23b3b', 'not decided': '#888' };
  let h = '<div style="font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;max-width:640px">';
  h += '<h2 style="margin:0 0 4px">Content sign-off</h2>';
  h += '<p style="margin:0 0 2px"><strong>Submitted by:</strong> ' + esc(exp.submittedBy) + '</p>';
  h += '<p style="margin:0 0 12px"><strong>Date:</strong> ' + esc(exp.submittedAt.slice(0, 10)) + '</p>';
  h += '<p style="margin:0 0 16px;font-size:14px">Approve <strong>' + c.approve + '</strong> &nbsp;|&nbsp; Change <strong>' + c.change + '</strong> &nbsp;|&nbsp; Drop <strong>' + c.drop + '</strong> &nbsp;|&nbsp; Not decided <strong>' + c['not decided'] + '</strong></p>';
  exp.groups.forEach((g) => {
    h += '<h3 style="margin:18px 0 6px;border-bottom:1px solid #e3e3e3;padding-bottom:4px">' + esc(g.group) + '</h3>';
    h += '<table style="width:100%;border-collapse:collapse;font-size:14px">';
    g.topics.forEach((t) => {
      const col = colour[t.decision] || '#888';
      const label = t.decision.charAt(0).toUpperCase() + t.decision.slice(1);
      h += '<tr>' +
        '<td style="padding:5px 8px 5px 0;vertical-align:top">' + esc(t.topic) +
        (t.note ? '<div style="color:#666;font-size:13px">Note: ' + esc(t.note) + '</div>' : '') +
        '</td>' +
        '<td style="padding:5px 0;vertical-align:top;text-align:right;white-space:nowrap"><span style="color:' + col + ';font-weight:bold">' + esc(label) + '</span>' +
        (t.tga ? '<span style="color:#999;font-size:12px"> &middot; ' + esc(t.tga) + '</span>' : '') +
        '</td></tr>';
    });
    h += '</table>';
    if (g.sectionNote) h += '<p style="margin:6px 0 0;color:#555;font-size:13px"><em>Section note:</em> ' + esc(g.sectionNote) + '</p>';
  });
  if (exp.guardrailsNote) {
    h += '<h3 style="margin:18px 0 6px;border-bottom:1px solid #e3e3e3;padding-bottom:4px">Guardrails note</h3>';
    h += '<p style="margin:0;font-size:14px">' + esc(exp.guardrailsNote) + '</p>';
  }
  h += '</div>';
  return h;
}

function json(obj, status, extra) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: Object.assign({ 'content-type': 'application/json', 'cache-control': 'no-store' }, extra || {})
  });
}

// Build a raw MIME message with both plain-text and HTML parts.
function buildMime(fromEmail, toEmail, subject, text, html) {
  const boundary = 'hm_' + crypto.randomUUID().replace(/-/g, '');
  const fromDomain = (fromEmail.split('@')[1] || 'divan.work');
  const messageId = '<' + crypto.randomUUID() + '@' + fromDomain + '>';
  const lines = [
    'From: Hellomello Sign-off <' + fromEmail + '>',
    'To: <' + toEmail + '>',
    'Subject: ' + subject,
    'Message-ID: ' + messageId,
    'Date: ' + new Date().toUTCString(),
    'MIME-Version: 1.0',
    'Content-Type: multipart/alternative; boundary="' + boundary + '"',
    '',
    '--' + boundary,
    'Content-Type: text/plain; charset="utf-8"',
    'Content-Transfer-Encoding: 7bit',
    '',
    text,
    '',
    '--' + boundary,
    'Content-Type: text/html; charset="utf-8"',
    'Content-Transfer-Encoding: 7bit',
    '',
    html,
    '',
    '--' + boundary + '--',
    ''
  ];
  return lines.join('\r\n');
}

// Send the summary through Cloudflare Email Workers, if the binding is set.
// Returns { emailed, error }.
async function sendEmail(env, fromEmail, toEmail, subject, text, html) {
  if (!env.SEND_EMAIL) return { emailed: false, error: '' };
  try {
    const raw = buildMime(fromEmail, toEmail, subject, text, html);
    const msg = new EmailMessage(fromEmail, toEmail, raw);
    await env.SEND_EMAIL.send(msg);
    return { emailed: true, error: '' };
  } catch (err) {
    console.log('EMAIL_SEND_ERROR', String(err && err.message ? err.message : err));
    return { emailed: false, error: String(err && err.message ? err.message : err) };
  }
}

async function handleApi(request, env, url) {
  const action = url.searchParams.get('action') || '';
  const notifyTo = env.SIGNOFF_NOTIFY_EMAIL || DEFAULT_NOTIFY;
  const fromEmail = env.SIGNOFF_FROM_EMAIL || DEFAULT_FROM;

  try {
    if (request.method === 'GET' && action === 'state') {
      // Drafts live in the reviewer's browser, so the server starts empty.
      return json(EMPTY_STATE);
    }

    if (request.method === 'POST' && action === 'save') {
      // No server draft store, the browser keeps it. Just acknowledge.
      return json({ ok: true, stored: false });
    }

    if (request.method === 'POST' && action === 'submit') {
      let body = {};
      try { body = await request.json(); } catch (e) { body = {}; }
      const exp = cleanExport(body);
      const subject = 'Content sign-off from ' + exp.submittedBy + ' (' + exp.submittedAt.slice(0, 10) + ')';
      const text = buildText(exp);
      const html = buildHtml(exp);

      let stored = false;
      if (env.SIGNOFF) {
        const stamp = (exp.submittedAt || new Date().toISOString()).replace(/[^0-9A-Za-z]/g, '').slice(0, 14);
        const key = 'submission:' + stamp + ':' + crypto.randomUUID().slice(0, 8);
        await env.SIGNOFF.put(key, JSON.stringify({ exp, text, html }));
        stored = true;
      }

      // Try Cloudflare Email Workers. If it is not configured yet, the browser
      // mail-app fallback below still notifies the team.
      const sent = await sendEmail(env, fromEmail, notifyTo, subject, text, html);

      const mailBody = text.length > 1600
        ? text.slice(0, 1600) + '\n\n(Full details are in the JSON file that just downloaded, please attach it.)'
        : text;
      const mailto = 'mailto:' + encodeURIComponent(notifyTo) +
        '?subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(mailBody);

      return json({ ok: true, stored, emailed: sent.emailed, to: notifyTo, mailto });
    }

    if (request.method === 'GET' && action === 'submissions') {
      const admin = env.ADMIN_TOKEN || '';
      const provided = url.searchParams.get('token') ||
        (request.headers.get('authorization') || '').replace(/^Bearer\s+/i, '');
      if (!admin || provided !== admin) return json({ ok: false, error: 'Forbidden' }, 403);
      if (!env.SIGNOFF) return json({ ok: true, submissions: [] });
      const list = await env.SIGNOFF.list({ prefix: 'submission:' });
      const submissions = [];
      for (const k of list.keys) {
        const raw = await env.SIGNOFF.get(k.name);
        const obj = raw ? JSON.parse(raw) : null;
        if (obj && obj.exp) {
          submissions.push({ key: k.name, submittedBy: obj.exp.submittedBy, submittedAt: obj.exp.submittedAt });
        }
      }
      return json({ ok: true, submissions });
    }

    return json({ ok: false, error: 'Unknown action' }, 404);
  } catch (err) {
    return json({ ok: false, error: String(err && err.message ? err.message : err) }, 500);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Password gate. Active only when SITE_PASSWORD is set, so deploying
    // without the secret never locks anyone out.
    if (env.SITE_PASSWORD) {
      if (url.pathname === '/__auth' && request.method === 'POST') {
        return handleLogin(request, env, url);
      }
      if (url.pathname === '/__logout') {
        return new Response(null, {
          status: 303,
          headers: {
            'location': url.origin + '/hellomello',
            'set-cookie': 'hm_gate=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0',
            'cache-control': 'no-store'
          }
        });
      }
      const authed = await isAuthed(request, env);
      if (!authed) {
        if (url.pathname === '/api/signoff') {
          return json({ ok: false, error: 'Unauthorized' }, 401);
        }
        return loginPage(url.pathname + url.search, false);
      }
    }

    if (url.pathname === '/') {
      return Response.redirect(url.origin + '/hellomello', 302);
    }

    if (url.pathname === '/api/signoff') {
      return handleApi(request, env, url);
    }

    // Everything else is a static asset.
    return env.ASSETS.fetch(request);
  }
};

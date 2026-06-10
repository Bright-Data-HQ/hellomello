'use strict';

/*
 * Hellomello content sign-off, serverless backend (Vercel function).
 *
 * One endpoint, switched by ?action= :
 *   GET  /api/signoff?action=state   -> empty draft shape (drafts live in the browser)
 *   POST /api/signoff?action=save    -> autosave acknowledgement (no server store)
 *   POST /api/signoff?action=submit  -> email the finished sign-off to the team
 *
 * The completed sign-off is sent by email, so there is no database to set up.
 *   - If RESEND_API_KEY is set, the email is sent server-side through Resend.
 *   - If not, the function returns a prefilled mailto: link and the reviewer's
 *     mail app opens ready to send. Either way a JSON copy downloads in the
 *     browser as a backup.
 *
 * Optional env vars:
 *   RESEND_API_KEY        Resend API key. When present, email is sent for you.
 *   SIGNOFF_NOTIFY_EMAIL  Where the sign-off goes. Default below.
 *   SIGNOFF_FROM_EMAIL    From address (must be a Resend-verified sender).
 */

const NOTIFY_TO = process.env.SIGNOFF_NOTIFY_EMAIL || 'vahid@brightdata.com.au';
const FROM_EMAIL = process.env.SIGNOFF_FROM_EMAIL || 'Hellomello Sign-off <onboarding@resend.dev>';

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c];
  });
}

function readBody(req) {
  if (req.body && typeof req.body === 'object') return Promise.resolve(req.body);
  return new Promise((resolve) => {
    let raw = '';
    req.on('data', (c) => {
      raw += c;
      if (raw.length > 1_000_000) req.destroy();
    });
    req.on('end', () => {
      if (!raw) return resolve({});
      try {
        resolve(JSON.parse(raw));
      } catch (err) {
        resolve({});
      }
    });
    req.on('error', () => resolve({}));
  });
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
    const d = c.hasOwnProperty(t.decision) ? t.decision : 'not decided';
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

async function sendViaResend(subject, html, text) {
  const key = process.env.RESEND_API_KEY;
  if (!key) return false;
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: FROM_EMAIL, to: [NOTIFY_TO], subject, html, text })
  });
  if (!r.ok) throw new Error('Resend ' + r.status + ': ' + (await r.text()));
  return true;
}

const EMPTY_STATE = { meta: { submitterName: '', submittedAt: '', updatedAt: '', version: 1 }, decisions: {}, pageNotes: {} };

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const action = (req.query && req.query.action) || '';

  try {
    if (req.method === 'GET' && action === 'state') {
      // Drafts live in the reviewer's browser, so the server starts empty.
      return res.status(200).json(EMPTY_STATE);
    }

    if (req.method === 'POST' && action === 'save') {
      // No server store, the browser keeps the draft. Just acknowledge.
      return res.status(200).json({ ok: true, stored: false });
    }

    if (req.method === 'POST' && action === 'submit') {
      const exp = cleanExport(await readBody(req));
      const subject = 'Content sign-off from ' + exp.submittedBy + ' (' + exp.submittedAt.slice(0, 10) + ')';
      const text = buildText(exp);
      const html = buildHtml(exp);

      let emailed = false;
      let error = '';
      try {
        emailed = await sendViaResend(subject, html, text);
      } catch (err) {
        emailed = false;
        error = String(err && err.message ? err.message : err);
      }

      const resp = { ok: true, emailed, to: NOTIFY_TO };
      if (!emailed) {
        // Mail-app fallback: keep the body within a safe length, the JSON
        // download holds the full record.
        const body = text.length > 1600
          ? text.slice(0, 1600) + '\n\n(Full details are in the JSON file that just downloaded, please attach it.)'
          : text;
        resp.mailto = 'mailto:' + encodeURIComponent(NOTIFY_TO) +
          '?subject=' + encodeURIComponent(subject) +
          '&body=' + encodeURIComponent(body);
        if (error) resp.note = 'email_not_sent';
      }
      return res.status(200).json(resp);
    }

    return res.status(404).json({ ok: false, error: 'Unknown action' });
  } catch (err) {
    return res.status(500).json({ ok: false, error: String(err && err.message ? err.message : err) });
  }
};

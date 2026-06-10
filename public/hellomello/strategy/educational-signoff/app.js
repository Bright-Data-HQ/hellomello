'use strict';

/* ------------------------------------------------------------------ *
 * Hellomello educational content, sign-off form.
 * Single-page app with step pages. Captures Approve / Change / Drop and
 * notes per topic, plus a note per page. Autosaves to the backend and to
 * the browser, and lets you download a JSON copy on submit.
 * ------------------------------------------------------------------ */

var API = '/api/signoff';
var LOCAL_KEY = 'hm-signoff-draft-v1';

/* ---- Topic data (the 44 educational topics) ---------------------- */
var GROUPS = [
  {
    id: 'product',
    label: 'Product forms',
    title: 'Product forms',
    intro: 'These pages explain each product format in plain language, so a new patient understands their options before a consult. They answer the simple "what is" questions people search, they carry the lowest claim risk, and they match the product library Polln has already built.',
    topics: [
      { id: 'cbd-oil', name: 'What is CBD oil', tga: 'care', links: [['Polln', 'cbd-oil-explained', 'https://www.polln.com/library/cbd-oil-explained']] },
      { id: 'vaporiser', name: 'Medical cannabis vaporiser', tga: 'care', links: [['Polln', 'guide to vaping', 'https://www.polln.com/library/ultimate-guide-to-vaping-medicinal-cannabis']] },
      { id: 'cannabis-oil', name: 'Medical cannabis oil', tga: 'care', links: [['Polln', 'cbd-oil-explained', 'https://www.polln.com/library/cbd-oil-explained']] },
      { id: 'flower', name: 'Medical cannabis flower', tga: 'care', links: [['Polln', 'sativa vs indica', 'https://www.polln.com/library/sativa-vs-indica-vs-hybrid-cannabis-what-to-expect']] },
      { id: 'gummies', name: 'Gummies and edibles', tga: 'care', links: [['Leafwell', 'cannabis edibles', 'https://leafwell.com/blog/9-benefits-of-cannabis-edibles'], ['Leafwell', 'dosing edibles', 'https://leafwell.com/blog/dose-cannabis-edibles'], ['Polln', 'how medicine is taken', 'https://www.polln.com/library/how-prescription-natural-medicine-can-be-consumed']] },
      { id: 'capsules', name: 'Capsules', tga: 'care', links: [['Leafwell', 'cannabis pills and capsules', 'https://leafwell.com/blog/thc-pills'], ['Polln', 'how medicine is taken', 'https://www.polln.com/library/how-prescription-natural-medicine-can-be-consumed']] },
      { id: 'topicals', name: 'Topicals and creams', tga: 'care', links: [['Releaf', 'topicals and CBD cream', 'https://releaf.co.uk/education/cannabis-101/administration/topical/a-beginners-guide-to-topical-cannabinoids-and-cbd-cream'], ['Leafwell', 'cannabis topicals', 'https://leafwell.com/blog/cannabis-topicals']] },
      { id: 'tinctures', name: 'Tinctures', tga: 'care', links: [['Leafwell', 'dosing tinctures', 'https://leafwell.com/blog/how-to-dose-cannabis-tinctures'], ['Leafwell', 'tincture vs oil', 'https://leafwell.com/blog/cbd-tincture-vs-oil']] },
      { id: 'how-taken', name: 'How medical cannabis is taken', tga: 'care', links: [['Polln', 'how medicine is taken', 'https://www.polln.com/library/how-prescription-natural-medicine-can-be-consumed'], ['Leafwell', 'how to use CBD oil', 'https://leafwell.com/blog/how-to-use-cbd-oil']] }
    ]
  },
  {
    id: 'howitworks',
    label: 'How it works',
    title: 'How it works',
    intro: 'These are the "how it works" basics that every other page links back to. It is the safest group on compliance and the strongest on evidence, and most competitors already rank here, so it sets up the rest of the library.',
    topics: [
      { id: 'cannabinoids', name: 'Cannabinoids explained', tga: 'safe', links: [['Polln', 'cbd-oil-explained', 'https://www.polln.com/library/cbd-oil-explained'], ['Herbly', 'understanding the ECS', 'https://herbly.com.au/blogs/latest-medical-articles/understanding-the-endocannabinoid-system']] },
      { id: 'indica-sativa', name: 'Indica vs sativa', tga: 'safe', links: [['Polln', 'sativa vs indica vs hybrid', 'https://www.polln.com/library/sativa-vs-indica-vs-hybrid-cannabis-what-to-expect'], ['Leafwell', 'sativa vs indica', 'https://leafwell.com/blog/sativa-indica-difference-which-is-right-for-me'], ['Releaf', 'indica vs sativa', 'https://releaf.co.uk/blog/indica-vs-sativa-effects-differences']] },
      { id: 'what-is-cbd', name: 'What is CBD', tga: 'safe', links: [['Polln', 'cbd-oil-explained', 'https://www.polln.com/library/cbd-oil-explained']] },
      { id: 'what-is-thc', name: 'What is THC', tga: 'safe', links: [['Polln', 'guide to vaping', 'https://www.polln.com/library/ultimate-guide-to-vaping-medicinal-cannabis'], ['Leafwell', 'what is THC', 'https://leafwell.com/blog/what-is-thc-tetrahydrocannabinol'], ['Releaf', 'what is THC', 'https://releaf.co.uk/education/cannabis-101/thc/what-is-thc-and-how-does-it-work-in-the-body']] },
      { id: 'ecs', name: 'Endocannabinoid system', tga: 'safe', links: [['Herbly', 'understanding the ECS', 'https://herbly.com.au/blogs/latest-medical-articles/understanding-the-endocannabinoid-system'], ['Polln', 'the ECS explained', 'https://www.polln.com/library/the-endocannabinoid-system-explained']] },
      { id: 'terpenes', name: 'Terpenes explained', tga: 'safe', links: [['Polln', 'cannabis terpenes', 'https://www.polln.com/library/everything-you-need-to-know-about-cannabis-terpenes']] },
      { id: 'driving', name: 'Cannabis and driving', tga: 'safe', links: [['Polln', 'cannabis and driving', 'https://www.polln.com/library/medicinal-cannabis-and-driving-what-you-need-to-know-as-a-patient-in-australia'], ['Herbly', 'drive with THC or CBD', 'https://herbly.com.au/blogs/latest-medical-articles/can-you-drive-with-thc-or-cbd-in-your-system'], ['Leafwell', 'cannabis in blood work', 'https://leafwell.com/blog/does-marijuana-show-up-in-regular-blood-work']] },
      { id: 'what-is-mc', name: 'What is medical cannabis', tga: 'care', links: [['Herbly', 'alternative medicine in Australia', 'https://herbly.com.au/blogs/latest-medical-articles/alternative-medicine-in-australia']] },
      { id: 'cbd-vs-thc', name: 'CBD versus THC', tga: 'safe', links: [['Leafwell', 'CBD vs THC', 'https://leafwell.com/blog/cbd-vs-thc'], ['Releaf', 'what is THC', 'https://releaf.co.uk/education/cannabis-101/thc/what-is-thc-and-how-does-it-work-in-the-body'], ['Polln', 'cbd-oil-explained', 'https://www.polln.com/library/cbd-oil-explained']] },
      { id: 'how-long', name: 'How long cannabis stays in your system', tga: 'safe', links: [['Polln', 'how long it stays', 'https://www.polln.com/library/how-long-does-cannabis-stay-in-your-system'], ['Leafwell', 'cannabis in blood work', 'https://leafwell.com/blog/does-marijuana-show-up-in-regular-blood-work'], ['Herbly', 'THC or CBD in your system', 'https://herbly.com.au/blogs/latest-medical-articles/can-you-drive-with-thc-or-cbd-in-your-system']] },
      { id: 'full-spectrum', name: 'Full spectrum versus isolate', tga: 'safe', links: [['Leafwell', 'full spectrum vs isolate', 'https://leafwell.com/blog/full-spectrum-cbd-vs-cbd-isolate'], ['Leafwell', 'broad spectrum vs isolate', 'https://leafwell.com/blog/broad-spectrum-cbd-vs-cbd-isolate']] },
      { id: 'entourage', name: 'The entourage effect', tga: 'safe', links: [['Leafwell', 'the entourage effect', 'https://leafwell.com/blog/entourage-effect'], ['Polln', 'cannabis terpenes', 'https://www.polln.com/library/everything-you-need-to-know-about-cannabis-terpenes']] },
      { id: 'how-mc-works', name: 'How medical cannabis works', tga: 'care', links: [['Leafwell', 'what is CBD', 'https://leafwell.com/blog/what-is-cbd'], ['Herbly', 'understanding the ECS', 'https://herbly.com.au/blogs/latest-medical-articles/understanding-the-endocannabinoid-system'], ['Polln', 'the ECS explained', 'https://www.polln.com/library/the-endocannabinoid-system-explained']] }
    ]
  },
  {
    id: 'symptoms',
    label: 'Symptoms',
    title: 'Symptoms',
    intro: 'These are the everyday wellbeing topics people search for. They build authority and traffic without naming a product or making a treatment claim, the same way the Alternaleaf hub does, and that hub already ranks.',
    topics: [
      { id: 'sleep', name: 'Sleep', tga: 'care', links: [['Alternaleaf', 'deep sleep', 'https://www.alternaleaf.com.au/hub/deep-sleep-meditation-restful-sleep'], ['Herbly', 'understanding insomnia', 'https://herbly.com.au/blogs/news/understanding-insomnia-the-hidden-struggles-of-sleep']] },
      { id: 'inflammation', name: 'Inflammation', tga: 'care', links: [['Alternaleaf', 'pain and inflammation diet', 'https://www.alternaleaf.com.au/hub/pain-inflammation-diet']] },
      { id: 'muscle-pain', name: 'Muscle and body pain', tga: 'care', links: [['Alternaleaf', 'relieve muscle pain', 'https://www.alternaleaf.com.au/hub/natural-ways-to-relieve-muscle-pain']] },
      { id: 'nausea', name: 'Nausea', tga: 'care', links: [] },
      { id: 'stress', name: 'Stress', tga: 'care', links: [['Herbly', 'natural stress remedies', 'https://herbly.com.au/blogs/news/natural-stress-remedies'], ['Alternaleaf', 'forest bathing for stress', 'https://www.alternaleaf.com.au/hub/forest-bathing-stress-relief']] },
      { id: 'chronic-pain', name: 'Chronic pain', tga: 'care', links: [['Herbly', 'holistic therapies for chronic pain', 'https://herbly.com.au/blogs/news/a-comprehensive-guide-to-holistic-therapies-and-treatments-for-chronic-pain'], ['Alternaleaf', 'managing pain naturally', 'https://www.alternaleaf.com.au/hub/managing-pain-acupressure-reflexology']] },
      { id: 'fatigue', name: 'Low energy and fatigue', tga: 'care', links: [['Alternaleaf', 'boost energy naturally', 'https://www.alternaleaf.com.au/hub/boost-energy-levels-naturally'], ['Alternaleaf', 'benefits of activity', 'https://www.alternaleaf.com.au/hub/emotional-benefits-of-physical-activity']] },
      { id: 'period-pain', name: 'Period and menstrual pain', tga: 'care', links: [['Herbly', 'period pain remedies', 'https://herbly.com.au/blogs/women-s-health/top-7-period-pain-remedies-and-the-role-of-cbd-thc'], ['Herbly', 'relieving menstrual cramps', 'https://herbly.com.au/blogs/women-s-health/cbd-and-thc-for-period-pain-natural-ways-to-relieve-menstrual-cramps']] },
      { id: 'nerve-pain', name: 'Nerve and neuropathic pain', tga: 'care', links: [['Herbly', 'neuropathic pain', 'https://herbly.com.au/blogs/news/neuropathic-pain-who-it-affects-causes-and-treatments'], ['Herbly', 'diabetic nerve pain', 'https://herbly.com.au/blogs/news/diabetic-nerve-pain-comprehensive-therapies-and-treatment-options']] }
    ]
  },
  {
    id: 'conditions',
    label: 'Conditions',
    title: 'Conditions',
    intro: 'These are the conditions patients search before they ever ask about cannabis. Herbly ranks for every one of them, which proves the demand is real, but this is also the riskiest group on compliance, so it needs care. The Restricted ones are covered again in the guardrails step.',
    topics: [
      { id: 'menopause', name: 'Menopause and women\u2019s health', tga: 'care', links: [['Herbly', 'menopause and natural therapies', 'https://herbly.com.au/blogs/women-s-health/women-turning-to-alternative-medicine-for-relief-of-menopause-symptoms']] },
      { id: 'migraine', name: 'Migraine and headache', tga: 'care', links: [['Herbly', 'natural remedies for migraines', 'https://herbly.com.au/pages/natural-remedies-for-migraines']] },
      { id: 'arthritis', name: 'Arthritis and joints', tga: 'care', links: [['Herbly', 'understanding arthritis', 'https://herbly.com.au/blogs/news/understanding-arthritis-causes-impacts-and-treatments']] },
      { id: 'endometriosis', name: 'Endometriosis', tga: 'care', links: [['Herbly', 'natural remedies for endometriosis', 'https://herbly.com.au/blogs/news/natural-remedies-for-endometriosis']] },
      { id: 'fibromyalgia', name: 'Fibromyalgia', tga: 'care', links: [['Herbly', 'natural medicine for fibromyalgia', 'https://herbly.com.au/blogs/news/natural-medicine-for-fibromyalgia-a-comprehensive-guide']] },
      { id: 'anxiety', name: 'Anxiety (general)', tga: 'restricted', links: [['Herbly', 'holistic support for anxiety', 'https://herbly.com.au/blogs/news/holistic-treatment-for-anxiety-exploring-alternative-medicine-and-natural-therapies-in-australia']] },
      { id: 'epilepsy', name: 'Epilepsy', tga: 'restricted', links: [['Herbly', 'natural approaches to epilepsy', 'https://herbly.com.au/blogs/news/exploring-natural-treatments-for-epilepsy-evidence-based-approaches-and-current-research']] },
      { id: 'adhd', name: 'ADHD', tga: 'restricted', links: [['Herbly', 'what is ADHD', 'https://herbly.com.au/blogs/news/what-is-adhd']] },
      { id: 'depression', name: 'Depression and low mood', tga: 'restricted', links: [['Herbly', 'understanding depression', 'https://herbly.com.au/blogs/news/understanding-depression-and-mental-health'], ['Herbly', 'natural support for low mood', 'https://herbly.com.au/blogs/news/natural-treatments-for-depression']] },
      { id: 'ptsd', name: 'PTSD', tga: 'restricted', links: [['Herbly', 'understanding PTSD', 'https://herbly.com.au/blogs/news/understanding-ptsd-who-it-affects-causes-and-treatments'], ['Herbly', 'PTSD support options', 'https://herbly.com.au/blogs/news/exploring-ptsd-treatment-options-conventional-natural-and-alternative-therapies']] },
      { id: 'ms', name: 'Multiple sclerosis', tga: 'care', links: [['Herbly', 'understanding MS', 'https://herbly.com.au/blogs/news/understanding-multiple-sclerosis'], ['Herbly', 'common MS symptoms', 'https://herbly.com.au/blogs/news/common-symptoms-of-multiple-sclerosis']] },
      { id: 'sciatica', name: 'Sciatica', tga: 'care', links: [['Herbly', 'sciatica support options', 'https://herbly.com.au/blogs/news/sciatica-therapies-and-treatment-exploring-conventional-alternative-and-natural-options'], ['Herbly', 'joint and back pain', 'https://herbly.com.au/blogs/news/joint-pain-understanding-causes-symptoms-and-holistic-treatments']] },
      { id: 'ibd', name: 'Ulcerative colitis and IBD', tga: 'care', links: [['Herbly', 'natural support for colitis', 'https://herbly.com.au/blogs/news/natural-treatments-for-ulcerative-colitis'], ['Herbly', 'natural medicine for IBD', 'https://herbly.com.au/blogs/news/natural-medicine-for-inflammatory-bowel-disease']] }
    ]
  }
];

/* Step list: intro, the four groups, guardrails, review. */
var STEPS = [
  { id: 'intro', label: 'Start' },
  { id: 'group:product', label: 'Product forms' },
  { id: 'group:howitworks', label: 'How it works' },
  { id: 'group:symptoms', label: 'Symptoms' },
  { id: 'group:conditions', label: 'Conditions' },
  { id: 'guardrails', label: 'Guardrails' },
  { id: 'review', label: 'Review & submit' }
];

var ALL_TOPICS = [];
GROUPS.forEach(function (g) { g.topics.forEach(function (t) { ALL_TOPICS.push({ group: g, topic: t }); }); });
var TOTAL = ALL_TOPICS.length;

/* ---- State ------------------------------------------------------- */
var state = { meta: { submitterName: '', submittedAt: '' }, decisions: {}, pageNotes: {} };
var current = 0;
var submitted = false;
var submitMode = 'email';
var saveTimer = null;

/* ---- Helpers ----------------------------------------------------- */
function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
function $(sel) { return document.querySelector(sel); }
function decided(id) { var d = state.decisions[id]; return d && d.choice; }
function decidedCount() { var n = 0; ALL_TOPICS.forEach(function (x) { if (decided(x.topic.id)) n++; }); return n; }
function setSaveState(text, cls) { var el = $('#saveState'); el.textContent = text; el.className = 'save-state' + (cls ? ' ' + cls : ''); }

/* ---- Persistence ------------------------------------------------- */
function loadLocal() { try { var raw = localStorage.getItem(LOCAL_KEY); if (raw) return JSON.parse(raw); } catch (e) {} return null; }
function saveLocal() { try { localStorage.setItem(LOCAL_KEY, JSON.stringify(state)); } catch (e) {} }

function scheduleSave() {
  saveLocal();
  setSaveState('Saving\u2026', 'saving');
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(pushSave, 700);
}

function pushSave() {
  fetch(API + '?action=save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(state)
  }).then(function (r) { return r.json(); }).then(function (res) {
    if (res && res.ok) setSaveState(res.stored ? 'Saved' : 'Saved on this device', 'saved');
    else setSaveState('Saved on this device', 'saved');
  }).catch(function () { setSaveState('Saved on this device', 'saved'); });
}

function loadState() {
  return fetch(API + '?action=state').then(function (r) { return r.json(); }).then(function (server) {
    var local = loadLocal();
    // Prefer whichever has more content; server wins on ties.
    var serverCount = server && server.decisions ? Object.keys(server.decisions).length : 0;
    var localCount = local && local.decisions ? Object.keys(local.decisions).length : 0;
    var chosen = serverCount >= localCount && serverCount > 0 ? server : (local || server || state);
    mergeState(chosen);
  }).catch(function () { var local = loadLocal(); if (local) mergeState(local); });
}

function mergeState(src) {
  if (!src || typeof src !== 'object') return;
  if (src.meta) state.meta.submitterName = src.meta.submitterName || '';
  state.decisions = src.decisions && typeof src.decisions === 'object' ? src.decisions : {};
  state.pageNotes = src.pageNotes && typeof src.pageNotes === 'object' ? src.pageNotes : {};
}

/* ---- Rendering --------------------------------------------------- */
function render() {
  renderSteps();
  var step = STEPS[current];
  var root = $('#pageRoot');
  if (step.id === 'intro') root.innerHTML = viewIntro();
  else if (step.id.indexOf('group:') === 0) root.innerHTML = viewGroup(step.id.split(':')[1]);
  else if (step.id === 'guardrails') root.innerHTML = viewGuardrails();
  else if (step.id === 'review') root.innerHTML = submitted ? viewSubmitted() : viewReview();
  wire(step);
  renderFoot();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderSteps() {
  var nav = $('#stepNav');
  nav.innerHTML = STEPS.map(function (s, i) {
    var cls = 'step-chip' + (i === current ? ' active' : (i < current ? ' done' : ''));
    return '<button class="' + cls + '" data-step="' + i + '">' + esc(s.label) + '</button>';
  }).join('');
  Array.prototype.forEach.call(nav.querySelectorAll('.step-chip'), function (chip) {
    chip.addEventListener('click', function () { go(parseInt(chip.getAttribute('data-step'), 10)); });
  });
  var pct = (current / (STEPS.length - 1)) * 100;
  $('#progressBar').style.width = pct + '%';
}

function renderFoot() {
  $('#footCount').textContent = decidedCount() + ' of ' + TOTAL + ' topics decided';
  var back = $('#btnBack'); var next = $('#btnNext');
  back.disabled = current === 0;
  if (STEPS[current].id === 'review') { next.textContent = submitted ? 'Done' : 'Submit sign-off'; next.disabled = submitted; }
  else { next.textContent = 'Next'; next.disabled = false; }
}

function viewIntro() {
  return '' +
    '<p class="sec-num">For sign-off, educational content</p>' +
    '<h1 class="sec-title">Educational <em>topics</em></h1>' +
    '<p class="sec-lead">Hi Rod, this is the educational content we would like you to sign off before we start writing. Go through each topic and mark Approve, Change or Drop. Add a note wherever you want to. Your answers save as you go, so you can stop and come back any time.</p>' +
    '<h2 class="sub-title">For each topic, choose one</h2>' +
    '<div class="howto">' +
      '<div class="card"><div class="n">01</div><h4>Approve</h4><p>Happy for us to write this one as planned.</p></div>' +
      '<div class="card"><div class="n">02</div><h4>Change</h4><p>Keep it, but with a tweak. Tell us in the note.</p></div>' +
      '<div class="card"><div class="n">03</div><h4>Drop</h4><p>Leave this one out for now.</p></div>' +
    '</div>' +
    '<h2 class="sub-title">What you will review, four groups</h2>' +
    '<div class="pillars">' +
      GROUPS.map(function (g, i) {
        return '<div class="pillar"><div class="n">0' + (i + 1) + '</div><h4>' + esc(g.title) + '</h4><p>' + g.topics.length + ' topics</p></div>';
      }).join('') +
    '</div>';
}

function viewGroup(gid) {
  var g = GROUPS.filter(function (x) { return x.id === gid; })[0];
  var idx = GROUPS.indexOf(g) + 1;
  var html = '' +
    '<p class="sec-num">Group ' + idx + ' of 4</p>' +
    '<h1 class="sec-title">' + esc(g.title) + '</h1>' +
    '<div class="group-intro">' + esc(g.intro) + '</div>';
  html += g.topics.map(function (t) { return topicCard(t); }).join('');
  html += pageNoteBlock('group:' + g.id, 'Overall note for ' + g.title.toLowerCase());
  return html;
}

function topicCard(t) {
  var d = state.decisions[t.id] || {};
  var proof = t.links.length
    ? '<div class="proof">' + t.links.map(function (l) {
        return '<div><span class="src">' + esc(l[0]) + '</span><a href="' + esc(l[2]) + '" target="_blank" rel="noopener">' + esc(l[1]) + '</a></div>';
      }).join('') + '</div>'
    : '<div class="proof none">No competitor page found yet, an open run.</div>';
  var tgaLabel = t.tga.charAt(0).toUpperCase() + t.tga.slice(1);
  function ch(val, label) {
    var sel = d.choice === val ? ' sel-' + val : '';
    return '<button type="button" class="choice' + sel + '" data-topic="' + t.id + '" data-choice="' + val + '">' + label + '</button>';
  }
  return '' +
    '<div class="topic" id="topic-' + t.id + '">' +
      '<div class="topic-head"><h3 class="topic-name">' + esc(t.name) + '</h3><span class="badge ' + t.tga + '">' + tgaLabel + '</span></div>' +
      proof +
      '<div class="choices">' + ch('approve', 'Approve') + ch('change', 'Change') + ch('drop', 'Drop') + '</div>' +
      '<div class="note-wrap"><label for="note-' + t.id + '">Note (optional)</label>' +
        '<textarea id="note-' + t.id + '" data-note="' + t.id + '" placeholder="Anything you want us to know about this topic">' + esc(d.note || '') + '</textarea>' +
      '</div>' +
    '</div>';
}

function pageNoteBlock(pageId, label) {
  return '' +
    '<div class="page-note">' +
      '<div class="note-wrap"><label for="pn-' + esc(pageId) + '">' + esc(label) + '</label>' +
      '<textarea id="pn-' + esc(pageId) + '" data-pagenote="' + esc(pageId) + '" placeholder="Optional, a note about this whole section">' + esc(state.pageNotes[pageId] || '') + '</textarea></div>' +
    '</div>';
}

function viewGuardrails() {
  return '' +
    '<p class="sec-num">Before we start</p>' +
    '<h1 class="sec-title">Winnability, structure and the guardrails</h1>' +
    '<p class="sec-lead">A few things that apply across every topic, so you have the full picture before you submit.</p>' +
    '<div class="callout warn"><h4>A competitor ranking is not a promise we will rank</h4><p>Competitor presence shows the demand is real, not that we will rank quickly. The broad, high-demand health terms, like arthritis, multiple sclerosis or nausea, are mostly held by government and major health sites such as Healthdirect and Better Health, so treat those as long-term authority plays. Our early wins come from the focused, lower-competition explainers where the cannabis clinics, not the health giants, own the results.</p></div>' +
    '<div class="callout ok"><h4>Fewer, deeper pages, not 44 thin ones</h4><p>Some topics are best built as one strong pillar page with sections rather than separate thin pages, the way Polln covers several on a single article. So the topics here become a smaller set of deeper pages, which ranks better and reads better.</p></div>' +
    '<div class="callout ok"><h4>Everything stays inside TGA and AHPRA boundaries</h4><p>No claim that a product or cannabis treats, cures or helps any condition. Symptom and condition pages stay general and helpful, never tied to a product. Nothing publishes without your sign-off.</p></div>' +
    '<div class="callout warn"><h4>Two separate checks, not one</h4><p>Clinical review and advertising compliance are different risks. Your named doctor confirms the content is medically accurate. That does not make it compliant with the Therapeutic Goods Act, which can treat health content from a clinic that sells access to prescription medicines as advertising to the public. Every Care and Restricted page gets both checks before it goes live.</p></div>' +
    '<div class="callout bad"><h4>Hold the Restricted conditions until legal sign-off</h4><p>The Restricted rows, anxiety, depression and low mood, PTSD, ADHD and epilepsy, sit inside the same TGA territory as the warning Hellomello has already received, and as you noted, Polln and Alternaleaf have run into trouble here. A competitor publishing it is a sign of their risk appetite, not a green light for us. Hold every Restricted condition until it has had a compliance and legal review, separate from clinical review, and drop the Schedule-controlled mental health conditions if there is any doubt.</p></div>' +
    pageNoteBlock('guardrails', 'Your note on the guardrails');
}

function viewReview() {
  var counts = { approve: 0, change: 0, drop: 0 };
  ALL_TOPICS.forEach(function (x) { var c = (state.decisions[x.topic.id] || {}).choice; if (c) counts[c]++; });
  var todo = TOTAL - counts.approve - counts.change - counts.drop;
  var html = '' +
    '<p class="sec-num">Last step</p>' +
    '<h1 class="sec-title">Review &amp; submit</h1>' +
    '<p class="sec-lead">Here is everything in one place. You can jump back to any section to change an answer, then submit.</p>' +
    '<div class="tally">' +
      '<div class="cell approve"><div class="n">' + counts.approve + '</div><div class="l">Approve</div></div>' +
      '<div class="cell change"><div class="n">' + counts.change + '</div><div class="l">Change</div></div>' +
      '<div class="cell drop"><div class="n">' + counts.drop + '</div><div class="l">Drop</div></div>' +
      '<div class="cell todo"><div class="n">' + todo + '</div><div class="l">Not decided</div></div>' +
    '</div>';
  if (todo > 0) html += '<div class="banner warn">' + todo + ' topic' + (todo === 1 ? '' : 's') + ' still need a decision. You can submit anyway, and anything left blank is recorded as "not decided".</div>';
  else html += '<div class="banner ok">Every topic has a decision. Nice work.</div>';

  GROUPS.forEach(function (g) {
    html += '<div class="review-group"><h3>' + esc(g.title) + '</h3>';
    g.topics.forEach(function (t) {
      var d = state.decisions[t.id] || {};
      var c = d.choice || 'todo';
      var label = c === 'todo' ? 'Not decided' : c.charAt(0).toUpperCase() + c.slice(1);
      html += '<div class="review-row"><div class="rn">' + esc(t.name) +
        (d.note ? '<span class="rnote">Note: ' + esc(d.note) + '</span>' : '') +
        '</div><span class="pill ' + c + '">' + label + '</span></div>';
    });
    if (state.pageNotes['group:' + g.id]) html += '<div class="review-row"><div class="rn"><em>Section note:</em> ' + esc(state.pageNotes['group:' + g.id]) + '</div></div>';
    html += '</div>';
  });

  html += '<div class="field"><label for="who2">Your name</label><input type="text" id="who2" placeholder="e.g. Rod" value="' + esc(state.meta.submitterName) + '"></div>';
  html += '<p style="font-size:13px;color:var(--muted)">When you submit, your answers are emailed straight to the Bright Data team.</p>';
  return html;
}

function viewSubmitted() {
  var msg = submitMode === 'mailto'
    ? 'Your email app has opened with everything filled in, just press send to deliver your sign-off to the Bright Data team. '
    : 'Your decisions have been emailed to the Bright Data team. Thanks for taking the time. ';
  return '' +
    '<div class="submitted-box">' +
      '<p class="sec-num">Thank you</p>' +
      '<div class="big">Sign-off submitted</div>' +
      '<p style="color:var(--muted);max-width:52ch;margin:0 auto 14px">' + msg + 'You can close this page, or ' +
      '<button class="btn-link" id="reopen">review your answers again</button>.</p>' +
    '</div>';
}

/* ---- Wiring ------------------------------------------------------ */
function wire(step) {
  var root = $('#pageRoot');

  var who = root.querySelector('#who');
  if (who) who.addEventListener('input', function () { state.meta.submitterName = who.value; scheduleSave(); });
  var who2 = root.querySelector('#who2');
  if (who2) who2.addEventListener('input', function () { state.meta.submitterName = who2.value; scheduleSave(); });

  Array.prototype.forEach.call(root.querySelectorAll('.choice'), function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-topic');
      var choice = btn.getAttribute('data-choice');
      var d = state.decisions[id] || {};
      d.choice = d.choice === choice ? '' : choice; // tap again to clear
      state.decisions[id] = d;
      // update just this card's buttons
      var card = document.getElementById('topic-' + id);
      Array.prototype.forEach.call(card.querySelectorAll('.choice'), function (b) {
        b.className = 'choice' + (d.choice && b.getAttribute('data-choice') === d.choice ? ' sel-' + d.choice : '');
      });
      renderFoot();
      scheduleSave();
    });
  });

  Array.prototype.forEach.call(root.querySelectorAll('[data-note]'), function (ta) {
    ta.addEventListener('input', function () {
      var id = ta.getAttribute('data-note');
      var d = state.decisions[id] || {};
      d.note = ta.value;
      state.decisions[id] = d;
      scheduleSave();
    });
  });

  Array.prototype.forEach.call(root.querySelectorAll('[data-pagenote]'), function (ta) {
    ta.addEventListener('input', function () {
      state.pageNotes[ta.getAttribute('data-pagenote')] = ta.value;
      scheduleSave();
    });
  });

  var reopen = root.querySelector('#reopen');
  if (reopen) reopen.addEventListener('click', function () { submitted = false; go(STEPS.length - 1); });
}

/* ---- Navigation -------------------------------------------------- */
function go(i) { if (i < 0 || i > STEPS.length - 1) return; current = i; render(); }

function onNext() {
  if (STEPS[current].id === 'review') { if (!submitted) submit(); return; }
  go(current + 1);
}

/* ---- Submit ------------------------------------------------------ */
function submit() {
  var next = $('#btnNext');
  next.disabled = true; next.textContent = 'Submitting\u2026';
  state.meta.submittedAt = new Date().toISOString();
  saveLocal();
  fetch(API + '?action=submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildExport())
  }).then(function (r) { return r.json(); }).then(function (res) {
    submitted = true;
    if (res && res.emailed) {
      submitMode = 'email';
      setSaveState('Submitted, email sent', 'saved');
    } else {
      submitMode = 'mailto';
      setSaveState('Submitted, opening your email', 'saved');
      downloadBackup();
      if (res && res.mailto) { try { window.location.href = res.mailto; } catch (e) {} }
    }
    render();
  }).catch(function () {
    submitted = true;
    submitMode = 'mailto';
    setSaveState('Submitted (backup downloaded)', 'saved');
    downloadBackup();
    render();
  });
}

function downloadBackup() {
  try {
    var payload = JSON.stringify(buildExport(), null, 2);
    var blob = new Blob([payload], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    var who = (state.meta.submitterName || 'hellomello').replace(/[^a-z0-9]+/gi, '-').toLowerCase();
    a.href = url;
    a.download = 'content-signoff-' + who + '-' + new Date().toISOString().slice(0, 10) + '.json';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  } catch (e) {}
}

// A readable export with topic names spelled out, not just ids.
function buildExport() {
  var out = { submittedBy: state.meta.submitterName, submittedAt: state.meta.submittedAt, groups: [] };
  GROUPS.forEach(function (g) {
    var grp = { group: g.title, sectionNote: state.pageNotes['group:' + g.id] || '', topics: [] };
    g.topics.forEach(function (t) {
      var d = state.decisions[t.id] || {};
      grp.topics.push({ topic: t.name, tga: t.tga, decision: d.choice || 'not decided', note: d.note || '' });
    });
    out.groups.push(grp);
  });
  out.guardrailsNote = state.pageNotes['guardrails'] || '';
  return out;
}

/* ---- Boot -------------------------------------------------------- */
$('#btnBack').addEventListener('click', function () { go(current - 1); });
$('#btnNext').addEventListener('click', onNext);

loadState().then(function () { render(); setSaveState('Ready'); });

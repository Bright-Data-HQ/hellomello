#!/usr/bin/env python3
"""Analyze Nuleaf Clinics exports and emit a JSON blob for the deck."""
import csv, json, re, os, collections, urllib.parse, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                              # competitors/candor
DATA = os.path.join(ROOT, 'data')
RAW  = os.path.join(DATA, 'raw')
PRES = os.path.join(ROOT, 'presentation')

def _find(pattern):
    matches = sorted(glob.glob(os.path.join(RAW, pattern)))
    return matches[-1] if matches else None

POS = _find('nuleafclinics.com.au-organic.Positions-*.csv')
PAGES = _find('nuleafclinics.com.au-organic.PagesV3-*.csv')
BL = _find('nuleafclinics.com.au-backlinks_pages*.csv')
NOTES = os.path.join(DATA, 'notes.json')

# ---------- topic taxonomy ----------
# tuples of (topic, regex). first match wins.
TOPICS = [
    ("Brand",            r"(\bnuleaf\b|nu leaf|cannihelp)"),
    ("Login / Portal",   r"(login|log in|log-in|portal|sign[- ]?in|account)"),
    ("Pricing",          r"(price|pricing|cost|cheap|discount|coupon|promo|free)"),
    ("Reviews",          r"(review|reddit|trustpilot|complaint)"),
    ("Contact / Support",r"(contact|phone|email|support|help|address|hours)"),
    ("Clinic / Doctor",  r"(doctor|gp|clinic|appointment|consult|prescriber|prescription|script|telehealth)"),
    ("Locations",        r"(sydney|melbourne|brisbane|perth|adelaide|canberra|hobart|darwin|gold coast|newcastle|wollongong|nsw|qld|vic|wa|sa|tas|act|nt|australia|near me)"),
    ("Conditions",       r"(anxiety|pain|sleep|insomnia|adhd|ptsd|depress|chronic|migraine|fibromyalgia|nausea|cancer|epilep|ms|arthritis|menopause|endometri)"),
    ("Product / Strain", r"(strain|flower|oil|tincture|vape|cartridge|gummies|cbd|thc|sativa|indica|hybrid|capsule|spray|lozenge|10:?10|20:?1|1:?1|cbn|cbg)"),
    ("Eligibility / Legal", r"(eligib|qualify|legal|approved|tga|sas|authorised prescriber|how to get|access|apply|how do i)"),
    ("Education / How-to",  r"(what is|how to|how does|guide|benefit|effect|side effect|dosage|dose|vs |difference|explained|work)"),
    ("Competitors",      r"(alterna ?leaf|montu|herbly|polln|dispensed|easykind|candor|acacia|greencare|horizon|econohealth|healing leaves|cannatrek|little green pharma|honahlee|releaf|hellomello|mello)"),
]

def categorize(kw):
    kw_l = kw.lower()
    for name, pat in TOPICS:
        if re.search(pat, kw_l):
            return name
    return "Other"

# ---------- load positions ----------
positions = []
with open(POS, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        try:
            pos = int(row['Position'] or 0)
            vol = int(row['Search Volume'] or 0)
            traffic = float(row['Traffic'] or 0)
            kd = float(row['Keyword Difficulty'] or 0)
            cpc = float(row['CPC'] or 0)
        except ValueError:
            continue
        positions.append({
            'kw': row['Keyword'], 'pos': pos, 'vol': vol, 'kd': kd, 'cpc': cpc,
            'traffic': traffic, 'url': row['URL'],
            'intents': row.get('Keyword Intents','').strip(),
            'serp': row.get('SERP Features by Keyword',''),
            'topic': categorize(row['Keyword']),
        })

total_traffic = sum(p['traffic'] for p in positions)
total_keywords = len(positions)

# ---------- topic rollup ----------
topic_rollup = collections.defaultdict(lambda: {'kw':0, 'traffic':0.0, 'examples':[]})
for p in positions:
    t = topic_rollup[p['topic']]
    t['kw'] += 1
    t['traffic'] += p['traffic']
for p in sorted(positions, key=lambda x: -x['traffic']):
    t = topic_rollup[p['topic']]
    if len(t['examples']) < 3:
        t['examples'].append({'kw': p['kw'], 'pos': p['pos'], 'vol': p['vol'], 'traffic': p['traffic']})

topics = [{'name':k, **v, 'traffic': round(v['traffic'])} for k,v in topic_rollup.items()]
topics.sort(key=lambda x: -x['traffic'])

# ---------- position buckets ----------
pos_buckets = [
    ('#1',           lambda p: p==1),
    ('#2–3',         lambda p: 2<=p<=3),
    ('#4–10',        lambda p: 4<=p<=10),
    ('#11–20',       lambda p: 11<=p<=20),
    ('#21–50',       lambda p: 21<=p<=50),
    ('#51–100',      lambda p: 51<=p<=100),
]
pos_dist = []
for label, fn in pos_buckets:
    items = [p for p in positions if fn(p['pos'])]
    pos_dist.append({'label':label, 'kw':len(items), 'traffic':round(sum(p['traffic'] for p in items))})

# ---------- intent split ----------
intent_split = collections.defaultdict(lambda: {'kw':0, 'traffic':0.0})
for p in positions:
    primary = (p['intents'].split(',')[0] if p['intents'] else 'unknown').strip().title() or 'Unknown'
    intent_split[primary]['kw'] += 1
    intent_split[primary]['traffic'] += p['traffic']
intent_split = [{'name':k, 'kw':v['kw'], 'traffic':round(v['traffic'])} for k,v in intent_split.items()]
intent_split.sort(key=lambda x: -x['traffic'])

# ---------- brand vs non-brand ----------
brand_re = re.compile(r"(\bnuleaf\b|nu leaf|cannihelp)", re.I)
brand_traffic = sum(p['traffic'] for p in positions if brand_re.search(p['kw']))
nonbrand_traffic = total_traffic - brand_traffic
brand_kw = sum(1 for p in positions if brand_re.search(p['kw']))
nonbrand_kw = total_keywords - brand_kw

# ---------- pages ----------
pages = []
with open(PAGES, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        try:
            traffic = float(row['Traffic'] or 0)
            kw = int(row['Number of Keywords'] or 0)
        except ValueError:
            continue
        pages.append({
            'url': row['URL'], 'traffic': traffic, 'kw': kw,
            'traffic_pct': float(row['Traffic (%)'] or 0),
            'intent': row.get('Primary Intent','—'),
            'top_kw': row.get('Top Keyword','—'),
        })
pages.sort(key=lambda x: -x['traffic'])

# subdomain / section split (Candor: www + app subdomains)
subdomain_split = collections.defaultdict(lambda: {'traffic':0.0, 'pages':0})
for pg in pages:
    host = urllib.parse.urlparse(pg['url']).netloc
    if host.startswith('app.'): sub = 'app'
    elif host.startswith('www.') or host == 'nuleafclinics.com.au': sub = 'www'
    else: sub = host or 'other'
    subdomain_split[sub]['traffic'] += pg['traffic']
    subdomain_split[sub]['pages'] += 1
subdomain_split = [{'name':k, 'traffic':round(v['traffic']), 'pages':v['pages']} for k,v in subdomain_split.items()]
subdomain_split.sort(key=lambda x: -x['traffic'])

# ---------- backlinks (optional — SEMrush backlinks export not always available) ----------
backlinks = []
if BL and os.path.exists(BL):
    with open(BL, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                bl = int(row['Backlinks'] or 0)
                dom = int(row['Domains'] or 0)
            except ValueError:
                continue
            backlinks.append({
                'url': row['Source url'], 'title': row.get('Source title',''),
                'code': row.get('Response code',''),
                'backlinks': bl, 'domains': dom,
            })
backlinks.sort(key=lambda x: -x['backlinks'])

total_backlinks = sum(b['backlinks'] for b in backlinks)
total_ref_domains_top = sum(b['domains'] for b in backlinks[:20])  # rough

# group backlinks by content type
def bl_type(url):
    u = url.lower()
    if '/treatments/' in u: return 'Treatments'
    if '/education/' in u: return 'Education / Blog'
    if u.rstrip('/').endswith('nuleafclinics.com.au'): return 'Homepage'
    return 'Other'

bl_rollup = collections.defaultdict(lambda: {'backlinks':0, 'pages':0})
for b in backlinks:
    t = bl_type(b['url'])
    bl_rollup[t]['backlinks'] += b['backlinks']
    bl_rollup[t]['pages'] += 1
bl_rollup = [{'name':k, **v} for k,v in bl_rollup.items()]
bl_rollup.sort(key=lambda x: -x['backlinks'])

# ---------- content clusters from page URLs (Candor is brand-fortress + thin treatments) ----------
CLUSTER_RULES = [
    ("Homepage",                 r"^https?://(www\.)?nuleafclinics\.com\.au/?$"),
    ("Contact / about",          r"candormedical\.com/(contact|about|faq|how-candor-works|work-with-us)"),
    ("Legal",                    r"candormedical\.com/(terms-and-conditions|privacy-policy|disclaimer)"),
]

def cluster_of(url):
    for name, pat in CLUSTER_RULES:
        if re.search(pat, url):
            return name
    return "Other pages"

clusters = collections.defaultdict(lambda: {'pages': 0, 'traffic': 0.0, 'kw': 0, 'examples': []})
for pg in pages:
    c = cluster_of(pg['url'])
    clusters[c]['pages'] += 1
    clusters[c]['traffic'] += pg['traffic']
    clusters[c]['kw'] += pg['kw']
# add example pages (top 3 by traffic per cluster)
for pg in sorted(pages, key=lambda x: -x['traffic']):
    c = cluster_of(pg['url'])
    if len(clusters[c]['examples']) < 4:
        clusters[c]['examples'].append({
            'url': pg['url'], 'traffic': round(pg['traffic']),
            'kw': pg['kw'], 'top_kw': pg['top_kw'], 'intent': pg['intent']
        })

cluster_list = [{'name':k, 'pages':v['pages'], 'traffic':round(v['traffic']), 'kw':v['kw'], 'examples':v['examples']} for k,v in clusters.items()]
cluster_list.sort(key=lambda x: -x['traffic'])

# ---------- per-topic top keywords (for the topic deep-dive slides) ----------
topic_keywords = collections.defaultdict(list)
for p in sorted(positions, key=lambda x: (-x['traffic'], -x['vol'])):
    topic_keywords[p['topic']].append(p)
topic_detail = {}
for tname, items in topic_keywords.items():
    nonbrand = [p for p in items if not brand_re.search(p['kw'])]
    topic_detail[tname] = {
        'total_kw': len(items),
        'total_traffic': round(sum(p['traffic'] for p in items)),
        'top1_count': sum(1 for p in items if p['pos']==1),
        'page2_count': sum(1 for p in items if 11<=p['pos']<=20),
        'avg_vol': round(sum(p['vol'] for p in items)/max(1,len(items))),
        'top_keywords': [{'kw':p['kw'],'pos':p['pos'],'vol':p['vol'],'traffic':round(p['traffic']),'url':p['url']} for p in items[:10]],
        'top_nonbrand': [{'kw':p['kw'],'pos':p['pos'],'vol':p['vol'],'traffic':round(p['traffic'])} for p in nonbrand[:8]],
    }

# ---------- locations breakdown (since 1,128 location keywords is a real story) ----------
LOC_PATTERNS = [
    ('Sydney / NSW', r'(sydney|nsw|newcastle|wollongong)'),
    ('Melbourne / VIC', r'(melbourne|victoria|geelong|\bvic\b)'),
    ('Brisbane / QLD', r'(brisbane|gold coast|sunshine coast|\bqld\b|queensland)'),
    ('Perth / WA', r'(perth|\bwa\b)'),
    ('Adelaide / SA', r'(adelaide|\bsa\b)'),
    ('Canberra / ACT', r'(canberra|\bact\b)'),
    ('Tasmania', r'(hobart|tasmania|\btas\b)'),
    ('Darwin / NT', r'(darwin|\bnt\b)'),
    ('National / "Australia"', r'(australia|aus\b|\baussie\b)'),
    ('"near me"', r'near me'),
]
loc_rollup = collections.defaultdict(lambda: {'kw':0, 'traffic':0.0})
for p in positions:
    if p['topic'] != 'Locations': continue
    kw_l = p['kw'].lower()
    matched = False
    for name, pat in LOC_PATTERNS:
        if re.search(pat, kw_l):
            loc_rollup[name]['kw'] += 1
            loc_rollup[name]['traffic'] += p['traffic']
            matched = True
            break
    if not matched:
        loc_rollup['Other']['kw'] += 1
        loc_rollup['Other']['traffic'] += p['traffic']
loc_list = [{'name':k, 'kw':v['kw'], 'traffic':round(v['traffic'])} for k,v in loc_rollup.items()]
loc_list.sort(key=lambda x: -x['kw'])

# ---------- conditions breakdown ----------
COND_PATTERNS = [
    ('Anxiety', r'anxi'),
    ('Sleep / insomnia', r'(sleep|insomnia)'),
    ('Chronic pain', r'(chronic|pain|migraine|fibromy|arthritis)'),
    ('ADHD', r'adhd'),
    ('PTSD', r'ptsd'),
    ('Depression', r'depress'),
    ('Nausea', r'nausea'),
    ('Cancer / palliative', r'cancer'),
    ('Endo / menopause', r'(endometri|menopause)'),
    ('Epilepsy / MS', r'(epilep|\bms\b)'),
]
cond_rollup = collections.defaultdict(lambda: {'kw':0, 'traffic':0.0, 'examples':[]})
for p in positions:
    if p['topic'] != 'Conditions': continue
    kw_l = p['kw'].lower()
    for name, pat in COND_PATTERNS:
        if re.search(pat, kw_l):
            cond_rollup[name]['kw'] += 1
            cond_rollup[name]['traffic'] += p['traffic']
            if len(cond_rollup[name]['examples']) < 2:
                cond_rollup[name]['examples'].append({'kw':p['kw'],'pos':p['pos'],'vol':p['vol']})
            break
cond_list = [{'name':k, 'kw':v['kw'], 'traffic':round(v['traffic']), 'examples':v['examples']} for k,v in cond_rollup.items()]
cond_list.sort(key=lambda x: -x['kw'])

# ---------- pillars: pillar = topic, sub-clusters derived per pillar ----------
# Reuse Locations/Conditions rollups as sub-clusters. For other pillars derive
# sub-clusters via bigram/unigram frequency, then assign each keyword to its
# best-matching label (greedy, most-frequent first).
PILLAR_STOPWORDS = set("""
the and or for to in of a an near me how what is does why when where can do i my our your
which from with by on at as it that this be are was were has have had not no yes than then
so if you we they he she them about into out up down over under more most less few many any
all some such here there now today tomorrow new old best better worst good bad cheap free
""".split())
PILLAR_BRAND_TOKENS = set("nuleaf cannihelp".split())

def _tokens(kw):
    toks = re.findall(r"[a-z][a-z]+", kw.lower())
    return [t for t in toks if t not in PILLAR_STOPWORDS and t not in PILLAR_BRAND_TOKENS and len(t) > 2]

def _derive_sub_clusters(items, max_labels=6):
    """Generic bigram/unigram sub-cluster extraction for a pillar."""
    counter = collections.Counter()
    per_kw = []
    for p in items:
        toks = _tokens(p['kw'])
        per_kw.append((p, toks))
        for t in toks:
            counter[t] += 1
        for a, b in zip(toks, toks[1:]):
            counter[f"{a} {b}"] += 3  # weight bigrams (more specific)
    # candidate labels: prefer multi-word, then longer single-words, drop trivial
    candidates = [l for l, c in counter.most_common(40) if c >= 2]
    # promote bigrams above unigrams that are substrings of them
    bigrams = [l for l in candidates if ' ' in l]
    unigrams = [l for l in candidates if ' ' not in l and not any(l in b.split() for b in bigrams)]
    labels = (bigrams + unigrams)[:max_labels]
    sub = {l: {'label': l, 'kw': 0, 'traffic': 0.0, 'examples': []} for l in labels}
    other = {'label': 'Other', 'kw': 0, 'traffic': 0.0, 'examples': []}
    for p, toks in per_kw:
        kw_l = p['kw'].lower()
        bucket = None
        for l in labels:
            if l in kw_l:
                bucket = sub[l]; break
        if bucket is None:
            bucket = other
        bucket['kw'] += 1
        bucket['traffic'] += p['traffic']
        if len(bucket['examples']) < 2:
            bucket['examples'].append({'kw': p['kw'], 'pos': p['pos'], 'traffic': round(p['traffic'])})
    result = [s for s in sub.values() if s['kw'] > 0]
    if other['kw'] > 0:
        result.append(other)
    for s in result:
        s['traffic'] = round(s['traffic'])
        s['label'] = s['label'].title() if s['label'] != 'Other' else 'Other'
    result.sort(key=lambda x: -x['traffic'])
    return result

# pre-built sub-cluster lookups for the two pillars that already have curated rollups
_loc_subs = [{'label': l['name'], 'kw': l['kw'], 'traffic': l['traffic'], 'examples': []} for l in loc_list]
_cond_subs = [{'label': c['name'], 'kw': c['kw'], 'traffic': c['traffic'], 'examples': c['examples']} for c in cond_list]

pillars = []
positions_by_topic = collections.defaultdict(list)
for p in positions:
    positions_by_topic[p['topic']].append(p)

for tname, items in positions_by_topic.items():
    if not items:
        continue
    if tname == 'Locations':
        subs = _loc_subs[:]
    elif tname == 'Conditions':
        subs = _cond_subs[:]
    else:
        subs = _derive_sub_clusters(items)
    total_kw = len(items)
    total_tr = sum(p['traffic'] for p in items)
    # top URLs hosting this pillar's keywords
    url_rollup = collections.defaultdict(lambda: {'traffic': 0.0, 'kw': 0})
    for p in items:
        u = url_rollup[p['url']]
        u['traffic'] += p['traffic']; u['kw'] += 1
    top_urls = sorted(
        [{'url': u, 'traffic': round(v['traffic']), 'kw': v['kw']} for u, v in url_rollup.items()],
        key=lambda x: -x['traffic'])[:3]
    pillars.append({
        'name': tname,
        'total_kw': total_kw,
        'total_traffic': round(total_tr),
        'efficiency': round(total_tr / total_kw, 2) if total_kw else 0,
        'top1_count': sum(1 for p in items if p['pos'] == 1),
        'sub_clusters': subs[:8],
        'top_urls': top_urls,
    })
pillars.sort(key=lambda x: -x['total_traffic'])

# ---------- backlink histogram by host TLD-ish ----------
def host_class(url):
    u = url.lower()
    host = urllib.parse.urlparse(url).netloc.lower()
    if any(t in host for t in ('news.com.au','abc.net.au','smh.com.au','theage','theguardian','9news','7news','dailymail','heraldsun','couriermail','perthnow','financialreview','nine.com.au','sbs.com.au','crikey')):
        return 'News / publisher'
    if any(t in host for t in ('reddit.com','quora.com','facebook.com','linkedin.com','twitter.com','x.com','youtube.com','tiktok.com')):
        return 'Social / forum'
    if any(t in host for t in ('crunchbase','similarweb','trustpilot','productreview','glassdoor','seek.com.au','indeed','wikipedia')):
        return 'Directory / aggregator'
    if host.endswith('.gov.au') or host.endswith('.edu.au') or host.endswith('.org.au'):
        return 'Gov / edu / NGO'
    if any(t in host for t in ('cannabis','weed','420','hemp','medicinal','marijuana')):
        return 'Cannabis vertical'
    if host.endswith('.com.au') or host.endswith('.au'):
        return 'AU commercial'
    return 'International / other'

bl_host_rollup = collections.defaultdict(lambda: {'backlinks':0,'pages':0})
for b in backlinks:
    c = host_class(b['url'])
    bl_host_rollup[c]['backlinks'] += b['backlinks']
    bl_host_rollup[c]['pages'] += 1
bl_host_rollup = [{'name':k, **v} for k,v in bl_host_rollup.items()]
bl_host_rollup.sort(key=lambda x: -x['backlinks'])

# crude backlinks-per-page histogram
hist_buckets = [(1,1),(2,5),(6,20),(21,50),(51,200),(201,10000)]
hist_labels  = ['1','2–5','6–20','21–50','51–200','200+']
bl_hist = []
for (lo,hi),lab in zip(hist_buckets, hist_labels):
    items = [b for b in backlinks if lo <= b['backlinks'] <= hi]
    bl_hist.append({'label':lab, 'pages':len(items), 'backlinks':sum(b['backlinks'] for b in items)})

# ---------- winners / losers by traffic share ----------
top_winners = pages[:10]
# "losers" = pages with ≥3 keywords but ≤5 visits (decaying or dormant)
losers = [p for p in pages if p['kw'] >= 3 and p['traffic'] <= 5]
losers.sort(key=lambda x: -x['kw'])
top_losers = losers[:10]

# ---------- notes.json ----------
notes = {}
if os.path.exists(NOTES):
    with open(NOTES, 'r') as f:
        notes = json.load(f)

# ---------- output ----------
out = {
    'totals': {
        'traffic': round(total_traffic),
        'keywords': total_keywords,
        'pages': len(pages),
        'backlinks': total_backlinks,
        'backlinked_pages': len(backlinks),
        'brand_traffic': round(brand_traffic),
        'nonbrand_traffic': round(nonbrand_traffic),
        'brand_kw': brand_kw,
        'nonbrand_kw': nonbrand_kw,
    },
    'topics': topics,
    'topic_detail': topic_detail,
    'pillars': pillars,
    'content_clusters': cluster_list,
    'locations': loc_list,
    'conditions': cond_list,
    'position_distribution': pos_dist,
    'intents': intent_split,
    'top_pages': pages[:12],
    'top_winners': top_winners,
    'top_losers': top_losers,
    'subdomains': subdomain_split,
    'top_keywords': sorted(positions, key=lambda x: -x['traffic'])[:15],
    'nonbrand_keywords': sorted([p for p in positions if not brand_re.search(p['kw'])], key=lambda x: -x['traffic'])[:12],
    'top_backlinks': backlinks[:10],
    'backlink_groups': bl_rollup,
    'backlink_hosts': bl_host_rollup,
    'backlink_histogram': bl_hist,
    'notes': notes,
}

with open(os.path.join(DATA, 'data.json'), 'w') as f:
    json.dump(out, f, indent=2)
with open(os.path.join(PRES, 'data.js'), 'w') as f:
    f.write('window.DATA = ' + json.dumps(out) + ';\n')

print(f"keywords={total_keywords}  traffic={int(total_traffic)}  topics={len(topics)}  pages={len(pages)}  bl_pages={len(backlinks)}")
for t in topics[:8]:
    print(f"  {t['name']:24s} kw={t['kw']:5d}  traffic={t['traffic']:6d}")

"""Builds shop.html (every live Etsy item) and the homepage #videos section from tools/products.tsv and VIDEOS below.
Run from the repo root: python3 tools/build_shop.py"""
import html, re, json

E = html.escape
rows = []
for ln in open("tools/products.tsv", encoding="utf-8"):
    ln = ln.rstrip("\n")
    if not ln:
        continue
    lid, img, price, title = ln.split("\t")
    rows.append(dict(url="https://www.etsy.com/listing/" + lid, img="https://images.printify.com/mockup/" + img,
                     price=float(price), title=title))

TYPES = [("Sweatshirts", r"sweatshirt"), ("Shirts", r"\bshirts?\b|\btee\b"), ("Ornaments", r"ornament"),
         ("Mugs", r"\bmug\b"), ("Blankets", r"blanket"), ("Ring dishes", r"ring dish")]
TAGS = {"grandma": r"grandma|nana|mimi|gigi|abuela|abuelita|lita|nonna|yaya|lola|gram\b|grandpa|papa",
        "mom": r"\bmama\b|\bmom\b",
        "pets": r"\bpet\b|\bdog\b|\bcat\b",
        "baby": r"baby|youth|kids|gingerbread",
        "wedding": r"couple|bride|bridesmaid|wedding|our first|nuestra primera|new home|nuevo hogar",
        "christmas": r"christmas|navidad|ornament",
        "espanol": r"navidad|abuela|abuelita|\blita\b|ponche|tamales|probable|primera|nuestra|spanish"}
CHIPS = [("all", "All"), ("grandma", "Grandma & Grandpa"), ("mom", "Mom"), ("pets", "Pets"), ("baby", "Baby & kids"),
         ("wedding", "Couples & weddings"), ("christmas", "Christmas"), ("espanol", "En español")]


def ptype(t):
    tl = t.lower()
    for name, rx in TYPES:
        if re.search(rx, tl):
            return name
    return "More gifts"


def short(t):
    return t.split(",")[0]


def card(r, btn="Shop on Etsy"):
    tl = r["title"].lower()
    tags = " ".join(k for k, rx in TAGS.items() if re.search(rx, tl))
    rest = ", ".join(x.strip() for x in r["title"].split(",")[1:])
    return f'''      <article class="pgift" data-tags="{tags}" data-q="{E(tl)}">
        <a class="pgift-img" href="{r['url']}" target="_blank" rel="noopener"><img src="{r['img']}" alt="{E(short(r['title']))}, product mockup" width="600" height="600" loading="lazy"></a>
        <h3>{E(short(r['title']))}</h3>
        <p>{E(rest)}</p>
        <div class="pgift-foot"><span class="price"><small>From</small>${r['price']:.2f}</span><a class="btn btn-primary btn-small" href="{r['url']}" target="_blank" rel="noopener">{btn}</a></div>
      </article>
'''


groups = {}
for r in rows:
    groups.setdefault(ptype(r["title"]), []).append(r)
order = [t for t, _ in TYPES] + ["More gifts"]

src = open("gifts-for-grandma.html", encoding="utf-8").read()
head = src[:src.index("<script type=\"application/ld+json\">")]
TITLE = "Shop All Personalized Gifts: Sweatshirts, Ornaments, Mugs and Blankets | Accessoriex"
DESC = f"Every Accessoriex personalized gift in one place: {len(rows)} sweatshirts, shirts, ornaments, mugs, blankets and ring dishes with the names you choose. Made to order in the US."
head = re.sub(r"<title>.*?</title>", f"<title>{E(TITLE)}</title>", head, flags=re.S)
head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + E(DESC), head)
head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(TITLE), head)
head = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + E(DESC), head)
head = head.replace("https://accessoriex.com/gifts-for-grandma.html", "https://accessoriex.com/shop.html")
extra_css = """<style>
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 10px}
.chip{border:1px solid var(--line);background:var(--surface);color:var(--fg);border-radius:999px;padding:7px 14px;font:inherit;font-size:.9rem;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.shop-search{width:100%;max-width:420px;padding:10px 14px;border-radius:12px;border:1px solid var(--line);background:var(--surface);color:var(--fg);font:inherit;margin:6px 0 8px}
.shop-group h2{font-family:var(--font-display);font-size:var(--step-2);margin:34px 0 12px}
.shop-empty{color:var(--muted)}
</style>
"""
NAV = '<header class="site-header"><div class="wrap"><a class="brand" href="/"><span class="brand-mark" aria-hidden="true"></span>Accessoriex</a><nav class="nav" aria-label="Main"><a class="nav-link" href="/shop.html">Shop all</a><a class="nav-link" href="/gifts-for-grandma.html">Grandma gifts</a><a class="nav-link" href="/custom-pet-gifts.html">Pet gifts</a><a class="nav-link" href="/regalos-para-abuela.html">Para Abuela</a><a class="btn btn-primary btn-small" href="/#videos">Videos</a></nav></div></header>'
FOOT = '<footer class="site-footer"><div class="wrap"><div class="footer-top"><a class="brand" href="/"><span class="brand-mark" aria-hidden="true"></span>Accessoriex</a><div class="footer-links"><a href="/shop.html">Shop all</a><a href="/#videos">Videos</a><a href="/gifts-for-grandma.html">Gifts for Grandma</a><a href="/custom-pet-gifts.html">Custom pet gifts</a><a href="/regalos-para-abuela.html">Regalos para Abuela</a></div></div><div class="legal"><p>Our own designs, sold through our Etsy shop and made to order by our US print partner. Photos are product mockups; names shown are examples.</p><p>© 2026 Accessoriex</p></div></div></footer>'
itemlist = {"@context": "https://schema.org", "@type": "ItemList", "name": "Accessoriex personalized gifts",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": r["url"], "name": short(r["title"])} for i, r in enumerate(rows)]}
body = [head, extra_css, '<script type="application/ld+json">' + json.dumps(itemlist) + "</script>\n</head>\n<body>\n", NAV,
        '\n<main>\n<section class="wrap personalized" style="padding-top:48px">\n<span class="eyebrow">Made by us · Personalized · Made to order in the US</span>\n',
        f'<h1 style="font-size:var(--step-4);margin:8px 0 12px">Shop all {len(rows)} gifts</h1>\n',
        '<p class="sub">Every piece is printed with the names, dates or photo you choose, then shipped from our US print partner. You check out securely on Etsy. For Christmas delivery in the US, order by December 10.</p>\n',
        '<input class="shop-search" id="shop-q" type="search" placeholder="Search: Nana, dog, ornament, bride…" aria-label="Search gifts">\n<div class="chips" role="group" aria-label="Filter by who it\'s for">\n']
for k, label in CHIPS:
    body.append(f'<button class="chip" type="button" data-chip="{k}" aria-pressed="{"true" if k == "all" else "false"}">{label}</button>\n')
body.append("</div>\n")
for t in order:
    if t not in groups:
        continue
    body.append(f'<div class="shop-group"><h2>{t} <small style="font-size:.6em;color:var(--muted)">({len(groups[t])})</small></h2>\n<div class="pgift-grid">\n')
    body += [card(r) for r in groups[t]]
    body.append("</div></div>\n")
body.append('<p class="shop-empty" id="shop-empty" hidden>Nothing matches yet. Try another word, or message us on Etsy for a custom request.</p>\n</section>\n</main>\n')
body.append(FOOT)
body.append("""
<script>
(function(){
  var q=document.getElementById('shop-q'), chips=[].slice.call(document.querySelectorAll('.chip')), active='all';
  function apply(){
    var term=(q.value||'').toLowerCase().trim(), shown=0;
    document.querySelectorAll('.shop-group').forEach(function(g){
      var n=0;
      g.querySelectorAll('.pgift').forEach(function(c){
        var ok=(active==='all'||(' '+c.dataset.tags+' ').indexOf(' '+active+' ')>-1)&&(!term||c.dataset.q.indexOf(term)>-1);
        c.hidden=!ok; if(ok) n++;
      });
      g.hidden=!n; shown+=n;
    });
    document.getElementById('shop-empty').hidden=shown>0;
  }
  chips.forEach(function(b){b.addEventListener('click',function(){active=b.dataset.chip;chips.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});apply();});});
  q.addEventListener('input',apply);
})();
</script>
</body>
</html>
""")
open("shop.html", "w", encoding="utf-8").write("".join(body))

# ---------- Homepage videos section ----------
VIDEOS = [
    ("vF-6XS3hALU", "Grandma sweatshirt with every grandkid's name", "7706600744966688014", "Dfkef7biWr3", ("etsy", "https://www.etsy.com/listing/4613660148/custom-grandma-sweatshirt-with-grandkids")),
    ("xJbXpI1MD7w", "Make a rental look finished in 3 easy moves", "7706639539091082510", "Dfkvb5dEbEH", ("anchor", "#picks-title")),
    ("gohZ86YhvnU", "Make a guest bed feel like a hotel bed", "7706376172585635086", "Dfi6tgLigM0", ("product", "topper")),
    ("DV0NM4JGFqI", "3 hotel details for a tidy bathroom counter", "7706267867737623822", "DfiKpD7Gezi", ("product", "caddy")),
    ("G_pyjT_Jgd0", "The gift for someone's first apartment", "7706005076460064013", "DfgV6ZwFX8c", ("product", "caddy")),
    ("4HIGiUCtH9A", "Light your living room like a designer", "7705896833448496397", "Dffl2MKFRBj", ("product", "lamp")),
    ("knm1YWKMIL0", "Make your living room feel like a boutique hotel", "7705633978237127949", "DfdxHcHjZxn", ("product", "lamp")),
    ("EYbhKDIFlko", "What 10 minutes does to a messy pantry", "7705525740938235150", "DfdBDPEkWgp", ("anchor", "#picks-title")),
    ("bHrZiDwljQg", "The blanket for the person who's always cold", None, "DfTV3LCDXgh", ("product", "blanket")),
    ("8zqDo252ckU", "Stop making your bed flat: the hotel trick", None, "DfTs_X6joeq", ("product", "comforter")),
]
v = ['  <section class="wrap videos" id="videos" aria-labelledby="videos-title">\n',
     '    <span class="eyebrow">Watch, then shop</span>\n',
     '    <h2 id="videos-title">Our latest videos</h2>\n',
     '    <p class="sub">Every video we post on TikTok, Instagram and YouTube, with the product link right under it.</p>\n',
     '    <div class="vid-grid">\n']
for yt, title, tt, ig, (kind, target) in VIDEOS:
    links = [f'<a href="https://www.youtube.com/shorts/{yt}" target="_blank" rel="noopener">YouTube</a>']
    if tt:
        links.append(f'<a href="https://www.tiktok.com/@accessoriex1/video/{tt}" target="_blank" rel="noopener">TikTok</a>')
    links.append(f'<a href="https://www.instagram.com/reel/{ig}/" target="_blank" rel="noopener">Instagram</a>')
    if kind == "etsy":
        shop = f'<a class="btn btn-primary btn-small" href="{target}" target="_blank" rel="noopener">Shop on Etsy</a>'
    elif kind == "product":
        fb = ' data-tiktok-fallback="blanket"' if target == "blanket" else ""
        shop = f'<a class="btn btn-primary btn-small" data-product="{target}"{fb} href="#picks-title">Shop this</a>'
    else:
        shop = f'<a class="btn btn-primary btn-small" href="{target}">See the picks</a>'
    v.append(f'''      <article class="vid">
        <a class="vid-thumb" href="https://www.youtube.com/shorts/{yt}" target="_blank" rel="noopener" aria-label="Watch: {E(title)}"><img src="https://i.ytimg.com/vi/{yt}/hqdefault.jpg" alt="" width="480" height="360" loading="lazy"><span class="vid-play" aria-hidden="true"></span></a>
        <h3>{E(title)}</h3>
        <div class="vid-links">{" &middot; ".join(links)}</div>
        {shop}
      </article>
''')
v.append('    </div>\n    <p class="sub"><a href="https://www.tiktok.com/@accessoriex1" target="_blank" rel="noopener">Follow @accessoriex1 on TikTok</a> for new videos every day.</p>\n  </section>\n')
VID = "".join(v)
VCSS = """.vid-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; margin-bottom: 14px; }
.vid { display: flex; flex-direction: column; gap: 8px; padding: 12px; border: 1px solid var(--line); border-radius: 16px; background: var(--surface); }
.vid-thumb { position: relative; display: block; border-radius: 12px; overflow: hidden; aspect-ratio: 9/14; background: #000; }
.vid-thumb img { width: 100%; height: 100%; object-fit: cover; }
.vid-play { position: absolute; inset: 0; margin: auto; width: 54px; height: 54px; border-radius: 50%; background: rgba(0,0,0,.55); }
.vid-play::after { content: ""; position: absolute; left: 21px; top: 16px; border-left: 16px solid #fff; border-top: 11px solid transparent; border-bottom: 11px solid transparent; }
.vid h3 { font-size: 1rem; line-height: 1.25; flex: 1; }
.vid-links { font-size: .85rem; color: var(--muted); }
.vid-links a { color: var(--muted); }
.vid .btn { align-self: flex-start; }
"""
idx = open("index.html", encoding="utf-8").read()
if "charset" not in idx[:500].lower():
    idx = '<!DOCTYPE html>\n<meta charset="utf-8">\n' + idx
idx = re.sub(r'  <section class="wrap videos" id="videos".*?</section>\n', "", idx, flags=re.S)
anchor = '  <section class="wrap shopvid" id="shop"'
idx = idx.replace(anchor, VID + "\n" + anchor, 1)
if ".vid-grid" not in idx:
    idx = idx.replace("</style>", VCSS + "</style>", 1)
# nav + personalized section link
if 'href="/shop.html">Shop all' not in idx:
    idx = idx.replace('<a class="nav-link" href="#personalized">Personalized gifts</a>',
                      '<a class="nav-link" href="/shop.html">Shop all</a>\n      <a class="nav-link" href="#videos">Videos</a>\n      <a class="nav-link" href="#personalized">Personalized gifts</a>', 1)
if 'class="btn btn-primary" href="/shop.html"' not in idx:
    idx = idx.replace('    <p class="sub">Gift guides:',
                      f'    <p><a class="btn btn-primary" href="/shop.html">Shop all {len(rows)} personalized gifts</a></p>\n    <p class="sub">Gift guides: <a href="/shop.html">Shop all</a> ·', 1)
open("index.html", "w", encoding="utf-8").write(idx)

# subpage nav/footer
for f in ["gifts-for-grandma.html", "custom-pet-gifts.html", "regalos-para-abuela.html"]:
    s = open(f, encoding="utf-8").read()
    s = re.sub(r'<header class="site-header">.*?</header>', NAV, s, count=1, flags=re.S)
    if 'footer-links"><a href="/shop.html"' not in s:
        s = s.replace('<div class="footer-links">', '<div class="footer-links"><a href="/shop.html">Shop all</a><a href="/#videos">Videos</a>', 1)
    open(f, "w", encoding="utf-8").write(s)

# sitemap
sm = open("sitemap.xml", encoding="utf-8").read()
if "shop.html" not in sm:
    sm = sm.replace("</urlset>", "  <url><loc>https://accessoriex.com/shop.html</loc><changefreq>daily</changefreq><priority>0.9</priority></url>\n</urlset>")
    open("sitemap.xml", "w", encoding="utf-8").write(sm)
print(len(rows), {t: len(g) for t, g in groups.items()})

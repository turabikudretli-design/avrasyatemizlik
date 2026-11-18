# -*- coding: utf-8 -*-
"""Avrasya Temizlik statik site üreticisi.
Çalıştır:  python _kaynak/build.py   (site kökü = bu dosyanın bir üst klasörü)
_kaynak/ içine konan hero-*.png / hizmet-*.png / ekip.png / og-kapak.png görselleri webp'ye çevrilir."""
import json, os, re, shutil, sys
from html import escape
from datetime import date

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, "_kaynak")
sys.path.insert(0, KAYNAK)
from veri import FIRMA, HIZMETLER, PROFIL, ILCELER  # noqa: E402
import eski  # noqa: E402

BUGUN = date.today().isoformat()

def kucuk(t):
    return t.replace("İ", "i").replace("I", "ı").lower()

IMG_DIR = os.path.join(KOK, "assets", "img")
HIZ = {h[0]: h for h in HIZMETLER}

# ---------- görseller ----------
def gorselleri_hazirla():
    os.makedirs(IMG_DIR, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        return
    for f in os.listdir(KAYNAK):
        ad, uz = os.path.splitext(f)
        if kucuk(uz) not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        hedef = os.path.join(IMG_DIR, ad + ".webp")
        kaynak = os.path.join(KAYNAK, f)
        if os.path.exists(hedef) and os.path.getmtime(hedef) >= os.path.getmtime(kaynak):
            continue
        im = Image.open(kaynak).convert("RGB")
        hedef_g = 1200 if ad.startswith("og") else (1400 if ad.startswith(("hero", "ekip")) else 900)
        if im.width > hedef_g:
            im = im.resize((hedef_g, round(im.height * hedef_g / im.width)), Image.LANCZOS)
        im.save(hedef, "WEBP", quality=80, method=6)
        print("görsel:", ad + ".webp", im.size)

def gorsel_var(ad):
    return os.path.exists(os.path.join(IMG_DIR, ad + ".webp"))

IKON = {
    "tel": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.6.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.3c0-.1-.2-.2-.5-.3z"/></svg>',
    "kalp": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 1 0-7.8 7.8L12 21.2l8.8-8.8a5.5 5.5 0 0 0 0-7.8z"/></svg>',
    "pirlanta": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l2.2 5.8L20 11l-5.8 2.2L12 19l-2.2-5.8L4 11l5.8-2.2z"/></svg>',
    "ev": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg>',
    "takvim": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="3"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h10"/></svg>',
    "posta": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3 7l9 6 9-6"/></svg>',
}
LOGO = ('<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="23" fill="#EFE6F8"/>'
        '<path d="M24 9c3 7 8 9.5 15 10-7 .5-12 3-15 10-3-7-8-9.5-15-10 7-.5 12-3 15-10z" fill="#8A67B5"/>'
        '<circle cx="34.5" cy="33.5" r="4" fill="#F2A28C"/><circle cx="15" cy="34" r="2.4" fill="#D9C8EE"/></svg>')
CICEK = ('<svg class="cicek" viewBox="0 0 100 100" aria-hidden="true"><g fill="currentColor">'
         + "".join(f'<ellipse cx="50" cy="26" rx="13" ry="22" transform="rotate({a} 50 50)" opacity=".55"/>' for a in range(0, 360, 60))
         + '</g><circle cx="50" cy="50" r="10" fill="#fff"/></svg>')

def resim(ad, alt, cls="", yukle="lazy", gen=None, yuk=None):
    if gorsel_var(ad):
        boy = f' width="{gen}" height="{yuk}"' if gen else ""
        return f'<img src="/assets/img/{ad}.webp" alt="{escape(alt)}" loading="{yukle}" decoding="async"{boy}{cls}>'
    return f'<div class="yer-tutucu" role="img" aria-label="{escape(alt)}">{IKON["pirlanta"]}</div>'

def wa_link(metin):
    from urllib.parse import quote
    return f"https://wa.me/{FIRMA['wa']}?text={quote(metin)}"

# ---------- sayfa parçaları ----------
def ust_bar():
    return f'''<header class="ust"><div class="kap">
<a class="logo" href="/" aria-label="{FIRMA['ad']} ana sayfa">{LOGO}<span><b>Avrasya</b><small>Temizlik · İstanbul</small></span></a>
<button class="menu-ac" type="button" aria-label="Menüyü aç" aria-expanded="false" aria-controls="menu">{IKON['menu']}</button>
<nav class="menu" id="menu" aria-label="Ana menü">
<a href="/#hizmetler">Hizmetler</a><a href="/#ilceler">İlçeler</a><a href="/blog/">Blog</a><a href="#sss">Sık Sorulanlar</a><a href="#iletisim">İletişim</a>
<a class="btn btn-ana" href="tel:{FIRMA['tel']}" data-olay="arama_tiklama">{IKON['tel']}{FIRMA['tel_goster']}</a>
</nav></div></header>'''

def hizmet_kartlari(sira, yer):
    out = []
    for slug in sira:
        _, baslik, _, gorsel, acik = HIZ[slug]
        out.append(f'''<a class="hizmet" href="/{slug}/"><div class="resim">{resim(gorsel, f"{yer} {kucuk(baslik)}")}</div>
<div class="ic"><h3>{baslik}</h3><p>{acik}</p><span class="ok">Detaylar →</span></div></a>''')
    return "\n".join(out)

def ilce_listesi(aktif=None):
    gr = {"Avrupa": [], "Anadolu": []}
    for d in ILCELER:
        cur = ' aria-current="page"' if d[0] == aktif else ""
        gr[d[3]].append(f'<li><a href="/{d[0]}-temizlik-sirketi/"{cur}>{d[1]}</a></li>')
    return (f'<h3>Avrupa Yakası</h3><ul class="ilce-liste">{"".join(gr["Avrupa"])}</ul>'
            f'<h3>Anadolu Yakası</h3><ul class="ilce-liste">{"".join(gr["Anadolu"])}</ul>')

def sss_html(sorular):
    return "\n".join(f'<details><summary>{escape(s)}</summary><p>{escape(c)}</p></details>' for s, c in sorular)

def uzun_html(c):
    if not c.get("uzun"):
        return ""
    return f'''<section class="bolum"><div class="kap"><article class="makale">{c["uzun"]}</article></div></section>'''

def sablon(c):
    """c: path, title, desc, h1, giris, hero, yer, yerde, sira, hakkinda, sss, yol, ilce_aktif, rozetler, wa_metin, og"""
    wa = wa_link(c["wa_metin"])
    url = FIRMA["alan"] + c["path"]
    og = FIRMA["alan"] + "/assets/img/" + ("og-kapak.webp" if gorsel_var("og-kapak") else (c["hero"] + ".webp"))
    yol_html = ""
    if c.get("yol"):
        yol_html = '<nav class="yol" aria-label="Sayfa yolu"><a href="/">Ana sayfa</a> › ' + " › ".join(
            (f'<a href="{u}">{escape(a)}</a>' if u else escape(a)) for a, u in c["yol"]) + "</nav>"
    sema = [{
        "@context": "https://schema.org", "@type": "LocalBusiness", "@id": FIRMA["alan"] + "/#isletme",
        "name": FIRMA["ad"], "url": FIRMA["alan"] + "/", "telephone": FIRMA["tel"], "email": FIRMA["eposta"],
        "image": og, "address": {"@type": "PostalAddress", "addressLocality": "İstanbul", "addressCountry": "TR"},
        "areaServed": c.get("area", {"@type": "City", "name": "İstanbul"}),
    }]
    if c["sss"]:
        sema.append({"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": s, "acceptedAnswer": {"@type": "Answer", "text": a}} for s, a in c["sss"]]})
    if c.get("makale"):
        sema.append({"@context": "https://schema.org", "@type": "BlogPosting", "headline": c["makale"]["baslik"],
            "datePublished": c["makale"]["tarih"], "dateModified": c["makale"]["guncel"], "mainEntityOfPage": url,
            "author": {"@type": "Organization", "name": FIRMA["ad"]}, "publisher": {"@id": FIRMA["alan"] + "/#isletme"}, "image": og})
    if c.get("yol"):
        items = [{"@type": "ListItem", "position": 1, "name": "Ana sayfa", "item": FIRMA["alan"] + "/"}]
        for i, (a, u) in enumerate(c["yol"], 2):
            items.append({"@type": "ListItem", "position": i, "name": a, "item": FIRMA["alan"] + (u or c["path"])})
        sema.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})
    sema_html = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in sema)
    hero_img = resim(c["hero"], c["hero_alt"], yukle="eager", gen=1400, yuk=1540).replace("<img ", '<img fetchpriority="high" ', 1)
    rozet = "".join(f"<li>{r}</li>" for r in c["rozetler"])
    gtm = FIRMA["gtm"]
    html = f'''<!doctype html>
<html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{gtm}');</script>
<title>{escape(c["title"])}</title>
<meta name="description" content="{escape(c["desc"])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#8A67B5">
<meta property="og:locale" content="tr_TR"><meta property="og:type" content="website"><meta property="og:site_name" content="{FIRMA['ad']}">
<meta property="og:title" content="{escape(c["title"])}"><meta property="og:description" content="{escape(c["desc"])}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;1,500&family=Quicksand:wght@500;600;700&display=swap">
<link rel="stylesheet" href="/assets/stil.css?v={c['v']}">
{sema_html}
</head><body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
{ust_bar()}
<main>
<section class="hero"><div class="kap">
<div>{yol_html}<span class="etiket">{escape(c["ust_etiket"])}</span>
<h1>{c["h1"]}</h1>
<p class="giris">{c["giris"]}</p>
<div class="dugmeler"><a class="btn btn-ana" href="tel:{FIRMA['tel']}" data-olay="arama_tiklama">{IKON['tel']}Hemen Ara</a>
<a class="btn btn-wa" href="{wa}" target="_blank" rel="noopener" data-olay="whatsapp_tiklama">{IKON['wa']}WhatsApp'tan Yaz</a></div>
<ul class="rozetler">{rozet}</ul></div>
<div class="hero-gorsel">{CICEK}<div class="cerceve">{hero_img}</div>
<div class="kart"><i>{IKON['kalp']}</i><div><b>{escape(c["kart_b"])}</b><span>{escape(c["kart_s"])}</span></div></div></div>
</div></section>

<section class="bolum pembe" id="hizmetler"><div class="kap">
<div class="bolum-bas"><span class="etiket">Hizmetlerimiz</span><h2>{c["yerde"]} <em>tertemiz</em> yaşam alanları</h2>
<p>Ev, işyeri ve özel alanlar için ihtiyacınıza göre planlanan temizlik hizmetleri.</p></div>
<div class="izgara hizmetler">{hizmet_kartlari(c["sira"], c["yer"])}</div>
</div></section>

<section class="bolum"><div class="kap ikili">
<div class="resim">{resim("ekip", f"{FIRMA['ad']} temizlik ekibi")}</div>
<div id="hakkimizda">{c["hakkinda"]}</div>
</div></section>
{uzun_html(c)}

<section class="bolum lila"><div class="kap">
<div class="bolum-bas"><span class="etiket">Nasıl çalışıyoruz?</span><h2>Üç adımda <em>randevu</em></h2></div>
<div class="izgara adimlar">
<div class="adim"><h3>Bize ulaşın</h3><p>Telefonla arayın ya da WhatsApp'tan yazın; adresinizi, alanın büyüklüğünü ve istediğiniz temizlik türünü paylaşın.</p></div>
<div class="adim"><h3>Planı birlikte yapalım</h3><p>İşin kapsamını ve size uygun günü konuşalım; fiyatı iş başlamadan önce netleştirelim.</p></div>
<div class="adim"><h3>Gerisini bize bırakın</h3><p>Ekibimiz belirlenen gün gelir, planlanan işleri tamamlar; siz yalnızca sonucun keyfini çıkarın.</p></div>
</div></div></section>

<section class="bolum"><div class="kap">
<div class="bolum-bas"><span class="etiket">Neler yapıyoruz?</span><h2>Talep edebileceğiniz <em>işler</em></h2>
<p>Kapsamı her evde ve işyerinde birlikte belirliyoruz; aşağıdakiler en sık istenen işler.</p></div>
<div class="izgara isler">
<div class="is-kutu"><h3><span>{IKON['ev']}</span>Mutfak ve banyo</h3><ul class="liste"><li>Tezgâh, dolap kapakları ve fayans yüzeyleri</li><li>Lavabo, batarya, duş alanı ve klozet</li><li>Ankastre cihazların dış yüzeyleri</li></ul></div>
<div class="is-kutu"><h3><span>{IKON['pirlanta']}</span>Odalar ve salon</h3><ul class="liste"><li>Toz alma, süpürme ve zemin silme</li><li>Kapı, pervaz, priz ve kulp temizliği</li><li>Camların iç yüzeyleri</li></ul></div>
<div class="is-kutu"><h3><span>{IKON['takvim']}</span>Taşınma ve boş ev</h3><ul class="liste"><li>Taşınmadan önce ya da sonra boş ev temizliği</li><li>Dolap içleri ve raflar</li><li>Kiracı değişiminde teslim temizliği</li></ul></div>
<div class="is-kutu"><h3><span>{IKON['kalp']}</span>İnşaat ve tadilat sonrası</h3><ul class="liste"><li>Boya, alçı ve silikon kalıntıları</li><li>İnce toz temizliği</li><li>Cam, doğrama ve zemin temizliği</li></ul></div>
</div></div></section>

<section class="bolum pembe" id="sss"><div class="kap">
<div class="bolum-bas"><span class="etiket">Sık sorulanlar</span><h2>Merak <em>ettikleriniz</em></h2></div>
<div class="sss">{sss_html(c["sss"])}</div>
</div></section>

<section class="bolum ilceler" id="ilceler"><div class="kap">
<div class="bolum-bas"><span class="etiket">Hizmet bölgeleri</span><h2>İstanbul'un <em>her ilçesinde</em></h2>
<p>İlçenizi seçin, size özel sayfadan bilgi alın ve hemen randevu oluşturun.</p></div>
{ilce_listesi(c.get("ilce_aktif"))}
</div></section>

<section class="kap"><div class="cta">
<div><h2>{c["cta_h"]}</h2><p>Ücretsiz bilgi almak ve randevu oluşturmak için hemen arayın ya da WhatsApp'tan yazın.</p></div>
<div class="dugmeler"><a class="btn btn-ana" href="tel:{FIRMA['tel']}" data-olay="arama_tiklama">{IKON['tel']}{FIRMA['tel_goster']}</a>
<a class="btn btn-wa" href="{wa}" target="_blank" rel="noopener" data-olay="whatsapp_tiklama">{IKON['wa']}WhatsApp'tan Yaz</a></div>
</div></section>

<section class="bolum" id="iletisim"><div class="kap">
<div class="bolum-bas"><span class="etiket">İletişim</span><h2>Bize <em>ulaşın</em></h2></div>
<div class="iletisim">
<a href="tel:{FIRMA['tel']}" data-olay="arama_tiklama"><span>Telefon</span><b>{FIRMA['tel_goster']}</b></a>
<a href="{wa}" target="_blank" rel="noopener" data-olay="whatsapp_tiklama"><span>WhatsApp</span><b>Mesaj gönderin</b></a>
<a href="mailto:{FIRMA['eposta']}"><span>E-posta</span><b>{FIRMA['eposta']}</b></a>
</div></div></section>
</main>

<footer><div class="kap">
<div><a class="logo" href="/">{LOGO}<span><b>Avrasya</b><small>Temizlik · İstanbul</small></span></a>
<p style="margin-top:16px">İstanbul'un Avrupa ve Anadolu yakasında ev, işyeri, villa ve inşaat sonrası temizlik hizmeti.</p></div>
<div><h4>Hizmetler</h4><ul>{"".join(f'<li><a href="/{h[0]}/">{h[1]}</a></li>' for h in HIZMETLER)}</ul></div>
<div><h4>İletişim</h4><ul><li><a href="tel:{FIRMA['tel']}" data-olay="arama_tiklama">{FIRMA['tel_goster']}</a></li><li><a href="{wa}" target="_blank" rel="noopener" data-olay="whatsapp_tiklama">WhatsApp</a></li><li><a href="mailto:{FIRMA['eposta']}">{FIRMA['eposta']}</a></li></ul></div>
<div class="alt">© {date.today().year} {FIRMA['ad']} · İstanbul</div>
</div></footer>
<div class="yapiskan"><a class="btn btn-ana" href="tel:{FIRMA['tel']}" data-olay="arama_tiklama">{IKON['tel']}Ara</a><a class="btn btn-wa" href="{wa}" target="_blank" rel="noopener" data-olay="whatsapp_tiklama">{IKON['wa']}WhatsApp</a></div>
<script>
(function(){{var b=document.querySelector('.menu-ac'),m=document.getElementById('menu');
b.addEventListener('click',function(){{var a=m.classList.toggle('acik');b.setAttribute('aria-expanded',a)}});
m.querySelectorAll('a').forEach(function(x){{x.addEventListener('click',function(){{m.classList.remove('acik');b.setAttribute('aria-expanded',false)}})}});
document.addEventListener('click',function(e){{var a=e.target.closest('[data-olay]');if(a){{(window.dataLayer=window.dataLayer||[]).push({{event:a.getAttribute('data-olay'),sayfa:location.pathname}})}}}});}})();
</script>
</body></html>
'''
    if not c["sss"]:
        html = re.sub(r'<section class="bolum pembe" id="sss">.*?</section>\n', '', html, flags=re.S)
    if c.get("ozel_main"):
        html = re.sub(r'<main>.*?(<section class="bolum ilceler")', lambda m: '<main>\n' + c["ozel_main"] + '\n' + m.group(1), html, flags=re.S)
    return html

# ---------- içerik ----------
GENEL_SSS = [
    ("Temizlik fiyatı nasıl belirleniyor?", "Fiyat; alanın büyüklüğüne, temizliğin türüne (düzenli, boş ev, inşaat sonrası vb.) ve yapılacak işlerin kapsamına göre belirlenir. Bize ulaştığınızda bilgileri alır, iş başlamadan önce fiyatı netleştiririz."),
    ("Temizlik malzemeleri kimden?", "Malzeme ve ekipman konusunu randevu sırasında sizinle birlikte netleştiriyoruz; özel bir ürün tercihiniz varsa belirtmeniz yeterli."),
    ("Randevuyu nasıl oluşturabilirim?", f"{FIRMA['tel_goster']} numarasını arayabilir ya da aynı numaraya WhatsApp'tan yazabilirsiniz. Adres, alan büyüklüğü ve istediğiniz tarihi paylaşmanız yeterli."),
]

def ilce_sayfasi(d, v):
    slug, ad, yerde, yaka, profil, mah, notu = d
    hero, sira = PROFIL[profil]
    mah_html = "".join(f"<li>{m}</li>" for m in mah)
    hakkinda = f'''<span class="etiket">{ad} · {yaka} Yakası</span>
<h2>{yerde} <em>güvenilir</em> temizlik</h2>
<p>{notu}</p>
<p>Avrasya Temizlik olarak {ad} genelinde ev, işyeri ve inşaat sonrası temizlik hizmeti veriyoruz. Hizmet verdiğimiz başlıca mahalleler:</p>
<ul class="mahalleler">{mah_html}</ul>
<p>Listede olmayan bir mahalledeyseniz de bize yazın; {ad} içindeki tüm adresler için uygunluğu birlikte kontrol edelim.</p>
<a class="btn btn-ana" href="tel:{FIRMA['tel']}" data-olay="arama_tiklama">{IKON['tel']}{ad} için bilgi alın</a>'''
    sss = [
        (f"{yerde} hangi temizlik hizmetlerini veriyorsunuz?", f"{ad} genelinde ev temizliği, işyeri temizliği, inşaat sonrası temizlik, villa temizliği, dış cephe ve cam temizliği ile yat ve tekne temizliği için randevu oluşturabilirsiniz."),
        (f"{ad} içinde hangi mahallelere geliyorsunuz?", f"{', '.join(mah)} başta olmak üzere {ad} içindeki adresler için hizmet planlıyoruz. Mahallenizi yazmanız yeterli, uygunluğu hemen kontrol ederiz."),
    ] + GENEL_SSS
    ilk = HIZ[sira[0]][1]
    return dict(
        path=f"/{slug}-temizlik-sirketi/", v=v, uzun=ESKI_SAYFA.get(f"{slug}-temizlik-sirketi", ""),
        title=f"{ad} Temizlik Şirketi | Ev ve İşyeri Temizliği | Avrasya Temizlik",
        desc=f"{yerde} ev temizliği, işyeri temizliği ve inşaat sonrası temizlik. {', '.join(mah[:3])} ve tüm {ad} için hemen arayın: {FIRMA['tel_goster']}.",
        ust_etiket=f"{ad} · İstanbul",
        h1=f"{ad} <em>Temizlik</em> Şirketi",
        giris=f"{yerde} evinizi, işyerinizi ya da yeni taşındığınız dairenizi özenle temizliyoruz. {ilk.split()[0]} {kucuk(" ".join(ilk.split()[1:]))} başta olmak üzere tüm hizmetler için bugün arayın, planı birlikte yapalım.",
        hero=hero, hero_alt=f"{ad} temizlik hizmeti", yer=ad, yerde=yerde, sira=sira,
        rozetler=[HIZ[s][2] for s in sira[:4]],
        kart_b=f"{ad} genelinde hizmet", kart_s=f"{yaka} Yakası · {len(mah)}+ mahalle",
        hakkinda=hakkinda, sss=sss,
        yol=[("İlçeler", "/#ilceler"), (f"{ad} Temizlik", None)], ilce_aktif=slug,
        wa_metin=f"Merhaba, {ad} için temizlik hizmeti hakkında bilgi almak istiyorum.",
        cta_h=f"{yerde} temizlik için <em>bugün</em> arayın",
        area={"@type": "AdministrativeArea", "name": f"{ad}, İstanbul"},
    )

def ana_sayfa(v):
    hakkinda = f'''<span class="etiket">Biz kimiz?</span>
<h2>Temizliği <em>özenle</em> yapan ekip</h2>
<p>Avrasya Temizlik; İstanbul'da ev temizliği, işyeri temizliği, villa temizliği ve inşaat sonrası temizlik hizmeti veren bir temizlik firmasıdır.</p>
<ul class="liste"><li>Avrupa ve Anadolu yakasındaki 39 ilçede hizmet</li><li>İşin kapsamı ve fiyatı iş başlamadan önce netleşir</li><li>Telefon ve WhatsApp'tan hızlı iletişim</li></ul>
<a class="btn btn-ana" href="tel:{FIRMA['tel']}" data-olay="arama_tiklama">{IKON['tel']}Hemen bilgi alın</a>'''
    sss = [("İstanbul'un hangi ilçelerine hizmet veriyorsunuz?", "Avrupa ve Anadolu yakasındaki 39 ilçenin tamamında hizmet planlıyoruz. Sayfanın altındaki listeden ilçenizi seçerek ayrıntılı bilgi alabilirsiniz.")] + GENEL_SSS
    return dict(
        path="/", v=v,
        title="Avrasya Temizlik | İstanbul Temizlik Şirketi – Ev, İşyeri, İnşaat Sonrası",
        desc=f"İstanbul'un 39 ilçesinde ev temizliği, işyeri temizliği, villa ve inşaat sonrası temizlik. Bilgi ve randevu için arayın: {FIRMA['tel_goster']}.",
        ust_etiket="İstanbul · Avrupa & Anadolu Yakası",
        h1="İstanbul'da <em>tertemiz</em> bir yaşam alanı",
        giris="Ev, işyeri, villa ve inşaat sonrası temizlikte yanınızdayız. İstanbul'un her ilçesinde ihtiyacınıza göre planlanan, özenli temizlik hizmeti.",
        hero="hero-salon", hero_alt="İstanbul ev temizliği", yer="İstanbul", yerde="İstanbul'da", sira=[h[0] for h in HIZMETLER],
        rozetler=["Ev", "İşyeri", "İnşaat sonrası", "Villa"],
        kart_b="39 ilçede hizmet", kart_s="Avrupa ve Anadolu yakası",
        hakkinda=hakkinda, sss=sss, yol=None, ilce_aktif=None,
        wa_metin="Merhaba, temizlik hizmeti hakkında bilgi almak istiyorum.",
        cta_h="Evinize <em>ferahlık</em> getirelim",
    )

def hizmet_sayfasi(h, v):
    slug, baslik, kisa, gorsel, acik = h
    sira = [slug] + [x[0] for x in HIZMETLER if x[0] != slug]
    hakkinda = f'''<span class="etiket">{baslik}</span>
<h2>İstanbul {kucuk(baslik)} <em>hizmeti</em></h2>
<p>{acik}</p>
<p>İşin kapsamını, alanın büyüklüğünü ve size uygun günü birlikte belirliyoruz; fiyatı iş başlamadan önce netleştiriyoruz.</p>
<a class="btn btn-ana" href="tel:{FIRMA['tel']}" data-olay="arama_tiklama">{IKON['tel']}{baslik} için arayın</a>'''
    sss = [(f"{baslik} hangi ilçelerde yapılıyor?", f"{baslik} hizmetini İstanbul'un Avrupa ve Anadolu yakasındaki tüm ilçelerde planlıyoruz.")] + GENEL_SSS
    hero = {"isyeri-temizligi": "hero-ofis", "villa-temizligi": "hero-villa", "insaat-sonrasi-temizlik": "hero-mutfak"}.get(slug, "hero-salon")
    return dict(
        path=f"/{slug}/", v=v, uzun=ESKI_SAYFA.get(slug, ""),
        title=f"İstanbul {baslik} | Avrasya Temizlik",
        desc=f"İstanbul {kucuk(baslik)}: {acik} Bilgi ve randevu: {FIRMA['tel_goster']}.",
        ust_etiket=f"{baslik} · İstanbul", h1=f"İstanbul <em>{baslik}</em>",
        giris=acik + " İstanbul'un 39 ilçesinde hizmet veriyoruz.",
        hero=hero, hero_alt=f"İstanbul {kucuk(baslik)}", yer="İstanbul", yerde="İstanbul'da", sira=sira,
        rozetler=[kisa, "39 ilçe", "Avrupa & Anadolu"],
        kart_b=baslik, kart_s="İstanbul genelinde",
        hakkinda=hakkinda, sss=sss, yol=[("Hizmetler", "/#hizmetler"), (baslik, None)], ilce_aktif=None,
        wa_metin=f"Merhaba, {kucuk(baslik)} hakkında bilgi almak istiyorum.",
        cta_h=f"{baslik} için <em>bugün</em> arayın",
    )

ESKI_SAYFA = eski.sayfa_metinleri()
YAZILAR = eski.yazilar()

def yaka_sayfasi(yaka, v):
    slug = "avrupa-yakasi" if yaka == "Avrupa" else "anadolu-yakasi"
    ilceler = [d for d in ILCELER if d[3] == yaka]
    liste = "".join(f'<li><a href="/{d[0]}-temizlik-sirketi/">{d[1]}</a></li>' for d in ilceler)
    hakkinda = f'''<span class="etiket">{yaka} Yakası</span>
<h2>{yaka} Yakası'nda <em>{len(ilceler)} ilçe</em></h2>
<p>İstanbul {yaka} Yakası'ndaki tüm ilçelerde ev, işyeri, villa ve inşaat sonrası temizlik hizmeti veriyoruz. İlçenizi seçerek size özel sayfaya geçebilirsiniz.</p>
<ul class="ilce-liste">{liste}</ul>'''
    sss = [(f"{yaka} Yakası'nda hangi ilçelere geliyorsunuz?", f"{', '.join(d[1] for d in ilceler)} ilçelerinin tamamında hizmet planlıyoruz.")] + GENEL_SSS
    return dict(
        path=f"/{slug}-temizlik-sirketi/", v=v, uzun=ESKI_SAYFA.get(f"{slug}-temizlik-sirketi", ""),
        title=f"İstanbul {yaka} Yakası Temizlik Şirketi | Avrasya Temizlik",
        desc=f"İstanbul {yaka} Yakası'nın {len(ilceler)} ilçesinde ev, işyeri, villa ve inşaat sonrası temizlik. Bilgi ve randevu: {FIRMA['tel_goster']}.",
        ust_etiket=f"İstanbul · {yaka} Yakası", h1=f"{yaka} Yakası <em>Temizlik</em> Şirketi",
        giris=f"İstanbul {yaka} Yakası'nın {len(ilceler)} ilçesinde evinizi ve işyerinizi özenle temizliyoruz. Bugün arayın, planı birlikte yapalım.",
        hero="hero-salon" if yaka == "Anadolu" else "hero-pencere", hero_alt=f"{yaka} Yakası temizlik", yer=f"{yaka} Yakası",
        yerde=f"{yaka} Yakası'nda", sira=[h[0] for h in HIZMETLER], rozetler=["Ev", "İşyeri", "İnşaat sonrası", "Villa"],
        kart_b=f"{len(ilceler)} ilçede hizmet", kart_s=f"İstanbul {yaka} Yakası",
        hakkinda=hakkinda, sss=sss, yol=[("İlçeler", "/#ilceler"), (f"{yaka} Yakası", None)], ilce_aktif=None,
        wa_metin=f"Merhaba, {yaka} Yakası'nda temizlik hizmeti hakkında bilgi almak istiyorum.",
        cta_h=f"{yaka} Yakası'nda <em>temizlik</em> için arayın",
    )

def makale_sayfasi(y, v):
    main = f'''<section class="hero makale-bas"><div class="kap" style="display:block">
<nav class="yol" aria-label="Sayfa yolu"><a href="/">Ana sayfa</a> › <a href="/blog/">Blog</a> › {escape(y["baslik"])}</nav>
<span class="etiket">Blog · Temizlik rehberi</span><h1>{escape(y["baslik"])}</h1>
<p class="giris">{escape(y["ozet"])}</p>
<div class="dugmeler"><a class="btn btn-ana" href="tel:{FIRMA['tel']}" data-olay="arama_tiklama">{IKON['tel']}Hemen Ara</a>
<a class="btn btn-wa" href="{wa_link('Merhaba, temizlik hizmeti hakkında bilgi almak istiyorum.')}" target="_blank" rel="noopener" data-olay="whatsapp_tiklama">{IKON['wa']}WhatsApp'tan Yaz</a></div>
</div></section>
<section class="bolum" style="padding-top:20px"><div class="kap makale-izgara">
<article class="makale">{y["govde"]}</article>
<aside class="makale-yan"><div class="yan-kart">{resim("ekip", "Avrasya Temizlik ekibi")}<div class="ic"><h3>Avrasya Temizlik</h3><p>İstanbul'un 39 ilçesinde ev, işyeri, villa ve inşaat sonrası temizlik.</p>
<a class="btn btn-ana" href="tel:{FIRMA['tel']}" data-olay="arama_tiklama">{IKON['tel']}{FIRMA['tel_goster']}</a></div></div>
<div class="yan-kart ic"><h3>Hizmetlerimiz</h3><ul class="liste">{"".join(f'<li><a href="/{h[0]}/">{h[1]}</a></li>' for h in HIZMETLER)}</ul></div></aside>
</div></section>
<section class="bolum pembe" id="hizmetler"><div class="kap"><div class="bolum-bas"><span class="etiket">Hizmetlerimiz</span><h2>İstanbul'da <em>tertemiz</em> yaşam alanları</h2></div>
<div class="izgara hizmetler">{hizmet_kartlari([h[0] for h in HIZMETLER][:3], "İstanbul")}</div></div></section>'''
    return dict(path=f"/{y['slug']}/", v=v, title=f"{y['baslik']} | Avrasya Temizlik", desc=y["desc"], sss=[],
                hero="hero-salon", hero_alt="", ust_etiket="", h1="", giris="", yer="İstanbul", yerde="İstanbul'da",
                sira=[h[0] for h in HIZMETLER], rozetler=[], kart_b="", kart_s="", hakkinda="", yol=[("Blog", "/blog/"), (y["baslik"], None)],
                ilce_aktif=None, wa_metin="Merhaba, temizlik hizmeti hakkında bilgi almak istiyorum.",
                cta_h="Temizlik için <em>bugün</em> arayın", ozel_main=main, makale=y)

def blog_sayfasi(yazilar, v):
    kartlar = "".join(f'<a class="hizmet yazi-kart" href="/{y["slug"]}/"><div class="ic"><span class="tarih">{y["tarih"]}</span><h3>{escape(y["baslik"])}</h3><p>{escape(y["ozet"])}</p><span class="ok">Devamını oku →</span></div></a>' for y in yazilar)
    main = f'''<section class="hero makale-bas"><div class="kap" style="display:block">
<nav class="yol" aria-label="Sayfa yolu"><a href="/">Ana sayfa</a> › Blog</nav>
<span class="etiket">Blog</span><h1>Temizlik <em>rehberi</em></h1>
<p class="giris">Ev, işyeri, inşaat sonrası ve villa temizliği hakkında {len(yazilar)} yazı.</p></div></section>
<section class="bolum" style="padding-top:10px"><div class="kap"><div class="izgara hizmetler">{kartlar}</div></div></section>'''
    return dict(path="/blog/", v=v, title="Blog – Temizlik Rehberi | Avrasya Temizlik",
                desc="Ev temizliği, işyeri temizliği, inşaat sonrası ve villa temizliği hakkında rehber yazılar.", sss=[],
                hero="hero-salon", hero_alt="", ust_etiket="", h1="", giris="", yer="İstanbul", yerde="İstanbul'da",
                sira=[h[0] for h in HIZMETLER], rozetler=[], kart_b="", kart_s="", hakkinda="", yol=[("Blog", None)],
                ilce_aktif=None, wa_metin="Merhaba, temizlik hizmeti hakkında bilgi almak istiyorum.",
                cta_h="Temizlik için <em>bugün</em> arayın", ozel_main=main)

def yaz(path, html):
    hedef = os.path.join(KOK, path.strip("/"), "index.html") if path != "/" else os.path.join(KOK, "index.html")
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    with open(hedef, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

def yonlendir(eski, yeni):
    hedef = os.path.join(KOK, eski.strip("/"), "index.html")
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    with open(hedef, "w", encoding="utf-8", newline="\n") as f:
        f.write(f'<!doctype html><meta charset="utf-8"><title>Yönlendiriliyor…</title><link rel="canonical" href="{FIRMA["alan"]}{yeni}">'
                f'<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url={yeni}"><a href="{yeni}">Devam</a>\n')

def main():
    gorselleri_hazirla()
    os.makedirs(os.path.join(KOK, "assets"), exist_ok=True)
    shutil.copyfile(os.path.join(KAYNAK, "stil.css"), os.path.join(KOK, "assets", "stil.css"))
    v = str(int(os.path.getmtime(os.path.join(KAYNAK, "stil.css"))))[-6:]
    sayfalar = ([ana_sayfa(v)] + [hizmet_sayfasi(h, v) for h in HIZMETLER] + [yaka_sayfasi(y, v) for y in ("Avrupa", "Anadolu")]
                + [ilce_sayfasi(d, v) for d in ILCELER])
    dolu = {c["path"] for c in sayfalar} | {"/blog/", "/about/", "/contact/", "/services/"}
    yazilar = [y for y in YAZILAR if f"/{y['slug']}/" not in dolu]
    sayfalar += [blog_sayfasi(yazilar, v)] + [makale_sayfasi(y, v) for y in yazilar]
    for c in sayfalar:
        yaz(c["path"], sablon(c))
    # eski WordPress adresleri
    for eski_url, yeni in {"/about/": "/#hakkimizda", "/contact/": "/#iletisim", "/services/": "/#hizmetler",
                           "/kategori/uncategorized/": "/blog/", "/feed/": "/blog/", "/comments/feed/": "/blog/"}.items():
        yonlendir(eski_url, yeni)
    with open(os.path.join(KOK, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for c in sayfalar:
            f.write(f"<url><loc>{FIRMA['alan']}{c['path']}</loc><lastmod>{BUGUN}</lastmod></url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(KOK, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {FIRMA['alan']}/sitemap.xml\n")
    with open(os.path.join(KOK, "CNAME"), "w", encoding="utf-8", newline="\n") as f:
        f.write("avrasyatemizlik.com.tr\n")
    with open(os.path.join(KOK, "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"') + "\n")
    with open(os.path.join(KOK, "404.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write('<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>Sayfa bulunamadı | Avrasya Temizlik</title><meta name="robots" content="noindex"><link rel="stylesheet" href="/assets/stil.css">'
                '<body><section class="hero"><div class="kap" style="display:block;text-align:center"><h1>Sayfa <em>bulunamadı</em></h1>'
                f'<p>Aradığınız sayfa taşınmış olabilir.</p><p><a class="btn btn-ana" href="/">Ana sayfaya dön</a> <a class="btn btn-wa" href="tel:{FIRMA["tel"]}">{FIRMA["tel_goster"]}</a></p></div></section></body></html>\n')
    print("sayfa sayısı:", len(sayfalar))

if __name__ == "__main__":
    main()

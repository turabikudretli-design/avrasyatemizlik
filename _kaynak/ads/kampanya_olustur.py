# -*- coding: utf-8 -*-
"""929-146-3056 'AVRASYA TEMİZLİK' kampanyasından taşınan kelimelerle 701-645-5988 için toplu yükleme CSV'si.
Kurallar: dönüşüm getirmeyen / gösterim almayan kelimeler (cikarilan-929.txt) alınmaz; her kelime içinde geçen
ilçe ya da semt adına göre o ilçenin sayfasına gider; ilçe adı geçmeyen genel kelimeler 'İstanbul Genel' grubunda."""
import csv, os, sys
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
from veri import ILCELER  # noqa: E402

ALAN = "https://avrasyatemizlik.com.tr"
KAMPANYA = "AVRASYA TEMİZLİK"

def kucuk(t):
    return t.replace("İ", "i").replace("I", "ı").lower()

def ascii_tr(t):
    return kucuk(t).translate(str.maketrans("çğıöşüâî", "cgiosuai"))

# ilçe ve semt sözlüğü (uzun adlar önce eşleşsin)
ESLES = []
for slug, ad, _, _, _, mah, _ in ILCELER:
    ESLES.append((kucuk(ad), slug, ad))
    ESLES.append((ascii_tr(ad), slug, ad))
    for m in mah:
        ESLES.append((kucuk(m), slug, ad))
ESLES.append(("kâğıthane", "kagithane", "Kağıthane"))
ESLES.append(("eyüp sultan", "eyupsultan", "Eyüpsultan"))
ESLES.append(("florya", "bakirkoy", "Bakırköy"))
ESLES.sort(key=lambda x: -len(x[0]))
AD = {slug: ad for slug, ad, *_ in ILCELER}

def ilce_bul(metin):
    m = kucuk(metin)
    for anahtar, slug, ad in ESLES:
        if anahtar and anahtar in m:
            return slug
    return None

cikar = {kucuk(l.strip()) for l in open(os.path.join(BURA, "cikarilan-929.txt"), encoding="utf-8") if l.strip()}

kelimeler = {}  # (grup, kelime_metni, eşleme) -> url
for satir in open(os.path.join(BURA, "kelimeler-929.txt"), encoding="utf-8"):
    satir = satir.strip()
    if not satir:
        continue
    eski_grup, kw = satir.split(";", 1)
    if kucuk(kw) in cikar:
        continue
    eslesme = "Exact" if kw.startswith("[") else "Phrase"
    metin = kw.strip('[]"').strip()
    slug = ilce_bul(metin)
    if slug:
        grup, url = AD[slug], f"{ALAN}/{slug}-temizlik-sirketi/"
    else:
        grup = "İstanbul Genel"
        km = kucuk(metin)
        if "anadolu yakas" in km:
            url = f"{ALAN}/anadolu-yakasi-temizlik-sirketi/"
        elif "avrupa yakas" in km:
            url = f"{ALAN}/avrupa-yakasi-temizlik-sirketi/"
        elif "inşaat" in km:
            url = f"{ALAN}/insaat-sonrasi-temizlik/"
        else:
            url = f"{ALAN}/"
    kelimeler[(grup, kucuk(metin), eslesme)] = (metin, url)

gruplar = sorted({g for g, _, _ in kelimeler})

def kes(t, n):
    assert len(t) <= n, (t, len(t))
    return t

def basliklar(ad):
    adaylar = [
        f"{ad} Temizlik Şirketi", f"{ad} Ev Temizliği", f"{ad} Temizlik Firması",
        "Avrasya Temizlik", "İnşaat Sonrası Temizlik", "Ev ve İşyeri Temizliği",
        "Villa ve Ofis Temizliği", "Hemen Arayın, Bilgi Alın", "WhatsApp'tan Hızlı Bilgi",
        "Boş Ev ve Taşınma Temizliği", "Cam ve Dış Cephe Temizliği", f"{ad} Genelinde Hizmet",
        "Planlı ve Özenli Temizlik", "Fiyatı Önceden Netleşir", "İstanbul Temizlik Şirketi",
    ]
    yedek = ["Profesyonel Temizlik", "Detaylı Ev Temizliği", "Ofis Temizliği", "Temizlik Randevusu"]
    out = []
    for b in adaylar:
        if len(b) > 30:
            b = yedek.pop(0)
        out.append(b)
    return out

def aciklamalar(ad):
    return [
        kes(f"{ad} ev, işyeri ve inşaat sonrası temizlik. Bilgi ve randevu için hemen arayın.", 90)
        if len(f"{ad} ev, işyeri ve inşaat sonrası temizlik. Bilgi ve randevu için hemen arayın.") <= 90
        else kes(f"{ad} ev ve işyeri temizliği. Bilgi ve randevu için hemen arayın.", 90),
        kes("Kapsamı ve fiyatı iş başlamadan önce birlikte netleştiriyoruz. Hemen bilgi alın.", 90),
        kes("Taşınma, boş ev, villa ve ofis temizliğinde özenli hizmet. WhatsApp'tan yazın.", 90),
        kes("Avrupa ve Anadolu yakasında 39 ilçede temizlik hizmeti. Hemen arayın, bilgi alın.", 90),
    ]

def yol(ad):
    p = ascii_tr(ad).replace(" ", "-")[:15]
    return p

BASLIK = (["Campaign", "Campaign Type", "Campaign Status", "Budget", "Bid Strategy Type", "Networks", "EU political ads",
           "Ad Group", "Ad Group Status", "Keyword", "Match Type", "Status", "Final URL", "Ad type"]
          + [f"Headline {i}" for i in range(1, 16)] + [f"Description {i}" for i in range(1, 5)] + ["Path 1", "Path 2"])

def bos():
    return {k: "" for k in BASLIK}

satirlar = []
r = bos(); r.update({"Campaign": KAMPANYA, "Campaign Type": "Search", "Campaign Status": "Paused", "Budget": "2100",
                     "Bid Strategy Type": "Maximize clicks", "Networks": "Google search", "EU political ads": "No"}); satirlar.append(r)
for g in gruplar:
    r = bos(); r.update({"Campaign": KAMPANYA, "Ad Group": g, "Ad Group Status": "Enabled"}); satirlar.append(r)
    if g == "İstanbul Genel":
        ad, url = "İstanbul", f"{ALAN}/"
    else:
        slug = [s for s, a, *_ in ILCELER if a == g][0]
        ad, url = g, f"{ALAN}/{slug}-temizlik-sirketi/"
    r = bos(); r.update({"Campaign": KAMPANYA, "Ad Group": g, "Ad type": "Responsive search ad", "Status": "Enabled",
                         "Final URL": url, "Path 1": yol(ad), "Path 2": "temizlik"})
    for i, b in enumerate(basliklar(ad), 1):
        r[f"Headline {i}"] = kes(b, 30)
    for i, d in enumerate(aciklamalar(ad), 1):
        r[f"Description {i}"] = d
    satirlar.append(r)
for (g, _, mt), (metin, url) in sorted(kelimeler.items()):
    r = bos(); r.update({"Campaign": KAMPANYA, "Ad Group": g, "Keyword": metin, "Match Type": mt, "Status": "Enabled", "Final URL": url})
    satirlar.append(r)

cikti = os.path.join(BURA, "avrasya-701-kampanya.csv")
with open(cikti, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=BASLIK); w.writeheader(); w.writerows(satirlar)
sys.stdout.reconfigure(encoding="utf-8")
print("grup:", len(gruplar), "kelime:", len(kelimeler), "satır:", len(satirlar))
print(", ".join(gruplar))
for (g, _, mt), (metin, url) in sorted(kelimeler.items()):
    if g == "İstanbul Genel" or "insaat" in url:
        print(" ", g, "|", metin, "|", mt, "->", url.replace(ALAN, ""))

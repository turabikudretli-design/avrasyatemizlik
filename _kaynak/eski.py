# -*- coding: utf-8 -*-
"""Eski WordPress sitesinden (2026-11-18 alınan _kaynak/eski/*.json) içerik okuma ve temizleme."""
import json, os, re
from html import unescape, escape

BURA = os.path.dirname(os.path.abspath(__file__))
IZINLI_BLOK = re.compile(r"<(h2|h3|h4|p|ul|ol)\b[^>]*>(.*?)</\1>", re.S | re.I)

def _ic(t):
    t = re.sub(r"<(/?)(strong|b)\b[^>]*>", r"<\1strong>", t, flags=re.I)
    t = re.sub(r"<(/?)(em|i)\b[^>]*>", r"<\1em>", t, flags=re.I)
    t = re.sub(r"<li\b[^>]*>", "<li>", t, flags=re.I)
    t = re.sub(r"<(?!/?(strong|em|li)>)[^>]+>", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def temizle(html):
    out = []
    for tag, ic in IZINLI_BLOK.findall(html):
        tag = tag.lower()
        if tag == "h4":
            tag = "h3"
        ic = _ic(ic)
        duz = re.sub(r"<[^>]+>", "", ic).strip()
        if len(duz) < 3:
            continue
        out.append(f"<{tag}>{ic}</{tag}>")
    return "\n".join(out)

def duz_metin(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()

def tr_baslik(t):
    t = unescape(t).strip()
    kucukler = {"ve", "ile", "için", "mi", "mı", "de", "da", "ya", "veya"}
    kel = []
    for i, w in enumerate(t.split()):
        if i and w in kucukler:
            kel.append(w)
        else:
            ilk = {"i": "İ", "ı": "I"}.get(w[0], w[0].upper())
            kel.append(ilk + w[1:])
    return " ".join(kel)

def yukle(ad):
    with open(os.path.join(BURA, "eski", ad), encoding="utf-8") as f:
        return json.load(f)

def yazilar():
    r = []
    for x in yukle("posts.json"):
        govde = temizle(x["content"]["rendered"])
        duz = duz_metin(govde)
        yo = x.get("yoast_head_json") or {}
        desc = (yo.get("description") or "").strip() or (duz[:150].rsplit(" ", 1)[0] + "…")
        r.append(dict(slug=x["slug"], baslik=tr_baslik(x["title"]["rendered"]), govde=govde, desc=desc,
                      tarih=x["date"][:10], guncel=x["modified"][:10], ozet=duz[:170].rsplit(" ", 1)[0] + "…"))
    r.sort(key=lambda y: y["tarih"], reverse=True)
    return r

def sayfa_metinleri():
    return {x["slug"]: temizle(x["content"]["rendered"]) for x in yukle("pages.json")}

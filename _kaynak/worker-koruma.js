// Cloudflare Worker — Avrasya Temizlik bot/tıklama koruması (2026-11-18)
// AntiClick Edge v2 (uygulama/deploy/worker-edge-v2.js) temel alındı. Farklar:
//  - Gizli anahtar gerekmez: AntiClick /api/edge-block/perm listesi kullanılır
//    (sitedeki görünmez tuzağa basan = kalıcı engelli cihaz ve IP'ler,
//    SHA-256(siteKey|değer) olarak döner). Cihaz SÜRESİZ, IP 30 gün
//    (mobil operatör IP'leri el değiştirir; botun eski IP'si gerçek müşteriye düşebilir).
//  - İsteğe bağlı: Worker'a EDGE_SECRET değişkeni eklenirse AntiClick'teki
//    TÜM engelli IP/cihazlar da (/api/edge-block/list) girişte engellenir.
//  - Yurt dışı engeli YOK (yalnız AntiClick listeleri).
//  - Google (ASN 15169 + yayınlanan bot IP'leri) hiçbir zaman engellenmez.
//  - Hata olursa site AÇIK kalır (fail-open).
const SITE_KEY = "cf_live_1cd50ec804b4446486df5ed8247fc66aa399";
const PERM_ENDPOINT = "https://anticlick.com.tr/api/edge-block/perm";
const LIST_ENDPOINT = "https://anticlick.com.tr/api/edge-block/list";
const REPORT_ENDPOINT = "https://anticlick.com.tr/api/edge-block";
const GOOGLE_IP_LISTS = [
  "https://developers.google.com/search/apis/ipranges/googlebot.json",
  "https://developers.google.com/search/apis/ipranges/special-crawlers.json",
];
const GOOGLE_ASN = 15169;
const ID_COOKIE = "ac_id";
const ID_MAX_AGE = 60 * 60 * 24 * 400;
const STATIC_RE = /\.(css|js|mjs|map|png|jpe?g|webp|avif|gif|svg|ico|bmp|woff2?|ttf|otf|eot|mp4|webm|mp3|pdf|txt|xml|json|zip)$/i;
const LIST_TTL_MS = 60 * 1000;
const GOOGLE_TTL_MS = 12 * 60 * 60 * 1000;

let permCache = { at: 0, ips: new Set(), devices: new Set() };
let permLoading = null;
let listCache = { at: 0, ips: new Set(), devices: new Set() };
let listLoading = null;
let googleCache = { at: 0, v4: [], v6: [] };
let googleLoading = null;

function ipv4ToInt(ip) {
  const p = ip.split(".").map(Number);
  if (p.length !== 4 || p.some((n) => Number.isNaN(n) || n < 0 || n > 255)) return null;
  return ((p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3]) >>> 0;
}
function ipv6ToBigInt(ip) {
  const parts = ip.includes("::")
    ? (() => {
        const [h, t] = ip.split("::");
        const hp = h ? h.split(":").filter(Boolean) : [];
        const tp = t ? t.split(":").filter(Boolean) : [];
        return [...hp, ...Array(8 - hp.length - tp.length).fill("0"), ...tp];
      })()
    : ip.split(":");
  if (parts.length !== 8) return null;
  let r = 0n;
  for (const part of parts) r = (r << 16n) | BigInt(parseInt(part || "0", 16));
  return r;
}

async function loadGoogle() {
  const v4 = [], v6 = [];
  for (const url of GOOGLE_IP_LISTS) {
    try {
      const res = await fetch(url, { cf: { cacheTtl: 43200, cacheEverything: true } });
      if (!res.ok) continue;
      const json = await res.json();
      for (const p of json.prefixes || []) {
        if (p.ipv4Prefix) {
          const [range, bits] = p.ipv4Prefix.split("/");
          const b = parseInt(bits, 10);
          const mask = b === 0 ? 0 : (~0 << (32 - b)) >>> 0;
          const base = ipv4ToInt(range);
          if (base !== null) v4.push([(base & mask) >>> 0, mask]);
        } else if (p.ipv6Prefix) {
          const [range, bits] = p.ipv6Prefix.split("/");
          const shift = 128n - BigInt(parseInt(bits, 10));
          const full = (1n << 128n) - 1n;
          const mask = shift === 0n ? full : (full >> shift) << shift;
          const base = ipv6ToBigInt(range);
          if (base !== null) v6.push([base & mask, mask]);
        }
      }
    } catch (e) {}
  }
  if (v4.length || v6.length) googleCache = { at: Date.now(), v4, v6 };
}

async function isGoogle(request, ip) {
  if (request.cf && request.cf.asn === GOOGLE_ASN) return true;
  try {
    if (Date.now() - googleCache.at > GOOGLE_TTL_MS) {
      googleLoading = googleLoading || loadGoogle().finally(() => { googleLoading = null; });
      await googleLoading;
    }
    if (!googleCache.v4.length && !googleCache.v6.length) return ip.startsWith("66.249.");
    if (ip.includes(":")) {
      const x = ipv6ToBigInt(ip);
      return x !== null && googleCache.v6.some(([base, mask]) => (x & mask) === base);
    }
    const x = ipv4ToInt(ip);
    return x !== null && googleCache.v4.some(([base, mask]) => ((x & mask) >>> 0) === base);
  } catch (e) {
    return ip.startsWith("66.249.");
  }
}

async function loadPerm() {
  try {
    const res = await fetch(`${PERM_ENDPOINT}?key=${encodeURIComponent(SITE_KEY)}`, { cf: { cacheTtl: 60, cacheEverything: true } });
    if (!res.ok) return;
    const json = await res.json();
    permCache = { at: Date.now(), ips: new Set(json.ips || []), devices: new Set(json.devices || []) };
  } catch (e) {}
}

async function loadList(secret) {
  try {
    const url = `${LIST_ENDPOINT}?key=${encodeURIComponent(SITE_KEY)}&secret=${encodeURIComponent(secret)}`;
    const res = await fetch(url, { cf: { cacheTtl: 60, cacheEverything: true } });
    if (!res.ok) return;
    const json = await res.json();
    listCache = { at: Date.now(), ips: new Set(json.ips || []), devices: new Set(json.devices || []) };
  } catch (e) {}
}

// Ziyaretçi asla beklemez: listeler arka planda yenilenir.
function refresh(ctx, secret) {
  if (Date.now() - permCache.at > LIST_TTL_MS) {
    permLoading = permLoading || loadPerm().finally(() => { permLoading = null; });
    ctx.waitUntil(permLoading);
  }
  if (secret && Date.now() - listCache.at > LIST_TTL_MS) {
    listLoading = listLoading || loadList(secret).finally(() => { listLoading = null; });
    ctx.waitUntil(listLoading);
  }
}

async function sha(v) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(SITE_KEY + "|" + v));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function cookieValue(request, name) {
  const raw = request.headers.get("cookie") || "";
  for (const part of raw.split(";")) {
    const i = part.indexOf("=");
    if (i > -1 && part.slice(0, i).trim() === name) {
      try { return decodeURIComponent(part.slice(i + 1).trim()); } catch (e) { return ""; }
    }
  }
  return "";
}

function newId() {
  const a = new Uint8Array(8);
  crypto.getRandomValues(a);
  return "cf_" + [...a].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function hmac(secret, message) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function reportBlock(secret, request, ip, country, reason, deviceId) {
  if (!secret) return;
  try {
    const url = new URL(request.url);
    await fetch(REPORT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        key: SITE_KEY, secret: await hmac(secret, ip), ip, country, reason,
        deviceId: deviceId || "", userAgent: request.headers.get("user-agent") || "",
        page: url.toString(), gclid: url.searchParams.get("gclid") || "",
        campaign: url.searchParams.get("utm_campaign") || "",
      }),
    });
  } catch (e) {}
}

function forbidden() {
  return new Response("Forbidden", {
    status: 403,
    headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store", "x-robots-tag": "noindex" },
  });
}

async function handle(request, env, ctx) {
  const url = new URL(request.url);
  if (STATIC_RE.test(url.pathname)) return fetch(request);

  const secret = (env && env.EDGE_SECRET) || "";
  const ip = request.headers.get("cf-connecting-ip") || "";
  const country = (request.cf && request.cf.country) || "";
  const acId = cookieValue(request, ID_COOKIE);
  const cfDid = cookieValue(request, "cf_did");
  refresh(ctx, secret);

  let reason = "", devId = "";
  if (permCache.ips.size || permCache.devices.size) {
    if (ip && permCache.ips.has(await sha(ip))) reason = "honeypot_ip";
    else if (acId && permCache.devices.has(await sha(acId))) { reason = "honeypot_device"; devId = acId; }
    else if (cfDid && permCache.devices.has(await sha(cfDid))) { reason = "honeypot_device"; devId = cfDid; }
  }
  if (!reason && secret) {
    if (listCache.ips.has(ip)) reason = "known_ip";
    else if (acId && listCache.devices.has(acId)) { reason = "known_device"; devId = acId; }
    else if (cfDid && listCache.devices.has(cfDid)) { reason = "known_device"; devId = cfDid; }
  }
  if (reason && !(await isGoogle(request, ip))) {
    ctx.waitUntil(reportBlock(secret, request, ip, country, reason, devId));
    return forbidden();
  }

  const isPage = request.method === "GET" && (request.headers.get("accept") || "").includes("text/html");
  const res = await fetch(request);
  if (acId || !isPage) return res;
  const out = new Response(res.body, res);
  out.headers.append("Set-Cookie", `${ID_COOKIE}=${newId()}; Max-Age=${ID_MAX_AGE}; Path=/; Secure; SameSite=Lax`);
  return out;
}

export default {
  async fetch(request, env, ctx) {
    try {
      return await handle(request, env, ctx);
    } catch (e) {
      return fetch(request);
    }
  },
};

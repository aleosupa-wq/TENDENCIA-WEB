#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TENDENCIA — obra satírica. (c) 2026 Alejandro Osuna Pacheco. Todos los derechos reservados.
# Prohibida su reproducción o reutilización sin permiso. Ver LICENCIA.txt.
"""
motor_tendencias.py  —  Motor de "TENDENCIA" (pieza satírica), versión local + mundial

Recoge lo que aparece AHORA en fuentes ABIERTAS (de España y del mundo) y lo
convierte en un "speech" de campaña, metiendo el término real dentro de la frase.
Escribe trends.json, que lee la obra (index.html) en la misma carpeta.

Coge lo primero que devuelven las fuentes; no exige que sea "trending".

Fuentes (todas públicas y pensadas para lectura por programas):
  - Google Trends  (RSS de varios países: ES, US, GB, MX, AR, FR, IT, DE, BR, JP)
  - Wikipedia      (artículos más vistos ayer, ediciones es y en — API pública)
  - Titulares RSS  (nacionales e internacionales; edita la lista a tu gusto)
  - Reddit         (r/es y r/popular — JSON público)

NO usa X, TikTok, Instagram ni Facebook: no abren sus tendencias y sacárselas
incumple sus términos. Quedan fuera a propósito.

Uso:
  python3 motor_tendencias.py                # genera trends.json una vez
  python3 motor_tendencias.py --loop 300     # lo regenera cada 300 s (en bucle)

Solo librería estándar. Sin dependencias.
"""

import json, re, sys, time, random, datetime, urllib.request
import xml.etree.ElementTree as ET

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
TIMEOUT = 12
MAX_ITEMS = 140

# --- Fuentes (edítalas libremente) --------------------------------------
GT_GEOS = ["ES", "US", "GB", "MX", "AR", "FR", "IT", "DE", "BR", "JP"]
GT_RSS = "https://trends.google.com/trending/rss?geo={geo}"

WIKI_LANGS = ["es", "en"]
WIKI_TOP = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/{lang}.wikipedia/all-access/{y}/{m}/{d}"

MEDIOS_RSS = [
    "https://www.eldiario.es/rss/",
    "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "https://e00-elmundo.uecdn.es/elmundo/rss/internacional.xml",
    "https://www.20minutos.es/rss/gente-television/",
    "https://www.lavanguardia.com/rss/home.xml",
    "https://www.abc.es/rss/feeds/abcPortada.xml",
    "https://www.europapress.es/rss/rss.aspx",
    "https://api.rtve.es/api/noticias.rss",
    "https://feeds.bbci.co.uk/mundo/rss.xml",                       # internacional (ES)
    "https://feeds.bbci.co.uk/news/world/rss.xml",                  # internacional (EN)
    "https://www.aljazeera.com/xml/rss/all.xml",                    # internacional
    "https://rss.dw.com/rdf/rss-sp-all",                            # Deutsche Welle (ES)
]

# Google News (muy abierto): titulares del momento por país
GOOGLE_NEWS = [
    "https://news.google.com/rss?hl=es&gl=ES&ceid=ES:es",           # España
    "https://news.google.com/rss?hl=es-419&gl=MX&ceid=MX:es-419",   # México
    "https://news.google.com/rss?hl=es-419&gl=AR&ceid=AR:es-419",   # Argentina
    "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",        # EE. UU.
    "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en",        # Reino Unido
]

HACKER_NEWS = "https://hnrss.org/frontpage"                         # tecnología / mundo

REDDIT = [
    "https://old.reddit.com/r/es/hot.json?limit=20",
    "https://old.reddit.com/r/popular.json?limit=25",               # mundial
    "https://old.reddit.com/r/worldnews/hot.json?limit=20",         # mundo
]
# ------------------------------------------------------------------------


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def safe(fn, label):
    try:
        return fn()
    except Exception as e:
        print(f"  [aviso] {label} no disponible: {e}", file=sys.stderr)
        return []


def from_google_trends():
    out = []
    for geo in GT_GEOS:
        try:
            root = ET.fromstring(fetch(GT_RSS.format(geo=geo)))
            for item in list(root.iter("item"))[:8]:
                t = item.findtext("title")
                if t:
                    out.append((t.strip(), f"Google Trends {geo}"))
        except Exception as e:
            print(f"  [aviso] Trends {geo} falló: {e}", file=sys.stderr)
    return out


def from_wikipedia():
    ayer = datetime.date.today() - datetime.timedelta(days=1)
    out = []
    for lang in WIKI_LANGS:
        try:
            url = WIKI_TOP.format(lang=lang, y=ayer.year, m=f"{ayer.month:02d}", d=f"{ayer.day:02d}")
            data = json.loads(fetch(url).decode("utf-8"))
            for a in data["items"][0]["articles"][:25]:
                name = a["article"].replace("_", " ")
                if name.startswith(("Especial:", "Wikipedia:", "Special:", "Portada", "Main Page")):
                    continue
                out.append((name, f"Wikipedia {lang}"))
        except Exception as e:
            print(f"  [aviso] Wikipedia {lang} falló: {e}", file=sys.stderr)
    return out


def _rss_titulos(feed, n, label):
    out = []
    try:
        root = ET.fromstring(fetch(feed))
        for item in list(root.iter("item"))[:n]:
            t = item.findtext("title")
            if t:
                out.append((t.strip(), label))
    except Exception as e:
        print(f"  [aviso] RSS {feed} falló: {e}", file=sys.stderr)
    return out


def from_medios():
    out = []
    for feed in MEDIOS_RSS:
        out += _rss_titulos(feed, 8, "titulares")
    return out


def from_google_news():
    out = []
    for feed in GOOGLE_NEWS:
        out += _rss_titulos(feed, 10, "Google News")
    return out


def from_hackernews():
    return _rss_titulos(HACKER_NEWS, 15, "Hacker News")


def from_reddit():
    out = []
    for url in REDDIT:
        try:
            data = json.loads(fetch(url).decode("utf-8"))
            for c in data["data"]["children"]:
                t = c["data"].get("title")
                if t:
                    out.append((t.strip(), "Reddit"))
        except Exception as e:
            print(f"  [aviso] Reddit falló: {e}", file=sys.stderr)
    return out


# --- Convertir cualquier cosa en discurso de campaña --------------------
# Regla: el partido es el sujeto del disparate; el término "{t}" es solo el
# objeto. Nunca se le atribuyen declaraciones a una persona real.
PLANTILLAS = [
    'Lo que España pide hoy es "{t}", y nosotros lo garantizamos. Quien no lo vea, no está escuchando a la gente.',
    'Haremos que "{t}" sea gratis para todas las familias antes de Navidad. Lo pagarán los de siempre, no te preocupes.',
    'Crearemos un Ministerio de "{t}" con partida propia. Porque un país moderno no puede vivir de espaldas a "{t}".',
    'Ponemos en marcha un plan nacional para "{t}", financiado desde el primer día. El anterior Gobierno lo ignoró; nosotros no.',
    '"{t}" para todos, sin letra pequeña y sin excusas. Es un derecho, no un privilegio.',
    'Escuchamos a la calle, y la calle habla de "{t}". Por eso hoy es nuestra máxima prioridad.',
    'Defenderemos "{t}" por encima de cualquier otra cosa. Que nadie dude de nuestro compromiso con "{t}".',
    'Se acabó esperar: "{t}" se resuelve esta misma semana. La burocracia no puede frenar lo que el pueblo reclama.',
    'Declararemos "{t}" fiesta nacional a partir de hoy. España necesita volver a ilusionarse, y "{t}" es esa ilusión.',
    'España liderará en el mundo la causa de "{t}". Mientras otros miran para otro lado, nosotros damos un paso al frente.',
    'Incluiremos "{t}" en la Seguridad Social este mismo mes. Porque la salud de un país también se mide por "{t}".',
    'Pondremos "{t}" en el temario de todos los colegios. Nuestros hijos merecen crecer sabiendo lo que importa de verdad.',
    'Convocaremos una cumbre mundial urgente sobre "{t}". El planeta entero está pendiente, y España no se va a quedar atrás.',
    'Habrá ayudas directas de mil euros para quien apoye "{t}". El esfuerzo de la gente corriente tiene que premiarse.',
    'Renombraremos una calle de cada ciudad como "{t}", para que nadie olvide este momento histórico.',
    'Si "{t}" existe, "{t}" ya está en nuestro programa. No venimos a prometer: venimos a cumplir con "{t}".',
    'Bajaremos los impuestos a todo lo relacionado con "{t}". Y, a la vez, invertiremos más en "{t}" que nunca.',
    'Lo decimos alto y claro: nuestro futuro se llama "{t}". Vota futuro, vota "{t}".',
]


def limpiar(term):
    term = re.sub(r"\s+", " ", term).strip().rstrip(".!?:;,")
    if len(term) > 68:
        term = re.split(r"[,:–—-]", term)[0].strip()[:68]
    return term


def a_discurso(term):
    return random.choice(PLANTILLAS).format(t=limpiar(term))


def recolectar():
    bruto = []
    bruto += safe(from_google_trends, "Google Trends")
    bruto += safe(from_google_news, "Google News")
    bruto += safe(from_wikipedia, "Wikipedia")
    bruto += safe(from_medios, "medios RSS")
    bruto += safe(from_hackernews, "Hacker News")
    bruto += safe(from_reddit, "Reddit")

    vistos, items = set(), []
    for term, source in bruto:
        clave = limpiar(term).lower()
        if not clave or clave in vistos or len(clave) < 3:
            continue
        vistos.add(clave)
        items.append({"term": limpiar(term), "source": source, "speech": a_discurso(term)})
    random.shuffle(items)
    return items[:MAX_ITEMS]


def escribir(path="trends.json"):
    items = recolectar()
    payload = {
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "count": len(items),
        "items": items,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"trends.json actualizado · {len(items)} entradas · {payload['updated']}")


if __name__ == "__main__":
    loop = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[1] == "--loop" else None
    while True:
        escribir()
        if not loop:
            break
        time.sleep(loop)

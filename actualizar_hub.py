#!/usr/bin/env python3
"""
actualizar_hub.py
Escanea las carpetas de semanales y digests diarios,
extrae metadata de cada HTML y actualiza el array REPORTS en index.html.
Correr desde la carpeta raíz del proyecto:
    python3 actualizar_hub.py
"""

import os, re, json
from datetime import datetime, date

BASE = os.path.dirname(os.path.abspath(__file__))

DIAS_ES = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
MESES_ES = ['','enero','febrero','marzo','abril','mayo','junio',
            'julio','agosto','septiembre','octubre','noviembre','diciembre']

def strip_tags(html):
    return re.sub(r'<[^>]+>', '', html).replace('&amp;', '&').replace('&nbsp;', ' ').strip()

def clean_html(html):
    """Elimina bloques <style> y <script> para que el parser no agarre CSS/JS."""
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S|re.I)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S|re.I)
    return html

def one_line(text):
    """Colapsa saltos de línea y espacios múltiples en un espacio."""
    return re.sub(r'\s+', ' ', text).strip()

def date_display(d: date) -> str:
    dia_sem = DIAS_ES[d.weekday()]
    return f"{dia_sem} {d.day} de {MESES_ES[d.month]} {d.year}"

def date_display_short(d: date) -> str:
    return f"{d.day} de {MESES_ES[d.month]} {d.year}"

# ── Parsers ──────────────────────────────────────────────────────────────────

def parse_semanal(filepath, relpath):
    with open(filepath, encoding='utf-8') as f:
        html = f.read()

    # Date from filename: digest-semanal-YYYY-MM-DD.html
    fname = os.path.basename(filepath)
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    if not m:
        return None
    d = datetime.strptime(m.group(1), '%Y-%m-%d').date()

    # Title from <h1> — normalize to full title
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    raw_title = strip_tags(h1.group(1)) if h1 else ''
    title = raw_title if ('—' in raw_title or len(raw_title) > 20) else 'Digest Semanal — Economía & Mercados'

    # Subtitle: try multiple patterns across different file versions
    subtitle = ''
    # v1: <p class="sub">Semana 28 abr – 2 may 2026 · ...</p>
    sub = re.search(r'<p class="sub">(.*?)</p>', html, re.S)
    if sub:
        raw = strip_tags(sub.group(1))
        subtitle = raw.split('·')[0].strip().rstrip('&').strip()
    # v2: <span class="badge">17–24 abr 2026</span>
    if not subtitle:
        badge = re.search(r'<span class="badge">(.*?)</span>', html, re.S)
        if badge:
            subtitle = 'Semana ' + strip_tags(badge.group(1))
    # v3: from <title> — "Digest Semanal — 24 de abril 2026"
    if not subtitle:
        ttl = re.search(r'<title>(.*?)</title>', html, re.S)
        if ttl:
            raw = strip_tags(ttl.group(1))
            parts = raw.split('—')
            if len(parts) > 1:
                subtitle = parts[-1].strip()

    # Tags from tab buttons
    tabs = re.findall(r'<button class="tab[^"]*"[^>]*>(.*?)</button>', html, re.S)
    tags = [one_line(strip_tags(t)) for t in tabs]

    # Snippet: buscar en HTML limpio
    body = clean_html(html)
    snippet = ''
    # v1: clase section-text
    st = re.search(r'class="section-text">(.*?)</div>', body, re.S)
    if st:
        snippet = one_line(strip_tags(st.group(1)))[:280].rstrip(',. ') + '...'
    # v2: cualquier texto largo en el body
    if not snippet:
        chunks = re.findall(r'>([^<]{80,})<', body)
        for c in chunks:
            c = one_line(c)
            if len(c) > 80 and not c.startswith(('--', '.', '#', '/*', 'Fuente')):
                snippet = c[:280].rstrip(',. ') + '...'
                break
    if not snippet and chunks:
        snippet = one_line(chunks[0])[:280].rstrip(',. ') + '...'

    return {
        'type': 'semanal',
        'title': title,
        'subtitle': subtitle,
        'date': d.isoformat(),
        'dateDisplay': date_display_short(d),
        'snippet': snippet,
        'tags': tags,
        'path': relpath,
    }

def parse_diario(filepath, relpath):
    with open(filepath, encoding='utf-8') as f:
        html = f.read()

    # Date from filename: Digest Diario - YYYY-MM-DD.html
    fname = os.path.basename(filepath)
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    if not m:
        return None
    d = datetime.strptime(m.group(1), '%Y-%m-%d').date()

    title = 'Digest Diario — Mercados'
    subtitle = date_display(d)

    # Trabajar siempre sobre HTML sin style/script
    body = clean_html(html)

    # Tags: section-title divs (ej: "Snapshot de Mercado · Cierre 5-may")
    section_titles = re.findall(r'class="section-title[^"]*"[^>]*>(.*?)</div>', body, re.S)
    tags = []
    for t in section_titles:
        clean = one_line(strip_tags(t)).split('·')[0].strip()
        if clean and len(clean) < 40:
            tags.append(clean)
    tags = list(dict.fromkeys(tags))[:5]   # dedup, máx 5
    if not tags:
        tags = ['Mercados', 'Renta Fija', 'FX', 'Global']

    # Snippet: primer bloque de texto largo
    snippet = ''
    # 1) Nueva estructura: clase 'point-text' (contenido del primer punto de un bloque temático)
    pt = re.search(r'class="point-text"[^>]*>([^<]{60,})<', body)
    if pt:
        snippet = one_line(strip_tags(pt.group(1)))[:280].rstrip(',. ') + '...'
    # 2) Estructura previa: section-block / block-cambio / block-importa
    if not snippet:
        for block_class in ('block-cambio', 'block-importa', 'section-block'):
            m2 = re.search(rf'class="[^"]*{block_class}[^"]*"[^>]*>(.*?)</div>', body, re.S)
            if m2:
                candidate = one_line(strip_tags(m2.group(1)))
                if len(candidate) > 60:
                    snippet = candidate[:280].rstrip(',. ') + '...'
                    break
    # 3) Fallback: primer texto largo de cualquier elemento, ignorando frases de empty/warning
    if not snippet:
        chunks = re.findall(r'>([^<]{80,})<', body)
        SKIP_PREFIXES = ('--', '.', '#', '/*', 'Sin contenido de MNH', 'Para fines informativos')
        for c in chunks:
            c = one_line(c)
            if len(c) > 80 and not c.startswith(SKIP_PREFIXES):
                snippet = c[:280].rstrip(',. ') + '...'
                break

    return {
        'type': 'diario',
        'title': title,
        'subtitle': subtitle,
        'date': d.isoformat(),
        'dateDisplay': date_display(d),
        'snippet': snippet,
        'tags': tags,
        'path': relpath,
    }

def parse_premarket(filepath, relpath):
    with open(filepath, encoding='utf-8') as f:
        html = f.read()

    # Date from filename: resumen-mercados-YYYY-MM-DD.html
    fname = os.path.basename(filepath)
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    if not m:
        return None
    d = datetime.strptime(m.group(1), '%Y-%m-%d').date()

    title = 'Pre-Market — Resumen de Mercados'
    subtitle = date_display(d)

    body = clean_html(html)

    # Tags: intentar extraer highlights (labels del .hl-item)
    labels = re.findall(r'class="label">(.*?)</div>', body, re.S)
    tags = [one_line(strip_tags(l)) for l in labels if strip_tags(l).strip()][:5]
    if not tags:
        tags = ['Pre-Market', 'Mercados', 'FX', 'Global']

    # Snippet: primer .hl-item val o cualquier texto largo
    snippet = ''
    hl_vals = re.findall(r'class="val[^"]*">(.*?)</div>', body, re.S)
    if hl_vals and labels:
        pairs = [f'{strip_tags(l)}: {strip_tags(v)}' for l, v in zip(labels[:4], hl_vals[:4])]
        snippet = ' · '.join(pairs)
    if not snippet:
        chunks = re.findall(r'>([^<]{60,})<', body)
        SKIP = ('--', '.', '#', '/*', 'Sin contenido')
        for c in chunks:
            c = one_line(c)
            if len(c) > 60 and not c.startswith(SKIP):
                snippet = c[:280].rstrip(',. ') + '...'
                break

    return {
        'type': 'premarket',
        'title': title,
        'subtitle': subtitle,
        'date': d.isoformat(),
        'dateDisplay': date_display(d),
        'snippet': snippet,
        'tags': tags,
        'path': relpath,
    }


# ── Scanner ──────────────────────────────────────────────────────────────────

def scan():
    reports = []

    # Pre-Markets
    pre_dir = os.path.join(BASE, 'Pre-Markets')
    if os.path.isdir(pre_dir):
        for fname in sorted(os.listdir(pre_dir), reverse=True):
            if not fname.endswith('.html'):
                continue
            fpath = os.path.join(pre_dir, fname)
            relpath = f'Pre-Markets/{fname}'
            r = parse_premarket(fpath, relpath)
            if r:
                reports.append(r)
                print(f'  ✓ premarket {r["date"]}')

    # Semanales
    sem_dir = os.path.join(BASE, 'semanales')
    if os.path.isdir(sem_dir):
        for fname in sorted(os.listdir(sem_dir), reverse=True):
            if not fname.endswith('.html') or not fname.startswith('digest-semanal-'):
                continue
            fpath = os.path.join(sem_dir, fname)
            relpath = f'semanales/{fname}'
            r = parse_semanal(fpath, relpath)
            if r:
                reports.append(r)
                print(f'  ✓ semanal   {r["date"]}')

    # Digests diarios
    dia_dir = os.path.join(BASE, 'digests-diarios', 'html')
    if os.path.isdir(dia_dir):
        for fname in sorted(os.listdir(dia_dir), reverse=True):
            if not fname.endswith('.html'):
                continue
            fpath = os.path.join(dia_dir, fname)
            relpath = f'digests-diarios/html/{fname}'
            r = parse_diario(fpath, relpath)
            if r:
                reports.append(r)
                print(f'  ✓ diario    {r["date"]}')

    # Sort all by date descending
    reports.sort(key=lambda r: r['date'], reverse=True)
    return reports

# ── Updater ──────────────────────────────────────────────────────────────────

def update_index(reports):
    index_path = os.path.join(BASE, 'index.html')
    with open(index_path, encoding='utf-8') as f:
        html = f.read()

    js_array = json.dumps(reports, ensure_ascii=False, indent=2)
    # Compact: keep readable but not too wide
    js_array = re.sub(r'\n    ', '\n  ', js_array)

    new_block = f'const REPORTS = {js_array};'

    updated = re.sub(
        r'const REPORTS = \[.*?\];',
        new_block,
        html,
        flags=re.S,
    )

    if updated == html:
        print('⚠  No se encontró el bloque REPORTS en index.html')
        return

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(updated)
    print(f'\n✅  index.html actualizado con {len(reports)} reporte(s)')

# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('Escaneando reportes...')
    reports = scan()
    if not reports:
        print('No se encontraron reportes.')
    else:
        update_index(reports)
        print('\nReportes incluidos:')
        for r in reports:
            print(f'  [{r["type"]:7}] {r["date"]}  {r["subtitle"]}')

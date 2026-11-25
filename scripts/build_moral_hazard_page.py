#!/usr/bin/env python3
"""Build research/moral-hazard/index.html from research/moral-hazard/article.md.

The markdown stays the single source: edit article.md, then rerun

    python3 scripts/build_moral_hazard_page.py

Requires Python-Markdown (pip install markdown). No network.

What the page adds to plain markdown:
- the layout and type of the demographics essay (top bar, a contents column,
  figure cards, callouts), so the two read as one site;
- math typeset in the browser by the KaTeX copy the site already hosts in
  demographics/vendor/katex (no CDN). TeX is pulled out of the markdown before
  conversion, so underscores and asterisks inside formulas cannot be read as
  emphasis, and is put back as escaped text that katex.render() typesets;
- figures as SVG with numbered captions, each linking to the full-size file;
- the two text versions of Figure 8 (ASCII art and Mermaid source) folded into
  collapsed boxes, since the figure itself already shows the graph.
"""
import html
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:  # pragma: no cover
    sys.exit("Python-Markdown is required: pip install markdown")

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "research" / "moral-hazard"
SRC = SRC_DIR / "article.md"
OUT = SRC_DIR / "index.html"
KATEX = "../../demographics/vendor/katex"   # relative to the page
WORDS_PER_MINUTE = 230


# ------------------------------------------------------------------ math
def protect_math(text):
    """Swap every $$..$$ and $..$ for a placeholder; return text and table."""
    table = []

    def stash(tex, display):
        table.append((tex.strip(), display))
        return f"MATHPH{len(table) - 1:04d}X"

    # fenced code blocks hold no math; leave them untouched
    parts = re.split(r"(^```.*?^```[ \t]*$)", text, flags=re.M | re.S)
    for i in range(0, len(parts), 2):
        chunk = parts[i]
        chunk = re.sub(r"\$\$(.+?)\$\$", lambda m: stash(m.group(1), True), chunk, flags=re.S)
        chunk = re.sub(r"(?<![\\$])\$(?!\$)([^\n$]+?)(?<!\\)\$", lambda m: stash(m.group(1), False), chunk)
        parts[i] = chunk
    return "".join(parts), table


def restore_math(body, table):
    def tag(i):
        tex, display = table[int(i)]
        tex = html.escape(tex, quote=False)
        if display:
            return f'<div class="math display">{tex}</div>'
        return f'<span class="math inline">{tex}</span>'

    # a display formula alone in a paragraph becomes a block
    body = re.sub(r"<p>\s*MATHPH(\d{4})X\s*</p>", lambda m: tag(m.group(1)), body)
    body = re.sub(r"MATHPH(\d{4})X", lambda m: tag(m.group(1)), body)
    return body


# --------------------------------------------------------------- headings
def slug(text):
    num = re.match(r"(\d+(?:\.\d+)*)\.?\s", text)
    if num:
        return "s" + num.group(1).replace(".", "-")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def number_headings(body):
    toc, seen = [], set()

    def fix(m):
        level, inner = m.group(1), m.group(2)
        hid = slug(strip_tags(inner))
        while hid in seen:
            hid += "-x"
        seen.add(hid)
        if level == "2":
            toc.append((hid, inner))
        return f'<h{level} id="{hid}">{inner}</h{level}>'

    body = re.sub(r"<h([23])>(.*?)</h\1>", fix, body, flags=re.S)
    return body, toc


# ---------------------------------------------------------------- figures
def fix_figures(body):
    """A paragraph holding only an image becomes a numbered figure card."""
    return re.sub(r'<p>\s*<img alt="([^"]*)" src="([^"]+)"\s*/?>\s*</p>',
                  lambda m: _figure(m.group(2), html.unescape(m.group(1))), body)


def _figure(src, alt):
    svg = re.sub(r"\.png$", ".svg", src)
    if (SRC_DIR / svg).exists():
        src = svg
    num = re.match(r"Figure\s+(\d+)\.\s*(.*)", alt)
    title = num.group(2) if num else alt
    label = f"Figure {num.group(1)}" if num else "Figure"
    fid = f' id="fig{num.group(1)}"' if num else ""
    return (
        f'<figure{fid}><a class="fig-link" href="{src}" '
        f'aria-label="{html.escape(label)}: {html.escape(title)} (opens the full-size image)">'
        f'<img src="{src}" alt="{html.escape(title)}" loading="lazy" decoding="async"></a>'
        f"<figcaption><b>{label}.</b> {html.escape(title)}</figcaption></figure>"
    )


# ------------------------------------------------------- code, tables, refs
def code_blocks(body):
    def box(m):
        lang, code = m.group(1), m.group(2)
        label = "The graph as Mermaid source" if lang == "mermaid" else "The graph as plain text"
        return (f'<details class="diagram-text"><summary>{label}</summary>'
                f"<pre><code>{code}</code></pre></details>")

    return re.sub(r'<pre><code(?: class="language-([\w-]+)")?>(.*?)</code></pre>', box, body, flags=re.S)


def tables(body):
    body = re.sub(r"<table>", '<div class="table-wrap"><table>', body)
    body = re.sub(r"</table>", "</table></div>", body)
    return re.sub(r"<th>", '<th scope="col">', body)


def references(body):
    m = re.search(r'(<h2 id="references">.*?</h2>)(.*)$', body, flags=re.S)
    if not m:
        return body
    return body[: m.start()] + m.group(1) + f'<div class="references">{m.group(2)}</div>'


# ----------------------------------------------------------------- header
def split_header(md_text):
    """Title, byline lines and the italic status note sit above the first ##."""
    head, rest = re.split(r"(?m)^(?=## )", md_text, maxsplit=1)
    lines = [l.strip() for l in head.splitlines() if l.strip()]
    title = re.sub(r"^#\s+", "", lines[0])
    note = next((l.strip("*") for l in lines[1:] if l.startswith("*") and l.endswith("*")), "")
    byline = [l for l in lines[1:] if not (l.startswith("*") and l.endswith("*"))]
    return title, byline, note, rest


# ----------------------------------------------------------------- render
def build():
    md_text = SRC.read_text(encoding="utf-8")
    title, byline, note, rest = split_header(md_text)
    words = len(re.findall(r"\w+", re.sub(r"\$[^$]*\$", " ", rest)))
    minutes = int(round(words / WORDS_PER_MINUTE / 5.0) * 5)

    protected, math_table = protect_math(rest)
    body = markdown.markdown(
        protected,
        extensions=["tables", "fenced_code", "sane_lists", "smarty"],
        output_format="html",
    )
    body = restore_math(body, math_table)
    body, toc = number_headings(body)
    body = fix_figures(body)
    body = code_blocks(body)
    body = tables(body)
    body = references(body)

    leftover = re.findall(r"(?<!\\)\$", re.sub(r'<(div|span) class="math[^>]*>.*?</\1>', "", body, flags=re.S))
    n_fig = len(re.findall(r"<figure", body))
    abstract = re.search(r'<h2 id="abstract">.*?</h2>\s*<p>(.*?)</p>', body, flags=re.S)
    description = strip_tags(abstract.group(1)) if abstract else title
    description = re.sub(r"\s+", " ", description)
    if len(description) > 300:
        description = description[:297].rsplit(" ", 1)[0] + "…"

    toc_html = "\n".join(
        f'        <li><a href="#{hid}">{strip_tags(text)}</a></li>' for hid, text in toc
    )
    page = TEMPLATE.format(
        title=html.escape(title),
        description=html.escape(description, quote=True),
        byline=" · ".join(html.escape(b.rstrip()) for b in byline),
        note=html.escape(note),
        minutes=minutes,
        n_fig=n_fig,
        toc=toc_html,
        body=body,
        katex=KATEX,
    )
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(page) / 1024:.0f} KB, {len(toc)} sections, "
          f"{len(math_table)} formulas, {n_fig} figures, about {minutes} min")
    if leftover:
        print(f"warning: {len(leftover)} stray $ left outside math", file=sys.stderr)
        return 1
    return 0


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:type" content="article" />
  <link rel="icon" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><text y='13' font-size='13'>&#9878;</text></svg>" />
  <link rel="stylesheet" href="{katex}/katex.min.css" />
  <!-- Generated from article.md by scripts/build_moral_hazard_page.py. Edit the markdown, not this file. -->
  <style>
    :root{{
      --bg:#FAFAFA; --card-bg:#FFFFFF; --text:#1E1E1E; --muted:#555; --rule:#E5E5EA;
      --accent:#1F4E9E; --accent-soft:#DCE6F4; --gold:#6B5409; --gold-line:#C9A227; --gold-soft:#F6EFD8; --code-bg:#F2F2F5;
      --shadow:0 1px 2px rgba(0,0,0,.04),0 6px 18px rgba(0,0,0,.05); --radius:12px;
    }}
    *,*::before,*::after{{box-sizing:border-box}}
    html{{scroll-padding-top:3.6rem}}
    @media (prefers-reduced-motion: no-preference){{html{{scroll-behavior:smooth}}}}
    body{{margin:0;background:var(--bg);color:var(--text);
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Helvetica,Arial,sans-serif;
      font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased}}
    a{{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(31,78,158,.25)}}
    a:hover{{border-bottom-color:var(--accent)}}
    a:focus-visible,summary:focus-visible,button:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
    .skip{{position:absolute;left:-9999px;top:0;background:#fff;color:#1a1a1a;padding:8px 14px;font-weight:600;z-index:3000;border:2px solid #1a1a1a}}
    .skip:focus{{left:8px;top:8px}}
    .topbar{{position:sticky;top:0;z-index:30;background:#1b2330;color:#fff;display:flex;gap:1rem;align-items:center;padding:.6rem 1.2rem;font-size:.92rem;flex-wrap:wrap}}
    .topbar a{{color:#cfe0ff;border:none}}
    .topbar a:hover{{color:#fff}}
    .topbar .brand{{font-weight:700;color:#fff;margin-right:auto}}
    .page{{display:grid;grid-template-columns:230px minmax(0,760px);gap:2.4rem;max-width:1080px;margin:0 auto;padding:2rem 1.2rem 5rem}}
    .toc{{position:sticky;top:3.4rem;align-self:start;font-size:.85rem;max-height:calc(100vh - 4.4rem);overflow:auto}}
    .toc ol{{list-style:none;margin:0;padding:0}}
    .toc li{{margin:.18rem 0;line-height:1.35}}
    .toc a{{color:var(--muted);border:none;display:block;padding:.12rem 0 .12rem .55rem;border-left:2px solid transparent}}
    .toc a:hover{{color:var(--accent)}}
    .toc a.on{{color:var(--text);font-weight:600;border-left-color:var(--accent)}}
    .toc .k{{font-weight:700;color:var(--text);text-transform:uppercase;letter-spacing:.04em;font-size:.72rem;margin:0 0 .4rem .55rem}}
    .toc-toggle{{display:none}}
    main{{min-width:0}}
    h1{{font-size:2.35rem;line-height:1.12;margin:.2rem 0 .7rem;letter-spacing:-.5px}}
    h2{{font-size:1.5rem;line-height:1.25;margin:2.6rem 0 .5rem;padding-top:.6rem;border-top:1px solid var(--rule)}}
    h3{{font-size:1.14rem;line-height:1.3;margin:1.8rem 0 .3rem}}
    p{{margin:.8rem 0}}
    .badges{{display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;margin-bottom:1rem}}
    .badges a{{display:inline-flex;border:none}}
    .badge{{font-size:.72rem;background:var(--accent-soft);color:var(--accent);padding:.2rem .6rem;border-radius:99px;border:none;font-weight:600}}
    .badge.draft{{background:var(--gold-soft);color:var(--gold)}}
    .byline{{color:var(--muted);font-size:.95rem;margin:0 0 1rem}}
    .callout{{background:var(--card-bg);border:1px solid var(--rule);border-left:4px solid var(--gold-line);border-radius:var(--radius);padding:.75rem 1rem;margin:1.1rem 0;box-shadow:var(--shadow);font-size:.95rem}}
    .callout .k{{font-weight:700;font-size:.74rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);display:block;margin-bottom:.15rem}}
    .math.display{{overflow-x:auto;overflow-y:hidden;margin:1rem 0;padding:.2rem 0;text-align:center;position:relative}}
    .katex{{font-size:1.06em}}
    figure{{margin:1.6rem 0}}
    figure .fig-link{{display:block;border:1px solid var(--rule);border-radius:var(--radius);background:var(--card-bg);box-shadow:var(--shadow);padding:.8rem}}
    figure .fig-link:hover{{border-color:var(--accent)}}
    figure img{{display:block;width:100%;height:auto}}
    figcaption{{font-size:.84rem;color:var(--muted);margin-top:.5rem;text-align:center;line-height:1.5}}
    figcaption b{{color:var(--text)}}
    /* position:relative makes each scroll box the containing block of KaTeX's
       absolutely positioned (hidden) MathML, so a wide table cannot widen the page */
    .table-wrap{{overflow-x:auto;margin:1.2rem 0;position:relative}}
    table{{border-collapse:collapse;width:100%;font-size:.86rem;line-height:1.5}}
    th,td{{border:1px solid var(--rule);padding:.45rem .6rem;text-align:left;vertical-align:top}}
    th{{background:var(--accent-soft);color:var(--accent)}}
    ol,ul{{padding-left:1.4rem}}
    li{{margin:.3rem 0}}
    details.diagram-text{{margin:.6rem 0;font-size:.88rem;border:1px dashed var(--rule);border-radius:8px;padding:.45rem .8rem;background:#FCFCFD}}
    details.diagram-text summary{{cursor:pointer;font-weight:600;color:var(--muted)}}
    details.diagram-text pre{{overflow-x:auto;background:var(--code-bg);border-radius:6px;padding:.7rem;margin:.6rem 0 .2rem;font-size:.78rem;line-height:1.35}}
    code{{font-family:SFMono-Regular,Consolas,Menlo,monospace}}
    .references p{{font-size:.86rem;line-height:1.55;padding-left:1.6rem;text-indent:-1.6rem;margin:.55rem 0;overflow-wrap:anywhere}}
    .references p:first-child{{padding-left:0;text-indent:0;color:var(--muted)}}
    .colophon{{margin-top:3rem;border-top:1px solid var(--rule);padding-top:1rem;font-size:.85rem;color:var(--muted)}}
    .colophon h2{{border:none;font-size:1.05rem;margin-top:.6rem;padding-top:0}}
    @media(max-width:880px){{
      .page{{grid-template-columns:minmax(0,1fr);gap:1rem;padding-top:1.2rem}}
      h1{{font-size:1.9rem}}
      .toc{{position:static;max-height:none}}
      .toc>nav{{display:none}}
      .toc.open>nav{{display:block}}
      .toc-toggle{{display:block;width:100%;text-align:left;background:var(--card-bg);border:1px solid var(--rule);border-radius:8px;padding:.45rem .8rem;font:inherit;font-size:.9rem;cursor:pointer}}
      figure .fig-link{{padding:.4rem}}
    }}
  </style>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <nav class="topbar" aria-label="Site">
    <a class="brand" href="../../index.html">Scott Nelson</a>
    <a href="../../index.html#projects">Projects</a>
    <a href="../../demographics/">Demographics</a>
    <a href="../../actuarial-pricing.html">Actuarial track</a>
    <a href="../../resume.html">Resume</a>
  </nav>

  <div class="page">
    <aside class="toc" id="toc" aria-label="Contents">
      <button type="button" class="toc-toggle" id="toc-toggle" aria-expanded="false" aria-controls="toc-nav">Contents ▾</button>
      <nav id="toc-nav" aria-label="Table of contents">
        <div class="k">Contents</div>
        <ol>
{toc}
        </ol>
      </nav>
    </aside>

    <main id="main">
      <header>
        <div class="badges">
          <span class="badge draft">Draft for review</span>
          <span class="badge">about {minutes} min read</span>
          <span class="badge">{n_fig} figures</span>
          <a href="moral-hazard-article.pdf"><span class="badge">PDF version</span></a>
        </div>
        <h1>{title}</h1>
        <p class="byline">{byline}</p>
        <div class="callout"><span class="k">Status</span>{note}</div>
      </header>

{body}

      <footer class="colophon" id="colophon">
        <h2>About this page</h2>
        <p>This page is generated from <a href="article.md">article.md</a> by
          <code>scripts/build_moral_hazard_page.py</code>. A letter-size reading copy is the
          <a href="moral-hazard-article.pdf">PDF version</a>. The figures are drawn by the scripts in
          <code>figures/scripts/</code> from the article's stated, illustrative parameters; they are
          not empirical estimates. Math is typeset with a self-hosted copy of
          <a href="https://katex.org/">KaTeX</a> 0.16.9. No CDNs, no trackers.</p>
        <p><a href="../../index.html#projects">← back to all projects</a></p>
      </footer>
    </main>
  </div>

  <script src="{katex}/katex.min.js"></script>
  <script>
    (function () {{
      // Typeset every formula the build marked; on failure leave the TeX visible.
      var bad = 0;
      document.querySelectorAll('.math').forEach(function (el) {{
        try {{
          katex.render(el.textContent, el, {{ displayMode: el.classList.contains('display'), throwOnError: true }});
        }} catch (e) {{
          bad++; el.classList.add('math-error'); console.warn('[katex]', e.message, '|', el.textContent);
        }}
      }});
      if (bad) console.warn('[katex] ' + bad + ' formula(s) left as TeX');

      // Contents: collapse on small screens; mark the section in view.
      var toc = document.getElementById('toc'), btn = document.getElementById('toc-toggle');
      btn.addEventListener('click', function () {{
        var open = toc.classList.toggle('open');
        btn.setAttribute('aria-expanded', open);
        btn.textContent = open ? 'Contents ▴' : 'Contents ▾';
      }});
      toc.querySelectorAll('a').forEach(function (a) {{
        a.addEventListener('click', function () {{
          if (window.matchMedia('(max-width: 880px)').matches && toc.classList.contains('open')) btn.click();
        }});
      }});
      // The section in view is the last heading above a line 30% down the window,
      // so a jump straight into the middle of a section still marks it.
      var links = {{}}, current = null, pending = false;
      toc.querySelectorAll('a').forEach(function (a) {{ links[a.getAttribute('href').slice(1)] = a; }});
      var heads = Array.prototype.slice.call(document.querySelectorAll('main h2[id]'));
      function mark() {{
        pending = false;
        var line = window.innerHeight * 0.3, hit = heads[0];
        for (var i = 0; i < heads.length; i++) {{ if (heads[i].getBoundingClientRect().top <= line) hit = heads[i]; else break; }}
        var a = hit && links[hit.id];
        if (a !== current) {{ if (current) current.classList.remove('on'); current = a; if (a) a.classList.add('on'); }}
      }}
      window.addEventListener('scroll', function () {{ if (!pending) {{ pending = true; requestAnimationFrame(mark); }} }}, {{ passive: true }});
      window.addEventListener('resize', mark);
      mark();
    }})();
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    sys.exit(build())

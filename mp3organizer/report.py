import html
from pathlib import Path


def write_html_report(entries, out_path: Path):
    rows = []
    for idx, e in enumerate(entries, 1):
        rows.append(
            f"<tr><td>{idx}</td><td>{html.escape(e['artist'])}</td><td>{html.escape(e['title'])}</td><td>{e['dest']}</td></tr>"
        )
    html_content = (
        "<html><body><table border='1'>"
        "<tr><th>#</th><th>Artist</th><th>Title</th><th>Destination</th></tr>"
        f"{''.join(rows)}" "</table></body></html>"
    )
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

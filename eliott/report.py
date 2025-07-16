import html
from pathlib import Path


def write_html_report(entries, out_path: Path):
    rows = []
    for idx, e in enumerate(entries, 1):
        rows.append(
            "<tr>"
            f"<td>{idx}</td>"
            f"<td>{html.escape(e['artist'])}</td>"
            f"<td>{html.escape(e['title'])}</td>"
            f"<td>{html.escape(e['album'])}</td>"
            f"<td>{html.escape(e['year'])}</td>"
            f"<td>{html.escape(e['genre'])}</td>"
            f"<td>{html.escape(e['dest'])}</td>"
            f"<td><audio controls src='{html.escape(e['path'])}'></audio></td>"
            "</tr>"
        )

    html_content = (
        "<html><body><table border='1'>"
        "<tr>"
        "<th>#</th><th>Artist</th><th>Title</th><th>Album</th><th>Year</th>"
        "<th>Genre</th><th>Destination</th><th>Preview</th>"
        "</tr>"
        f"{''.join(rows)}" "</table></body></html>"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

type Row = { patent: string; title: string; grant_date?: string | null };

const normalizeId = (pn: string) => pn.trim().replace(/\s+/g, "");

const googleId = (pn: string) => {
  const raw = normalizeId(pn);

  if (/^US/i.test(raw)) return raw;

  if (/^D\d+/i.test(raw)) return `USD${raw.slice(1)}`;

  if (/^(RE|PP|H|T)\d+/i.test(raw)) return `US${raw.toUpperCase()}`;

  return `US${raw}`;
};

const googlePatentsSearchUrl = (pn: string) =>
  `https://patents.google.com/?q=${encodeURIComponent(googleId(pn))}&oq=${encodeURIComponent(
    pn
  )}`;

export default function ResultsTable({ rows, total }: { rows: Row[]; total: number }) {
  if (!rows?.length) {
    return (
      <div className="card-empty">
        No results yet. Try a broader keyword (e.g., <span className="fw-500">sensor</span>).
      </div>
    );
  }

  return (
    <div className="list">
      <div className="meta small">Found {total.toLocaleString()} result{total === 1 ? "" : "s"}</div>

      <ul className="list-gap">
        {rows.map((r) => {
          const gpListUrl = googlePatentsSearchUrl(r.patent);

          return (
            <li key={r.patent} className="card">
              <div className="card-main">
                <div className="patent-line">
                  <a
                    href={gpListUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="patent-link"
                    title="Open on Google Patents (search list)"
                  >
                    {r.patent}
                  </a>
                  {r.grant_date && (
                    <span className="pill-date">
                      {new Date(r.grant_date).toLocaleDateString()}
                    </span>
                  )}
                </div>

                <div className="title-line">{r.title}</div>
              </div>

              <div className="card-actions">
                <a
                  href={gpListUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-outline"
                  title="Open on Google Patents (search list)"
                >
                  View →
                </a>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
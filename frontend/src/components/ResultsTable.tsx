type Row = { patent: string; title: string; grant_date?: string | null };

/* ---------- helpers for external links ---------- */

// squash spaces like "12 440 146" -> "12440146"
const normalizeId = (pn: string) => pn.trim().replace(/\s+/g, "");

/** Build the identifier Google/USPTO expect. Kind code optional. */
const googleId = (pn: string) => {
  const raw = normalizeId(pn);

  // Already prefixed (US, USD, USRE, USPP, etc.)
  if (/^US/i.test(raw)) return raw;

  // Design patents: D123456 -> USD123456
  if (/^D\d+/i.test(raw)) return `USD${raw.slice(1)}`;

  // Reissue/Plant/H-Patents/etc. -> add US prefix
  if (/^(RE|PP|H|T)\d+/i.test(raw)) return `US${raw.toUpperCase()}`;

  // Utility: 12440146 -> US12440146
  return `US${raw}`;
};

/** Open the **Google Patents search list** (more reliable for very new grants). */
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
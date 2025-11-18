type Row = { patent: string; title: string; grant_date?: string | null };

const normalizeId = (pn: string) => pn.trim();

const usptoPatentUrl = (pn: string) => {
  const raw = normalizeId(pn);
  const digits = raw.replace(/\D/g, "");
  if (!digits) {
    return "https://patft.uspto.gov/";
  }
  return `https://patft.uspto.gov/netacgi/nph-Parser?patentnumber=${digits}`;
};

function formatYMDLocal(ymd: string) {
  const [y, m, d] = ymd.split("-").map((v) => parseInt(v, 10));
  if (!y || !m || !d) return ymd;
  const dt = new Date(y, m - 1, d);
  return dt.toLocaleDateString();
}

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
      <div className="meta small">
        Found {total.toLocaleString()} result{total === 1 ? "" : "s"}
      </div>

      <ul className="list-gap">
        {rows.map((r) => {
          const usptoUrl = usptoPatentUrl(r.patent);

          return (
            <li key={r.patent} className="card">
              <div className="card-main">
                <div className="patent-line">
                  <a
                    href={usptoUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="patent-link"
                    title="Open on USPTO (full record)"
                  >
                    {r.patent}
                  </a>
                  {r.grant_date && (
                    <span className="pill-date">
                      {formatYMDLocal(r.grant_date)}
                    </span>
                  )}
                </div>

                <div className="title-line">{r.title}</div>
              </div>

              <div className="card-actions">
                <a
                  href={usptoUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-outline"
                  title="Open on USPTO (full record)"
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
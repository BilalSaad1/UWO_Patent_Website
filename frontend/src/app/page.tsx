"use client";
import { useState } from "react";

type Hit = { patent: string; title: string; grant_date?: string | null };
type ApiResp = { q: string; page: number; per_page: number; total: number; results: Hit[] };

export default function Home() {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<Hit[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const per_page = 20;
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function go(nextPage = 1) {
    if (!q.trim()) return;
    setLoading(true); setErr(null);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/search?q=${encodeURIComponent(q)}&page=${nextPage}&per_page=${per_page}`
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: ApiResp = await res.json();
      setRows(data.results); setTotal(data.total); setPage(nextPage);
    } catch {
      setErr("Failed to fetch"); setRows([]); setTotal(0);
    } finally { setLoading(false); }
  }

  const pages = Math.max(1, Math.ceil(total / per_page));
  const from = total ? (page - 1) * per_page + 1 : 0;
  const to   = total ? Math.min(page * per_page, total) : 0;

  return (
    <div className="container">
      <h1 className="section-title">Find inactive U.S. patents</h1>
      <div className="section-sub">
        Search by title keyword. Results include patent number, title, and grant date.
      </div>

      <div className="search-wrap">
        <div className="search-pill">
          {/* magnifier svg */}
          <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor"
              d="M21 20.3 16.7 16A7.5 7.5 0 1 0 16 16.7L20.3 21zM4.5 11a6.5 6.5 0 1 1 13 0a6.5 6.5 0 0 1-13 0Z" />
          </svg>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && go(1)}
            placeholder="Search titles"
            aria-label="Search patents by title"
          />
        </div>
        <button className="search-btn" onClick={() => go(1)} disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
      </div>

      {err && <div className="meta">{err}</div>}

      {!rows.length ? (
        <div className="meta">
          No results yet.
        </div>
      ) : (
        <>
          <div className="meta">
            Showing {from}–{to} of {total} results
          </div>

          <table className="table" role="grid" aria-label="Search results">
            <tbody>
              {rows.map((r) => (
                <tr className="row" key={r.patent}>
                  <td className="cell pat">{r.patent}</td>
                  <td className="cell">{r.title}</td>
                  <td className="cell date">{r.grant_date ?? ""}</td>
                  <td className="cell" style={{ width: 80, textAlign: "right" }}>
                    <a
                      href={`https://patents.google.com/patent/${encodeURIComponent(r.patent)}`}
                      target="_blank" rel="noreferrer"
                    >
                      View →
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="pager">
            <button className="btn" onClick={() => go(Math.max(1, page - 1))} disabled={page <= 1 || loading}>
              Prev
            </button>
            <span className="meta">Page {page} / {pages}</span>
            <button className="btn" onClick={() => go(Math.min(pages, page + 1))} disabled={page >= pages || loading}>
              Next
            </button>
          </div>
        </>
      )}

      <div className="meta" style={{ marginTop: 18 }}>
        Data from USPTO Open Data (weekly). Open-source (GPL-3.0).
      </div>
    </div>
  );
}
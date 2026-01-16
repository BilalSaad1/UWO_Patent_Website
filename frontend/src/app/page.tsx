"use client";

import { useState } from "react";
import ResultsTable from "@/components/ResultsTable";
import SearchForm, { SortBy, SortDir } from "@/components/SearchForm";

type Hit = {
  patent: string;
  title: string;
  grant_date?: string | null;
};

type ApiResp = {
  q: string;
  page: number;
  per_page: number;
  total: number;
  results: Hit[];
};

const PER_PAGE = 20;

export default function Home() {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<Hit[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const [yearFrom, setYearFrom] = useState<number | null>(null);
  const [yearTo, setYearTo] = useState<number | null>(null);
  const [sortBy, setSortBy] = useState<SortBy>("date");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  async function fetchResults(
    nextPage = 1,
    params?: {
      q?: string;
      year_from?: number | null;
      year_to?: number | null;
      sort_by?: SortBy;
      sort_dir?: SortDir;
    }
  ) {
    const _q = (params?.q ?? q).trim();
    if (!_q) return;

    const yf = params?.year_from ?? yearFrom;
    const yt = params?.year_to ?? yearTo;
    const sb = params?.sort_by ?? sortBy;
    const sd = params?.sort_dir ?? sortDir;

    setLoading(true);
    setErr(null);

    try {
      const usp = new URLSearchParams({
        q: _q,
        page: String(nextPage),
        per_page: String(PER_PAGE),
        sort_by: sb,
        sort_dir: sd,
      });

      if (yf) usp.set("year_from", String(yf));
      if (yt) usp.set("year_to", String(yt));

      // IMPORTANT: relative URL so it works on freeip.uwo.ca
      const res = await fetch(`/api/search?${usp.toString()}`);

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: ApiResp = await res.json();

      setQ(_q);
      setYearFrom(yf ?? null);
      setYearTo(yt ?? null);
      setSortBy(sb);
      setSortDir(sd);

      setRows(data.results);
      setTotal(data.total);
      setPage(nextPage);
    } catch (e) {
      console.error("Search failed", e);
      setErr("Failed to fetch");
      setRows([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }

  const pages = Math.max(1, Math.ceil(total / PER_PAGE));
  const from = total ? (page - 1) * PER_PAGE + 1 : 0;
  const to = total ? Math.min(page * PER_PAGE, total) : 0;

  return (
    <div className="container">
      <h1 className="section-title">Find inactive U.S. patents</h1>
      <div className="section-sub">
        Search by title keyword. Results include patent number, title, and grant date.
      </div>

      <SearchForm
        defaultQuery={q}
        defaultYearFrom={yearFrom}
        defaultYearTo={yearTo}
        defaultSortBy={sortBy}
        defaultSortDir={sortDir}
        onSearch={(p) => fetchResults(1, p)}
      />

      {err && <div className="meta">{err}</div>}

      {!rows.length && !loading ? (
        <div className="meta">No results yet.</div>
      ) : null}

      {rows.length > 0 && (
        <>
          <div className="meta">
            Found <strong>{total.toLocaleString()}</strong> inactive patent
            {total === 1 ? "" : "s"}
            {q ? (
              <>
                {" "}
                for “<strong>{q}</strong>”
              </>
            ) : null}
            {yearFrom ? (
              <>
                {" "}
                • from <strong>{yearFrom}</strong>
              </>
            ) : null}
            {yearTo ? (
              <>
                {" "}
                • to <strong>{yearTo}</strong>
              </>
            ) : null}
            <> • sorted by{" "}
              <strong>{sortBy === "date" ? "grant date" : "title"}</strong> ({sortDir})
            </>
          </div>

          <div className="meta">
            Showing {from}–{to} of {total} results
          </div>

          <ResultsTable rows={rows} total={total} />

          <div className="pager">
            <button
              className="btn"
              onClick={() => fetchResults(Math.max(1, page - 1))}
              disabled={page <= 1 || loading}
            >
              Prev
            </button>
            <span className="meta">
              Page {page} / {pages}
            </span>
            <button
              className="btn"
              onClick={() => fetchResults(Math.min(pages, page + 1))}
              disabled={page >= pages || loading}
            >
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
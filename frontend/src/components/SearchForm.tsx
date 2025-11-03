"use client";
import { useEffect, useMemo, useState } from "react";

export type SortBy = "date" | "title";
export type SortDir = "asc" | "desc";

type Props = {
  onSearch: (params: {
    q: string;
    year_from?: number | null;
    year_to?: number | null;
    sort_by: SortBy;
    sort_dir: SortDir;
  }) => void;
  defaultQuery?: string;
  defaultYearFrom?: number | null;
  defaultYearTo?: number | null;
  defaultSortBy?: SortBy;
  defaultSortDir?: SortDir;
};

export default function SearchForm({
  onSearch,
  defaultQuery = "",
  defaultYearFrom = null,
  defaultYearTo = null,
  defaultSortBy = "date",
  defaultSortDir = "desc",
}: Props) {
  const [q, setQ] = useState(defaultQuery);
  const [yearFrom, setYearFrom] = useState<number | "">(defaultYearFrom ?? "");
  const [yearTo, setYearTo] = useState<number | "">(defaultYearTo ?? "");
  const [sortBy, setSortBy] = useState<SortBy>(defaultSortBy);
  const [sortDir, setSortDir] = useState<SortDir>(defaultSortDir);

  const years = useMemo(() => {
    const now = new Date().getFullYear();
    const arr: number[] = [];
    for (let y = now; y >= 1976; y--) arr.push(y);
    return arr;
  }, []);

  function submit() {
    onSearch({
      q,
      year_from: yearFrom === "" ? null : Number(yearFrom),
      year_to: yearTo === "" ? null : Number(yearTo),
      sort_by: sortBy,
      sort_dir: sortDir,
    });
  }

  // “Enter” submits
  function keyHandler(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") submit();
  }

  return (
    <div className="space-y-2">
      {/* search bar */}
      <div className="search-wrap">
        <div className="search-pill">
          <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" style={{ opacity: 0.7 }}>
            <path
              fill="currentColor"
              d="M21 20.3 16.7 16A7.5 7.5 0 1 0 16 16.7L20.3 21zM4.5 11a6.5 6.5 0 1 1 13 0a6.5 6.5 0 0 1-13 0Z"
            />
          </svg>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={keyHandler}
            placeholder="Search titles (e.g., sensor, polymer, valve)"
            aria-label="Search patents by title"
          />
        </div>
        <button className="search-btn" onClick={submit}>Search</button>
      </div>

      {/* filters + sort */}
      <div className="filters-row">
        <div className="filters-group">
          <label className="filters-label">Year from</label>
          <select
            value={yearFrom === "" ? "" : String(yearFrom)}
            onChange={(e) => setYearFrom(e.target.value === "" ? "" : Number(e.target.value))}
            className="filters-select"
          >
            <option value="">Any</option>
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

        <div className="filters-group">
          <label className="filters-label">Year to</label>
          <select
            value={yearTo === "" ? "" : String(yearTo)}
            onChange={(e) => setYearTo(e.target.value === "" ? "" : Number(e.target.value))}
            className="filters-select"
          >
            <option value="">Any</option>
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

        <div className="filters-group">
          <label className="filters-label">Sort by</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value as SortBy)} className="filters-select">
            <option value="date">Grant date</option>
            <option value="title">Title</option>
          </select>
        </div>

        <div className="filters-group">
          <label className="filters-label">Order</label>
          <select value={sortDir} onChange={(e) => setSortDir(e.target.value as SortDir)} className="filters-select">
            <option value="desc">Desc</option>
            <option value="asc">Asc</option>
          </select>
        </div>

        <div className="filters-spacer" />
        <button className="btn-outline" onClick={submit}>Apply</button>
      </div>
    </div>
  );
}
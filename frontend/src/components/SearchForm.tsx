"use client";
import { useState } from "react";

type Props = { onSearch: (q: string) => void; defaultQuery?: string };

export default function SearchForm({ onSearch, defaultQuery = "" }: Props) {
  const [q, setQ] = useState(defaultQuery);

  return (
    <div className="mb-6">
      <label htmlFor="q" className="sr-only">Search patents</label>
      <div className="flex items-center gap-2 rounded-pill bg-uwo.lilac/50 p-1">
        <div className="flex w-full items-center rounded-pill bg-white pl-4 pr-1 shadow-card ring-1 ring-gray-200">
          <svg width="18" height="18" viewBox="0 0 24 24" className="opacity-60">
            <path fill="currentColor" d="M15.5 14h-.79l-.28-.27a6.471 6.471 0 0 0 1.57-4.23A6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79L20 21.5 21.5 20zM4 9.5C4 6.46 6.46 4 9.5 4S15 6.46 15 9.5 12.54 15 9.5 15 4 12.54 4 9.5z"/>
          </svg>
          <input
            id="q"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSearch(q)}
            placeholder="Search titles (e.g., polymer, injector, valve)"
            className="w-full bg-transparent px-3 py-3 outline-none placeholder:text-gray-400"
          />
          <button
            onClick={() => onSearch(q)}
            className="rounded-pill bg-uwo-purple px-5 py-2.5 text-white transition hover:bg-uwo-purple/90 active:scale-[0.99]"
            aria-label="Search"
          >
            Search
          </button>
        </div>
      </div>
      <p className="mt-2 text-xs text-gray-500">Tip: results show currently inactive (lapsed) patents.</p>
    </div>
  );
}
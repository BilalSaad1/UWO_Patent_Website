"use client";
import { useState } from "react";

export default function SearchForm({ onSearch, disabled }: { onSearch: (q: string)=>void; disabled?: boolean; }) {
  const [q, setQ] = useState("");
  return (
    <div className="rounded-xl border p-4 shadow-sm bg-white">
      <label className="block text-sm font-medium mb-2">searh by keywords</label>
      <div className="flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && q.trim().length >= 2 && onSearch(q.trim())}
          placeholder="fuel injector"
          className="flex-1 rounded-lg border px-3 py-2 focus:outline-none focus:ring-2 focus:ring-western-purple"
        />
        <button
          onClick={() => onSearch(q.trim())}
          disabled={disabled || q.trim().length < 2}
          className="rounded-lg px-4 py-2 bg-western-purple text-white disabled:opacity-50"
        >
          Search
        </button>
      </div>
    </div>
  );
}
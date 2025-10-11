"use client";
import { useState } from "react";
import Header from "@/components/Header";
import SearchForm from "@/components/SearchForm";
import ResultsTable from "@/components/ResultsTable";

type PatentHit = { patent: string; title: string; grant_date?: string | null; };
type SearchResponse = { q: string; page: number; per_page: number; total: number; results: PatentHit[]; };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export default function Page() {
  const [page, setPage] = useState(1);
  const [perPage] = useState(20);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");

  async function fetchSearch(query: string, p = 1) {
    setLoading(true); setError(null); setQ(query);
    try {
      const url = new URL(`${API_BASE}/search`);
      url.searchParams.set("q", query);
      url.searchParams.set("page", String(p));
      url.searchParams.set("per_page", String(perPage));
      const res = await fetch(url.toString(), { cache: "no-store" });
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const json = (await res.json()) as SearchResponse;
      setData(json); setPage(p);
    } catch (e:any) { setError(e.message || "Search failed"); }
    finally { setLoading(false); }
  }

  return (
    <main className="min-h-screen bg-white">
      <Header />
      <section className="mx-auto max-w-6xl px-4 py-8">
        <SearchForm onSearch={(query)=>fetchSearch(query,1)} disabled={loading} />
        {error && <div className="mt-6 rounded-lg border border-red-300 bg-red-50 p-3 text-red-800">{error}</div>}
        {data ? (
          <>
            <div className="mt-4 text-sm text-gray-700">
              {data.total} result{data.total===1?"":"s"} for <span className="font-medium">“{data.q}”</span>
            </div>
            <ResultsTable results={data.results} total={data.total} page={page} perPage={perPage} onPage={(p)=>fetchSearch(q,p)} />
          </>
        ) : (
          <div className="mt-6 text-sm text-gray-600">searching for <span className="font-medium">fuel injector</span></div>
        )}
      </section>
      <footer className="mt-12 border-t">
        <div className="mx-auto max-w-6xl px-4 py-6 text-xs text-gray-600">

        </div>
      </footer>
    </main>
  );
}
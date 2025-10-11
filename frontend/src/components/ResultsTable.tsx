"use client";

type PatentHit = { patent: string; title: string; grant_date?: string | null; };
export default function ResultsTable({
  results, total, page, perPage, onPage,
}: { results: PatentHit[]; total: number; page: number; perPage: number; onPage: (p:number)=>void; }) {
  const start = (page - 1) * perPage + 1, end = Math.min(page * perPage, total);
  const pages = Math.max(1, Math.ceil(total / perPage));
  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-3 text-sm text-gray-700">
        <p>Showing {total ? start : 0}–{end} of {total} results</p>
        <div className="flex items-center gap-2">
          <button className="rounded border px-3 py-1 disabled:opacity-50" disabled={page<=1} onClick={()=>onPage(page-1)}>Prev</button>
          <span>Page {page} / {pages}</span>
          <button className="rounded border px-3 py-1 disabled:opacity-50" disabled={page>=pages} onClick={()=>onPage(page+1)}>Next</button>
        </div>
      </div>
      <div className="overflow-x-auto rounded-xl border">
        <table className="min-w-full text-sm">
          <thead><tr className="bg-gray-50 text-left">
            <th className="px-4 py-2 font-medium">Patent</th>
            <th className="px-4 py-2 font-medium">Title</th>
            <th className="px-4 py-2 font-medium">Grant Date</th>
            <th className="px-4 py-2 font-medium"></th>
          </tr></thead>
          <tbody>
            {results.map(r=>(
              <tr key={r.patent} className="border-t">
                <td className="px-4 py-2 font-mono">{r.patent}</td>
                <td className="px-4 py-2">{r.title}</td>
                <td className="px-4 py-2">{r.grant_date ?? "—"}</td>
                <td className="px-4 py-2">
                  <a href={`https://patents.google.com/patent/${encodeURIComponent(r.patent)}`} target="_blank" rel="noreferrer" className="text-western-purple hover:underline">View →</a>
                </td>
              </tr>
            ))}
            {results.length===0 && <tr><td className="px-4 py-6 text-center text-gray-500" colSpan={4}>No results. Try different keywords.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
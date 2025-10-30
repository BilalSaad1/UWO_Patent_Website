type Row = { patent: string; title: string; grant_date?: string | null };

export default function ResultsTable({ rows, total }: { rows: Row[]; total: number }) {
  if (!rows?.length) {
    return (
      <div className="rounded-xl border border-dashed border-gray-300 bg-white/60 p-10 text-center text-gray-600">
        No results yet. Try a broader keyword (e.g., <span className="font-medium">sensor</span>).
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="text-sm text-gray-500">Found {total.toLocaleString()} result{total === 1 ? "" : "s"}</div>

      <ul className="grid gap-3">
        {rows.map((r) => (
          <li key={r.patent} className="rounded-xl bg-white p-4 shadow-card ring-1 ring-gray-200 hover:shadow-lg transition">
            <div className="flex items-start justify-between gap-3">
              <div>
                <a
                  href={`https://patents.google.com/patent/${encodeURIComponent(r.patent)}`}
                  target="_blank" rel="noreferrer"
                  className="text-uwo-purple hover:underline font-medium"
                >
                  {r.patent}
                </a>
                {r.grant_date && (
                  <span className="ml-2 rounded-full bg-uwo.lilac px-2 py-0.5 text-xs text-uwo-purple">
                    {new Date(r.grant_date).toLocaleDateString()}
                  </span>
                )}
                <div className="mt-1 text-[15px] text-gray-800">{r.title}</div>
              </div>

              <a
                href={`https://patents.google.com/patent/${encodeURIComponent(r.patent)}`}
                target="_blank" rel="noreferrer"
                className="rounded-lg border px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
              >
                View
              </a>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
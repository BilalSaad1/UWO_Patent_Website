from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Dict, Tuple
from collections import defaultdict
from .maintenance import MaintEvent
from .grants import GrantDoc

EXPIRE_CODES = {"EXP"}              # expired for non-payment
REINSTATE_HINTS = {"EXPX", "PMT"}   # reinstated/paid

@dataclass
class InactiveRow:
    patent: str
    title: str
    grant_date: str | None

def reduce_inactive(events: Iterable[MaintEvent], biblio: Dict[str, GrantDoc]) -> Tuple[list[InactiveRow], int]:
    by_pat = defaultdict(list)
    for ev in events:
        by_pat[ev.patent].append(ev)

    result: list[InactiveRow] = []
    for pn, evs in by_pat.items():
        evs.sort(key=lambda e: e.date)
        last = evs[-1]
        last_code = last.code.strip(".").upper()
        any_reinstate = any(c.code.strip(".").upper() in REINSTATE_HINTS for c in evs if c.date >= last.date)
        if last_code in EXPIRE_CODES and not any_reinstate:
            meta = biblio.get(pn)
            title = meta.title if meta else "(title unavailable)"
            gd = meta.grant_date if meta else None
            result.append(InactiveRow(patent=pn, title=title, grant_date=gd))
    return result, len(by_pat)

from zipfile import ZipFile
from lxml import etree

G = r"C:\Users\bilal\Documents\UWO_Patent_Website\data\downloads\ptblxml_20251014.zip"

with ZipFile(G) as z:
    names = sorted(z.namelist(), key=lambda n: z.getinfo(n).file_size, reverse=True)
    print("GRANTS zip entries (top 3 by size):", names[:3])
    xmls = [n for n in names if n.lower().endswith((".xml",".sgm"))]
    print("XML chosen:", xmls[0] if xmls else None)
    if not xmls:
        raise SystemExit("No XML inside grants zip")

    with z.open(xmls[0]) as fh:
        count = 0
        first = None
        it = etree.iterparse(fh, events=("end",), recover=True, huge_tree=True)
        for _, elem in it:
            tag = elem.tag.split("}")[-1] if isinstance(elem.tag, str) else ""
            if tag != "us-patent-grant":
                elem.clear()
                continue
            count += 1
            if first is None:
                # quick helper to snag a couple fields without worrying about namespaces
                def text_first(e, names):
                    # names is a list like ["publication-reference","document-id","doc-number"]
                    cur = e
                    for name in names:
                        found = None
                        for c in cur.iter():
                            t = c.tag.split("}")[-1] if isinstance(c.tag, str) else ""
                            if t == name:
                                found = c
                                break
                        if not found:
                            return ""
                        cur = found
                    return (cur.text or "").strip()
                pn = text_first(elem, ["publication-reference","document-id","doc-number"])
                title = text_first(elem, ["invention-title"])
                first = (pn, title)
            elem.clear()

        print("us-patent-grant elements counted:", count)
        print("first record:", first)

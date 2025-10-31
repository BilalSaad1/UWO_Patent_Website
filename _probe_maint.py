from zipfile import ZipFile

M = r"C:\Users\bilal\Documents\UWO_Patent_Website\data\downloads\ptmnfee2_20251014.zip"

with ZipFile(M) as z:
    names = sorted([n for n in z.namelist() if n.lower().endswith((".txt",".csv"))],
                   key=lambda n: z.getinfo(n).file_size, reverse=True)
    print("MAINT text chosen:", names[0] if names else None)
    if not names:
        raise SystemExit("No TXT/CSV inside maintenance zip")

    with z.open(names[0]) as fh:
        head = fh.readline().decode("utf-8","ignore").rstrip("\r\n")
        first = fh.readline().decode("utf-8","ignore").rstrip("\r\n")
        print("Header line:", head[:400])
        print("First data line:", first[:400])

"""
Lake Erie surface temperature from NOAA GLERL GLSEA (lake-wide daily averages).

Downloads one file per year from the GLERL ERDDAP server, averages Lake Erie's
temperature over the bloom season, and writes:

    data/processed/series/lake_temperature.csv   (columns: year, lake)

GLSEA's daily average file gives one number for the whole lake, so there is no
west/east split for this variable; the web app handles that.

Run (needs internet):
    python data/scripts/get_glsea_temperature.py
    python data/scripts/get_glsea_temperature.py --start-month 7 --end-month 10   # bloom season, NOAA: July to October
    python data/scripts/get_glsea_temperature.py --allow-expired-cert   # if NOAA's certificate has expired

Source and file format: NOAA CoastWatch Great Lakes tutorial,
https://coastwatch-training.github.io/tutorials/gl-timeseries-surface-temp/python/gl-timeseries-surface-temp.html
"""

import argparse
import io
import urllib.error
import urllib.parse
import urllib.request
import ssl
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

BASE = "https://apps.glerl.noaa.gov/erddap/files/glsea_avgtemps_3/"
COLS = ["YEAR", "JD", "S", "M", "H", "E", "O", "St"]  # E = Lake Erie
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed" / "series" / "lake_temperature.csv"
_warned = False


ALLOW_EXPIRED = False  # set by --allow-expired-cert
NOAA_HOST = "apps.glerl.noaa.gov"


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "lake-effect-space-apps/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        expired = "CERTIFICATE_VERIFY_FAILED" in str(e) and "expired" in str(e)
        if not (expired and ALLOW_EXPIRED and urllib.parse.urlparse(url).hostname == NOAA_HOST):
            if expired and not ALLOW_EXPIRED:
                raise SystemExit(
                    "NOAA's HTTPS certificate has expired, so the download was refused.\n"
                    "This is public, read-only data. To accept the expired certificate for "
                    f"{NOAA_HOST} only, run again with --allow-expired-cert"
                )
            raise
        global _warned
        if not _warned:
            print(f"  note: accepting the expired certificate for {NOAA_HOST} only (--allow-expired-cert)")
            _warned = True
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
            return r.read().decode("utf-8", errors="replace")


def read_year(year: int) -> pd.DataFrame:
    text = _fetch(f"{BASE}{year}/glsea-temps{year}_1024_3.dat")
    return pd.read_csv(io.StringIO(text), skiprows=9, sep=r"\s+", header=None, names=COLS, dtype=np.float64)


def season_mean(df: pd.DataFrame, year: int, start_month: int, end_month: int) -> float:
    first = date(year, start_month, 1)
    last = date(year + (end_month == 12), (end_month % 12) + 1, 1) - timedelta(days=1)
    jd0, jd1 = first.timetuple().tm_yday, last.timetuple().tm_yday
    rows = df[(df["YEAR"] == year) & (df["JD"] >= jd0) & (df["JD"] <= jd1)]
    return float(rows["E"].mean()) if len(rows) else float("nan")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--first-year", type=int, default=2007)
    p.add_argument("--last-year", type=int, default=date.today().year - 1)
    p.add_argument("--start-month", type=int, default=7, help="bloom season start: July (NOAA HAB FAQ)")
    p.add_argument("--end-month", type=int, default=10, help="bloom season end: October (NOAA HAB FAQ)")
    p.add_argument("--allow-expired-cert", action="store_true",
                   help=f"accept an expired HTTPS certificate from {NOAA_HOST} only")
    a = p.parse_args()
    global ALLOW_EXPIRED
    ALLOW_EXPIRED = a.allow_expired_cert

    rows = []
    for y in range(a.first_year, a.last_year + 1):
        try:
            v = season_mean(read_year(y), y, a.start_month, a.end_month)
            print(f"{y}: {v:.2f} °C")
        except SystemExit:
            raise
        except Exception as e:  # missing year or network hiccup
            v = float("nan")
            print(f"{y}: skipped ({e.__class__.__name__}: {str(e)[:120]})")
        rows.append({"year": y, "lake": round(v, 3) if v == v else None})

    if all(r["lake"] is None for r in rows):
        raise SystemExit("No years downloaded, so nothing was written. Check the errors above.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"wrote {OUT.relative_to(ROOT)}  (months {a.start_month} to {a.end_month})")


if __name__ == "__main__":
    main()

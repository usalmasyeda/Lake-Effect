# AI-assisted: written by Mehak with help from ChatGPT (an AI assistant) and reviewed by team Lake Effect.

"""Download only new NASA MODIS-Aqua chlorophyll observations."""

import calendar
import os
import subprocess
import tempfile
from datetime import date
from pathlib import Path

import xarray as xr

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
MASTER = ROOT / "data" / "processed" / "chlorophyll_yearly.nc"

BASE_URL = (
    "https://obdaac-tea.earthdatacloud.nasa.gov/"
    "ob-cumulus-prod-public"
)

MONTHS = (7, 8, 9, 10)


def main():
    username = os.environ.get("NASA_EARTHDATA_USERNAME")
    password = os.environ.get("NASA_EARTHDATA_PASSWORD")

    if not username or not password:
        raise RuntimeError("NASA Earthdata credentials are missing.")

    if not MASTER.exists():
        raise FileNotFoundError("Historical NetCDF is missing.")

    RAW.mkdir(parents=True, exist_ok=True)

    with xr.open_dataset(MASTER) as ds:
        last_year = int(ds.year.max().item())

    current_year = date.today().year

    print(f"Historical data ends in {last_year}")
    print(f"Checking new seasons through {current_year}")

    # Keep credentials in a temporary file, never in Git.
    with tempfile.TemporaryDirectory() as temp_dir:
        netrc = Path(temp_dir) / "netrc"
        cookies = Path(temp_dir) / "cookies"

        # Reject characters that could corrupt the netrc format.
        if any(c in username + password for c in "\r\n"):
            raise ValueError("Invalid newline in credentials.")

        netrc.write_text(
            f"machine urs.earthdata.nasa.gov "
            f"login {username} password {password}\n"
        )
        netrc.chmod(0o600)
        cookies.touch()
        cookies.chmod(0o600)

        
        for year in range(last_year + 1, current_year + 1):
            for month in MONTHS:
                today = date.today()

                # Only check months that have fully ended.
                if (year, month) >= (today.year, today.month):
                    continue

                last_day = calendar.monthrange(year, month)[1]

                filename = (
                    f"AQUA_MODIS.{year}{month:02d}01_"
                    f"{year}{month:02d}{last_day:02d}"
                    ".L3m.MO.CHL.chlor_a.4km.nc"
                )


                destination = RAW / filename
                partial = RAW / (filename + ".part")

                if destination.exists() and destination.stat().st_size > 0:
                    print(f"SKIP: {filename}")
                    continue

                print(f"Checking: {filename}")

                partial.unlink(missing_ok=True)

                result = subprocess.run(
                    [
                        "curl",
                        "--location",
                        "--silent",
                        "--show-error",
                        "--retry", "2",
                        "--connect-timeout", "30",
                        "--max-time", "300",
                        "--netrc-file", str(netrc),
                        "--cookie", str(cookies),
                        "--cookie-jar", str(cookies),
                        "--output", str(partial),
                        "--write-out", "%{http_code}",
                        f"{BASE_URL}/{filename}",
                    ],
                    capture_output=True,
                    text=True,
                )

                status = result.stdout.strip()

                if result.returncode != 0 or status != "200":
                    partial.unlink(missing_ok=True)

                if result.returncode != 0:
                    raise RuntimeError(
                        f"NASA request failed for {filename} "
                        f"(curl exit code {result.returncode})."
                    )

                    if status == "404":
                        print(f"Not yet available: {filename}")
                        continue

                    if status in ("401", "403"):
                        raise RuntimeError(
                            "NASA authentication or access failed. "
                            "Check your Earthdata credentials and permissions."
                        )

                    raise RuntimeError(
                        f"NASA download failed for {filename}: "
                        f"HTTP {status}, curl exit {result.returncode}"
                    )

                # Confirm that the download is a valid chlorophyll dataset.
                try:
                    with xr.open_dataset(partial) as ds:
                        if "chlor_a" not in ds:
                            raise ValueError("Missing chlor_a variable.")
                except Exception:
                    partial.unlink(missing_ok=True)
                    raise

                partial.replace(destination)
                print(f"SAVED: {filename}")

    print("NASA incremental download check completed.")


if __name__ == "__main__":
    main()


#!/bin/bash
set -euo pipefail

# Run this script from anywhere inside the Lake-Effect project.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW_DIR="$SCRIPT_DIR/../raw"
mkdir -p "$RAW_DIR"

BASE_URL="https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public"

# Temporary credential and cookie files
NETRC_FILE=$(mktemp)
COOKIE_FILE=$(mktemp)
chmod 600 "$NETRC_FILE" "$COOKIE_FILE"

cleanup() {
    rm -f "$NETRC_FILE" "$COOKIE_FILE"
}
trap cleanup EXIT

echo "NASA Earthdata Login"
read -r -p "Username: " USERNAME
read -r -s -p "Password: " PASSWORD
echo

# Store credentials temporarily, not in the project.
printf 'machine urs.earthdata.nasa.gov login %s password %s\n' \
    "$USERNAME" "$PASSWORD" > "$NETRC_FILE"
unset PASSWORD

# Only the four missing months

FILES=(
    "AQUA_MODIS.20230601_20230630.L3m.MO.CHL.chlor_a.4km.nc"
    "AQUA_MODIS.20230701_20230731.L3m.MO.CHL.chlor_a.4km.nc"
    "AQUA_MODIS.20230801_20230831.L3m.MO.CHL.chlor_a.4km.nc"
    "AQUA_MODIS.20230901_20230930.L3m.MO.CHL.chlor_a.4km.nc"
    "AQUA_MODIS.20231001_20231031.L3m.MO.CHL.chlor_a.4km.nc"
)


for FILE in "${FILES[@]}"; do
    DEST="$RAW_DIR/$FILE"

    if [ -s "$DEST" ]; then
        echo "Already exists: $FILE"
        continue
    fi

    echo "Downloading: $FILE"

    curl --fail --location \
        --retry 3 \
        --netrc-file "$NETRC_FILE" \
        --cookie "$COOKIE_FILE" \
        --cookie-jar "$COOKIE_FILE" \
        --output "$DEST.part" \
        "$BASE_URL/$FILE"

    mv "$DEST.part" "$DEST"
    echo "Saved: $FILE"
done

echo "All four monthly files downloaded!"

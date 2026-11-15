
#!/bin/bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW_DIR="$SCRIPT_DIR/../raw"
mkdir -p "$RAW_DIR"

BASE_URL="https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public"

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

printf 'machine urs.earthdata.nasa.gov login %s password %s\n' \
    "$USERNAME" "$PASSWORD" > "$NETRC_FILE"
unset PASSWORD

SUCCESS=0
SKIPPED=0
FAILED=0

for YEAR in $(seq 2002 2026); do
    for MONTH in 06 07 08 09 10; do

        # Calculate the last day of each month
        case "$MONTH" in
            06|09) LAST_DAY=30 ;;
            *) LAST_DAY=31 ;;
        esac

        FILE="AQUA_MODIS.${YEAR}${MONTH}01_${YEAR}${MONTH}${LAST_DAY}.L3m.MO.CHL.chlor_a.4km.nc"
        DEST="$RAW_DIR/$FILE"

        if [ -s "$DEST" ]; then
            echo "SKIP: $FILE"
            SKIPPED=$((SKIPPED + 1))
            continue
        fi

        echo "Downloading: $FILE"

        if curl --fail --location --silent --show-error \
            --retry 2 \
            --connect-timeout 30 \
    --max-time 300 \
            --netrc-file "$NETRC_FILE" \
            --cookie "$COOKIE_FILE" \
            --cookie-jar "$COOKIE_FILE" \
            --output "$DEST.part" \
            "$BASE_URL/$FILE"; then

            mv "$DEST.part" "$DEST"
            echo "SAVED: $FILE"
            SUCCESS=$((SUCCESS + 1))
        else
            rm -f "$DEST.part"
            echo "UNAVAILABLE OR FAILED: $FILE"
            FAILED=$((FAILED + 1))
        fi
    done
done

echo
echo "Download summary:"
echo "New downloads: $SUCCESS"
echo "Already present: $SKIPPED"
echo "Unavailable or failed: $FAILED"

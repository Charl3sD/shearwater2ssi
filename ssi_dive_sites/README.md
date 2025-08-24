# SSI Dive Sites Directory

This directory contains JSON files with SSI dive site information for different regions.

## File Format

Each JSON file should:
- Be named after the region (e.g., `bonaire.json`, `curacao.json`, `red_sea.json`)
- Contain SSI dive site data in the format returned by the SSI API
- Include site IDs, names, coordinates, and other metadata

## Obtaining Dive Site Data

### Method 1: SSI Website with Developer Tools (Recommended)

1. Visit https://www.divessi.com/en/locator/divesites
2. Open your browser's Developer Tools (F12 or right-click → Inspect)
3. Go to the "Network" tab
4. On the website, navigate/zoom to your diving region on the map
5. Look for requests to `locationServices.php` in the Network tab
6. Click on a `locationServices.php` request
7. Go to the "Response" tab to see the JSON data
8. Copy the entire JSON response
9. Save it as a `.json` file in this directory (e.g., `bonaire.json`)

**Tips:**
- Filter the Network tab by "XHR" or "Fetch" to find API calls easier
- The response will contain all dive sites visible in the current map view
- Zoom out to get more sites, zoom in for specific areas
- You may need to clear the network log and move the map to trigger new requests

### Method 2: Direct API Request
Make a POST request to `https://www.divessi.com/api/locationServices.php` with form data:

```
------WebKitFormBoundary
Content-Disposition: form-data; name="request"

{"type":"BOUNDS_CHANGED","filter":{"targets":["DiveSites"],"geoBounds":{"south":11.87,"west":-68.54,"north":12.50,"east":-67.85},"viewportCenter":{"lat":12.18,"lng":-68.19}}}
------WebKitFormBoundary--
```

Adjust the coordinates in `geoBounds` to match your diving region.

## File Naming

- Use lowercase
- Replace spaces with underscores
- Examples:
  - `bonaire.json`
  - `red_sea.json`
  - `raja_ampat.json`
  - `great_barrier_reef.json`

## Usage in Application

1. Place region JSON files in this directory
2. The application will automatically detect them
3. Select regions from the dropdown in the UI
4. Dive sites for that region will load automatically

## Sample Structure

```json
{
  "stats": {"total": 94},
  "result": {
    "type": "collection",
    "elements": [
      {
        "data": {
          "properties": {
            "id": "621168",
            "name": "Bonaire",
            "lat": "12.1607",
            "lng": "-68.2400"
          }
        }
      }
    ]
  }
}
```

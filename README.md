# Shearwater to SSI QR Code Generator

A Python tool that extracts dive information from Shearwater database files and generates QR codes compatible with the SSI (Scuba Schools International) mobile app.

## Features

- Import dive data from Shearwater Cloud database exports (.db files)
- Interactive GUI for selecting specific dives
- Assign SSI dive sites to each dive (sorted alphabetically for easy selection)
- Configure entry type (Shore/Boat) for each dive
- Generate QR codes that can be scanned directly in the SSI app
- Display generated QR codes directly in the application
- Load and view validation QR codes from `ssi_validations_qr_codes` folder
- Navigate through multiple QR codes with Previous/Next buttons
- Batch processing for multiple dives

## Requirements

- Python 3.6+
- Required packages:
  ```bash
  pip install qrcode pillow
  ```

## Setup

1. Clone or download this repository
2. Install the required Python packages
3. Obtain the `divesites.json` file (see below)

## Getting Dive Site Data

The SSI dive sites data can be obtained in two ways:

### Option 1: Direct Download
Visit https://www.divessi.com/en/locator/divesites and export the dive sites for your region.

### Option 2: API Request
Make a POST request to `https://www.divessi.com/api/locationServices.php` with the following form data:

```
------WebKitFormBoundaryXPrNwbBxLUX96frW
Content-Disposition: form-data; name="request"

{"type":"BOUNDS_CHANGED","filter":{"targets":["DiveSites"],"geoBounds":{"south":11.876243280094853,"west":-68.54084456467353,"north":12.502437021293536,"east":-67.85007918381416},"viewportCenter":{"lat":12.189524945643287,"lng":-68.19546187424385}}}
------WebKitFormBoundaryXPrNwbBxLUX96frW--
```

Adjust the coordinates in `geoBounds` and `viewportCenter` to match your diving region.

## Usage

1. **Export your Shearwater dive data**:
   - Open the Shearwater Cloud app
   - Export your dive log as a `.db` file

2. **Run the application**:
   ```bash
   python shearwater2ssi.py
   ```

3. **Configure your dives**:
   - Click "Select Shearwater DB File" and choose your exported `.db` file
   - Enter your SSI user information (name and user ID)
   - Select the dives you want to convert
   - For each selected dive, choose the appropriate SSI dive site from the dropdown
   - Set the entry type (Shore or Boat) for each dive
   - Click "Apply to Selected" to update multiple dives at once

4. **Generate QR codes**:
   - Click "Generate QR Codes"
   - QR code images will be saved in a `ssi_dives_qr_codes` folder
   - Each QR code is named with the dive's date and time
   - Generated QR codes are automatically displayed in the preview pane

5. **View QR codes in the application**:
   - Generated dive QR codes are automatically displayed after generation
   - Use the radio buttons to switch between "Dive QR Codes" and "Validation QR Codes"
   - Click "Load Validations" to load QR codes from the `ssi_validations_qr_codes` folder
   - Use Previous/Next buttons to navigate through multiple QR codes

6. **Import to SSI app**:
   - Open the SSI app on your mobile device
   - Navigate to the QR code import section
   - Scan the generated QR codes directly from the screen or from saved files

## QR Code Format

The generated QR codes contain the following SSI-compatible data:
- Dive type
- Dive time (duration in minutes)
- Date and time
- Maximum depth
- Dive site ID
- Environmental variables (weather, entry type, water body, etc.)
- User information

## Entry Types

- **Shore (21)**: Dive entry from the shore/beach
- **Boat (22)**: Dive entry from a boat

## Validation QR Codes

The SSI app uses validation QR codes to verify dives at training centers. These QR codes contain the training center information.

### QR Code Format

The validation QR payload follows this structure:
```
center;<Center ID>;name:<Center Name>, <Location>
```

Example:
```
center;750405;name:Infinity Divers, Roatan
```

### Finding Training Center IDs

Visit https://www.divessi.com/en/locator/trainingcenters to search for training centers and their IDs.

### Generating Validation QR Codes with qrencode

You can generate validation QR codes using the `qrencode` command-line tool:

#### Installation
```bash
# Ubuntu/Debian
sudo apt-get install qrencode

# macOS
brew install qrencode

# Arch/Manjaro
sudo pacman -S qrencode
```

#### Generate a validation QR code
```bash
# Generate PNG file
qrencode -o validation-CenterName.png "center;750405;name:Infinity Divers, Roatan"

# Generate with specific size
qrencode -s 10 -o validation-CenterName.png "center;750405;name:Infinity Divers, Roatan"

# Display in terminal (for testing)
qrencode -t UTF8 "center;750405;name:Infinity Divers, Roatan"
```

Place generated validation QR codes in the `ssi_validations_qr_codes` folder to view them in the application.

## Troubleshooting

- **No dive sites available**: Ensure `divesites.json` is in the same directory as the script
- **QR codes not scanning**: Verify your SSI user ID is correct
- **Missing dive data**: Some Shearwater exports may have incomplete data; the tool will use default values where necessary

## License

This tool is provided as-is for personal use to facilitate dive log management between Shearwater and SSI platforms.
# Shearwater to SSI QR Code Generator

A Python tool that extracts dive information from Shearwater database files and generates QR codes compatible with the SSI mobile app.

⚠️ **IMPORTANT: Please read the [DISCLAIMER](DISCLAIMER.md) before using this software.**

This project is for **DEMONSTRATION AND EDUCATIONAL PURPOSES ONLY**. It is not affiliated with Shearwater Research Inc., SSI, or any diving organization.

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
3. Add dive site JSON files to `ssi_dive_sites/` directory (see directory README for details)

## Usage

1. **Export your Shearwater dive data**:
   - Open the Shearwater Cloud app
   - Export your dive log as a `.db` file
   - Place the file in `shearwater_databases/` folder

2. **Run the application**:
   ```bash
   python shearwater2ssi.py
   ```

3. **Configure your dives**:
   - The latest database will be auto-loaded from `shearwater_databases/`
   - Fill in buddy information (name and SSI ID) for the QR codes
   - Select dives from the list
   - Choose region and dive site from the dropdowns
   - Set entry type (Shore/Boat)
   - Click "Apply to Selected" to update multiple dives at once

4. **Generate and use QR codes**:
   - Click "Generate QR Codes"
   - QR codes are saved to `ssi_dives_qr_codes/` and displayed in the preview
   - Open the SSI app on your mobile device
   - Scan the QR codes to import dives

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

Validation QR codes contain training center information.

### QR Code Format

The validation QR payload follows this structure:
```
center;<Center ID>;name:<Center Name>, <Location>
```

Example:
```
center;123456;name:Example Dive Center, Sample Location
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
qrencode -o validation-CenterName.png "center;123456;name:Example Dive Center, Sample Location"

# Generate with specific size
qrencode -s 10 -o validation-CenterName.png "center;123456;name:Example Dive Center, Sample Location"

# Display in terminal (for testing)
qrencode -t UTF8 "center;123456;name:Example Dive Center, Sample Location"
```

Place generated validation QR codes in the `ssi_validations_qr_codes` folder to view them in the application.

## Directory Structure

- `shearwater_databases/` - Place your Shearwater .db exports here
- `ssi_dive_sites/` - JSON files with dive sites for different regions
- `ssi_dives_qr_codes/` - Generated QR codes for dives (auto-created)
- `ssi_validations_qr_codes/` - Training center validation QR codes

Each directory contains its own README with detailed instructions.

## Troubleshooting

- **No dive sites available**: Ensure you have region JSON files in `ssi_dive_sites/`
- **No databases found**: Place .db files in `shearwater_databases/`
- **QR codes not scanning**: Verify buddy's SSI ID is correct
- **Missing dive data**: Some Shearwater exports may have incomplete data; the tool will use default values where necessary

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is provided for demonstration and educational purposes only. Please read the full [DISCLAIMER](DISCLAIMER.md) before use.

**USE AT YOUR OWN RISK** - Always verify converted data and maintain proper dive logs according to your certification agency's requirements.
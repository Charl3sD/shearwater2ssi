# SSI Validation QR Codes Directory

This directory contains validation QR codes for training centers.

## QR Code Format

Each validation QR code contains:
```
center;<Center ID>;name:<Center Name>, <Location>
```

Example:
```
center;750405;name:Infinity Divers, Roatan
```

## Creating Validation QR Codes

### Method 1: Using qrencode (Recommended)

```bash
# Install qrencode
sudo apt-get install qrencode  # Ubuntu/Debian
brew install qrencode           # macOS
sudo pacman -S qrencode        # Arch/Manjaro

# Generate QR code
qrencode -s 10 -o validation-RajaAmpat.png "center;750405;name:Infinity Divers, Roatan"
```

### Method 2: Online QR Generator

1. Visit any QR code generator website
2. Enter the validation string (e.g., `center;750405;name:Infinity Divers, Roatan`)
3. Download as PNG
4. Save to this directory

## Finding Training Center IDs

Visit https://www.divessi.com/en/locator/trainingcenters to search for:
- Training center IDs
- Exact center names
- Location information

## File Naming Convention

Recommended format: `validation-<CenterName>.png`
- Example: `validation-InfinityDivers.png`
- Example: `validation-RajaAmpat.png`

## Viewing in Application

1. Place validation QR codes in this directory
2. In the application, click "Validation QR Codes" radio button
3. Select the validation QR from the dropdown
4. Use Previous/Next buttons to navigate between multiple validations

## Privacy

Files in this directory are excluded from version control via `.gitignore`.
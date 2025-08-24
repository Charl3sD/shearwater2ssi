# SSI Dive QR Codes Directory

This directory contains generated QR codes for importing dives into the SSI app.

## Generated Files

QR codes are automatically generated here when you:
1. Select dives from your Shearwater database
2. Configure dive sites and entry types
3. Click "Generate QR Codes"

## File Naming

Files are named using the dive date and time:
- Format: `dive_YYYYMMDD_HHMMSS.png`
- Example: `dive_20250305_103845.png`

## Using the QR Codes

1. Open the SSI app on your mobile device
2. Navigate to the dive log import section
3. Scan the QR code with your phone's camera
4. The dive will be imported with all details

## Management

- **Overwrite Mode**: When enabled (default), generating new QR codes clears this directory first
- **Append Mode**: When disabled, new QR codes are added to existing ones
- **Clean**: Use the "Clean Dive QRs" button to delete all QR codes

## Privacy

Files in this directory are excluded from version control via `.gitignore` to protect your personal dive data.
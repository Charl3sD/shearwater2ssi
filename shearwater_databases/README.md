# Shearwater Databases Directory

This directory contains Shearwater Cloud database exports (`.db` files).

## How to Export Your Shearwater Database

1. Open the Shearwater Cloud app
2. Go to Settings or Export options
3. Export your dive log as a `.db` file
4. Place the exported file in this directory

## File Format

The application expects SQLite database files with the `.db` extension containing:
- `dive_details` table with dive information
- `dive_logs` and `dive_log_records` tables with detailed dive data

## Notes

- The application will automatically scan this directory for `.db` files
- The most recent database (by modification time) will be loaded automatically
- You can have multiple database files and switch between them using the dropdown

## Privacy

Files in this directory are excluded from version control via `.gitignore` to protect your personal dive data.
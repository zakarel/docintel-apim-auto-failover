# Architecture Diagrams

This folder contains architecture diagrams for the APIM Document Intelligence solution.

## Files

- `APIM-DocIntel-Architecture.drawio` - Main architecture diagram (editable source)
- `APIM-DocIntel-Architecture.png` - Main architecture diagram (exported PNG)
- `POST.png` - POST /analyze request flow diagram
- `GET.png` - GET /analyzeResults polling flow diagram
- `export-diagrams.py` - Automated export utility script

## Quick Export

Use the automated export script:

```bash
python3 diagrams/export-diagrams.py
```

The script will:
- Check if draw.io CLI is installed
- Export diagrams automatically (if CLI available)
- Provide manual export instructions (if CLI not available)
- Show status of all diagram files

## Manual Export Instructions

If you prefer to export manually or the automated script doesn't work:

### Option 1: Using draw.io Desktop App

1. Install draw.io from: https://github.com/jgraph/drawio-desktop/releases
2. Open `APIM-DocIntel-Architecture.drawio`
3. Click **File → Export as → PNG...**
4. Use these settings:
   - Zoom: 100%
   - Border Width: 10px
   - Transparent Background: Unchecked
   - Selection Only: Unchecked
5. Save as `APIM-DocIntel-Architecture.png` in this same folder

### Option 2: Using draw.io Online

1. Go to https://app.diagrams.net/
2. Open `APIM-DocIntel-Architecture.drawio`
3. Click **File → Export as → PNG...**
4. Use the same settings as above
5. Download and save as `APIM-DocIntel-Architecture.png` in this folder

### Option 3: Using Command Line (if draw.io is installed)

```bash
# From the repository root
drawio -x -f png -o diagrams/APIM-DocIntel-Architecture.png diagrams/APIM-DocIntel-Architecture.drawio
```

## After Exporting

Once you've exported the PNG file, the main README.md will automatically display it in the Architecture section.

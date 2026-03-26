# FileMorph

**FileMorph** is a universal desktop file converter in Python (PyQt6) with support for images, documents, tables, audio and video.

The project was created as a portfolio and demonstrates:
- clean architecture
- work with GUI (PyQt6)
- multithreading (QThread)
- processing files of different types
- history system (SQLite)
- localization (RU / EN)

---

## Opportunities

###  Images
- JPG, PNG, WebP, BMP, TIFF → conversion between formats
- Resize
- Compression (quality)
- Rotate
-Grayscale

### Documents
- DOCX ↔ PDF
- PDF → TXT
- TXT → DOCX / PDF

### Data
- CSV ↔ JSON ↔ XLSX
- Settings: separator, encoding, sheet

###  Audio (via FFmpeg)
- MP3, WAV, FLAC, OGG, AAC, M4A
- Bitrate and sample rate settings

###  Video (via FFmpeg)
- MP4, AVI, MKV, MOV, WEBM
- Convert to GIF
- FPS, resolution, codec

###  Architecture
- Strategy (converters)
- Registry (formats)
- QThread (asynchronous)
- SQLite (history)

---

##  Interface

- Drag & Drop files
- Preview: 
- images 
- text (txt/docx/pdf)
- Operation history
- Conversion progress
- Dark theme
- Language switching (RU / EN)

---

## Third-party

This project uses FFmpeg (https://ffmpeg.org/)  
Licensed under GPL/LGPL.

---

## License

MIT License

PS: Before instaling or trying in your code editor - please run this command in terminal - python -m venv venv

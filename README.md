<h1 align="center">NHaiku 🌸</h1>

<p align="center">
  <strong>Self-hosted nhentai, cached as you browse</strong>
</p>

<p align="center">
  <em>Visit, cache, forget</em><br>
  <em>Duplicates dissolved to one</em><br>
  <em>Yours, even offline</em>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/github/v/tag/Valcrist/nhaiku?style=flat&label=version&color=brightgreen" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-polyform--nc-orange?style=flat" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/github/languages/top/Valcrist/nhaiku?style=flat" alt="Top Language"></a>
  <a href="https://peps.python.org/pep-0008/"><img src="https://img.shields.io/badge/code%20style-pep8-73e?style=flat" alt="Code Style"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/req:python-3.10%2B-c47?style=flat" alt="Python Version"></a>
  <a href="https://github.com/Valcrist/nhaiku/activity"><img src="https://img.shields.io/badge/status-active-green?style=flat" alt="Status"></a>
</p>

---

## Overview

A self-hosted nhentai mirror that builds itself passively from your browsing. Every gallery you visit gets cached locally - metadata, pages, images. Revisit any time, with or without internet. The archive never grows beyond what you've actually read.

Perceptually identical images across re-uploaded or duplicate galleries are automatically deduplicated using perceptual hashing. Only the best version is kept, ranked by resolution and PSNR, so storage stays lean even if you've browsed the same content multiple times under different IDs.

## Features

- **Passive caching**: Builds your library automatically as you browse
- **Offline access**: All cached data available without internet
- **Image optimization**: Efficient storage with perceptual hashing to merge duplicate images
- **Smart deduplication**: Keeps best version based on resolution and PSNR
- **Tag management**: Automatic tag extraction and organization
- **Fuzzy title search**: Find related titles with slight variations using PostgreSQL trigram similarity
- **Manga merging**: Detects duplicate/partial gallery entries by comparing cached page images and consolidates them under a single master record

## Manga Merging

Duplicate or partial gallery entries (re-uploads, subsets of a longer gallery) can be consolidated by running the merge script. It compares cached page images across all manga, groups entries that share enough identical pages, and promotes the most complete entry as the master.

```bash
.venv/bin/python merge.py
# or with a custom threshold (minimum shared pages to consider a match)
.venv/bin/python merge.py --threshold 3
```

Merged entries are hidden from search and transparently redirect to their master on lookup. Entries that share pages but aren't full duplicates are tagged as related and still appear independently. The script is safe to re-run — it recomputes all relationships incrementally and preserves existing group IDs.

## Requirements

### PostgreSQL Extensions

The following extensions must be enabled on the database before running:

```sql
CREATE EXTENSION pg_trgm;  -- fuzzy title search via trigram similarity
```


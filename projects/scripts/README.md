# Portfolio Project Scripts

This folder contains Python scripts for managing the portfolio website's project content.

## Quick Start

Run the deploy preparation script before deploying to GitHub Pages:

```bash
cd projects/scripts
python deploy.py
```

This runs all necessary maintenance tasks in order.

## Scripts Overview

### `deploy.py`
**One-command deploy preparation.** Runs all maintenance scripts in order:
1. `maintain_portfolios.py` - Ensure all projects have `_portfolio` folders
2. `manage_order.py` - Sync `order.txt` with existing projects
3. `build_website.py` - Generate website data and copy assets

Usage:
```bash
python deploy.py           # Run all steps
python deploy.py --check   # Check only, don't modify
```

### `migrate_assets.py`
**One-time migration script.** Migrates assets from `_PortfolioAssets` to individual project `_portfolio` folders. Only needed when initially setting up the new structure.

Usage:
```bash
python migrate_assets.py --dry-run   # Preview changes
python migrate_assets.py             # Execute migration
```

### `manage_order.py`
**Project ordering.** Manages `order.txt` which controls the display order of projects on the website.

Usage:
```bash
python manage_order.py         # Sync order.txt with projects
python manage_order.py --show  # Display current order
```

To reorder projects, simply edit `order.txt` and move lines up/down.

### `maintain_portfolios.py`
**Create missing folders.** Ensures all project folders have properly configured `_portfolio` directories with template files.

Usage:
```bash
python maintain_portfolios.py         # Create missing folders
python maintain_portfolios.py --check # Check only
```

### `build_website.py`
**Generate website data.** Aggregates project data from all `_portfolio` folders into `projects_data.json` and copies assets to the website content folder.

Usage:
```bash
python build_website.py         # Build website data
python build_website.py --clean # Clean output folders first
```

### `validate.py`
**Validate configurations.** Checks all projects for issues like missing thumbnails, invalid categories, or malformed YAML.

Usage:
```bash
python validate.py           # Validate all projects
python validate.py --verbose # Show all details
```

## File Structure

Each project should have:
```
Project Folder/
├── _portfolio/
│   ├── project.yaml      # Project metadata
│   ├── thumbnail.webp    # Project thumbnail
│   ├── readme.md         # Project description
│   ├── .gitignore        # Prevents tracking in project repos
│   ├── images/           # Gallery images (optional)
│   └── downloads/        # Downloadable files (optional)
└── ... (project files)
```

## Project YAML Format

```yaml
title: "Project Name"
description: "Brief description"
category: hardware  # academic, hardware, games, applications, other
public: true        # true = visible on website

# Optional
youtube: "https://www.youtube.com/watch?v=..."
date: "2024-03"
notes: "Internal notes"
```

## Order File

The `order.txt` file in `projects/` controls display order:
- One project folder name per line
- Projects appear in this order on the website
- New projects are auto-added at the end
- Deleted projects are auto-removed

# Gravel God Training Guide Generator

Production-ready HTML training guide generator for Gravel God Cycling training plans.

## Overview

Generates comprehensive 35-page HTML training guides from race JSON data and plan JSON templates. Outputs are styled with neo-brutalist design and include all sections: Welcome, Structure, Training, Zones, Execution, Recovery, Skills, Fueling, Mental, Race Day, Tires, and Glossary.

## Features

- ✅ Generates complete HTML guides (~800+ lines, ~43KB)
- ✅ Neo-brutalist design system (cream, turquoise, yellow, brown)
- ✅ Race-specific content (distance, elevation, terrain, challenges)
- ✅ Plan-specific content (tier, level, weekly hours, duration)
- ✅ Radar chart visualization for race difficulty
- ✅ Phase progression bars
- ✅ Responsive navigation with sticky header
- ✅ UTF-8 encoding with proper charset declarations

## Structure

```
gravel-god-guides/
├── generators/
│   └── guide_generator.py    # Main generator script
├── race_data/
│   ├── unbound_gravel_200.json              # Sample race data
│   └── ayahuasca_beginner_template.json     # Sample plan template
├── templates/                                # HTML templates (if needed)
├── output/                                   # Generated guides
└── docs/                                     # Documentation
```

## Usage

### Basic Usage

```bash
python generators/guide_generator.py \
  --race race_data/unbound_gravel_200.json \
  --plan race_data/ayahuasca_beginner_template.json \
  --output-dir output/
```

### Arguments

- `--race`: Path to race JSON file (required)
- `--plan`: Path to plan JSON template file (required)
- `--output-dir`: Output directory for generated HTML (default: current directory)
- `--output`: Specific output filename (auto-generated if not specified)

### Example Output

Generates: `unbound_gravel_200_ayahuasca_beginner_ayahuasca_beginner_guide.html`

## Race JSON Format

See `race_data/unbound_gravel_200.json` for example structure. Required fields:

- `race_metadata`: name, distance_miles, elevation_feet, location, date
- `race_characteristics`: climate, terrain, technical_difficulty, typical_weather
- `race_hooks`: punchy, detail
- `non_negotiables`: Array of requirements (dict format with `requirement`, `by_when`, `why`)
- `guide_variables`: race_name, race_distance, race_elevation, race_challenges, etc.

## Plan JSON Format

See `race_data/ayahuasca_beginner_template.json` for example structure. Required fields:

- `plan_metadata`: name, duration_weeks, target_hours, target_athlete, goal
- `philosophy`: name, description
- `workouts`: Array of weekly workout structures

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## Output

Generated HTML files include:

- Complete HTML5 structure with DOCTYPE
- UTF-8 charset declaration
- Neo-brutalist styling (inline CSS)
- Responsive navigation
- Race difficulty radar chart (SVG)
- Phase progression visualization
- All training guide sections
- JavaScript for active navigation highlighting

## License

Proprietary - Gravel God Cycling

## Contact

gravelgodcoaching@gmail.com


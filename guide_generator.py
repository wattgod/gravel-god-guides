#!/usr/bin/env python3
"""
Gravel God Training Guide Generator V7
Generates full-length HTML training guides from V7 template
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Neo-brutalist color scheme
COLORS = {
    'cream': '#f5f5dc',
    'turquoise': '#4ecdc4',
    'yellow': '#f4d03f',
    'brown_dark': '#59473C',
    'text_dark': '#2c2c2c',
}

def load_template() -> str:
    """Load the V7 template from extracted text file"""
    template_path = Path(__file__).parent.parent / 'v7_template_extracted.txt'
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found at {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_sections(template: str) -> Dict[str, str]:
    """Extract sections from template - captures ALL content"""
    sections = {}
    current_section = None
    current_content = []
    
    lines = template.split('\n')
    
    for line in lines:
        stripped = line.strip()
        
        # Check if it's a section header
        if stripped.startswith('SECTION ') or (stripped.isupper() and 'SECTION' in stripped and len(stripped) < 100):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = stripped
            current_content = []
        elif stripped.startswith('ALTITUDE TRAINING SECTION'):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = stripped
            current_content = []
        elif stripped == 'CLOSING' or stripped.startswith('CLOSING'):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = 'CLOSING'
            current_content = []
        else:
            # Add ALL content, including empty lines (they help with formatting)
            if current_section:
                current_content.append(line)
            elif not current_section and stripped:  # Content before first section
                # This is the header/title - create a section for it
                if 'SECTION' not in sections:
                    sections['HEADER'] = []
                if isinstance(sections['HEADER'], list):
                    sections['HEADER'].append(line)
                else:
                    sections['HEADER'] = sections['HEADER'] + '\n' + line
    
    # Add final section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    # Convert header list to string
    if 'HEADER' in sections and isinstance(sections['HEADER'], list):
        sections['HEADER'] = '\n'.join(sections['HEADER'])
    
    return sections

def replace_variables(text: str, race_data: Dict[str, Any]) -> str:
    """Replace all template variables with race data"""
    # Build variable mapping
    vars_map = {
        'RACE_NAME': race_data.get('race', {}).get('name', '{{RACE_NAME}}'),
        'DISTANCE': str(race_data.get('race', {}).get('vitals', {}).get('distance_miles', '{{DISTANCE}}')),
        'ELEVATION_GAIN': str(race_data.get('race', {}).get('vitals', {}).get('elevation_gain_ft', '{{ELEVATION_GAIN}}')),
        'TERRAIN_DESCRIPTION': race_data.get('race', {}).get('terrain_description', '{{TERRAIN_DESCRIPTION}}'),
        'DURATION_ESTIMATE': race_data.get('race', {}).get('duration_estimate', '{{DURATION_ESTIMATE}}'),
        'RACE_DESCRIPTION': race_data.get('race', {}).get('description', '{{RACE_DESCRIPTION}}'),
        'ABILITY_LEVEL': race_data.get('ability_level', '{{ABILITY_LEVEL}}'),
        'TIER_NAME': race_data.get('tier_name', '{{TIER_NAME}}'),
        'WEEKLY_HOURS': str(race_data.get('weekly_hours', '{{WEEKLY_HOURS}}')),
        'RACE_KEY_CHALLENGES': race_data.get('race', {}).get('key_challenges', '{{RACE_KEY_CHALLENGES}}'),
        'WEEKLY_STRUCTURE_DESCRIPTION': race_data.get('weekly_structure', '{{WEEKLY_STRUCTURE_DESCRIPTION}}'),
        'RACE_SUPPORT_URL': race_data.get('race', {}).get('support_url', '{{RACE_SUPPORT_URL}}'),
        'RECOMMENDED_TIRE_WIDTH': race_data.get('race', {}).get('recommended_tire_width', '{{RECOMMENDED_TIRE_WIDTH}}'),
        'AID_STATION_STRATEGY': race_data.get('race', {}).get('aid_station_strategy', '{{AID_STATION_STRATEGY}}'),
        'WEATHER_STRATEGY': race_data.get('race', {}).get('weather_strategy', '{{WEATHER_STRATEGY}}'),
        'RACE_ELEVATION': str(race_data.get('race', {}).get('vitals', {}).get('elevation_ft', 0)),
    }
    
    # Calculate altitude power loss if elevation > 3000
    elevation = race_data.get('race', {}).get('vitals', {}).get('elevation_ft', 0)
    if elevation > 3000:
        power_loss = round((elevation / 1000) * 1.75, 1)
        vars_map['ALTITUDE_POWER_LOSS'] = str(power_loss)
    else:
        vars_map['ALTITUDE_POWER_LOSS'] = '0'
    
    # Key workouts
    workouts = race_data.get('key_workouts', [])
    for i in range(1, 5):
        if i <= len(workouts):
            vars_map[f'KEY_WORKOUT_{i}_NAME'] = workouts[i-1].get('name', f'{{KEY_WORKOUT_{i}_NAME}}')
            vars_map[f'KEY_WORKOUT_{i}_PURPOSE'] = workouts[i-1].get('purpose', f'{{KEY_WORKOUT_{i}_PURPOSE}}')
        else:
            vars_map[f'KEY_WORKOUT_{i}_NAME'] = f'{{KEY_WORKOUT_{i}_NAME}}'
            vars_map[f'KEY_WORKOUT_{i}_PURPOSE'] = f'{{KEY_WORKOUT_{i}_PURPOSE}}'
    
    # Non-negotiables
    non_negs = race_data.get('race', {}).get('non_negotiables', [])
    for i in range(1, 6):
        if i <= len(non_negs):
            req = non_negs[i-1]
            vars_map[f'NON_NEG_{i}_REQUIREMENT'] = req.get('requirement', f'{{NON_NEG_{i}_REQUIREMENT}}')
            vars_map[f'NON_NEG_{i}_BY_WHEN'] = req.get('by_when', f'{{NON_NEG_{i}_BY_WHEN}}')
            vars_map[f'NON_NEG_{i}_WHY'] = req.get('why', f'{{NON_NEG_{i}_WHY}}')
        else:
            vars_map[f'NON_NEG_{i}_REQUIREMENT'] = f'{{NON_NEG_{i}_REQUIREMENT}}'
            vars_map[f'NON_NEG_{i}_BY_WHEN'] = f'{{NON_NEG_{i}_BY_WHEN}}'
            vars_map[f'NON_NEG_{i}_WHY'] = f'{{NON_NEG_{i}_WHY}}'
    
    # Race-specific content
    vars_map['RACE_SPECIFIC_SKILL_NOTES'] = race_data.get('race', {}).get('skill_notes', '{{RACE_SPECIFIC_SKILL_NOTES}}')
    vars_map['RACE_SPECIFIC_TACTICS'] = race_data.get('race', {}).get('tactics', '{{RACE_SPECIFIC_TACTICS}}')
    vars_map['EQUIPMENT_CHECKLIST'] = race_data.get('race', {}).get('equipment_checklist', '{{EQUIPMENT_CHECKLIST}}')
    
    # Skills
    skills = race_data.get('race', {}).get('skills', {})
    vars_map['SKILL_5_NAME'] = skills.get('skill_5_name', '{{SKILL_5_NAME}}')
    vars_map['SKILL_5_WHY'] = skills.get('skill_5_why', '{{SKILL_5_WHY}}')
    vars_map['SKILL_5_HOW'] = skills.get('skill_5_how', '{{SKILL_5_HOW}}')
    vars_map['SKILL_5_CUE'] = skills.get('skill_5_cue', '{{SKILL_5_CUE}}')
    
    # Replace all variables
    result = text
    for var, value in vars_map.items():
        result = result.replace(f'{{{{{var}}}}}', str(value))
    
    return result

def generate_svg_phase_bars() -> str:
    """Generate SVG phase bars with neo-brutalist styling"""
    return '''<svg width="100%" height="80" style="margin: 1.5rem 0; border: 3px solid #2c2c2c; box-shadow: 6px 6px 0 rgba(0,0,0,0.2);">
        <defs>
            <style>
                .phase-text { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 14px; }
            </style>
        </defs>
        <rect x="0" y="0" width="25%" height="80" fill="#4ECDC4" stroke="#2c2c2c" stroke-width="2" />
        <text x="12.5%" y="45" text-anchor="middle" fill="#2c2c2c" class="phase-text">BASE</text>
        <text x="12.5%" y="60" text-anchor="middle" fill="#2c2c2c" class="phase-text" font-size="10px">Wks 1-3</text>
        <rect x="25%" y="0" width="33%" height="80" fill="#F4D03F" stroke="#2c2c2c" stroke-width="2" />
        <text x="41.5%" y="45" text-anchor="middle" fill="#2c2c2c" class="phase-text">BUILD</text>
        <text x="41.5%" y="60" text-anchor="middle" fill="#2c2c2c" class="phase-text" font-size="10px">Wks 4-7</text>
        <rect x="58%" y="0" width="25%" height="80" fill="#e74c3c" stroke="#2c2c2c" stroke-width="2" />
        <text x="70.5%" y="45" text-anchor="middle" fill="#f5f5dc" class="phase-text">PEAK</text>
        <text x="70.5%" y="60" text-anchor="middle" fill="#f5f5dc" class="phase-text" font-size="10px">Wks 8-10</text>
        <rect x="83%" y="0" width="17%" height="80" fill="#27ae60" stroke="#2c2c2c" stroke-width="2" />
        <text x="91.5%" y="45" text-anchor="middle" fill="#f5f5dc" class="phase-text">TAPER</text>
        <text x="91.5%" y="60" text-anchor="middle" fill="#f5f5dc" class="phase-text" font-size="10px">Wks 11-12</text>
    </svg>'''

def generate_svg_radar_chart(race_data: Dict[str, Any]) -> str:
    """Generate SVG radar chart from race data with neo-brutalist styling"""
    scores = race_data.get('race', {}).get('radar_scores', {})
    # Default scores if not provided
    elevation = scores.get('elevation', {}).get('score', 3)
    length = scores.get('length', {}).get('score', 5)
    technicality = scores.get('technicality', {}).get('score', 2)
    climate = scores.get('climate', {}).get('score', 5)
    altitude = scores.get('altitude', {}).get('score', 2)
    adventure = scores.get('adventure', {}).get('score', 3)
    
    # Enhanced table with neo-brutalist styling
    return f'''<table class="zone-table">
        <tr><th>Factor</th><th>Score</th><th>What It Means</th></tr>
        <tr><td><strong>Elevation</strong></td><td style="font-family: 'JetBrains Mono', monospace; color: #4ecdc4; font-weight: 700;">{"●" * elevation}{"○" * (5-elevation)}</td><td>Cumulative elevation challenge</td></tr>
        <tr><td><strong>Length</strong></td><td style="font-family: 'JetBrains Mono', monospace; color: #4ecdc4; font-weight: 700;">{"●" * length}{"○" * (5-length)}</td><td>Distance demands</td></tr>
        <tr><td><strong>Technicality</strong></td><td style="font-family: 'JetBrains Mono', monospace; color: #4ecdc4; font-weight: 700;">{"●" * technicality}{"○" * (5-technicality)}</td><td>Bike handling requirements</td></tr>
        <tr><td><strong>Climate</strong></td><td style="font-family: 'JetBrains Mono', monospace; color: #4ecdc4; font-weight: 700;">{"●" * climate}{"○" * (5-climate)}</td><td>Weather challenges</td></tr>
        <tr><td><strong>Altitude</strong></td><td style="font-family: 'JetBrains Mono', monospace; color: #4ecdc4; font-weight: 700;">{"●" * altitude}{"○" * (5-altitude)}</td><td>Elevation effects</td></tr>
        <tr><td><strong>Adventure</strong></td><td style="font-family: 'JetBrains Mono', monospace; color: #4ecdc4; font-weight: 700;">{"●" * adventure}{"○" * (5-adventure)}</td><td>Logistical complexity</td></tr>
    </table>'''

def format_paragraph(text: str) -> str:
    """Format a paragraph with proper HTML"""
    if not text.strip():
        return '<br>'
    
    stripped = text.strip()
    
    # Check if it's a header (all caps, short)
    if stripped.isupper() and len(stripped) < 100 and not stripped.startswith('{{'):
        return f'<h2>{stripped}</h2>'
    
    # Check for numbered lists
    if re.match(r'^\d+[\.\)]\s+', stripped):
        num_part = re.match(r'^(\d+[\.\)])\s+', stripped).group(1)
        content = stripped[len(num_part):].strip()
        return f'<p><strong>{num_part}</strong> {content}</p>'
    
    # Check for bullet points
    if stripped.startswith('-') or stripped.startswith('•'):
        content = stripped.lstrip('-•').strip()
        return f'<p>• {content}</p>'
    
    # Check for bold text patterns (text: description)
    if ':' in stripped and len(stripped.split(':')) == 2:
        parts = stripped.split(':', 1)
        if len(parts[0]) < 50:  # Likely a label
            return f'<p><strong>{parts[0]}:</strong> {parts[1].strip()}</p>'
    
    # Regular paragraph
    return f'<p>{stripped}</p>'

def format_table(text: str) -> str:
    """Format table from text"""
    lines = text.strip().split('\n')
    if len(lines) < 2:
        return f'<p>{text}</p>'
    
    # Try to detect table structure
    if '|' in lines[0] or '\t' in lines[0]:
        rows = []
        for line in lines:
            if '|' in line:
                cells = [c.strip() for c in line.split('|')]
                rows.append(cells)
            elif '\t' in line:
                cells = [c.strip() for c in line.split('\t')]
                rows.append(cells)
        
        if len(rows) > 1:
            html = '<table class="zone-table">\n'
            # First row as header
            html += '<tr>' + ''.join(f'<th>{cell}</th>' for cell in rows[0] if cell) + '</tr>\n'
            # Rest as data rows
            for row in rows[1:]:
                html += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row if cell) + '</tr>\n'
            html += '</table>'
            return html
    
    return f'<p>{text}</p>'

def load_neo_brutalist_css() -> str:
    """Load the complete neo-brutalist CSS from template"""
    css_path = Path(__file__).parent / 'neo_brutalist_css.txt'
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    # Fallback: return inline CSS if file doesn't exist
    return ""

def generate_html(race_data: Dict[str, Any], output_path: Optional[Path] = None) -> str:
    """Generate full HTML guide from race data"""
    
    # Load template
    template = load_template()
    sections = extract_sections(template)
    
    # Replace variables in template
    processed_template = replace_variables(template, race_data)
    processed_sections = extract_sections(processed_template)
    
    # Load neo-brutalist CSS
    css_content = load_neo_brutalist_css()
    
    # Build HTML
    html_parts = []
    
    # Get race data
    race_name = race_data.get('race', {}).get('name', 'Gravel God Training Guide')
    tagline = race_data.get('race', {}).get('tagline', 'Your Complete Training Resource')
    ability_level = race_data.get('ability_level', 'Training Guide')
    tier_name = race_data.get('tier_name', 'Tier')
    location = race_data.get('race', {}).get('vitals', {}).get('location', {})
    location_str = f"{location.get('city', '')}, {location.get('state', '')}".strip(', ')
    if not location_str:
        location_str = ability_level
    
    # HTML header with exact neo-brutalist CSS from template
    html_parts.append(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>{race_name} Training Guide | {tier_name} - {ability_level}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Sometype+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
{css_content}
    </style>
</head>
<body>

<!-- STICKY NAVIGATION -->
<nav class="sticky-nav">
    <a href="#welcome" class="active">Welcome</a>
    <a href="#structure">Structure</a>
    <a href="#before">Before</a>
    <a href="#how-training-works">Training</a>
    <a href="#zones">Zones</a>
    <a href="#execution">Execution</a>
    <a href="#recovery">Recovery</a>
    <a href="#strength">Strength</a>
    <a href="#skills">Skills</a>
    <a href="#fueling">Fuel</a>
    <a href="#mental">Mental</a>
    <a href="#race-day">Race Day</a>
    <a href="#tires">Tires</a>
    <a href="#glossary">Glossary</a>
</nav>

<!-- HEADER -->
<header class="header">
    <div class="race-badge">{location_str}</div>
    <h1>{race_name}</h1>
    <p class="header-subtitle">{tagline}</p>
    <div class="tier-badges">
        <span class="tier-badge">{tier_name} Tier</span>
        <span class="level-badge">{ability_level}</span>
    </div>
</header>

<!-- MAIN CONTENT -->
<main class="main-content">
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            border-radius: 0 !important;
        }}
        
        body {{
            font-family: 'JetBrains Mono', 'Sometype Mono', 'Courier New', monospace;
            font-size: 16px;
            line-height: 1.7;
            color: var(--text-dark);
            max-width: 900px;
            margin: 0 auto;
            padding: 0;
            background: linear-gradient(135deg, var(--cream) 0%, #ede5d0 100%);
            min-height: 100vh;
        }}
        
        /* Sticky Navigation */
        .sticky-nav {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: var(--brown-dark);
            border-bottom: 3px solid var(--text-dark);
            padding: 0.75rem 1rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }}
        
        .sticky-nav a {{
            color: var(--cream);
            text-decoration: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            font-size: 0.875rem;
            border: 2px solid var(--text-dark);
            background: var(--brown-dark);
            transition: all 0.1s;
            box-shadow: 2px 2px 0 rgba(0,0,0,0.2);
        }}
        
        .sticky-nav a:hover {{
            background: var(--turquoise);
            color: var(--text-dark);
            transform: translate(1px, 1px);
            box-shadow: 1px 1px 0 rgba(0,0,0,0.2);
        }}
        
        .sticky-nav a.active {{
            background: var(--turquoise);
            color: var(--text-dark);
            font-weight: 700;
        }}
        
        .content-wrapper {{
            padding: 20px;
        }}
        
        /* Section Headers with Number Badges */
        section {{
            scroll-margin-top: 80px;
            margin-bottom: 3rem;
        }}
        
        .section-header {{
            background: var(--text-dark);
            color: var(--cream);
            padding: 1rem 1.5rem 1rem 3.5rem;
            position: relative;
            box-shadow: 6px 6px 0 rgba(0,0,0,0.2);
            margin: 2.5rem 0 1.5rem 0;
        }}
        
        .section-number {{
            position: absolute;
            left: -10px;
            top: 50%;
            transform: translateY(-50%);
            background: var(--turquoise);
            color: var(--text-dark);
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.25rem;
            border: 3px solid var(--text-dark);
            box-shadow: 3px 3px 0 rgba(0,0,0,0.2);
        }}
        
        h1 {{
            font-family: 'JetBrains Mono', 'Sometype Mono', 'Courier New', monospace;
            font-size: 1.5rem;
            color: var(--cream);
            margin: 0;
            font-weight: 700;
        }}
        
        h2 {{
            font-family: 'JetBrains Mono', 'Sometype Mono', 'Courier New', monospace;
            font-size: 1.25rem;
            color: var(--brown-dark);
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-left: 4px solid var(--turquoise);
            padding-left: 1rem;
            font-weight: 500;
        }}
        
        h3 {{
            font-size: 13pt;
            color: {COLORS['brown_dark']};
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        /* Header Design */
        .header-box {{
            background: var(--brown-dark);
            color: var(--cream);
            padding: 3rem 2rem;
            text-align: center;
            font-family: 'JetBrains Mono', 'Sometype Mono', 'Courier New', monospace;
            margin: 0;
            border-bottom: 3px solid var(--text-dark);
            position: relative;
            overflow: hidden;
        }}
        
        .header-box::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 10px,
                rgba(78, 205, 196, 0.1) 10px,
                rgba(78, 205, 196, 0.1) 20px
            );
            pointer-events: none;
        }}
        
        .header-box h1 {{
            color: var(--turquoise);
            font-size: 3rem;
            font-weight: 700;
            text-transform: uppercase;
            margin: 0 0 0.5rem 0;
            text-shadow: 
                3px 3px 0 var(--yellow),
                6px 6px 0 var(--text-dark);
            position: relative;
            z-index: 1;
        }}
        
        .header-box .tagline {{
            color: var(--cream);
            font-size: 1.125rem;
            margin-top: 0.5rem;
            font-weight: 400;
            position: relative;
            z-index: 1;
        }}
        
        .race-badge {{
            display: inline-block;
            background: var(--turquoise);
            color: var(--text-dark);
            padding: 0.5rem 1rem;
            margin-top: 1rem;
            border: 3px solid var(--text-dark);
            font-weight: 700;
            box-shadow: 3px 3px 0 rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
        }}
        
        /* Callout Boxes - Four Types */
        .callout {{
            border: 3px solid var(--text-dark);
            border-left-width: 6px;
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 4px 4px 0 rgba(0,0,0,0.15);
        }}
        
        .callout-warning {{
            border-left-color: var(--yellow);
            background: #fef9e7;
        }}
        
        .callout-info {{
            border-left-color: var(--turquoise);
            background: #e8f8f5;
        }}
        
        .callout-danger {{
            border-left-color: var(--red);
            background: #fdedec;
        }}
        
        .callout-success {{
            border-left-color: var(--green);
            background: #e9f7ef;
        }}
        
        /* Legacy class support */
        .callout-box {{
            border: 3px solid var(--text-dark);
            border-left-width: 6px;
            border-left-color: var(--turquoise);
            background: var(--cream);
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 4px 4px 0 rgba(0,0,0,0.15);
        }}
        
        .callout-turquoise {{
            border-left-color: var(--turquoise);
            background: #e8f8f5;
        }}
        
        .warning-box {{
            border-left-color: var(--yellow);
            background: #fef9e7;
            border: 3px solid var(--text-dark);
            border-left-width: 6px;
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 4px 4px 0 rgba(0,0,0,0.15);
        }}
        
        /* Tables - Neo-Brutalist */
        table, .zone-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            border: 3px solid var(--text-dark);
            box-shadow: 6px 6px 0 rgba(0,0,0,0.2);
            background: white;
        }}
        
        th {{
            background: var(--brown-dark);
            color: var(--cream);
            padding: 0.75rem;
            text-align: left;
            border: 2px solid var(--text-dark);
            font-family: 'JetBrains Mono', 'Sometype Mono', 'Courier New', monospace;
            font-weight: 700;
        }}
        
        td {{
            padding: 0.75rem;
            border: 1px solid var(--text-dark);
        }}
        
        tr:nth-child(even) {{
            background: rgba(0,0,0,0.03);
        }}
        
        tr:hover {{
            background: rgba(78, 205, 196, 0.1);
        }}
        
        /* G Spot row highlight */
        tr.g-spot-row,
        .zone-table tr:has(td:contains("G Spot")) {{
            background: rgba(78, 205, 196, 0.2) !important;
            font-weight: 500;
        }}
        
        /* Table of Contents */
        .toc {{
            background: var(--cream);
            border: 3px solid var(--text-dark);
            padding: 1.5rem;
            margin: 2rem 0;
            box-shadow: 6px 6px 0 rgba(0,0,0,0.2);
        }}
        
        .toc h2 {{
            margin-top: 0;
            border: none;
            padding: 0;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }}
        
        .toc-buttons {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.75rem;
            margin-top: 1rem;
        }}
        
        .toc-button {{
            background: var(--brown-dark);
            color: var(--cream);
            border: 3px solid var(--text-dark);
            padding: 0.75rem 1rem;
            text-decoration: none;
            font-family: 'JetBrains Mono', 'Sometype Mono', 'Courier New', monospace;
            font-weight: 500;
            text-align: center;
            display: block;
            box-shadow: 4px 4px 0 rgba(0,0,0,0.2);
            transition: transform 0.1s, box-shadow 0.1s;
            font-size: 0.875rem;
        }}
        
        .toc-button:hover {{
            transform: translate(2px, 2px);
            box-shadow: 2px 2px 0 rgba(0,0,0,0.2);
            background: var(--turquoise);
            color: var(--text-dark);
        }}
        
        .toc-button:active {{
            transform: translate(4px, 4px);
            box-shadow: 0px 0px 0 rgba(0,0,0,0.2);
        }}
        
        p {{
            margin: 15px 0;
        }}
        
        /* Neo-brutalist lists */
        /* Lists */
        ul, ol {{
            margin: 1.5rem 0;
            padding: 1rem 1.5rem 1rem 2.5rem;
            border-left: 3px solid var(--turquoise);
            border: 2px solid var(--text-dark);
            background: white;
            box-shadow: 3px 3px 0 rgba(0,0,0,0.1);
            margin-left: 0;
        }}
        
        li {{
            margin: 0.5rem 0;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            body {{
                font-size: 14px;
            }}
            
            .header-box h1 {{
                font-size: 2rem;
            }}
            
            .sticky-nav {{
                flex-wrap: wrap;
                gap: 0.25rem;
                padding: 0.5rem;
            }}
            
            .sticky-nav a {{
                font-size: 0.75rem;
                padding: 0.375rem 0.75rem;
            }}
            
            .toc-buttons {{
                grid-template-columns: 1fr;
            }}
            
            table {{
                display: block;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}
            
            .section-header {{
                padding: 0.75rem 1rem 0.75rem 3rem;
            }}
            
            .section-number {{
                width: 35px;
                height: 35px;
                font-size: 1rem;
            }}
        }}
        
        @media print {{
            .sticky-nav {{
                display: none;
            }}
            
            body {{
                background: white;
            }}
            
            .callout-box, .callout {{
                page-break-inside: avoid;
            }}
            
            section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>''')
    
    # Header
    race_name = race_data.get('race', {}).get('name', 'Gravel God Training Guide')
    tagline = race_data.get('race', {}).get('tagline', 'Your Complete Training Resource')
    
    # Get location for race badge
    location = race_data.get('race', {}).get('vitals', {}).get('location', {})
    location_str = f"{location.get('city', '')}, {location.get('state', '')}".strip(', ')
    
    html_parts.append(f'''    <div class="header-box">
        <h1>{race_name}</h1>
        <p class="tagline">{tagline}</p>
        <div class="race-badge">{location_str if location_str else race_data.get('ability_level', 'Training Guide')}</div>
        <p class="tagline" style="margin-top: 1rem;">{race_data.get('ability_level', 'Training Guide')} | {race_data.get('tier_name', 'Tier')}</p>
    </div>''')
    
    # Build sticky navigation
    nav_sections = [
        ('brief', 'Brief'),
        ('before', 'Before'),
        ('fundamentals', 'Fundamentals'),
        ('arc', '12-Week Arc'),
        ('zones', 'Zones'),
        ('workouts', 'Workouts'),
        ('skills', 'Skills'),
        ('fuel', 'Fuel'),
        ('mental', 'Mental'),
        ('tactics', 'Tactics'),
        ('prep', 'Prep'),
        ('race-day', 'Race Day'),
        ('reference', 'Ref'),
        ('glossary', 'Glossary'),
    ]
    
    html_parts.append('    <nav class="sticky-nav">')
    for nav_id, nav_label in nav_sections:
        html_parts.append(f'        <a href="#{nav_id}" class="nav-link">{nav_label}</a>')
    html_parts.append('    </nav>')
    html_parts.append('    <div class="content-wrapper">')
    
    # Define section order
    section_order = [
        'SECTION 1: Training Plan Brief',
        'SECTION 2: BEFORE YOU START',
        'SECTION 3: TRAINING FUNDAMENTALS',
        'SECTION 4: YOUR 12-WEEK ARC',
        'SECTION 5: TRAINING ZONES',
        'SECTION 6: WORKOUT EXECUTION',
        'SECTION 7: TECHNICAL SKILLS FOR',
        'SECTION 8: FUELING & HYDRATION',
        'SECTION 9: MENTAL TRAINING',
        'SECTION 10: RACE TACTICS FOR',
        'SECTION 11: RACE-SPECIFIC PREPARATION FOR',
        'ALTITUDE TRAINING SECTION',
        'SECTION 12: RACE WEEK PROTOCOL',
        'SECTION 13: QUICK REFERENCE',
        'SECTION 14: GLOSSARY',
        'CLOSING',
    ]
    
    # Build table of contents
    section_titles = []
    for section_key in section_order:
        matching_section = None
        for key in processed_sections.keys():
            if section_key in key:
                matching_section = key
                break
        
        if not matching_section:
            continue
        
        # Skip altitude section if elevation < 3000
        if 'ALTITUDE' in matching_section:
            elevation = race_data.get('race', {}).get('vitals', {}).get('elevation_ft', 0)
            if elevation < 3000:
                continue
        
        section_title = matching_section.replace('SECTION ', '').replace(':', '')
        section_id = section_title.lower().replace(' ', '-').replace('&', 'and')
        section_titles.append((section_id, section_title))
    
    # Add table of contents
    html_parts.append('    <div class="toc">')
    html_parts.append('        <h2>Table of Contents</h2>')
    html_parts.append('        <div class="toc-buttons">')
    for section_id, section_title in section_titles:
        html_parts.append(f'            <a href="#{section_id}" class="toc-button">{section_title}</a>')
    html_parts.append('        </div>')
    html_parts.append('    </div>')
    
    # Process each section
    for section_key in section_order:
        # Find matching section
        matching_section = None
        for key in processed_sections.keys():
            if section_key in key:
                matching_section = key
                break
        
        if not matching_section:
            continue
        
        # Skip altitude section if elevation < 3000
        if 'ALTITUDE' in matching_section:
            elevation = race_data.get('race', {}).get('vitals', {}).get('elevation_ft', 0)
            if elevation < 3000:
                continue
        
        content = processed_sections[matching_section]
        
        # Format section header with ID and number badge
        section_title = matching_section.replace('SECTION ', '').replace(':', '')
        section_id = section_title.lower().replace(' ', '-').replace('&', 'and')
        
        # Extract section number for badge
        section_num = None
        if section_title[0].isdigit():
            section_num = section_title.split()[0]
        elif 'CLOSING' in section_title.upper():
            section_num = '✓'
        elif 'ALTITUDE' in section_title.upper():
            section_num = 'A'
        
        # Map to nav IDs - check for partial matches too
        nav_id_map = {
            '1-training-plan-brief': 'brief',
            '2-before-you-start': 'before',
            '3-training-fundamentals': 'fundamentals',
            '4-your-12-week-arc': 'arc',
            '5-training-zones': 'zones',
            '6-workout-execution': 'workouts',
            '7-technical-skills-for': 'skills',
            '8-fueling-and-hydration': 'fuel',
            '9-mental-training': 'mental',
            '10-race-tactics-for': 'tactics',
            '11-race-specific-preparation-for': 'prep',
            '12-race-week-protocol': 'race-day',
            '13-quick-reference': 'reference',
            '14-glossary': 'glossary',
        }
        
        # Try exact match first, then partial match
        nav_id = nav_id_map.get(section_id)
        if not nav_id:
            # Check for partial matches (e.g., "7-technical-skills-for-unbound-gravel-200" -> "skills")
            for key, value in nav_id_map.items():
                if key in section_id or section_id.startswith(key.split('-')[0]):
                    nav_id = value
                    break
        
        # Fallback to section_id if no match
        if not nav_id:
            nav_id = section_id
        
        html_parts.append(f'<!-- SECTION: {section_title} -->')
        html_parts.append(f'<section class="section" id="{nav_id}">')
        if section_num:
            html_parts.append(f'    <div class="section-header">')
            html_parts.append(f'        <span class="section-number">{section_num}</span>')
            html_parts.append(f'        <h2>{section_title}</h2>')
            html_parts.append(f'    </div>')
        else:
            html_parts.append(f'    <div class="section-header">')
            html_parts.append(f'        <h2>{section_title}</h2>')
            html_parts.append(f'    </div>')
        html_parts.append('    <div class="section-content">')
        
        # Process content - process EVERY line to capture all content
        paragraphs = content.split('\n')
        in_list = False
        list_items = []
        current_list_type = None
        
        for para in paragraphs:
            stripped = para.strip()
            
            # Replace infographic placeholders
            if 'INFOGRAPHIC_PHASE_BARS' in stripped:
                html_parts.append('        <div class="graphic-container">')
                html_parts.append('            <div class="graphic-title">Training Phases</div>')
                html_parts.append('            ' + generate_svg_phase_bars())
                html_parts.append('        </div>')
                continue
            elif 'INFOGRAPHIC_RATING_HEX' in stripped:
                html_parts.append('        <div class="graphic-container">')
                html_parts.append('            <div class="graphic-title">Race Difficulty Profile</div>')
                html_parts.append('            ' + generate_svg_radar_chart(race_data))
                html_parts.append('        </div>')
                continue
            elif 'INFOGRAPHIC' in stripped and stripped.startswith('{{'):
                # Skip infographic placeholders
                continue
            elif 'TABLE' in stripped and stripped.startswith('['):
                # Table placeholder - skip
                continue
            
            # Handle lists
            if stripped.startswith('-') or stripped.startswith('•') or re.match(r'^\d+[\.\)]\s+', stripped):
                if not in_list:
                    in_list = True
                    list_items = []
                list_items.append(stripped)
                continue
            else:
                # Close list if we were in one
                if in_list and list_items:
                    html_parts.append('    <ul>')
                    for item in list_items:
                        content = item.lstrip('-•').strip()
                        if re.match(r'^\d+[\.\)]\s+', item):
                            num_part = re.match(r'^(\d+[\.\)])\s+', item).group(1)
                            content = item[len(num_part):].strip()
                            html_parts.append(f'    <li><strong>{num_part}</strong> {content}</li>')
                        else:
                            html_parts.append(f'    <li>{content}</li>')
                    html_parts.append('    </ul>')
                    list_items = []
                    in_list = False
            
            # Format as paragraph (including empty lines for spacing)
            formatted = format_paragraph(para)
            if formatted:
                html_parts.append('        ' + formatted)
        
            # Close any remaining list
        if in_list and list_items:
            html_parts.append('        <ul>')
            for item in list_items:
                content = item.lstrip('-•').strip()
                if re.match(r'^\d+[\.\)]\s+', item):
                    num_part = re.match(r'^(\d+[\.\)])\s+', item).group(1)
                    content = item[len(num_part):].strip()
                    html_parts.append(f'            <li><strong>{num_part}</strong> {content}</li>')
                else:
                    html_parts.append(f'            <li>{content}</li>')
            html_parts.append('        </ul>')
        
        # Close any open lists
        if current_list_type:
            if current_list_type == 'ul':
                html_parts.append('        </ul>')
            elif current_list_type == 'ol':
                html_parts.append('        </ol>')
            current_list_type = None
        
        # Close section content and section
        html_parts.append('    </div>')
        html_parts.append('</section>')
    
    # Close main content
    html_parts.append('</main>')
    
    # Add footer
    html_parts.append('''<!-- FOOTER -->
<footer class="footer">
    <div class="footer-tagline">See You at the Finish</div>
    <p>You have the plan. You understand how training works, how to execute the workouts, how to fuel and hydrate, how to manage your mental game, and how to approach race day.</p>
    <p><strong>Now do the work.</strong></p>
    <p>Not perfectly. Not heroically. <em>Consistently. Intelligently. Over 12 weeks.</em></p>
    <p>On race morning, you'll stand at the start line knowing you did everything you could to prepare. That confidence—not hope, not optimism, but confidence based on completed work—is what this plan builds.</p>
    <p><strong>The race will be hard. You trained for hard.</strong></p>
    <br>
    <p class="footer-email">gravelgodcoaching@gmail.com</p>
    <p class="footer-motto">Become what you could be.</p>
</footer>

<!-- SCROLL SPY JAVASCRIPT -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.section');
    const navLinks = document.querySelectorAll('.sticky-nav a');
    
    function updateActiveLink() {
        let current = '';
        const scrollPos = window.scrollY + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    }
    
    window.addEventListener('scroll', updateActiveLink);
    updateActiveLink();
});
</script>''')
    
    # Close HTML
    html_parts.append('</body>\n</html>')
    
    html_output = '\n'.join(html_parts)
    
    # Save if output path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        print(f"Generated guide: {output_path}")
    
    return html_output

def main():
    """Main function for CLI usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: guide_generator.py <race_json_file> [output_html_file]")
        sys.exit(1)
    
    race_json_path = Path(sys.argv[1])
    if not race_json_path.exists():
        print(f"Error: Race JSON file not found: {race_json_path}")
        sys.exit(1)
    
    with open(race_json_path, 'r') as f:
        race_data = json.load(f)
    
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        race_name = race_data.get('race', {}).get('slug', 'race')
        ability = race_data.get('ability_level', 'guide').lower().replace(' ', '-')
        output_path = Path(f'{race_name}_{ability}_guide.html')
    
    generate_html(race_data, output_path)
    print(f"✅ Guide generated: {output_path}")

if __name__ == '__main__':
    main()


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
            html = '<div class="table-wrapper">\n'
            html += '<table>\n'
            # First row as header
            html += '<thead>\n<tr>' + ''.join(f'<th>{cell}</th>' for cell in rows[0] if cell) + '</tr>\n</thead>\n'
            # Rest as data rows
            html += '<tbody>\n'
            for row in rows[1:]:
                # Check if this is a G Spot row
                g_spot_class = ' class="g-spot-row"' if any('g spot' in str(cell).lower() for cell in row) else ''
                html += f'<tr{g_spot_class}>' + ''.join(f'<td>{cell}</td>' for cell in row if cell) + '</tr>\n'
            html += '</tbody>\n'
            html += '</table>\n'
            html += '</div>'
            return html
    
    return f'<p>{text}</p>'

def load_neo_brutalist_css() -> str:
    """Load the complete neo-brutalist CSS from template"""
    css_path = Path(__file__).parent / 'neo_brutalist_css.txt'
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read().strip()  # Remove leading/trailing whitespace
            # Ensure it starts properly
            if not css.startswith('/*'):
                # Try to extract from template_styled.html as fallback
                template_path = Path(__file__).parent / 'template_styled.html'
                if template_path.exists():
                    import re
                    with open(template_path, 'r', encoding='utf-8') as tf:
                        template_content = tf.read()
                        css_match = re.search(r'<style>(.*?)</style>', template_content, re.DOTALL)
                        if css_match:
                            return css_match.group(1).strip()
            return css
    # Fallback: try to extract from template_styled.html
    template_path = Path(__file__).parent / 'template_styled.html'
    if template_path.exists():
        import re
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            css_match = re.search(r'<style>(.*?)</style>', template_content, re.DOTALL)
            if css_match:
                return css_match.group(1).strip()
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
<main class="main-content">''')
    
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
    
    # Process each section (no table of contents - using sticky nav instead)
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
        
        # Track if we're in intro section (first section)
        is_intro_section = (nav_id == 'welcome' or '1' in section_title or 'TRAINING PLAN BRIEF' in section_title.upper())
        intro_paragraphs_collected = []
        intro_collected = False
        processed_paragraphs = set()  # Track paragraphs we've already processed
        in_list = False
        list_items = []
        current_list_type = None
        
        for para in paragraphs:
            stripped = para.strip()
            
            # Collect intro paragraphs for intro-box (first 3-4 paragraphs of welcome section)
            if is_intro_section and not intro_collected and stripped:
                if not stripped.startswith('-') and not stripped.startswith('•') and not re.match(r'^\d+[\.\)]', stripped):
                    if 'This plan isn' in stripped or 'Welcome' in stripped or 'By the time you roll' in stripped or '200 miles' in stripped:
                        intro_paragraphs_collected.append(para)
                        if len(intro_paragraphs_collected) >= 3:
                            # Output intro box
                            html_parts.append('        <div class="intro-box">')
                            for intro_para in intro_paragraphs_collected:
                                formatted = format_paragraph(intro_para)
                                if formatted and '<p>' in formatted:
                                    html_parts.append('        ' + formatted)
                            html_parts.append('        </div>')
                            intro_collected = True
                            continue  # Skip this paragraph, already added
            
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
            
            # Handle lists - use checklist class for "Non-negotiables" or similar
            if stripped.startswith('-') or stripped.startswith('•') or re.match(r'^\d+[\.\)]\s+', stripped):
                if not in_list:
                    in_list = True
                    list_items = []
                list_items.append(stripped)
                continue
            else:
                # Close list if we were in one
                if in_list and list_items:
                    # Check if this should be a checklist (for "Non-negotiables", equipment lists, etc.)
                    use_checklist = any(keyword in ' '.join(list_items).lower() for keyword in ['non-negotiable', 'equipment', 'required', 'checklist'])
                    list_class = ' class="checklist"' if use_checklist else ''
                    html_parts.append(f'        <ul{list_class}>')
                    for item in list_items:
                        content = item.lstrip('-•').strip()
                        if re.match(r'^\d+[\.\)]\s+', item):
                            num_part = re.match(r'^(\d+[\.\)])\s+', item).group(1)
                            content = item[len(num_part):].strip()
                            html_parts.append(f'            <li><strong>{num_part}</strong> {content}</li>')
                        else:
                            html_parts.append(f'            <li>{content}</li>')
                    html_parts.append('        </ul>')
                    list_items = []
                    in_list = False
            
            # Skip if this was already added to intro-box
            if is_intro_section and para in intro_paragraphs_collected:
                continue
            
            # Skip if this was already added to intro-box
            if is_intro_section and para in intro_paragraphs_collected:
                continue
            
            # Detect "What Makes This Plan Different" section - use card-grid
            if 'What Makes This Plan Different' in stripped:
                # Look ahead for card content
                card_content = []
                idx = paragraphs.index(para)
                for next_para in paragraphs[idx+1:idx+15]:
                    next_stripped = next_para.strip()
                    if 'Built for' in next_stripped and len(next_stripped) < 200:
                        card_content.append(next_para)
                    if len(card_content) >= 3:
                        break
                
                if len(card_content) >= 3:
                    html_parts.append('        <h3>What Makes This Plan Different</h3>')
                    html_parts.append('        <div class="card-grid">')
                    for i, card_para in enumerate(card_content, 1):
                        card_text = card_para.strip()
                        if 'Built for' in card_text:
                            # Extract title and description
                            if '.' in card_text:
                                parts = card_text.split('.', 1)
                                title = parts[0].replace('Built for', '').strip()
                                desc = parts[1].strip() if len(parts) > 1 else ''
                            else:
                                title = card_text.replace('Built for', '').strip()
                                desc = ''
                            
                            # Get description from next paragraph if available
                            if not desc and i < len(card_content):
                                next_idx = paragraphs.index(card_para) + 1
                                if next_idx < len(paragraphs):
                                    next_text = paragraphs[next_idx].strip()
                                    if next_text and not next_text.startswith('Built for'):
                                        desc = next_text
                            
                            html_parts.append('            <div class="card">')
                            html_parts.append(f'                <div class="card-number">{i}</div>')
                            html_parts.append(f'                <h4>Built for {title}</h4>')
                            if desc:
                                html_parts.append(f'                <p>{desc}</p>')
                            html_parts.append('            </div>')
                    html_parts.append('        </div>')
                    # Mark these paragraphs as processed
                    processed_paragraphs = set(card_content)
                    continue
            
            # Detect "12 Weeks, 4 Phases" - use phase-list
            if '12 Weeks, 4 Phases' in stripped:
                phase_items = []
                idx = paragraphs.index(para)
                for next_para in paragraphs[idx+1:idx+10]:
                    next_stripped = next_para.strip()
                    if re.search(r'Weeks \d+-\d+:', next_stripped):
                        phase_items.append(next_para)
                    if len(phase_items) >= 4:
                        break
                
                if len(phase_items) >= 4:
                    html_parts.append('        <h3>12 Weeks, 4 Phases</h3>')
                    html_parts.append('        <div class="phase-list">')
                    phase_classes = ['phase-base', 'phase-build', 'phase-peak', 'phase-taper']
                    phase_names = ['BASE', 'BUILD', 'PEAK', 'TAPER']
                    for i, phase_para in enumerate(phase_items[:4]):
                        phase_text = phase_para.strip()
                        # Extract weeks and description
                        weeks_match = re.search(r'Weeks (\d+-\d+)', phase_text)
                        weeks = weeks_match.group(1) if weeks_match else ''
                        # Extract description after em dash or colon
                        desc_match = re.search(r'[—:] (.+)$', phase_text)
                        desc = desc_match.group(1).strip() if desc_match else phase_text.split('—', 1)[-1].strip() if '—' in phase_text else phase_text.split(':', 1)[-1].strip() if ':' in phase_text else ''
                        
                        html_parts.append(f'            <div class="phase-item {phase_classes[i]}">')
                        html_parts.append(f'                <span class="phase-weeks">Weeks {weeks}</span>')
                        html_parts.append(f'                <span class="phase-name">{phase_names[i]}</span>')
                        html_parts.append(f'                <span class="phase-desc">{desc}</span>')
                        html_parts.append('            </div>')
                    html_parts.append('        </div>')
                    # Mark as processed
                    processed_paragraphs.update(phase_items[:4])
                    continue
            
            # Detect callout boxes (warning, danger, info, success patterns)
            callout_type = None
            if '⚠️' in stripped or 'Important' in stripped or 'WARNING' in stripped.upper() or 'DANGER' in stripped.upper():
                callout_type = 'warning'
            elif 'CYCLING IS DANGEROUS' in stripped.upper() or 'danger' in stripped.lower():
                callout_type = 'danger'
            elif 'INFO' in stripped.upper() or 'NOTE' in stripped.upper() or 'TIP' in stripped.upper():
                callout_type = 'info'
            elif 'SUCCESS' in stripped.upper() or '✓' in stripped:
                callout_type = 'success'
            
            if callout_type:
                # Collect callout content
                callout_title = stripped.replace('⚠️', '').replace('Important:', '').replace('WARNING:', '').strip()
                callout_content = []
                idx = paragraphs.index(para)
                for next_para in paragraphs[idx+1:idx+5]:
                    next_stripped = next_para.strip()
                    if next_stripped and not next_stripped.startswith('-') and not next_stripped.startswith('•'):
                        callout_content.append(next_para)
                    if len(callout_content) >= 2:
                        break
                
                html_parts.append(f'        <div class="callout callout-{callout_type}">')
                if callout_title:
                    html_parts.append(f'            <div class="callout-title">{callout_title}</div>')
                for callout_para in callout_content:
                    formatted = format_paragraph(callout_para)
                    if formatted and '<p>' in formatted:
                        html_parts.append('        ' + formatted.replace('<p>', '<p>').replace('</p>', '</p>'))
                html_parts.append('        </div>')
                processed_paragraphs.update([para] + callout_content)
                continue
            
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
</script>

</body>
</html>''')
    
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


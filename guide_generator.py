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
    
    # Calculate altitude power loss if elevation > 5000
    elevation = race_data.get('race', {}).get('vitals', {}).get('elevation_ft', 0)
    if elevation > 5000:
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
    """Generate SVG phase bars"""
    return '''<svg width="100%" height="60" style="margin: 20px 0;">
        <rect x="0" y="0" width="25%" height="60" fill="#4ECDC4" />
        <text x="12.5%" y="35" text-anchor="middle" fill="white" font-weight="bold">BASE</text>
        <rect x="25%" y="0" width="33%" height="60" fill="#40E0D0" />
        <text x="41.5%" y="35" text-anchor="middle" fill="white" font-weight="bold">BUILD</text>
        <rect x="58%" y="0" width="25%" height="60" fill="#59473C" />
        <text x="70.5%" y="35" text-anchor="middle" fill="#F5F5DC" font-weight="bold">PEAK</text>
        <rect x="83%" y="0" width="17%" height="60" fill="#F4D03F" />
        <text x="91.5%" y="35" text-anchor="middle" fill="#2c2c2c" font-weight="bold">TAPER</text>
    </svg>'''

def generate_svg_radar_chart(race_data: Dict[str, Any]) -> str:
    """Generate SVG radar chart from race data"""
    scores = race_data.get('race', {}).get('radar_scores', {})
    # Default scores if not provided
    elevation = scores.get('elevation', {}).get('score', 3)
    length = scores.get('length', {}).get('score', 5)
    technicality = scores.get('technicality', {}).get('score', 2)
    climate = scores.get('climate', {}).get('score', 5)
    altitude = scores.get('altitude', {}).get('score', 2)
    adventure = scores.get('adventure', {}).get('score', 3)
    
    # Simple radar visualization as table for now
    return f'''<table class="zone-table" style="margin: 20px 0;">
        <tr><th>Factor</th><th>Score</th><th>What It Means</th></tr>
        <tr><td><strong>Elevation</strong></td><td style="font-family: monospace; color: #40E0D0;">{"●" * elevation}{"○" * (5-elevation)}</td><td>Cumulative elevation challenge</td></tr>
        <tr><td><strong>Length</strong></td><td style="font-family: monospace; color: #40E0D0;">{"●" * length}{"○" * (5-length)}</td><td>Distance demands</td></tr>
        <tr><td><strong>Technicality</strong></td><td style="font-family: monospace; color: #40E0D0;">{"●" * technicality}{"○" * (5-technicality)}</td><td>Bike handling requirements</td></tr>
        <tr><td><strong>Climate</strong></td><td style="font-family: monospace; color: #40E0D0;">{"●" * climate}{"○" * (5-climate)}</td><td>Weather challenges</td></tr>
        <tr><td><strong>Altitude</strong></td><td style="font-family: monospace; color: #40E0D0;">{"●" * altitude}{"○" * (5-altitude)}</td><td>Elevation effects</td></tr>
        <tr><td><strong>Adventure</strong></td><td style="font-family: monospace; color: #40E0D0;">{"●" * adventure}{"○" * (5-adventure)}</td><td>Logistical complexity</td></tr>
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

def generate_html(race_data: Dict[str, Any], output_path: Optional[Path] = None) -> str:
    """Generate full HTML guide from race data"""
    
    # Load template
    template = load_template()
    sections = extract_sections(template)
    
    # Replace variables in template
    processed_template = replace_variables(template, race_data)
    processed_sections = extract_sections(processed_template)
    
    # Build HTML
    html_parts = []
    
    # HTML header with neo-brutalist CSS
    html_parts.append(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{race_data.get('race', {}).get('name', 'Gravel God Training Guide')} - {race_data.get('ability_level', 'Training Guide')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', monospace, 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.7;
            color: {COLORS['text_dark']};
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: {COLORS['cream']};
        }}
        
        h1 {{
            font-family: 'Courier New', monospace;
            font-size: 24pt;
            color: {COLORS['brown_dark']};
            border-bottom: 4px solid {COLORS['turquoise']};
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        
        h2 {{
            font-family: 'Courier New', monospace;
            font-size: 16pt;
            color: {COLORS['brown_dark']};
            margin-top: 30px;
            border-left: 4px solid {COLORS['turquoise']};
            padding-left: 12px;
        }}
        
        h3 {{
            font-size: 13pt;
            color: {COLORS['brown_dark']};
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        .header-box {{
            background: {COLORS['brown_dark']};
            color: {COLORS['cream']};
            padding: 20px;
            text-align: center;
            font-family: 'Courier New', monospace;
            margin: 20px 0;
        }}
        
        .header-box h1 {{
            color: {COLORS['cream']};
            border: none;
            margin: 0;
        }}
        
        .header-box .tagline {{
            color: {COLORS['turquoise']};
            font-size: 14pt;
            margin-top: 10px;
        }}
        
        .callout-box {{
            background: {COLORS['cream']};
            border: 3px solid {COLORS['brown_dark']};
            padding: 15px;
            margin: 20px 0;
            box-shadow: 6px 6px 0 rgba(0,0,0,0.2);
        }}
        
        .callout-turquoise {{
            border-color: {COLORS['turquoise']};
            box-shadow: 6px 6px 0 {COLORS['turquoise']};
        }}
        
        .warning-box {{
            background: #FFF3CD;
            border-left: 4px solid #FFC107;
            padding: 15px;
            margin: 20px 0;
        }}
        
        .zone-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .zone-table th {{
            background: {COLORS['brown_dark']};
            color: {COLORS['cream']};
            padding: 10px;
            text-align: left;
            font-family: 'Courier New', monospace;
        }}
        
        .zone-table td {{
            border: 1px solid #ddd;
            padding: 10px;
        }}
        
        .zone-table tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        
        .zone-table tr:nth-child(odd) {{
            background: white;
        }}
        
        /* G Spot highlighting */
        .zone-table tr:has(td:contains("G Spot")) {{
            background: #E8F5E9 !important;
        }}
        
        p {{
            margin: 15px 0;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .callout-box {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>''')
    
    # Header
    race_name = race_data.get('race', {}).get('name', 'Gravel God Training Guide')
    tagline = race_data.get('race', {}).get('tagline', 'Your Complete Training Resource')
    
    html_parts.append(f'''    <div class="header-box">
        <h1>{race_name}</h1>
        <p class="tagline">{tagline}</p>
        <p class="tagline">{race_data.get('ability_level', 'Training Guide')} | {race_data.get('tier_name', 'Tier')}</p>
    </div>''')
    
    # Process each section
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
    
    for section_key in section_order:
        # Find matching section
        matching_section = None
        for key in processed_sections.keys():
            if section_key in key:
                matching_section = key
                break
        
        if not matching_section:
            continue
        
        # Skip altitude section if elevation < 5000
        if 'ALTITUDE' in matching_section:
            elevation = race_data.get('race', {}).get('vitals', {}).get('elevation_ft', 0)
            if elevation < 5000:
                continue
        
        content = processed_sections[matching_section]
        
        # Format section header
        section_title = matching_section.replace('SECTION ', '').replace(':', '')
        html_parts.append(f'    <h1>{section_title}</h1>')
        
        # Process content - process EVERY line to capture all content
        paragraphs = content.split('\n')
        in_list = False
        list_items = []
        
        for para in paragraphs:
            stripped = para.strip()
            
            # Replace infographic placeholders
            if 'INFOGRAPHIC_PHASE_BARS' in stripped:
                html_parts.append('    ' + generate_svg_phase_bars())
                continue
            elif 'INFOGRAPHIC_RATING_HEX' in stripped:
                html_parts.append('    ' + generate_svg_radar_chart(race_data))
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
                html_parts.append('    ' + formatted)
        
        # Close any remaining list
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


#!/usr/bin/env python3
"""
Complete Gravel God Training Guide Generator
Handles all 14+ sections from JSON data with full content processing
"""
import json
import sys
import math
from pathlib import Path

def calculate_radar_points(values, center_x=200, center_y=160, max_radius=120):
    order = ['elevation', 'length', 'technical', 'climate', 'altitude', 'adventure']
    angles = [270, 330, 30, 90, 150, 210]
    points = []
    for i, key in enumerate(order):
        value = values.get(key, 1)
        radius = max_radius * (value / 5)
        angle_rad = math.radians(angles[i])
        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)
        points.append((round(x), round(y)))
    return points

def generate_radar_svg(radar_data):
    points = calculate_radar_points(radar_data)
    polygon_points = " ".join(f"{x},{y}" for x, y in points)
    circles = "\n                ".join(
        f'<circle cx="{x}" cy="{y}" r="6" fill="#4ecdc4" stroke="#2c2c2c" stroke-width="2"/>'
        for x, y in points
    )
    return f'''            <svg viewBox="0 0 400 350" width="400" height="350">
                <rect x="0" y="0" width="400" height="350" fill="white"/>
                <circle cx="200" cy="160" r="120" fill="none" stroke="#e0e0e0" stroke-width="1"/>
                <circle cx="200" cy="160" r="96" fill="none" stroke="#e0e0e0" stroke-width="1"/>
                <circle cx="200" cy="160" r="72" fill="none" stroke="#e0e0e0" stroke-width="1"/>
                <circle cx="200" cy="160" r="48" fill="none" stroke="#e0e0e0" stroke-width="1"/>
                <circle cx="200" cy="160" r="24" fill="none" stroke="#e0e0e0" stroke-width="1"/>
                <line x1="200" y1="160" x2="200" y2="40" stroke="#ccc" stroke-width="1"/>
                <line x1="200" y1="160" x2="304" y2="100" stroke="#ccc" stroke-width="1"/>
                <line x1="200" y1="160" x2="304" y2="220" stroke="#ccc" stroke-width="1"/>
                <line x1="200" y1="160" x2="200" y2="280" stroke="#ccc" stroke-width="1"/>
                <line x1="200" y1="160" x2="96" y2="220" stroke="#ccc" stroke-width="1"/>
                <line x1="200" y1="160" x2="96" y2="100" stroke="#ccc" stroke-width="1"/>
                <polygon points="{polygon_points}" fill="rgba(78, 205, 196, 0.3)" stroke="#4ecdc4" stroke-width="3"/>
                {circles}
                <text x="200" y="25" text-anchor="middle" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">ELEVATION ({radar_data['elevation']}/5)</text>
                <text x="330" y="95" text-anchor="start" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">LENGTH ({radar_data['length']}/5)</text>
                <text x="330" y="230" text-anchor="start" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">TECHNICAL ({radar_data['technical']}/5)</text>
                <text x="200" y="305" text-anchor="middle" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">CLIMATE ({radar_data['climate']}/5)</text>
                <text x="70" y="230" text-anchor="end" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">ALTITUDE ({radar_data['altitude']}/5)</text>
                <text x="70" y="95" text-anchor="end" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">ADVENTURE ({radar_data['adventure']}/5)</text>
            </svg>'''

def generate_phase_bars(phases):
    bars = []
    x_positions = [50, 175, 300, 425]
    for i, phase in enumerate(phases):
        bars.append(f'''                <rect x="{x_positions[i]}" y="30" width="100" height="50" fill="{phase['color']}" stroke="#2c2c2c" stroke-width="2"/>
                <text x="{x_positions[i] + 50}" y="60" text-anchor="middle" font-family="Sometype Mono, monospace" font-size="14" font-weight="700">{phase['name']}</text>
                <text x="{x_positions[i] + 50}" y="100" text-anchor="middle" font-family="Sometype Mono, monospace" font-size="11">Weeks {phase['weeks']}</text>''')
    return "\n".join(bars)

def format_content(content):
    """Format content that may contain HTML"""
    if isinstance(content, list):
        return "\n".join(format_content(item) for item in content)
    return str(content) if content else ""

def process_content(content_data, meta, radar_svg, phase_bars, parent_key=None):
    """Process any content structure and return HTML - handles all content types"""
    html = ""
    
    if isinstance(content_data, dict):
        # Handle different content types based on keys
        
        # Intro paragraphs (wrapped in intro-box)
        if 'intro_paragraphs' in content_data:
            html += '        <div class="intro-box">\n'
            for para in content_data['intro_paragraphs']:
                html += f'            <p>{format_content(para)}</p>\n'
            html += '        </div>\n'
        
        # Intro (single string or list)
        if 'intro' in content_data:
            if isinstance(content_data['intro'], list):
                for para in content_data['intro']:
                    html += f'        <p>{format_content(para)}</p>\n'
            else:
                html += f'        <p>{format_content(content_data["intro"])}</p>\n'
        
        # Cards grid
        if 'cards' in content_data:
            html += '        <div class="card-grid">\n'
            for card in content_data['cards']:
                html += f'''            <div class="card">
                <h4>{card['title']}</h4>
                <p>{format_content(card['content'])}</p>
            </div>\n'''
            html += '        </div>\n'
        
        # Phases with SVG
        if 'phases' in content_data:
            html += '        <div class="graphic-container">\n'
            html += '            <div class="graphic-title">Training Phases</div>\n'
            html += '            <svg viewBox="0 0 600 120" width="600" height="120">\n'
            html += '                <rect x="0" y="0" width="600" height="120" fill="white"/>\n'
            html += generate_phase_bars(content_data['phases'])
            html += '\n            </svg>\n'
            html += '        </div>\n'
        
        # Phase list (text format)
        if 'phase_list' in content_data:
            html += '        <div class="phase-list">\n'
            phase_map = {"Base Phase": "phase-base", "Build Phase": "phase-build", 
                        "Peak Phase": "phase-peak", "Taper Phase": "phase-taper"}
            for phase in content_data['phase_list']:
                phase_class = phase_map.get(phase.get('name', ''), 'phase-item')
                html += f'''            <div class="phase-item {phase_class}">
                <span class="phase-weeks">{phase.get('weeks', '')}</span>
                <span class="phase-name">{phase.get('name', '').upper()}</span>
                <span class="phase-desc">{phase.get('description', '')}</span>
            </div>\n'''
            html += '        </div>\n'
        
        # Weekly structure table
        if 'weekly_structure' in content_data:
            html += '        <h3>Weekly Structure</h3>\n'
            html += '        <div class="table-wrapper">\n'
            html += '            <table>\n'
            html += '                <thead>\n'
            html += '                    <tr><th>Day</th><th>Session</th><th>Duration</th></tr>\n'
            html += '                </thead>\n'
            html += '                <tbody>\n'
            for day in content_data['weekly_structure']:
                row_class = ' class="g-spot-row"' if day.get('highlight') else ''
                html += f'                    <tr{row_class}>\n'
                html += f'                        <td><strong>{day["day"]}</strong></td>\n'
                html += f'                        <td>{day["session"]}</td>\n'
                html += f'                        <td>{day["duration"]}</td>\n'
                html += '                    </tr>\n'
            html += '                </tbody>\n'
            html += '            </table>\n'
            html += '        </div>\n'
        
        # Warnings/callouts
        if 'warnings' in content_data:
            for warning in content_data['warnings']:
                callout_type = warning.get('type', 'danger')
                html += f'''        <div class="callout callout-{callout_type}">
            <div class="callout-title">{warning['title']}</div>
            <p>{format_content(warning['content'])}</p>
        </div>\n'''
        
        # Health advice (list of paragraphs)
        if 'health_advice' in content_data:
            html += '        <h3>Health & Safety Check</h3>\n'
            for advice in content_data['health_advice']:
                html += f'        <p>{format_content(advice)}</p>\n'
        
        # Safety tips (checklist)
        if 'safety_tips' in content_data:
            html += '        <h3>Safety Guidelines</h3>\n'
            html += '        <ul class="checklist">\n'
            for tip in content_data['safety_tips']:
                html += f'            <li>{format_content(tip)}</li>\n'
            html += '        </ul>\n'
        
        # Non-negotiables (checklist)
        if 'non_negotiables' in content_data:
            html += '        <h3>What You Need to Succeed</h3>\n'
            html += '        <h4>Non-Negotiables:</h4>\n'
            html += '        <ul class="checklist">\n'
            for item in content_data['non_negotiables']:
                html += f'            <li>{item}</li>\n'
            html += '        </ul>\n'
        
        # Equipment mandatory (list with items and reasons)
        if 'equipment_mandatory' in content_data:
            html += '        <h3>Equipment Requirements</h3>\n'
            html += '        <p><strong>Mandatory:</strong></p>\n'
            html += '        <ul>\n'
            for item in content_data['equipment_mandatory']:
                html += f'            <li><strong>{item["item"]}</strong> — {item["reason"]}</li>\n'
            html += '        </ul>\n'
        
        # FTP Testing
        if 'ftp_testing' in content_data:
            ftp = content_data['ftp_testing']
            html += '        <h3>FTP Testing</h3>\n'
            if 'when_to_test' in ftp:
                html += '        <h4>When to test:</h4>\n'
                html += '        <ul>\n'
                for item in ftp['when_to_test']:
                    html += f'            <li>{format_content(item)}</li>\n'
                html += '        </ul>\n'
            if 'twenty_min_protocol' in ftp:
                html += '        <h4>How to test (20-Minute Test):</h4>\n'
                html += '        <ol>\n'
                for step in ftp['twenty_min_protocol']:
                    html += f'            <li>{format_content(step)}</li>\n'
                html += '        </ol>\n'
            if 'formula' in ftp:
                html += f'        <p><strong>Formula:</strong> {ftp["formula"]}</p>\n'
            if 'execute_callout' in ftp:
                execute = ftp['execute_callout']
                html += f'''        <div class="callout callout-info">
            <div class="callout-title">{execute['title']}</div>
            <p>{format_content(execute['content'])}</p>
        </div>\n'''
        
        # Adaptation steps
        if 'adaptation_steps' in content_data:
            html += '        <h3>The Foundational Model: How Adaptation Works</h3>\n'
            for i, step in enumerate(content_data['adaptation_steps'], 1):
                html += f'        <h4>Step {i}: {step["name"]}</h4>\n'
                html += f'        <p>{format_content(step["description"])}</p>\n'
        
        # Where it goes wrong
        if 'where_it_goes_wrong' in content_data:
            html += '        <h3>Where It Goes Wrong</h3>\n'
            for item in content_data['where_it_goes_wrong']:
                callout_type = item.get('type', 'warning')
                html += f'''        <div class="callout callout-{callout_type}">
            <div class="callout-title">{item['title']}</div>
            <p>{format_content(item['content'])}</p>
        </div>\n'''
        
        # Practical rules (list)
        if 'practical_rules' in content_data:
            html += '        <h3>The Practical Rules</h3>\n'
            html += '        <ul>\n'
            for rule in content_data['practical_rules']:
                html += f'            <li>{format_content(rule)}</li>\n'
            html += '        </ul>\n'
        
        # Phase details
        if 'phase_details' in content_data:
            html += '        <h3>Understanding the Phases</h3>\n'
            for phase in content_data['phase_details']:
                html += f'        <h4>{phase.get("phase", "")}</h4>\n'
                if 'goal' in phase:
                    html += f'        <p><strong>Goal:</strong> {phase["goal"]}</p>\n'
                if 'what_youre_doing' in phase:
                    html += f'        <p><strong>What you\'re doing:</strong> {phase["what_youre_doing"]}</p>\n'
                if 'why' in phase:
                    html += f'        <p><strong>Why:</strong> {phase["why"]}</p>\n'
                if 'how_it_feels' in phase:
                    html += f'        <p><strong>How it feels:</strong> {phase["how_it_feels"]}</p>\n'
                if 'content' in phase:
                    html += f'        <p>{format_content(phase["content"])}</p>\n'
        
        # Point of zones (list of paragraphs)
        if 'point_of_zones' in content_data:
            html += '        <h3>The Point of Zones</h3>\n'
            for para in content_data['point_of_zones']:
                html += f'        <p>{format_content(para)}</p>\n'
        
        # Measurement systems
        if 'measurement_systems' in content_data:
            html += '        <h3>The Three Measurement Systems</h3>\n'
            for system in content_data['measurement_systems']:
                html += f'        <h4>{system["name"]}</h4>\n'
                html += f'        <p>{format_content(system["description"])}</p>\n'
        
        # Zone table
        if 'zone_table' in content_data:
            html += '        <h3>The Zone Chart</h3>\n'
            html += '        <div class="table-wrapper">\n'
            html += '            <table>\n'
            html += '                <thead>\n'
            html += '                    <tr><th>Zone</th><th>Name</th><th>% FTP</th><th>% HRmax</th><th>RPE</th><th>Feel</th></tr>\n'
            html += '                </thead>\n'
            html += '                <tbody>\n'
            for zone in content_data['zone_table']:
                row_class = ' class="g-spot-row"' if zone.get('highlight') else ''
                html += f'                    <tr{row_class}>\n'
                html += f'                        <td><strong>{zone["zone"]}</strong></td>\n'
                html += f'                        <td>{zone["name"]}</td>\n'
                html += f'                        <td>{zone["ftp"]}</td>\n'
                html += f'                        <td>{zone["hrmax"]}</td>\n'
                html += f'                        <td>{zone["rpe"]}</td>\n'
                html += f'                        <td>{zone["feel"]}</td>\n'
                html += '                    </tr>\n'
            html += '                </tbody>\n'
            html += '            </table>\n'
            html += '        </div>\n'
        
        # G Spot callout
        if 'g_spot_callout' in content_data:
            callout = content_data['g_spot_callout']
            html += f'''        <div class="callout callout-info">
            <div class="callout-title">{callout['title']}</div>
            <p>{format_content(callout['content'])}</p>
        </div>\n'''
        
        # Common mistake callout
        if 'common_mistake_callout' in content_data:
            callout = content_data['common_mistake_callout']
            html += f'''        <div class="callout callout-warning">
            <div class="callout-title">{callout['title']}</div>
            <p>{format_content(callout['content'])}</p>
        </div>\n'''
        
        # Critical notes (list)
        if 'critical_notes' in content_data:
            html += '        <h3>Critical Notes on Using Zones</h3>\n'
            html += '        <ul>\n'
            for note in content_data['critical_notes']:
                html += f'            <li>{format_content(note)}</li>\n'
            html += '        </ul>\n'
        
        # Bottom line
        if 'bottom_line' in content_data:
            html += f'        <p><strong>The Bottom Line:</strong> {format_content(content_data["bottom_line"])}</p>\n'
        
        # Execution gap
        if 'execution_gap' in content_data:
            gap = content_data['execution_gap']
            html += '        <h3>The Execution Gap</h3>\n'
            html += f'        <p><strong>The plan says:</strong> {gap.get("plan_says", "")}</p>\n'
            html += '        <p><strong>What actually happens:</strong></p>\n'
            html += '        <ul>\n'
            for item in gap.get('what_happens', []):
                html += f'            <li>{item}</li>\n'
            html += '        </ul>\n'
            html += f'        <p><strong>Result:</strong> {gap.get("result", "")}</p>\n'
        
        # Universal rules
        if 'universal_rules' in content_data:
            html += '        <h3>Universal Execution Rules</h3>\n'
            for rule in content_data['universal_rules']:
                html += f'        <h4>{rule["rule"]}</h4>\n'
                html += f'        <p>{format_content(rule["details"])}</p>\n'
        
        # Zone execution
        if 'zone_execution' in content_data:
            html += '        <h3>Zone-Specific Execution</h3>\n'
            for zone_exec in content_data['zone_execution']:
                html += f'        <h4>{zone_exec["zone"]}</h4>\n'
                html += f'        <p><strong>Target:</strong> {zone_exec.get("target", "")}</p>\n'
                if 'how_to' in zone_exec:
                    html += '        <p><strong>How to:</strong></p>\n'
                    html += '        <ul>\n'
                    for item in zone_exec['how_to']:
                        html += f'            <li>{format_content(item)}</li>\n'
                    html += '        </ul>\n'
                if 'mistakes' in zone_exec:
                    html += f'        <p><strong>Common mistakes:</strong> {zone_exec["mistakes"]}</p>\n'
                if 'fix' in zone_exec:
                    html += f'        <p><strong>Fix:</strong> {zone_exec["fix"]}</p>\n'
        
        # Indoor vs outdoor
        if 'indoor_vs_outdoor' in content_data:
            io = content_data['indoor_vs_outdoor']
            html += '        <h3>Indoor vs Outdoor Workouts</h3>\n'
            html += '        <h4>Best done indoors:</h4>\n'
            html += '        <ul>\n'
            for item in io.get('indoor', []):
                html += f'            <li>{item}</li>\n'
            html += '        </ul>\n'
            html += '        <h4>Best done outdoors:</h4>\n'
            html += '        <ul>\n'
            for item in io.get('outdoor', []):
                html += f'            <li>{item}</li>\n'
            html += '        </ul>\n'
            if 'balance' in io:
                html += f'        <p><strong>Balance:</strong> {io["balance"]}</p>\n'
        
        # Modification rules
        if 'modification_rules' in content_data:
            mod = content_data['modification_rules']
            html += '        <h3>When and How to Modify Workouts</h3>\n'
            if 'when_appropriate' in mod:
                html += '        <h4>When modification is appropriate:</h4>\n'
                html += '        <ul>\n'
                for item in mod['when_appropriate']:
                    html += f'            <li>{format_content(item)}</li>\n'
                html += '        </ul>\n'
            if 'how_to_modify' in mod:
                html += '        <h4>How to modify:</h4>\n'
                html += '        <ul>\n'
                for item in mod['how_to_modify']:
                    html += f'            <li>{format_content(item)}</li>\n'
                html += '        </ul>\n'
            if 'missed_workouts_rule' in mod:
                html += f'        <p><strong>{mod["missed_workouts_rule"]}</strong></p>\n'
        
        # Recovery protocol
        if 'protocol' in content_data:
            html += '        <h3>Recovery Protocol</h3>\n'
            for step in content_data['protocol']:
                html += f'        <h4>{step["timing"]}</h4>\n'
                html += '        <ul>\n'
                for action in step.get('actions', []):
                    html += f'            <li>{format_content(action)}</li>\n'
                html += '        </ul>\n'
        
        # HRV section
        if 'hrv' in content_data:
            hrv = content_data['hrv']
            html += '        <h3>HRV: What It Is, What It Isn\'t, and How to Use It</h3>\n'
            if 'what_it_measures' in hrv:
                html += f'        <p>{hrv["what_it_measures"]}</p>\n'
            if 'good_for' in hrv:
                html += '        <h4>What HRV Is Good For</h4>\n'
                html += '        <ul>\n'
                for item in hrv['good_for']:
                    html += f'            <li>{format_content(item)}</li>\n'
                html += '        </ul>\n'
            if 'not_good_for' in hrv:
                html += '        <h4>What HRV Is NOT Good For</h4>\n'
                html += '        <ul>\n'
                for item in hrv['not_good_for']:
                    html += f'            <li>{format_content(item)}</li>\n'
                html += '        </ul>\n'
            if 'how_to_use' in hrv:
                html += '        <h4>How to Actually Use HRV</h4>\n'
                html += '        <ul>\n'
                for item in hrv['how_to_use']:
                    html += f'            <li>{format_content(item)}</li>\n'
                html += '        </ul>\n'
            if 'apps' in hrv:
                html += f'        <p><strong>Recommended apps:</strong> {hrv["apps"]}</p>\n'
        
        # Performance benefits
        if 'performance_benefits' in content_data:
            html += '        <h3>The Performance Benefits</h3>\n'
            html += '        <ul>\n'
            for benefit in content_data['performance_benefits']:
                html += f'            <li>{format_content(benefit)}</li>\n'
            html += '        </ul>\n'
        
        # Injury benefits
        if 'injury_benefits' in content_data:
            html += '        <h3>The Injury Prevention Benefits</h3>\n'
            html += '        <ul>\n'
            for benefit in content_data['injury_benefits']:
                html += f'            <li>{format_content(benefit)}</li>\n'
            html += '        </ul>\n'
        
        # Policy
        if 'policy' in content_data:
            policy = content_data['policy']
            html += '        <h3>Here\'s My Policy</h3>\n'
            if 'mobility' in policy:
                html += f'        <p><strong>Mobility and stability work:</strong> {policy["mobility"]}</p>\n'
            if 'full_strength' in policy:
                html += f'        <p><strong>Full periodized strength training:</strong> {policy["full_strength"]}</p>\n'
        
        # What to actually do
        if 'what_to_actually_do' in content_data:
            wtd = content_data['what_to_actually_do']
            html += '        <h3>What To Actually Do</h3>\n'
            if 'with_habit' in wtd:
                html += f'        <h4>{wtd["with_habit"]["title"]}</h4>\n'
                for item in wtd['with_habit'].get('content', []):
                    html += f'        <p>{format_content(item)}</p>\n'
            if 'without_habit' in wtd:
                html += f'        <h4>{wtd["without_habit"]["title"]}</h4>\n'
                if 'intro' in wtd['without_habit']:
                    html += f'        <p>{format_content(wtd["without_habit"]["intro"])}</p>\n'
                html += '        <ul>\n'
                for item in wtd['without_habit'].get('items', []):
                    html += f'            <li>{format_content(item)}</li>\n'
                html += '        </ul>\n'
            if 'bottom_line' in wtd:
                html += '        <h4>The Bottom Line</h4>\n'
                for item in wtd['bottom_line']:
                    html += f'        <p>{format_content(item)}</p>\n'
        
        # Important callout
        if 'important_callout' in content_data:
            html += f'''        <div class="callout callout-warning">
            <div class="callout-title">Important</div>
            <p>{format_content(content_data["important_callout"])}</p>
        </div>\n'''
        
        # Skills list
        if 'skills_list' in content_data:
            html += '        <div class="skills-grid">\n'
            for i, skill in enumerate(content_data['skills_list'], 1):
                html += f'''            <div class="skill-item">
                <h4>Skill {i}: {skill['name']}</h4>
                <p><strong>Why:</strong> {skill.get('why', '')}</p>
                <p><strong>Technique:</strong> {format_content(skill.get('technique', ''))}</p>
                <p><strong>Practice:</strong> {skill.get('practice', '')}</p>
                <p><strong>Cue:</strong> {skill.get('cue', '')}</p>
            </div>\n'''
            html += '        </div>\n'
        
        # Practice callout
        if 'practice_callout' in content_data:
            callout = content_data['practice_callout']
            html += f'''        <div class="callout callout-success">
            <div class="callout-title">{callout['title']}</div>
            <p>{format_content(callout['content'])}</p>
        </div>\n'''
        
        # Race specific callout
        if 'race_specific_callout' in content_data:
            callout = content_data['race_specific_callout']
            html += f'''        <div class="callout callout-info">
            <div class="callout-title">{callout['title']}</div>
            <p>{format_content(callout['content'])}</p>
        </div>\n'''
        
        # Quick reference (fueling table)
        if 'quick_reference' in content_data:
            html += '        <h3>Quick Reference: Fueling Guidelines</h3>\n'
            html += '        <div class="table-wrapper">\n'
            html += '            <table>\n'
            html += '                <thead>\n'
            html += '                    <tr><th>Scenario</th><th>Carbs</th><th>Fluids</th><th>Notes</th></tr>\n'
            html += '                </thead>\n'
            html += '                <tbody>\n'
            for ref in content_data['quick_reference']:
                row_class = ' class="g-spot-row"' if ref.get('highlight') else ''
                html += f'                    <tr{row_class}>\n'
                html += f'                        <td><strong>{ref["scenario"]}</strong></td>\n'
                html += f'                        <td>{ref["carbs"]}</td>\n'
                html += f'                        <td>{ref["fluids"]}</td>\n'
                html += f'                        <td>{ref.get("notes", "")}</td>\n'
                html += '                    </tr>\n'
            html += '                </tbody>\n'
            html += '            </table>\n'
            html += '        </div>\n'
        
        # Hydration
        if 'hydration' in content_data:
            hyd = content_data['hydration']
            html += '        <h3>Understanding Hydration</h3>\n'
            if 'baseline' in hyd:
                html += f'        <p>{hyd["baseline"]}</p>\n'
            if 'sodium' in hyd:
                html += f'        <p>{hyd["sodium"]}</p>\n'
            if 'salty_sweater' in hyd:
                html += f'        <p>{hyd["salty_sweater"]}</p>\n'
            if 'verify_callout' in hyd:
                callout = hyd['verify_callout']
                html += f'''        <div class="callout callout-info">
            <div class="callout-title">{callout['title']}</div>
            <p>{format_content(callout['content'])}</p>
        </div>\n'''
        
        # Gut training
        if 'gut_training' in content_data:
            gut = content_data['gut_training']
            html += '        <h3>Training Your Gut</h3>\n'
            if 'intro' in gut:
                html += f'        <p>{gut["intro"]}</p>\n'
            if 'progression' in gut:
                html += '        <h4>Progression:</h4>\n'
                html += '        <ul>\n'
                for item in gut['progression']:
                    html += f'            <li>{item}</li>\n'
                html += '        </ul>\n'
            if 'tip' in gut:
                html += f'        <p><strong>Tip:</strong> {gut["tip"]}</p>\n'
        
        # Solution callout
        if 'solution_callout' in content_data:
            callout = content_data['solution_callout']
            html += f'''        <div class="callout callout-success">
            <div class="callout-title">{callout['title']}</div>
            <p>{format_content(callout['content'])}</p>
        </div>\n'''
        
        # Reality check
        if 'reality_check' in content_data:
            html += f'        <p><strong>Reality check:</strong> {format_content(content_data["reality_check"])}</p>\n'
        
        # Breathing 6-2-7
        if 'breathing_627' in content_data:
            breath = content_data['breathing_627']
            html += '        <h3>The 6-2-7 Breathing Technique</h3>\n'
            html += f'        <p><strong>Pattern:</strong> {breath["pattern"]}</p>\n'
            html += f'        <p><strong>Key:</strong> {breath["key"]}</p>\n'
            html += '        <h4>When to use:</h4>\n'
            html += '        <ul>\n'
            for item in breath.get('when_to_use', []):
                html += f'            <li>{format_content(item)}</li>\n'
            html += '        </ul>\n'
            html += f'        <p><strong>Practice:</strong> {breath.get("practice", "")}</p>\n'
        
        # Performance statements
        if 'performance_statements' in content_data:
            ps = content_data['performance_statements']
            html += '        <h3>Performance Statements</h3>\n'
            if 'intro' in ps:
                html += f'        <p>{ps["intro"]}</p>\n'
            if 'types' in ps:
                html += '        <h4>Three types:</h4>\n'
                html += '        <ul>\n'
                for item in ps['types']:
                    html += f'            <li>{format_content(item)}</li>\n'
                html += '        </ul>\n'
            if 'callout' in ps:
                html += f'        <p><strong>{ps["callout"]}</strong></p>\n'
        
        # Highlight reel
        if 'highlight_reel' in content_data:
            hr = content_data['highlight_reel']
            html += '        <h3>Personal Highlight Reel</h3>\n'
            if 'intro' in hr:
                html += f'        <p>{hr["intro"]}</p>\n'
            if 'scenes' in hr:
                html += '        <h4>Build your reel with these scenes:</h4>\n'
                html += '        <ul>\n'
                for scene in hr['scenes']:
                    html += f'            <li>{format_content(scene)}</li>\n'
                html += '        </ul>\n'
            if 'when_to_use' in hr:
                html += '        <h4>When to use:</h4>\n'
                html += '        <ul>\n'
                for item in hr['when_to_use']:
                    html += f'            <li>{format_content(item)}</li>\n'
                html += '        </ul>\n'
        
        # Race day checklist
        if 'race_day_checklist' in content_data:
            html += '        <h3>Race Day Mental Checklist</h3>\n'
            html += '        <ul class="checklist">\n'
            for item in content_data['race_day_checklist']:
                html += f'            <li>{format_content(item)}</li>\n'
            html += '        </ul>\n'
        
        # Three acts
        if 'three_acts' in content_data:
            html += '        <h3>The Three-Act Structure</h3>\n'
            html += '        <p>Every long gravel race follows a predictable three-act structure.</p>\n'
            html += '        <div class="table-wrapper">\n'
            html += '            <table>\n'
            html += '                <thead>\n'
            html += '                    <tr><th>Phase</th><th>When</th><th>What\'s Happening</th><th>Your Job</th></tr>\n'
            html += '                </thead>\n'
            html += '                <tbody>\n'
            for act in content_data['three_acts']:
                row_class = ' class="g-spot-row"' if act.get('highlight') else ''
                html += f'                    <tr{row_class}>\n'
                html += f'                        <td><strong>{act["name"]}</strong></td>\n'
                html += f'                        <td>{act["when"]}</td>\n'
                html += f'                        <td>{act["whats_happening"]}</td>\n'
                html += f'                        <td>{format_content(act["your_job"])}</td>\n'
                html += '                    </tr>\n'
            html += '                </tbody>\n'
            html += '            </table>\n'
            html += '        </div>\n'
        
        # Phase details (race tactics)
        if 'phase_details' in content_data and parent_key == 'race_tactics':
            html += '        <h3>Phase Details</h3>\n'
            for phase in content_data['phase_details']:
                html += f'        <h4>{phase["phase"]}</h4>\n'
                html += f'        <p>{format_content(phase["content"])}</p>\n'
        
        # Tactical principles
        if 'tactical_principles' in content_data:
            html += '        <h3>Tactical Principles</h3>\n'
            for principle in content_data['tactical_principles']:
                html += f'        <h4>{principle["name"]}</h4>\n'
                html += f'        <p>{format_content(principle["content"])}</p>\n'
        
        # Key question
        if 'key_question' in content_data:
            html += '        <h4>Be Efficient</h4>\n'
            html += '        <p>Keep asking yourself this question:</p>\n'
            html += f'''        <div class="callout callout-success">
            <div class="callout-title">The Key Question</div>
            <p style="font-size: 1.2rem; font-weight: 700;">"{content_data['key_question']}"</p>
        </div>\n'''
        
        # Efficiency explanation
        if 'efficiency_explanation' in content_data:
            html += f'        <p>{format_content(content_data["efficiency_explanation"])}</p>\n'
        
        # Efficiency tips
        if 'efficiency_tips' in content_data:
            for tip in content_data['efficiency_tips']:
                html += f'        <h4>{tip["name"]}</h4>\n'
                html += f'        <p>{format_content(tip["content"])}</p>\n'
        
        # Race specific callout (race tactics)
        if 'race_specific_callout' in content_data and parent_key == 'race_tactics':
            html += f'''        <div class="callout callout-info">
            <div class="callout-title">Race-Specific Notes</div>
            <p>{format_content(content_data["race_specific_callout"])}</p>
        </div>\n'''
        
        # Aid station
        if 'aid_station' in content_data:
            html += f'        <p><strong>Aid Station Strategy:</strong> {format_content(content_data["aid_station"])}</p>\n'
        
        # Non-negotiables (race tactics) - special handling for table format
        if 'non_negotiables' in content_data and parent_key == 'race_tactics':
            # Check if it's a list of dicts (race tactics format) or strings (before_you_start format)
            if content_data['non_negotiables'] and isinstance(content_data['non_negotiables'][0], dict):
                html += '        <h3>The Non-Negotiables</h3>\n'
                html += '        <p>These are the requirements that determine whether you finish strong, finish barely, or don\'t finish at all.</p>\n'
                html += '        <div class="table-wrapper">\n'
                html += '            <table>\n'
                html += '                <thead>\n'
                html += '                    <tr><th>Requirement</th><th>By When</th><th>Why It Matters</th></tr>\n'
                html += '                </thead>\n'
                html += '                <tbody>\n'
                for req in content_data['non_negotiables']:
                    html += '                    <tr>\n'
                    html += f'                        <td>{req.get("requirement", "")}</td>\n'
                    html += f'                        <td>{req.get("by_when", "")}</td>\n'
                    html += f'                        <td>{req.get("why", "")}</td>\n'
                    html += '                    </tr>\n'
                html += '                </tbody>\n'
                html += '            </table>\n'
                html += '        </div>\n'
        
        # Weather
        if 'weather' in content_data:
            html += f'        <h3>Weather Strategy</h3>\n'
            html += f'        <p>{format_content(content_data["weather"])}</p>\n'
        
        # Race week
        if 'race_week' in content_data:
            html += '        <h3>The 7-Day Countdown</h3>\n'
            html += '        <div class="table-wrapper">\n'
            html += '            <table>\n'
            html += '                <thead>\n'
            html += '                    <tr><th>Day</th><th>Training</th><th>Focus</th></tr>\n'
            html += '                </thead>\n'
            html += '                <tbody>\n'
            for day in content_data['race_week']:
                html += '                    <tr>\n'
                html += f'                        <td><strong>{day["day"]}</strong></td>\n'
                html += f'                        <td>{day["training"]}</td>\n'
                html += f'                        <td>{day["focus"]}</td>\n'
                html += '                    </tr>\n'
            html += '                </tbody>\n'
            html += '            </table>\n'
            html += '        </div>\n'
        
        # Race morning
        if 'race_morning' in content_data:
            html += '        <h3>Race Morning Timeline</h3>\n'
            html += '        <ul class="checklist">\n'
            for item in content_data['race_morning']:
                html += f'            <li>{format_content(item)}</li>\n'
            html += '        </ul>\n'
        
        # Race week bottom line
        if 'race_week_bottom_line' in content_data:
            bottom = content_data['race_week_bottom_line']
            html += f'''        <div class="callout callout-info">
            <div class="callout-title">{bottom['title']}</div>
            <p>{format_content(bottom['content'])}</p>
        </div>\n'''
        
        # Counterintuitive truth (tires)
        if 'counterintuitive_truth' in content_data:
            truth = content_data['counterintuitive_truth']
            html += f'        <h3>{truth["headline"]}</h3>\n'
            html += f'        <p>{format_content(truth["content"])}</p>\n'
            if 'prediction' in truth:
                html += f'        <p><strong>Prediction:</strong> {truth["prediction"]}</p>\n'
        
        # Why wider faster
        if 'why_wider_faster' in content_data:
            html += '        <h3>Why Wider Tires Are Faster on Gravel</h3>\n'
            for reason in content_data['why_wider_faster']:
                html += f'        <h4>{reason["reason"]}</h4>\n'
                html += f'        <p>{format_content(reason["explanation"])}</p>\n'
        
        # Weight myth
        if 'weight_myth' in content_data:
            myth = content_data['weight_myth']
            html += f'        <h3>{myth["title"]}</h3>\n'
            html += f'        <p>{format_content(myth["content"])}</p>\n'
        
        # Factors that matter
        if 'factors_that_matter' in content_data:
            html += '        <h3>The Factors That Actually Matter</h3>\n'
            for factor in content_data['factors_that_matter']:
                html += f'        <h4>{factor["factor"]}</h4>\n'
                html += f'        <p>{format_content(factor["explanation"])}</p>\n'
        
        # What doesn't matter
        if 'what_doesnt_matter' in content_data:
            html += '        <h3>What Doesn\'t Matter (Much)</h3>\n'
            html += '        <ul>\n'
            for item in content_data['what_doesnt_matter']:
                html += f'            <li>{format_content(item)}</li>\n'
            html += '        </ul>\n'
        
        # Width guide
        if 'width_guide' in content_data:
            html += '        <h3>Width Selection Guide</h3>\n'
            html += '        <div class="table-wrapper">\n'
            html += '            <table>\n'
            html += '                <thead>\n'
            html += '                    <tr><th>Width</th><th>Best For</th><th>Pros</th><th>Cons</th></tr>\n'
            html += '                </thead>\n'
            html += '                <tbody>\n'
            for width in content_data['width_guide']:
                row_class = ' class="g-spot-row"' if width.get('highlight') else ''
                html += f'                    <tr{row_class}>\n'
                html += f'                        <td><strong>{width["width"]}</strong></td>\n'
                html += f'                        <td>{width["best_for"]}</td>\n'
                html += f'                        <td>{width.get("pros", "")}</td>\n'
                html += f'                        <td>{width.get("cons", "")}</td>\n'
                html += '                    </tr>\n'
            html += '                </tbody>\n'
            html += '            </table>\n'
            html += '        </div>\n'
        
        # Race recommendation
        if 'race_recommendation' in content_data:
            html += f'        <p><strong>For {meta.get("race_name", "this race")}:</strong> {content_data["race_recommendation"]}</p>\n'
        
        # Pressure
        if 'pressure' in content_data:
            press = content_data['pressure']
            html += '        <h3>Pressure Guidelines</h3>\n'
            if 'guidelines' in press:
                html += '        <ul>\n'
                for item in press['guidelines']:
                    html += f'            <li>{format_content(item)}</li>\n'
                html += '        </ul>\n'
            if 'advice' in press:
                html += f'        <p>{press["advice"]}</p>\n'
        
        # Tubeless
        if 'tubeless' in content_data:
            tub = content_data['tubeless']
            html += '        <h3>Tubeless vs Tubes</h3>\n'
            html += f'        <p><strong>Pros:</strong> {tub.get("pros", "")}</p>\n'
            html += f'        <p><strong>Cons:</strong> {tub.get("cons", "")}</p>\n'
            html += f'        <p><strong>Verdict:</strong> {tub.get("verdict", "")}</p>\n'
        
        # Don't switch race week
        if 'dont_switch_race_week' in content_data:
            html += f'''        <div class="callout callout-warning">
            <div class="callout-title">Important</div>
            <p>{format_content(content_data["dont_switch_race_week"])}</p>
        </div>\n'''
        
        # Goal callout
        if 'goal_callout' in content_data:
            callout = content_data['goal_callout']
            html += f'''        <div class="callout callout-info">
            <div class="callout-title">{callout['title']}</div>
            <p>{format_content(callout['content'])}</p>
        </div>\n'''
        
        # Terms (glossary)
        if 'terms' in content_data:
            html += '        <div class="glossary-list">\n'
            for term in content_data['terms']:
                html += f'''            <div class="glossary-item">
                <div class="glossary-term">{term["term"]}</div>
                <div class="glossary-def">{format_content(term["definition"])}</div>
            </div>\n'''
            html += '        </div>\n'
        
        # Key workouts
        if 'key_workouts' in content_data:
            html += '        <h3>Key Workouts in This Plan</h3>\n'
            html += '        <div class="card-grid">\n'
            for workout in content_data['key_workouts']:
                row_class = ' class="g-spot-row"' if workout.get('highlight') else ''
                html += f'''            <div class="card"{row_class}>
                <h4>{workout["name"]}</h4>
                <p>{workout["purpose"]}</p>
            </div>\n'''
            html += '        </div>\n'
        
        # Support
        if 'support' in content_data:
            support = content_data['support']
            html += '        <h3>Support & Resources</h3>\n'
            if 'race_info' in support:
                ri = support['race_info']
                html += f'        <p><strong>{ri["text"]}</strong> <a href="{ri["url"]}">{ri["url"]}</a></p>\n'
            if 'questions' in support:
                q = support['questions']
                html += f'        <p><strong>{q["text"]}</strong> <a href="mailto:{q["email"]}">{q["email"]}</a></p>\n'
        
        # Recovery weeks callout
        if 'recovery_weeks_callout' in content_data:
            callout = content_data['recovery_weeks_callout']
            html += f'''        <div class="callout callout-info">
            <div class="callout-title">{callout['title']}</div>
            <p>{format_content(callout['content'])}</p>
        </div>\n'''
        
        # Compliance note
        if 'compliance_note' in content_data:
            note = content_data['compliance_note']
            html += f'''        <div class="callout callout-info">
            <div class="callout-title">{note['title']}</div>\n'''
            for para in note.get('paragraphs', []):
                html += f'            <p>{format_content(para)}</p>\n'
            html += '        </div>\n'
        
        # Recovery truth
        if 'recovery_truth' in content_data:
            html += f'        <p><strong>{format_content(content_data["recovery_truth"])}</strong></p>\n'
        
        # Math (fueling)
        if 'math' in content_data:
            html += f'        <p>{format_content(content_data["math"])}</p>\n'
        
        # Process any remaining keys as paragraphs
        for key, value in content_data.items():
            if key not in ['intro_paragraphs', 'cards', 'phases', 'weekly_structure', 'warnings', 
                          'health_advice', 'safety_tips', 'non_negotiables', 'equipment_mandatory',
                          'ftp_testing', 'adaptation_steps', 'where_it_goes_wrong', 'practical_rules',
                          'phase_details', 'point_of_zones', 'measurement_systems', 'zone_table',
                          'g_spot_callout', 'common_mistake_callout', 'critical_notes', 'bottom_line',
                          'execution_gap', 'universal_rules', 'zone_execution', 'indoor_vs_outdoor',
                          'modification_rules', 'protocol', 'hrv', 'performance_benefits', 'injury_benefits',
                          'policy', 'what_to_actually_do', 'important_callout', 'skills_list',
                          'practice_callout', 'race_specific_callout', 'quick_reference', 'hydration',
                          'gut_training', 'solution_callout', 'reality_check', 'breathing_627',
                          'performance_statements', 'highlight_reel', 'race_day_checklist', 'three_acts',
                          'tactical_principles', 'key_question', 'efficiency_explanation', 'efficiency_tips',
                          'aid_station', 'weather', 'race_week', 'race_morning', 'race_week_bottom_line',
                          'counterintuitive_truth', 'why_wider_faster', 'weight_myth', 'factors_that_matter',
                          'what_doesnt_matter', 'width_guide', 'race_recommendation', 'pressure',
                          'tubeless', 'dont_switch_race_week', 'goal_callout', 'terms', 'key_workouts',
                          'support', 'recovery_weeks_callout', 'compliance_note', 'recovery_truth', 'math',
                          'intro']:
                if isinstance(value, str) and value.strip():
                    html += f'        <p>{format_content(value)}</p>\n'
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            html += f'        <p>{format_content(item)}</p>\n'
        
    elif isinstance(content_data, list):
        for item in content_data:
            html += process_content(item, meta, radar_svg, phase_bars, parent_key)
    elif isinstance(content_data, str):
        html += f'        <p>{format_content(content_data)}</p>\n'
    
    return html

def generate_section(section_key, section_data, meta, radar_svg, phase_bars):
    """Generate HTML for any section dynamically"""
    number = section_data.get('number', '')
    title = section_data.get('title', '')
    section_id = section_data.get('id', section_key)
    
    html = f'''<!-- SECTION {number}: {title.upper()} -->
<section class="section" id="{section_id}">
    <div class="section-header">
        <span class="section-number">{number}</span>
        <h2>{title}</h2>
    </div>
    <div class="section-content">'''
    
    # Special handling for welcome section - add radar chart
    if section_key == 'welcome' and 'intro_paragraphs' in section_data:
        html += '        <div class="intro-box">\n'
        for para in section_data['intro_paragraphs']:
            html += f'            <p>{format_content(para)}</p>\n'
        html += '        </div>\n'
        html += '        <h3>Race Profile</h3>\n'
        html += '        <div class="graphic-container">\n'
        html += '            <div class="graphic-title">Course Demands</div>\n'
        html += f'{radar_svg}\n'
        html += '        </div>\n'
    
    # Process all content in the section
    for key, value in section_data.items():
        # Skip metadata keys, but process all content keys
        if key not in ['number', 'title', 'id']:
            # For welcome section, skip intro_paragraphs (already handled above)
            if section_key == 'welcome' and key == 'intro_paragraphs':
                continue
            # Pass the value directly, not wrapped in a dict
            if isinstance(value, dict):
                html += process_content(value, meta, radar_svg, phase_bars, section_key)
            elif isinstance(value, list):
                # For lists, check if it's a list of dicts (like cards) or strings
                # Also check if the key itself indicates structured content
                structured_list_keys = ['cards', 'non_negotiables', 'safety_tips', 'warnings', 
                                       'health_advice', 'skills_list', 'terms', 'key_workouts',
                                       'three_acts', 'race_week', 'phase_details', 'zone_table',
                                       'weekly_structure', 'quick_reference', 'width_guide',
                                       'efficiency_tips', 'tactical_principles', 'race_morning',
                                       'non_negotiables']
                if key in structured_list_keys or (value and isinstance(value[0], dict)):
                    # Process as a structured list (cards, non-negotiables, etc.)
                    html += process_content({key: value}, meta, radar_svg, phase_bars, section_key)
                else:
                    # Process each item individually
                    for item in value:
                        html += process_content(item, meta, radar_svg, phase_bars, section_key)
            elif isinstance(value, str):
                html += f'        <p>{format_content(value)}</p>\n'
    
    html += '''
    </div>
</section>'''
    return html

def load_css():
    """Load the complete neo-brutalist CSS"""
    css_file = Path(__file__).parent / 'neo_brutalist_css.txt'
    if css_file.exists():
        return css_file.read_text(encoding='utf-8')
    return "/* CSS not found */"

def generate_html(data):
    meta = data['meta']
    radar_svg = generate_radar_svg(data['radar_chart'])
    sections = data.get('sections', {})
    footer = data['footer']
    css = load_css()
    
    # Build navigation
    nav_items = []
    section_order = ['welcome', 'structure', 'before_you_start', 'how_training_works', 'zones', 
                     'execution', 'recovery', 'strength', 'skills', 'fueling', 'mental', 
                     'race_tactics', 'tires', 'glossary']
    
    nav_map = {
        'welcome': 'Welcome',
        'structure': 'Structure',
        'before_you_start': 'Before',
        'how_training_works': 'Training',
        'zones': 'Zones',
        'execution': 'Execution',
        'recovery': 'Recovery',
        'strength': 'Strength',
        'skills': 'Skills',
        'fueling': 'Fuel',
        'mental': 'Mental',
        'race_tactics': 'Race Day',
        'tires': 'Tires',
        'glossary': 'Glossary'
    }
    
    for key in section_order:
        if key in sections:
            section = sections[key]
            nav_id = section.get('id', key)
            nav_title = nav_map.get(key, section.get('title', '').split()[-1] if section.get('title') else key.replace('_', ' ').title())
            nav_items.append(f'    <a href="#{nav_id}">{nav_title}</a>')
    
    nav_html = '\n'.join(nav_items)
    
    # Generate all sections
    sections_html = []
    phase_bars_data = sections.get('structure', {}).get('phases', [])
    phase_bars_svg = generate_phase_bars(phase_bars_data) if phase_bars_data else ""
    
    for key in section_order:
        if key in sections:
            section_html = generate_section(key, sections[key], meta, radar_svg, phase_bars_svg)
            sections_html.append(section_html)
    
    sections_content = '\n\n'.join(sections_html)
    
    # Location string
    location = f"{meta.get('race_location', '')}"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta['race_name']} Training Guide | {meta['tier']} - {meta['level']}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Sometype+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
{css}
    </style>
</head>
<body>

<nav class="sticky-nav">
{nav_html}
</nav>

<header class="header">
    <div class="race-badge">{location}</div>
    <h1>{meta['race_name']}</h1>
    <p class="header-subtitle">Training Guide</p>
    <div class="tier-badges">
        <span class="tier-badge">{meta['tier']} Tier</span>
        <span class="level-badge">{meta['level']}</span>
    </div>
</header>

<main class="main-content">
{sections_content}
</main>

<footer class="footer">
    <div class="footer-tagline">{footer['tagline']}</div>
    <div class="footer-content">
        <p>{footer['body']}</p>
        <p class="footer-emphasis">{footer['emphasis_1']}</p>
        <p><em>{footer['middle']}</em></p>
        <p>{footer['confidence']}</p>
        <p class="footer-emphasis">{footer['emphasis_2']}</p>
    </div>
    <div class="footer-contact">
        <p class="footer-email">{footer['email']}</p>
        <p class="footer-motto">{footer['motto']}</p>
    </div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function() {{
    const sections = document.querySelectorAll('.section');
    const navLinks = document.querySelectorAll('.sticky-nav a');
    function updateActiveLink() {{
        let current = '';
        const scrollPos = window.scrollY + 100;
        sections.forEach(section => {{
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {{
                current = section.getAttribute('id');
            }}
        }});
        navLinks.forEach(link => {{
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {{
                link.classList.add('active');
            }}
        }});
    }}
    window.addEventListener('scroll', updateActiveLink);
    updateActiveLink();
}});
</script>

</body>
</html>'''
    return html

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_guide_complete.py <input.json> <output.html>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    print(f"Reading data from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Generating HTML...")
    html = generate_html(data)
    
    print(f"Writing output to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Done! Generated {len(html):,} bytes")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Training Guide Generator
Reads the HTML template and substitutes race-specific data.
"""

import json
from pathlib import Path


def load_race_data(race_json_path):
    """Load race data from JSON file"""
    with open(race_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_template():
    """Load the HTML template"""
    # Get path relative to this script's location
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    template_path = repo_root / 'templates' / 'guide_template_full.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_non_negotiables(race_data, index):
    """Extract non-negotiable data, handling both dict and string formats"""
    # Check multiple possible locations for non_negotiables
    non_negs = (race_data.get('non_negotiables', []) or
                race_data.get('race_metadata', {}).get('non_negotiables', []) or
                race_data.get('guide_variables', {}).get('non_negotiables', []))
    if index < len(non_negs):
        nn = non_negs[index]
        if isinstance(nn, dict):
            return {
                'requirement': nn.get('requirement', ''),
                'by_when': nn.get('by_when', ''),
                'why': nn.get('why', '')
            }
        else:
            # String format - use as requirement
            return {
                'requirement': str(nn),
                'by_when': '',
                'why': ''
            }
    # Defaults
    defaults = [
        {'requirement': 'Power meter or heart rate monitor', 'by_when': 'Week 1', 'why': 'Precise power data ensures correct training zones and optimal adaptation'},
        {'requirement': 'Heart rate monitor', 'by_when': 'Week 1', 'why': 'Heart rate provides backup data and helps gauge recovery status'},
        {'requirement': 'Professional bike fit', 'by_when': 'Week 2-3', 'why': 'Proper position prevents injury and maximizes power transfer'},
        {'requirement': 'Consistent training', 'by_when': 'Ongoing', 'why': 'Consistency is the foundation of adaptation - skip weeks, lose gains'},
        {'requirement': 'Follow the plan', 'by_when': 'Ongoing', 'why': 'The plan works if you work it - modifications undermine the system'}
    ]
    return defaults[index] if index < len(defaults) else {'requirement': '', 'by_when': '', 'why': ''}


def generate_guide(race_data, tier_name, ability_level, output_path):
    """
    Generate a training guide for a specific race, tier, and ability level.
    
    Args:
        race_data: Dict containing race information
        tier_name: str - "AYAHUASCA", "FINISHER", "COMPETE", or "PODIUM"
        ability_level: str - "Beginner", "Intermediate", or "Advanced"
        output_path: str - Where to save the generated HTML
    """
    
    # Load template
    template = load_template()
    
    # Helper function to safely extract nested data
    def get_nested(data, *keys, default=None):
        """Safely extract nested dictionary values"""
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                return default
            if data is None:
                return default
        return data if data is not None else default
    
    # Extract race data from nested structure
    race_metadata = race_data.get('race_metadata', {})
    guide_vars = race_data.get('guide_variables', {})
    race_chars = race_data.get('race_characteristics', {})
    
    # Extract elevation gain - check multiple possible locations
    elevation_gain = (race_data.get('elevation_gain_feet') or 
                     race_metadata.get('elevation_feet') or
                     race_data.get('elevation_feet') or 0)
    try:
        elevation_gain = int(elevation_gain) if elevation_gain else 0
        elevation_gain_str = f"~{elevation_gain:,} ft" if elevation_gain else "~11,000 ft"
    except (ValueError, TypeError):
        elevation_gain_str = "~11,000 ft"
    
    # Extract race name
    race_name = (race_data.get('name') or 
                race_metadata.get('name') or 
                guide_vars.get('race_name') or 
                'Race Name')
    
    # Extract distance
    distance = (race_data.get('distance_miles') or 
               race_metadata.get('distance_miles') or 
               'XXX')
    
    # Extract terrain description
    terrain_desc = (race_data.get('terrain_description') or 
                   guide_vars.get('race_terrain') or 
                   'varied terrain')
    
    # Extract description
    description = (race_data.get('description') or 
                  race_data.get('race_hooks', {}).get('detail') or 
                  'Race description here')
    
    # Extract key challenges
    challenges = (race_data.get('key_challenges') or 
                 ', '.join(guide_vars.get('race_challenges', [])) or 
                 'technical terrain, elevation, and endurance')
    
    # Extract duration estimate
    duration = race_data.get('duration_estimate', '10-15 hours')
    
    # Build substitution dictionary
    substitutions = {
        '{{RACE_NAME}}': race_name,
        '{{DISTANCE}}': str(distance),
        '{{TERRAIN_DESCRIPTION}}': terrain_desc,
        '{{ELEVATION_GAIN}}': elevation_gain_str,
        '{{DURATION_ESTIMATE}}': duration,
        '{{RACE_DESCRIPTION}}': description,
        '{{ABILITY_LEVEL}}': ability_level,
        '{{TIER_NAME}}': tier_name,
        '{{WEEKLY_HOURS}}': get_weekly_hours(tier_name),
        '{{plan_weeks}}': '12',  # Default to 12 weeks, can be made dynamic
        '{{RACE_KEY_CHALLENGES}}': challenges,
        '{{WEEKLY_STRUCTURE_DESCRIPTION}}': get_weekly_structure(tier_name),
        '{{RACE_ELEVATION}}': str(elevation_gain),
        '{{RACE_SPECIFIC_SKILL_NOTES}}': (race_data.get('specific_skill_notes') or 
                                          'Practice descending, cornering, and rough terrain handling.'),
        '{{RACE_SPECIFIC_TACTICS}}': (race_data.get('specific_tactics') or 
                                      'Start conservatively. Fuel early and often. Be patient on climbs.'),
        '{{WEATHER_STRATEGY}}': (race_chars.get('typical_weather') or 
                                race_data.get('weather_strategy') or 
                                'Check forecast week of. Pack layers.'),
        '{{AID_STATION_STRATEGY}}': (race_data.get('aid_station_strategy') or 
                                    'Use aid stations for quick refills. Don\'t linger.'),
        '{{ALTITUDE_POWER_LOSS}}': (race_data.get('altitude_power_loss') or 
                                    'Minimal - race is at low elevation'),
        '{{RECOMMENDED_TIRE_WIDTH}}': (race_data.get('recommended_tire_width') or 
                                      '38-42mm'),
        '{{EQUIPMENT_CHECKLIST}}': generate_equipment_checklist(race_data),
        '{{RACE_SUPPORT_URL}}': (race_data.get('website') or 
                                 'https://unboundgravel.com'),
        
        # Infographic placeholders (now all generated as HTML tables/diagrams)
        '{{INFOGRAPHIC_PHASE_BARS}}': '[Phase progression infographic]',  # Could be enhanced later
        '{{INFOGRAPHIC_RATING_HEX}}': generate_rating_hex(race_data),
        '{{INFOGRAPHIC_DIFFICULTY_TABLE}}': generate_difficulty_table(race_data),
        '{{INFOGRAPHIC_FUELING_TABLE}}': generate_fueling_table(race_data),
        '{{INFOGRAPHIC_MENTAL_MAP}}': generate_mental_map(race_data),
        '{{INFOGRAPHIC_THREE_ACTS}}': generate_three_acts(race_data),
        '{{INFOGRAPHIC_INDOOR_OUTDOOR_DECISION}}': generate_indoor_outdoor_decision(race_data),
        '{{INFOGRAPHIC_TIRE_DECISION}}': generate_tire_decision(race_data),
        '{{INFOGRAPHIC_KEY_WORKOUT_SUMMARY}}': generate_key_workout_summary(race_data),
        
        # Non-negotiables (extract from race_data)
        '{{NON_NEG_1_REQUIREMENT}}': extract_non_negotiables(race_data, 0)['requirement'],
        '{{NON_NEG_1_BY_WHEN}}': extract_non_negotiables(race_data, 0)['by_when'],
        '{{NON_NEG_1_WHY}}': extract_non_negotiables(race_data, 0)['why'],
        '{{NON_NEG_2_REQUIREMENT}}': extract_non_negotiables(race_data, 1)['requirement'],
        '{{NON_NEG_2_BY_WHEN}}': extract_non_negotiables(race_data, 1)['by_when'],
        '{{NON_NEG_2_WHY}}': extract_non_negotiables(race_data, 1)['why'],
        '{{NON_NEG_3_REQUIREMENT}}': extract_non_negotiables(race_data, 2)['requirement'],
        '{{NON_NEG_3_BY_WHEN}}': extract_non_negotiables(race_data, 2)['by_when'],
        '{{NON_NEG_3_WHY}}': extract_non_negotiables(race_data, 2)['why'],
        '{{NON_NEG_4_REQUIREMENT}}': extract_non_negotiables(race_data, 3)['requirement'],
        '{{NON_NEG_4_BY_WHEN}}': extract_non_negotiables(race_data, 3)['by_when'],
        '{{NON_NEG_4_WHY}}': extract_non_negotiables(race_data, 3)['why'],
        '{{NON_NEG_5_REQUIREMENT}}': extract_non_negotiables(race_data, 4)['requirement'],
        '{{NON_NEG_5_BY_WHEN}}': extract_non_negotiables(race_data, 4)['by_when'],
        '{{NON_NEG_5_WHY}}': extract_non_negotiables(race_data, 4)['why'],
        
        # Skill placeholder examples (would be race-specific)
        '{{SKILL_5_NAME}}': 'Emergency Repairs',
        '{{SKILL_5_WHY}}': 'Mechanical issues will happen. Knowing how to fix them keeps you racing.',
        '{{SKILL_5_HOW}}': 'Practice changing tubes, fixing chains, and adjusting brakes before race day.',
        '{{SKILL_5_CUE}}': 'Carry tools. Know your bike. Practice fixes.',
    }
    
    # Perform all substitutions
    output = template
    for placeholder, value in substitutions.items():
        output = output.replace(placeholder, str(value))
    
    # Conditionally remove altitude section if elevation < 3000 feet
    # Check multiple possible field names for elevation
    race_elevation = 0
    if isinstance(race_data, dict):
        race_elevation = (race_data.get('race_metadata', {}).get('avg_elevation_feet', 0) or
                         race_data.get('race_characteristics', {}).get('altitude_feet', 0) or
                         race_data.get('elevation_feet', 0) or
                         race_data.get('avg_elevation_feet', 0) or
                         race_data.get('altitude_feet', 0))
    
    try:
        race_elevation = int(race_elevation) if race_elevation else 0
    except (ValueError, TypeError):
        race_elevation = 0
    
    if race_elevation < 3000:
        # Remove altitude section (between START and END comments)
        import re
        altitude_pattern = r'<!-- START ALTITUDE SECTION[^>]*-->.*?<!-- END ALTITUDE SECTION -->'
        output = re.sub(altitude_pattern, '', output, flags=re.DOTALL)
        print(f"  → Removed altitude section (race elevation: {race_elevation} feet < 3000)")
    else:
        print(f"  → Included altitude section (race elevation: {race_elevation} feet >= 3000)")
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"✓ Generated: {output_path}")
    return output_path


def get_weekly_hours(tier_name):
    """Return weekly hours for each tier"""
    hours = {
        'AYAHUASCA': '0-5',
        'FINISHER': '8-12',
        'COMPETE': '12-18',
        'PODIUM': '18+'
    }
    return hours.get(tier_name, '8-12')


def get_weekly_structure(tier_name):
    """Return weekly structure description for each tier"""
    structures = {
        'AYAHUASCA': '3-4 sessions per week: 2 high-intensity intervals, 1-2 endurance rides',
        'FINISHER': '4-5 sessions per week: 1-2 intervals, 2-3 endurance rides, 1 long weekend ride',
        'COMPETE': '5-6 sessions per week: 2-3 intervals, 2-3 endurance rides, 1 long ride, 1 recovery',
        'PODIUM': '6-7 sessions per week: 3 intervals, 2-3 endurance rides, 1 long ride, 1-2 recovery'
    }
    return structures.get(tier_name, structures['FINISHER'])


def generate_equipment_checklist(race_data):
    """Generate race-specific equipment checklist with checkboxes"""
    items = [
        'Power meter (calibrated)',
        'Heart rate monitor',
        'GPS bike computer',
        f'Tires: {race_data.get("recommended_tire_width", "38-42mm")}',
        'Spare tubes/plugs',
        'Multi-tool',
        'Pump/CO2',
        'Nutrition for race duration',
        'Water bottles (2-3)',
        'Race number',
        'ID and emergency contact'
    ]
    
    # Add race-specific items
    if race_data.get('elevation_gain_feet', 0) > 5000:
        items.append('Gear range for climbing')
    
    if 'hot' in str(race_data.get('weather_strategy', '')).lower():
        items.append('Extra electrolytes')
        items.append('Sun protection')
    
    # Generate HTML with checkboxes
    checklist_html = '<div class="equipment-checklist-items">\n'
    for item in items:
        checklist_html += f'  <label class="checklist-item">\n'
        checklist_html += f'    <input type="checkbox">\n'
        checklist_html += f'    <span>{item}</span>\n'
        checklist_html += f'  </label>\n'
    checklist_html += '</div>\n'
    checklist_html += '<p class="checklist-download"><a href="#" onclick="downloadChecklistPDF()" class="download-link">📥 Download Printable Checklist (PDF)</a></p>'
    
    return checklist_html


def generate_fueling_table(race_data):
    """Generate fueling and hydration calculator table"""
    distance = race_data.get('distance_miles', 200)
    duration_hours = distance / 15  # Rough estimate: 15 mph average
    
    # Base scenarios
    scenarios = [
        {
            'scenario': 'Training Ride < 2 hours',
            'carbs': '30-45g/hour',
            'fluid': '500-750ml/hour',
            'notes': 'Water + electrolytes. Start fueling after 60 min if needed.'
        },
        {
            'scenario': 'Training Ride 2-4 hours',
            'carbs': '45-60g/hour',
            'fluid': '500-750ml/hour',
            'notes': 'Mix of gels, bars, and real food. Practice your race nutrition.'
        },
        {
            'scenario': 'Long Training Ride 4-6 hours',
            'carbs': '60-75g/hour',
            'fluid': '500-750ml/hour',
            'notes': 'Aggressive gut training. Test race-day nutrition strategy.'
        },
        {
            'scenario': f'Race Day ({distance} miles, ~{int(duration_hours)} hours)',
            'carbs': '60-90g/hour',
            'fluid': '500-750ml/hour',
            'notes': 'Start fueling in first 30 min. Mix multiple carb sources (glucose + fructose).'
        },
        {
            'scenario': 'Hot Conditions (>80°F)',
            'carbs': '60-90g/hour',
            'fluid': '750-1000ml/hour',
            'notes': 'Increase sodium to 500-700mg/hour. Pre-cool if possible.'
        },
        {
            'scenario': 'Cold Conditions (<50°F)',
            'carbs': '60-90g/hour',
            'fluid': '400-600ml/hour',
            'notes': 'Lower fluid needs, but still fuel aggressively. Warm fluids help.'
        }
    ]
    
    # Build HTML table
    html = '<table class="fueling-table">\n'
    html += '  <thead>\n'
    html += '    <tr>\n'
    html += '      <th>Scenario</th>\n'
    html += '      <th>Carbohydrate Intake</th>\n'
    html += '      <th>Fluid Intake</th>\n'
    html += '      <th>Notes</th>\n'
    html += '    </tr>\n'
    html += '  </thead>\n'
    html += '  <tbody>\n'
    
    for scenario in scenarios:
        html += '    <tr>\n'
        html += f'      <td><strong>{scenario["scenario"]}</strong></td>\n'
        html += f'      <td>{scenario["carbs"]}</td>\n'
        html += f'      <td>{scenario["fluid"]}</td>\n'
        html += f'      <td>{scenario["notes"]}</td>\n'
        html += '    </tr>\n'
    
    html += '  </tbody>\n'
    html += '</table>'
    
    return html


def generate_difficulty_table(race_data):
    """Generate difficulty rating table"""
    # Extract distance
    distance = (race_data.get('distance_miles') or 
               race_data.get('race_metadata', {}).get('distance_miles') or 
               'N/A')
    
    # Extract elevation gain
    elevation = (race_data.get('elevation_gain_feet') or 
                race_data.get('race_metadata', {}).get('elevation_feet') or 
                0)
    try:
        elevation = int(elevation) if elevation else 0
        elevation_str = f"{elevation:,} feet" if elevation else "N/A"
    except (ValueError, TypeError):
        elevation_str = "N/A"
    
    # Extract technical rating
    tech_rating = (race_data.get('technical_rating') or 
                  race_data.get('race_characteristics', {}).get('technical_difficulty', 'Moderate') or
                  'Moderate')
    
    # Extract time cutoff
    time_cutoff = race_data.get('time_cutoff', 'None')
    
    return f'''
    <table class="difficulty-table">
        <thead>
            <tr>
                <th>Category</th>
                <th>Rating</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Distance</strong></td>
                <td>{distance} miles</td>
            </tr>
            <tr>
                <td><strong>Elevation Gain</strong></td>
                <td>{elevation_str}</td>
            </tr>
            <tr>
                <td><strong>Technical Difficulty</strong></td>
                <td>{tech_rating}</td>
            </tr>
            <tr>
                <td><strong>Time Cutoff</strong></td>
                <td>{time_cutoff}</td>
            </tr>
        </tbody>
    </table>
    '''


def generate_rating_hex(race_data):
    """Generate race difficulty rating hex (radar chart as HTML table)"""
    # Calculate ratings (1-5 scale) based on race characteristics
    distance = race_data.get('distance_miles', 200)
    elevation = race_data.get('elevation_gain_feet', 0)
    terrain = race_data.get('terrain', 'rolling')
    altitude = race_data.get('altitude_feet', 0)
    
    # Distance rating (1-5)
    if distance >= 200:
        dist_rating = 5
    elif distance >= 150:
        dist_rating = 4
    elif distance >= 100:
        dist_rating = 3
    elif distance >= 50:
        dist_rating = 2
    else:
        dist_rating = 1
    
    # Elevation rating
    if elevation >= 15000:
        elev_rating = 5
    elif elevation >= 10000:
        elev_rating = 4
    elif elevation >= 5000:
        elev_rating = 3
    elif elevation >= 2000:
        elev_rating = 2
    else:
        elev_rating = 1
    
    # Technicality rating
    tech_map = {
        'mountain': 5,
        'flint_hills': 4,
        'rolling': 3,
        'flat': 2
    }
    tech_rating = tech_map.get(terrain, 3)
    
    # Climate rating (default moderate)
    climate_rating = 3
    
    # Altitude rating
    if altitude >= 8000:
        alt_rating = 5
    elif altitude >= 5000:
        alt_rating = 4
    elif altitude >= 3000:
        alt_rating = 3
    elif altitude >= 1000:
        alt_rating = 2
    else:
        alt_rating = 1
    
    # Adventure rating (combination of factors)
    adventure_rating = min(5, max(1, (dist_rating + elev_rating + tech_rating) // 3))
    
    html = '<div class="rating-hex">\n'
    html += '  <table class="rating-table">\n'
    html += '    <thead>\n'
    html += '      <tr>\n'
    html += '        <th>Dimension</th>\n'
    html += '        <th>Rating (1-5)</th>\n'
    html += '        <th>Visual</th>\n'
    html += '      </tr>\n'
    html += '    </thead>\n'
    html += '    <tbody>\n'
    
    ratings = [
        ('Elevation', elev_rating),
        ('Length', dist_rating),
        ('Technicality', tech_rating),
        ('Climate', climate_rating),
        ('Altitude', alt_rating),
        ('Adventure', adventure_rating)
    ]
    
    for name, rating in ratings:
        bars = '█' * rating + '░' * (5 - rating)
        html += f'      <tr>\n'
        html += f'        <td><strong>{name}</strong></td>\n'
        html += f'        <td>{rating}/5</td>\n'
        html += f'        <td class="rating-bars">{bars}</td>\n'
        html += f'      </tr>\n'
    
    html += '    </tbody>\n'
    html += '  </table>\n'
    html += '</div>'
    
    return html


def generate_indoor_outdoor_decision(race_data):
    """Generate indoor vs outdoor decision tree/table"""
    html = '<table class="decision-table">\n'
    html += '  <thead>\n'
    html += '    <tr>\n'
    html += '      <th>Condition</th>\n'
    html += '      <th>Ride Indoors</th>\n'
    html += '      <th>Ride Outdoors</th>\n'
    html += '    </tr>\n'
    html += '  </thead>\n'
    html += '  <tbody>\n'
    
    decisions = [
        {
            'condition': 'Temperature < 20°F or > 100°F',
            'indoors': 'Yes - Safety risk',
            'outdoors': 'No - Dangerous conditions'
        },
        {
            'condition': 'Ice, snow, or dangerous road conditions',
            'indoors': 'Yes - Crash risk too high',
            'outdoors': 'No - Unsafe'
        },
        {
            'condition': 'Structured intervals (VO2max, Threshold)',
            'indoors': 'Yes - Better control, no traffic',
            'outdoors': 'Maybe - If safe route available'
        },
        {
            'condition': 'Endurance ride (Z1-Z2)',
            'indoors': 'Avoid - Too boring',
            'outdoors': 'Yes - Mental training, skills practice'
        },
        {
            'condition': 'Time-crunched (< 60 min)',
            'indoors': 'Yes - No travel time, immediate start',
            'outdoors': 'No - Travel time wastes workout'
        },
        {
            'condition': 'Long ride (4+ hours)',
            'indoors': 'No - Mental torture',
            'outdoors': 'Yes - Essential for race prep'
        },
        {
            'condition': 'Recovery ride',
            'indoors': 'Maybe - If weather is terrible',
            'outdoors': 'Yes - Fresh air aids recovery'
        }
    ]
    
    for item in decisions:
        html += '    <tr>\n'
        html += f'      <td><strong>{item["condition"]}</strong></td>\n'
        html += f'      <td>{item["indoors"]}</td>\n'
        html += f'      <td>{item["outdoors"]}</td>\n'
        html += '    </tr>\n'
    
    html += '  </tbody>\n'
    html += '</table>'
    
    return html


def generate_mental_map(race_data):
    """Generate mental framework diagram as structured content"""
    html = '<div class="mental-map">\n'
    html += '  <div class="mental-framework">\n'
    html += '    <h3>Mental Training Framework</h3>\n'
    html += '    <div class="mental-layers">\n'
    html += '      <div class="mental-layer">\n'
    html += '        <h4>1. Foundation: Breathing & Presence</h4>\n'
    html += '        <p><strong>6-2-7 Technique:</strong> Inhale 6 counts, hold 2, exhale 7. Calms nervous system, brings focus to present moment.</p>\n'
    html += '      </div>\n'
    html += '      <div class="mental-layer">\n'
    html += '        <h4>2. Reframing: Change Your Story</h4>\n'
    html += '        <p><strong>Instead of:</strong> <q>This hurts</q> → <strong>Say:</strong> <q>This is my body adapting. I\'m getting stronger.</q></p>\n'
    html += '        <p><strong>Instead of:</strong> <q>I can\'t do this</q> → <strong>Say:</strong> <q>I\'m doing it right now. One pedal stroke at a time.</q></p>\n'
    html += '      </div>\n'
    html += '      <div class="mental-layer">\n'
    html += '        <h4>3. Anchoring: Physical Cues</h4>\n'
    html += '        <p><strong>Power position:</strong> Hands in drops, core engaged, smooth pedal stroke. This is your <q>race mode</q> trigger.</p>\n'
    html += '        <p><strong>Breathing rhythm:</strong> Match cadence to breath (e.g., 2 pedal strokes per breath). Creates flow state.</p>\n'
    html += '      </div>\n'
    html += '      <div class="mental-layer">\n'
    html += '        <h4>4. Acceptance: The Suffering Contract</h4>\n'
    html += '        <p><strong>You signed up for this.</strong> Discomfort is part of the deal. Accept it. Don\'t fight it. Work with it.</p>\n'
    html += '        <p><strong>Pain is temporary. Quitting lasts forever.</strong></p>\n'
    html += '      </div>\n'
    html += '      <div class="mental-layer">\n'
    html += '        <h4>5. Purpose: Remember Your Why</h4>\n'
    html += '        <p><strong>Why are you here?</strong> Connect to your deeper motivation. This race matters because you chose it.</p>\n'
    html += '      </div>\n'
    html += '    </div>\n'
    html += '  </div>\n'
    html += '</div>'
    
    return html


def generate_three_acts(race_data):
    """Generate three-act race structure table"""
    distance = race_data.get('distance_miles', 200)
    duration_hours = distance / 15
    
    html = '<table class="three-acts-table">\n'
    html += '  <thead>\n'
    html += '    <tr>\n'
    html += '      <th>Phase</th>\n'
    html += '      <th>When</th>\n'
    html += '      <th>What\'s Happening</th>\n'
    html += '      <th>Your Job</th>\n'
    html += '    </tr>\n'
    html += '  </thead>\n'
    html += '  <tbody>\n'
    
    acts = [
        {
            'phase': 'Act 1: The Start',
            'when': f'0 - {int(duration_hours * 0.2)} hours',
            'happening': 'High energy, adrenaline, everyone goes too hard. Groups form. Positioning matters.',
            'job': 'Stay calm. Don\'t chase. Fuel early (first 30 min). Find your rhythm. Let the race come to you.'
        },
        {
            'phase': 'Act 2: The Grind',
            'when': f'{int(duration_hours * 0.2)} - {int(duration_hours * 0.8)} hours',
            'happening': 'The real race. Fatigue sets in. Groups break up. Mental game begins. This is where races are won or lost.',
            'job': 'Stay consistent. Fuel every 20-30 min. Manage effort (don\'t redline). Use mental techniques. One section at a time.'
        },
        {
            'phase': 'Act 3: The Finish',
            'when': f'{int(duration_hours * 0.8)} hours - Finish',
            'happening': 'Everything hurts. Decision fatigue. Final push. This is where training pays off.',
            'job': 'Empty the tank. Use everything you\'ve got. Remember your why. Push through the pain. Finish strong.'
        }
    ]
    
    for act in acts:
        html += '    <tr>\n'
        html += f'      <td><strong>{act["phase"]}</strong></td>\n'
        html += f'      <td>{act["when"]}</td>\n'
        html += f'      <td>{act["happening"]}</td>\n'
        html += f'      <td>{act["job"]}</td>\n'
        html += '    </tr>\n'
    
    html += '  </tbody>\n'
    html += '</table>'
    
    return html


def generate_tire_decision(race_data):
    """Generate tire selection decision tree/table"""
    terrain = race_data.get('terrain', 'rolling')
    distance = race_data.get('distance_miles', 200)
    
    html = '<div class="tire-decision">\n'
    html += '  <table class="tire-table">\n'
    html += '    <thead>\n'
    html += '      <tr>\n'
    html += '        <th>Condition</th>\n'
    html += '        <th>Tire Width</th>\n'
    html += '        <th>Tread</th>\n'
    html += '        <th>Pressure</th>\n'
    html += '        <th>Why</th>\n'
    html += '      </tr>\n'
    html += '    </thead>\n'
    html += '    <tbody>\n'
    
    tire_scenarios = [
        {
            'condition': 'Smooth gravel, dry',
            'width': '38-40mm',
            'tread': 'Semi-slick or light file tread',
            'pressure': '35-40 PSI',
            'why': 'Low rolling resistance. Speed matters more than grip.'
        },
        {
            'condition': 'Rough/loose gravel',
            'width': '40-42mm',
            'tread': 'Moderate knobs (2-3mm)',
            'pressure': '30-35 PSI',
            'why': 'Need grip and comfort. Wider = lower pressure = better traction.'
        },
        {
            'condition': 'Mud or wet conditions',
            'width': '42-45mm',
            'tread': 'Aggressive knobs (4-5mm)',
            'pressure': '28-32 PSI',
            'why': 'Maximum grip. Lower pressure helps mud clear from tread.'
        },
        {
            'condition': 'Mixed terrain (your race)',
            'width': '40-42mm',
            'tread': 'Moderate knobs (2-3mm)',
            'pressure': '32-36 PSI',
            'why': 'Versatile. Handles most conditions. Good balance of speed and grip.'
        },
        {
            'condition': 'Long distance (6+ hours)',
            'width': '40-42mm',
            'tread': 'Moderate knobs',
            'pressure': '32-35 PSI',
            'why': 'Comfort matters. Lower pressure reduces fatigue. Still fast enough.'
        }
    ]
    
    for scenario in tire_scenarios:
        html += '      <tr>\n'
        html += f'        <td><strong>{scenario["condition"]}</strong></td>\n'
        html += f'        <td>{scenario["width"]}</td>\n'
        html += f'        <td>{scenario["tread"]}</td>\n'
        html += f'        <td>{scenario["pressure"]}</td>\n'
        html += f'        <td>{scenario["why"]}</td>\n'
        html += '      </tr>\n'
    
    html += '    </tbody>\n'
    html += '  </table>\n'
    html += '  <p class="tire-note"><strong>Rule of thumb:</strong> When in doubt, go wider and lower pressure. Comfort and grip beat marginal speed gains on rough terrain.</p>\n'
    html += '</div>'
    
    return html


def generate_key_workout_summary(race_data):
    """Generate key workout types overview table"""
    html = '<table class="workout-summary-table">\n'
    html += '  <thead>\n'
    html += '    <tr>\n'
    html += '      <th>Workout Type</th>\n'
    html += '      <th>Zone</th>\n'
    html += '      <th>Duration</th>\n'
    html += '      <th>Purpose</th>\n'
    html += '      <th>Key Focus</th>\n'
    html += '    </tr>\n'
    html += '  </thead>\n'
    html += '  <tbody>\n'
    
    workouts = [
        {
            'type': 'Endurance',
            'zone': 'Z1-Z2',
            'duration': '2-6 hours',
            'purpose': 'Aerobic base, fat adaptation',
            'focus': 'Easy pace. Conversational. Builds durability.'
        },
        {
            'type': 'G-Spot Intervals',
            'zone': '87-92% FTP',
            'duration': '15-60 min blocks',
            'purpose': 'Race-specific power',
            'focus': 'Sustained gravel race pace. Practice position.'
        },
        {
            'type': 'Threshold',
            'zone': 'Z4 (93-105% FTP)',
            'duration': '10-30 min blocks',
            'purpose': 'Lactate clearance, sustained power',
            'focus': 'Hard but controlled. Can say a few words.'
        },
        {
            'type': 'VO2max',
            'zone': 'Z5 (106-120% FTP)',
            'duration': '2-8 min intervals',
            'purpose': 'Max aerobic capacity',
            'focus': 'Very hard. Near max. Single words only.'
        },
        {
            'type': 'Anaerobic',
            'zone': 'Z6 (121-150% FTP)',
            'duration': '30 sec - 3 min',
            'purpose': 'Power, lactate tolerance',
            'focus': 'All-out efforts. Sharp, explosive.'
        },
        {
            'type': 'Neuromuscular',
            'zone': 'Z7 (>150% FTP)',
            'duration': '5-15 seconds',
            'purpose': 'Max power, sprint',
            'focus': 'Pure explosive. All-out sprints.'
        },
        {
            'type': 'Tempo',
            'zone': 'Z3 (76-90% FTP)',
            'duration': '20-60 min',
            'purpose': 'Moderate intensity (limited use)',
            'focus': 'Comfortably hard. Used sparingly in polarized plans.'
        }
    ]
    
    for workout in workouts:
        html += '    <tr>\n'
        html += f'      <td><strong>{workout["type"]}</strong></td>\n'
        html += f'      <td>{workout["zone"]}</td>\n'
        html += f'      <td>{workout["duration"]}</td>\n'
        html += f'      <td>{workout["purpose"]}</td>\n'
        html += f'      <td>{workout["focus"]}</td>\n'
        html += '    </tr>\n'
    
    html += '  </tbody>\n'
    html += '</table>'
    
    return html


def main():
    """Example usage"""
    
    # Example: Generate guide for Unbound Gravel 200
    # In practice, you'd load race data from your JSON file
    
    race_data = {
        'name': 'Unbound Gravel 200',
        'distance_miles': 200,
        'elevation_gain_feet': 10000,
        'terrain_description': 'Kansas flint rock, rollers, and endless dirt roads',
        'duration_estimate': '10-15 hours',
        'description': 'The original and most iconic gravel race in North America. 200 miles of Kansas flint, heat, and suffering.',
        'key_challenges': 'extreme distance, heat exposure, rough flint rock, and relentless mental grind',
        'recommended_tire_width': '40-45mm',
        'technical_rating': 'Moderate',
        'time_cutoff': '30 hours',
        'website': 'https://unboundgravel.com',
        'weather_strategy': 'Expect heat. Start hydrated. Cool with water at aid stations.',
        'aid_station_strategy': 'Quick stops only. Have crew support if possible.',
        'altitude_power_loss': 'Minimal - race is at ~1,200 feet elevation',
        'specific_skill_notes': 'Practice riding washboard. Learn to float over rough surfaces.',
        'specific_tactics': 'Start slow. The first 100 miles is just warm-up. Real race starts at mile 150.'
    }
    
    # Generate guide
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    output_dir = repo_root / 'output'
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / 'test_guide_unbound_200_finisher_intermediate.html'
    
    generate_guide(
        race_data=race_data,
        tier_name='FINISHER',
        ability_level='Intermediate',
        output_path=str(output_path)
    )
    
    print(f"\n✓ Test guide generated successfully!")
    print(f"✓ Open {output_path} in a browser to view")


if __name__ == '__main__':
    main()

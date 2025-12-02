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
    
    # Build substitution dictionary
    substitutions = {
        '{{RACE_NAME}}': race_data.get('name', 'Race Name'),
        '{{DISTANCE}}': str(race_data.get('distance_miles', 'XXX')),
        '{{TERRAIN_DESCRIPTION}}': race_data.get('terrain_description', 'varied terrain'),
        '{{ELEVATION_GAIN}}': f"{race_data.get('elevation_gain_feet', 'XXX'):,} feet of elevation gain",
        '{{DURATION_ESTIMATE}}': race_data.get('duration_estimate', 'X-X hours'),
        '{{RACE_DESCRIPTION}}': race_data.get('description', 'Race description here'),
        '{{ABILITY_LEVEL}}': ability_level,
        '{{TIER_NAME}}': tier_name,
        '{{WEEKLY_HOURS}}': get_weekly_hours(tier_name),
        '{{plan_weeks}}': '12',  # Default to 12 weeks, can be made dynamic
        '{{RACE_KEY_CHALLENGES}}': race_data.get('key_challenges', 'technical terrain, elevation, and endurance'),
        '{{WEEKLY_STRUCTURE_DESCRIPTION}}': get_weekly_structure(tier_name),
        '{{RACE_ELEVATION}}': str(race_data.get('elevation_gain_feet', 'XXX')),
        '{{RACE_SPECIFIC_SKILL_NOTES}}': race_data.get('specific_skill_notes', 'Practice descending, cornering, and rough terrain handling.'),
        '{{RACE_SPECIFIC_TACTICS}}': race_data.get('specific_tactics', 'Start conservatively. Fuel early and often. Be patient on climbs.'),
        '{{WEATHER_STRATEGY}}': race_data.get('weather_strategy', 'Check forecast week of. Pack layers.'),
        '{{AID_STATION_STRATEGY}}': race_data.get('aid_station_strategy', 'Use aid stations for quick refills. Don\'t linger.'),
        '{{ALTITUDE_POWER_LOSS}}': race_data.get('altitude_power_loss', '5-10% power loss expected above 8,000 feet'),
        '{{RECOMMENDED_TIRE_WIDTH}}': race_data.get('recommended_tire_width', '38-42mm'),
        '{{EQUIPMENT_CHECKLIST}}': generate_equipment_checklist(race_data),
        '{{RACE_SUPPORT_URL}}': race_data.get('website', 'https://example.com'),
        
        # Infographic placeholders (these would be replaced with actual SVG/images later)
        '{{INFOGRAPHIC_PHASE_BARS}}': '[Phase progression infographic]',
        '{{INFOGRAPHIC_RATING_HEX}}': '[Race difficulty rating hex]',
        '{{INFOGRAPHIC_DIFFICULTY_TABLE}}': generate_difficulty_table(race_data),
        '{{INFOGRAPHIC_FUELING_TABLE}}': generate_fueling_table(race_data),
        '{{INFOGRAPHIC_MENTAL_MAP}}': '[Mental framework diagram]',
        '{{INFOGRAPHIC_THREE_ACTS}}': '[Three-act race structure]',
        '{{INFOGRAPHIC_INDOOR_OUTDOOR_DECISION}}': '[Indoor vs Outdoor decision tree]',
        '{{INFOGRAPHIC_TIRE_DECISION}}': '[Tire selection flowchart]',
        '{{INFOGRAPHIC_KEY_WORKOUT_SUMMARY}}': '[Key workout types overview]',
        
        # Non-negotiables
        '{{NON_NEG_1_WHY}}': 'Precise power data ensures correct training zones and optimal adaptation',
        '{{NON_NEG_2_WHY}}': 'Heart rate provides backup data and helps gauge recovery status',
        '{{NON_NEG_3_WHY}}': 'Proper position prevents injury and maximizes power transfer',
        '{{NON_NEG_4_WHY}}': 'Consistency is the foundation of adaptation - skip weeks, lose gains',
        '{{NON_NEG_5_WHY}}': 'The plan works if you work it - modifications undermine the system',
        
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
    """Generate race-specific equipment checklist"""
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
    
    if 'hot' in race_data.get('weather_strategy', '').lower():
        items.append('Extra electrolytes')
        items.append('Sun protection')
    
    return '<br>'.join([f'• {item}' for item in items])


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
    return f'''
    <table>
        <tr>
            <th>Category</th>
            <th>Rating</th>
        </tr>
        <tr>
            <td>Distance</td>
            <td>{race_data.get('distance_miles', 'N/A')} miles</td>
        </tr>
        <tr>
            <td>Elevation Gain</td>
            <td>{race_data.get('elevation_gain_feet', 'N/A'):,} feet</td>
        </tr>
        <tr>
            <td>Technical Difficulty</td>
            <td>{race_data.get('technical_rating', 'Moderate')}</td>
        </tr>
        <tr>
            <td>Time Cutoff</td>
            <td>{race_data.get('time_cutoff', 'None')}</td>
        </tr>
    </table>
    '''


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

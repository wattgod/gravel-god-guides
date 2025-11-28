#!/usr/bin/env python3

"""

Gravel God Training Guide Generator

====================================

Generates styled HTML training guides from JSON data files.

Usage:

    python generate_guide.py guide_data.json output.html

The JSON file contains all variable content. The HTML template is embedded

in this script. Cursor should ONLY edit the JSON file, never this script.

"""

import json

import sys

import math

from pathlib import Path

def calculate_radar_points(values: dict, center_x: int = 200, center_y: int = 160, max_radius: int = 120) -> list:

    """Calculate SVG polygon points for radar chart."""

    # Order: elevation (top), length (60°), technical (120°), climate (180°), altitude (240°), adventure (300°)

    order = ['elevation', 'length', 'technical', 'climate', 'altitude', 'adventure']

    angles = [270, 330, 30, 90, 150, 210]  # degrees, starting from top

    

    points = []

    for i, key in enumerate(order):

        value = values.get(key, 1)

        radius = max_radius * (value / 5)

        angle_rad = math.radians(angles[i])

        x = center_x + radius * math.cos(angle_rad)

        y = center_y + radius * math.sin(angle_rad)

        points.append((round(x), round(y)))

    

    return points

def generate_radar_svg(radar_data: dict) -> str:

    """Generate the complete radar chart SVG."""

    points = calculate_radar_points(radar_data)

    polygon_points = " ".join(f"{x},{y}" for x, y in points)

    

    # Generate data point circles

    circles = "\n                ".join(

        f'<circle cx="{x}" cy="{y}" r="6" fill="#4ecdc4" stroke="#2c2c2c" stroke-width="2"/>'

        for x, y in points

    )

    

    return f'''            <svg viewBox="0 0 400 350" width="400" height="350">

                <!-- Background -->

                <rect x="0" y="0" width="400" height="350" fill="white"/>

                

                <!-- Grid circles (5 levels) -->

                <circle cx="200" cy="160" r="120" fill="none" stroke="#e0e0e0" stroke-width="1"/>

                <circle cx="200" cy="160" r="96" fill="none" stroke="#e0e0e0" stroke-width="1"/>

                <circle cx="200" cy="160" r="72" fill="none" stroke="#e0e0e0" stroke-width="1"/>

                <circle cx="200" cy="160" r="48" fill="none" stroke="#e0e0e0" stroke-width="1"/>

                <circle cx="200" cy="160" r="24" fill="none" stroke="#e0e0e0" stroke-width="1"/>

                

                <!-- Axis lines -->

                <line x1="200" y1="160" x2="200" y2="40" stroke="#ccc" stroke-width="1"/>

                <line x1="200" y1="160" x2="304" y2="100" stroke="#ccc" stroke-width="1"/>

                <line x1="200" y1="160" x2="304" y2="220" stroke="#ccc" stroke-width="1"/>

                <line x1="200" y1="160" x2="200" y2="280" stroke="#ccc" stroke-width="1"/>

                <line x1="200" y1="160" x2="96" y2="220" stroke="#ccc" stroke-width="1"/>

                <line x1="200" y1="160" x2="96" y2="100" stroke="#ccc" stroke-width="1"/>

                

                <!-- Data polygon -->

                <polygon 

                    points="{polygon_points}"

                    fill="rgba(78, 205, 196, 0.3)"

                    stroke="#4ecdc4"

                    stroke-width="3"/>

                

                <!-- Data points -->

                {circles}

                

                <!-- Labels -->

                <text x="200" y="25" text-anchor="middle" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">ELEVATION ({radar_data['elevation']}/5)</text>

                <text x="330" y="95" text-anchor="start" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">LENGTH ({radar_data['length']}/5)</text>

                <text x="330" y="230" text-anchor="start" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">TECHNICAL ({radar_data['technical']}/5)</text>

                <text x="200" y="305" text-anchor="middle" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">CLIMATE ({radar_data['climate']}/5)</text>

                <text x="70" y="230" text-anchor="end" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">ALTITUDE ({radar_data['altitude']}/5)</text>

                <text x="70" y="95" text-anchor="end" font-family="Sometype Mono, monospace" font-size="12" font-weight="700">ADVENTURE ({radar_data['adventure']}/5)</text>

            </svg>'''

def generate_zones_table(zones: list) -> str:

    """Generate the training zones table HTML."""

    rows = []

    for z in zones:

        highlight = ' class="g-spot-row"' if z.get('highlight') else ''

        rows.append(f'''                    <tr{highlight}>

                        <td><strong>{z['zone']}</strong></td>

                        <td>{z['name']}</td>

                        <td>{z['ftp_range']}</td>

                        <td>{z['rpe']}</td>

                        <td>{z['description']}</td>

                    </tr>''')

    return "\n".join(rows)

def generate_glossary(glossary: list) -> str:

    """Generate glossary definition list HTML."""

    items = []

    for g in glossary:

        items.append(f'''            <div class="glossary-item">

                <dt>{g['term']}</dt>

                <dd>{g['definition']}</dd>

            </div>''')

    return "\n".join(items)

def generate_skills(skills: list) -> str:

    """Generate skills section HTML."""

    items = []

    for s in skills:

        items.append(f'''            <div class="skill-item">

                <h4>{s['name']}</h4>

                <p>{s['description']}</p>

            </div>''')

    return "\n".join(items)

def generate_three_acts_table(acts: list) -> str:

    """Generate the three acts table HTML."""

    rows = []

    for act in acts:

        highlight = ' class="g-spot-row"' if act.get('highlight') else ''

        rows.append(f'''                    <tr{highlight}>

                        <td><strong>{act['name']}</strong></td>

                        <td>{act['when']}</td>

                        <td>{act['whats_happening']}</td>

                        <td>{act['your_job']}</td>

                    </tr>''')

    return "\n".join(rows)

def generate_race_week_table(days: list) -> str:

    """Generate race week countdown table HTML."""

    rows = []

    for day in days:

        rows.append(f'''                    <tr>

                        <td><strong>{day['day']}</strong></td>

                        <td>{day['training']}</td>

                        <td>{day['focus']}</td>

                    </tr>''')

    return "\n".join(rows)

def generate_phase_bars(phases: list) -> str:

    """Generate phase bars SVG."""

    bars = []

    x_positions = [50, 175, 300, 425]

    for i, phase in enumerate(phases):

        bars.append(f'''                <rect x="{x_positions[i]}" y="30" width="100" height="50" fill="{phase['color']}" stroke="#2c2c2c" stroke-width="2"/>

                <text x="{x_positions[i] + 50}" y="60" text-anchor="middle" font-family="Sometype Mono, monospace" font-size="14" font-weight="700">{phase['name']}</text>

                <text x="{x_positions[i] + 50}" y="100" text-anchor="middle" font-family="Sometype Mono, monospace" font-size="11">Weeks {phase['weeks']}</text>''')

    return "\n".join(bars)

def generate_html(data: dict) -> str:

    """Generate the complete HTML document from JSON data."""

    

    meta = data['meta']

    radar_svg = generate_radar_svg(data['radar_chart'])

    zones_rows = generate_zones_table(data['zones'])

    glossary_html = generate_glossary(data['glossary'])

    skills_html = generate_skills(data['skills'])

    three_acts_rows = generate_three_acts_table(data['race_tactics']['three_acts'])

    race_week_rows = generate_race_week_table(data['race_week'])

    phase_bars = generate_phase_bars(data['plan_phases'])

    footer = data['footer']

    tactics = data['race_tactics']

    

    # Primary demands as formatted list

    primary_demands = ", ".join(f"<strong>{d}</strong>" for d in data['race_demands']['primary'])

    

    html = f'''<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{meta['race_name']} Training Guide | Gravel God</title>

    <link href="https://fonts.googleapis.com/css2?family=Sometype+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>

        /* ============================================

           GRAVEL GOD NEO-BRUTALIST DESIGN SYSTEM

           ============================================ */

        

        :root {{

            --cream: #f5f5dc;

            --cream-dark: #ede5d0;

            --turquoise: #4ecdc4;

            --turquoise-light: rgba(78, 205, 196, 0.15);

            --yellow: #f4d03f;

            --yellow-light: #fef9e7;

            --brown-dark: #59473C;

            --text-dark: #2c2c2c;

            --red: #e74c3c;

            --red-light: #fdedec;

            --green: #27ae60;

            --green-light: #e9f7ef;

            --border-width: 3px;

            --shadow-offset: 6px;

            --shadow-color: rgba(0,0,0,0.2);

        }}

        * {{

            margin: 0;

            padding: 0;

            box-sizing: border-box;

        }}

        html {{

            scroll-behavior: smooth;

        }}

        body {{

            font-family: 'Sometype Mono', monospace;

            background: var(--cream);

            color: var(--text-dark);

            line-height: 1.7;

            font-size: 16px;

        }}

        /* ============================================

           STICKY NAVIGATION

           ============================================ */

        

        .sticky-nav {{

            position: sticky;

            top: 0;

            background: var(--brown-dark);

            padding: 0.75rem 1rem;

            display: flex;

            gap: 0.5rem;

            flex-wrap: wrap;

            justify-content: center;

            z-index: 1000;

            border-bottom: var(--border-width) solid var(--text-dark);

        }}

        .sticky-nav a {{

            color: var(--cream);

            text-decoration: none;

            padding: 0.4rem 0.8rem;

            font-size: 0.75rem;

            font-weight: 600;

            text-transform: uppercase;

            letter-spacing: 0.5px;

            border: 2px solid transparent;

            transition: all 0.2s ease;

        }}

        .sticky-nav a:hover {{

            background: var(--turquoise);

            color: var(--text-dark);

        }}

        .sticky-nav a.active {{

            background: var(--turquoise);

            color: var(--text-dark);

            border-color: var(--text-dark);

        }}

        /* ============================================

           HEADER

           ============================================ */

        

        .header {{

            background: var(--brown-dark);

            color: var(--cream);

            padding: 3rem 2rem;

            text-align: center;

            border-bottom: var(--border-width) solid var(--text-dark);

        }}

        .header-brand {{

            font-size: 0.9rem;

            text-transform: uppercase;

            letter-spacing: 3px;

            color: var(--turquoise);

            margin-bottom: 1rem;

        }}

        .header h1 {{

            font-size: 3rem;

            font-weight: 700;

            margin-bottom: 0.5rem;

            text-transform: uppercase;

            letter-spacing: 2px;

        }}

        .header-subtitle {{

            font-size: 1.1rem;

            color: var(--cream);

            opacity: 0.9;

        }}

        .header-meta {{

            display: flex;

            justify-content: center;

            gap: 2rem;

            margin-top: 1.5rem;

            flex-wrap: wrap;

        }}

        .header-meta-item {{

            background: rgba(255,255,255,0.1);

            padding: 0.5rem 1rem;

            border: 2px solid var(--turquoise);

        }}

        .header-meta-item strong {{

            color: var(--turquoise);

        }}

        /* ============================================

           SECTIONS

           ============================================ */

        

        .section {{

            padding: 3rem 2rem;

            max-width: 900px;

            margin: 0 auto;

            border-bottom: 2px dashed var(--brown-dark);

        }}

        .section:last-of-type {{

            border-bottom: none;

        }}

        .section-header {{

            display: flex;

            align-items: center;

            gap: 1rem;

            margin-bottom: 2rem;

            padding-bottom: 1rem;

            border-bottom: var(--border-width) solid var(--text-dark);

        }}

        .section-number {{

            background: var(--turquoise);

            color: var(--text-dark);

            width: 50px;

            height: 50px;

            display: flex;

            align-items: center;

            justify-content: center;

            font-size: 1.2rem;

            font-weight: 700;

            border: var(--border-width) solid var(--text-dark);

            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-dark);

        }}

        .section-header h2 {{

            font-size: 1.8rem;

            text-transform: uppercase;

            letter-spacing: 1px;

        }}

        .section-content h3 {{

            font-size: 1.3rem;

            margin: 2rem 0 1rem;

            color: var(--brown-dark);

            border-left: 4px solid var(--turquoise);

            padding-left: 1rem;

        }}

        .section-content h4 {{

            font-size: 1.1rem;

            margin: 1.5rem 0 0.75rem;

            color: var(--text-dark);

        }}

        .section-content p {{

            margin-bottom: 1rem;

        }}

        .section-content ul, .section-content ol {{

            margin: 1rem 0 1rem 1.5rem;

        }}

        .section-content li {{

            margin-bottom: 0.5rem;

        }}

        /* ============================================

           TABLES

           ============================================ */

        

        .table-wrapper {{

            overflow-x: auto;

            margin: 1.5rem 0;

            border: var(--border-width) solid var(--text-dark);

            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-dark);

        }}

        table {{

            width: 100%;

            border-collapse: collapse;

            background: white;

        }}

        th {{

            background: var(--brown-dark);

            color: var(--cream);

            padding: 1rem;

            text-align: left;

            font-weight: 700;

            text-transform: uppercase;

            font-size: 0.85rem;

            letter-spacing: 0.5px;

        }}

        td {{

            padding: 0.875rem 1rem;

            border-bottom: 1px solid var(--cream-dark);

            font-size: 0.9rem;

        }}

        tr:hover {{

            background: var(--cream-dark);

        }}

        tr.g-spot-row {{

            background: var(--turquoise-light);

        }}

        tr.g-spot-row:hover {{

            background: rgba(78, 205, 196, 0.25);

        }}

        /* ============================================

           CALLOUTS

           ============================================ */

        

        .callout {{

            padding: 1.5rem;

            margin: 1.5rem 0;

            border: var(--border-width) solid var(--text-dark);

            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-dark);

        }}

        .callout-title {{

            font-weight: 700;

            text-transform: uppercase;

            font-size: 0.9rem;

            letter-spacing: 0.5px;

            margin-bottom: 0.75rem;

        }}

        .callout-info {{

            background: var(--turquoise-light);

            border-color: var(--turquoise);

        }}

        .callout-info .callout-title {{

            color: var(--brown-dark);

        }}

        .callout-warning {{

            background: var(--yellow-light);

            border-color: var(--yellow);

        }}

        .callout-warning .callout-title {{

            color: var(--brown-dark);

        }}

        .callout-danger {{

            background: var(--red-light);

            border-color: var(--red);

        }}

        .callout-danger .callout-title {{

            color: var(--red);

        }}

        .callout-success {{

            background: var(--green-light);

            border-color: var(--green);

        }}

        .callout-success .callout-title {{

            color: var(--green);

        }}

        /* ============================================

           CARDS

           ============================================ */

        

        .card-grid {{

            display: grid;

            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));

            gap: 1.5rem;

            margin: 1.5rem 0;

        }}

        .card {{

            background: white;

            padding: 1.5rem;

            border: var(--border-width) solid var(--text-dark);

            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-dark);

        }}

        .card h4 {{

            color: var(--brown-dark);

            margin-bottom: 0.75rem;

            font-size: 1rem;

        }}

        .card p {{

            font-size: 0.9rem;

            margin: 0;

        }}

        /* ============================================

           GRAPHICS

           ============================================ */

        

        .graphic-container {{

            background: white;

            border: var(--border-width) solid var(--text-dark);

            box-shadow: var(--shadow-offset) var(--shadow-offset) 0 var(--text-dark);

            padding: 1.5rem;

            margin: 1.5rem 0;

            text-align: center;

        }}

        .graphic-title {{

            font-weight: 700;

            text-transform: uppercase;

            font-size: 0.9rem;

            letter-spacing: 1px;

            margin-bottom: 1rem;

            color: var(--brown-dark);

        }}

        .graphic-container svg {{

            max-width: 100%;

            height: auto;

        }}

        /* ============================================

           GLOSSARY

           ============================================ */

        

        .glossary-grid {{

            display: grid;

            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));

            gap: 1rem;

            margin: 1.5rem 0;

        }}

        .glossary-item {{

            background: white;

            padding: 1rem;

            border: 2px solid var(--cream-dark);

        }}

        .glossary-item dt {{

            font-weight: 700;

            color: var(--turquoise);

            margin-bottom: 0.25rem;

        }}

        .glossary-item dd {{

            font-size: 0.85rem;

            margin: 0;

        }}

        /* ============================================

           SKILLS

           ============================================ */

        

        .skills-grid {{

            display: grid;

            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));

            gap: 1.5rem;

            margin: 1.5rem 0;

        }}

        .skill-item {{

            background: white;

            padding: 1.25rem;

            border: var(--border-width) solid var(--text-dark);

            box-shadow: 4px 4px 0 var(--text-dark);

        }}

        .skill-item h4 {{

            color: var(--brown-dark);

            margin-bottom: 0.5rem;

            font-size: 1rem;

            border-bottom: 2px solid var(--turquoise);

            padding-bottom: 0.5rem;

        }}

        .skill-item p {{

            font-size: 0.9rem;

            margin: 0;

        }}

        /* ============================================

           FOOTER

           ============================================ */

        

        .footer {{

            background: var(--brown-dark);

            color: var(--cream);

            text-align: center;

            padding: 4rem 2rem;

            border-top: var(--border-width) solid var(--text-dark);

        }}

        .footer-tagline {{

            font-size: 2rem;

            font-weight: 700;

            color: var(--turquoise);

            margin-bottom: 2rem;

            text-transform: uppercase;

            letter-spacing: 2px;

        }}

        .footer-content {{

            max-width: 700px;

            margin: 0 auto 2rem;

        }}

        .footer-content p {{

            margin-bottom: 1.25rem;

            line-height: 1.8;

        }}

        .footer-emphasis {{

            font-size: 1.1rem;

            font-weight: 700;

            color: var(--turquoise);

        }}

        .footer-contact {{

            margin-top: 3rem;

            padding-top: 2rem;

            border-top: 1px solid rgba(255,255,255,0.2);

        }}

        .footer-email {{

            font-size: 0.95rem;

            margin-bottom: 0.5rem;

        }}

        .footer-motto {{

            font-size: 1rem;

            font-style: italic;

            color: var(--turquoise);

            margin-top: 1rem;

        }}

        /* ============================================

           RESPONSIVE

           ============================================ */

        

        @media (max-width: 768px) {{

            .header h1 {{

                font-size: 2rem;

            }}

            

            .sticky-nav {{

                padding: 0.5rem;

            }}

            

            .sticky-nav a {{

                font-size: 0.65rem;

                padding: 0.3rem 0.5rem;

            }}

            

            .section {{

                padding: 2rem 1rem;

            }}

            

            .section-header h2 {{

                font-size: 1.4rem;

            }}

            

            th, td {{

                padding: 0.5rem;

                font-size: 0.8rem;

            }}

        }}

        /* Horizontal rule */

        hr {{

            border: none;

            border-top: 2px dashed var(--text-dark);

            margin: 2rem 0;

            opacity: 0.3;

        }}

    </style>

</head>

<body>

<!-- STICKY NAVIGATION -->

<nav class="sticky-nav">

    <a href="#welcome" class="active">Welcome</a>

    <a href="#structure">Structure</a>

    <a href="#zones">Zones</a>

    <a href="#glossary">Glossary</a>

    <a href="#skills">Skills</a>

    <a href="#race-day">Race Day</a>

</nav>

<!-- HEADER -->

<header class="header">

    <div class="header-brand">Gravel God Coaching</div>

    <h1>{meta['race_name']}</h1>

    <p class="header-subtitle">Training Guide</p>

    <div class="header-meta">

        <div class="header-meta-item"><strong>{meta['tier']}</strong> Tier</div>

        <div class="header-meta-item"><strong>{meta['level']}</strong> Level</div>

        <div class="header-meta-item"><strong>{meta['hours_per_week']}</strong> hrs/week</div>

        <div class="header-meta-item"><strong>{meta['plan_weeks']}</strong> weeks</div>

    </div>

</header>

<!-- SECTION 1: WELCOME -->

<section class="section" id="welcome">

    <div class="section-header">

        <span class="section-number">01</span>

        <h2>Welcome</h2>

    </div>

    <div class="section-content">

        <p><strong>{meta['race_name']}</strong> is {meta['race_distance']} of Flint Hills gravel. {meta['race_location']}. {meta['race_date']}.</p>

        

        <p>This plan targets the key demands of the race: {primary_demands}.</p>

        <h3>Race Profile</h3>

        <div class="graphic-container">

            <div class="graphic-title">Course Demands</div>

{radar_svg}

        </div>

        <h3>What Makes This Plan Different</h3>

        

        <div class="card-grid">

            <div class="card">

                <h4>Built for Your Ability Level</h4>

                <p>You're on the <strong>{meta['level']}</strong> version. The load and intensity match where you are right now.</p>

            </div>

            <div class="card">

                <h4>Built for Your Schedule</h4>

                <p>This is the <strong>{meta['tier']}</strong> tier, designed around <strong>{meta['hours_per_week']} hours/week</strong>.</p>

            </div>

            <div class="card">

                <h4>Built for This Race</h4>

                <p>The sessions target the key demands of {meta['race_name']}: {primary_demands}.</p>

            </div>

        </div>

    </div>

</section>

<!-- SECTION 2: STRUCTURE -->

<section class="section" id="structure">

    <div class="section-header">

        <span class="section-number">02</span>

        <h2>Plan Structure</h2>

    </div>

    <div class="section-content">

        <h3>{meta['plan_weeks']} Weeks, 4 Phases</h3>

        

        <div class="graphic-container">

            <div class="graphic-title">Training Phases</div>

            <svg viewBox="0 0 600 120" width="600" height="120">

                <rect x="0" y="0" width="600" height="120" fill="white"/>

{phase_bars}

            </svg>

        </div>

    </div>

</section>

<!-- SECTION 3: ZONES -->

<section class="section" id="zones">

    <div class="section-header">

        <span class="section-number">03</span>

        <h2>Training Zones</h2>

    </div>

    <div class="section-content">

        <p>These zones are based on your FTP. If you don't know your FTP, do a 20-minute test and multiply by 0.95.</p>

        

        <div class="table-wrapper">

            <table>

                <thead>

                    <tr>

                        <th>Zone</th>

                        <th>Name</th>

                        <th>% FTP</th>

                        <th>RPE</th>

                        <th>Description</th>

                    </tr>

                </thead>

                <tbody>

{zones_rows}

                </tbody>

            </table>

        </div>

        <div class="callout callout-info">

            <div class="callout-title">The G Spot</div>

            <p>The "G Spot" (88-92% FTP) is our signature zone for gravel racing. Hard enough to be race-relevant, sustainable enough for long efforts. This is where gravel races are won.</p>

        </div>

    </div>

</section>

<!-- SECTION 4: GLOSSARY -->

<section class="section" id="glossary">

    <div class="section-header">

        <span class="section-number">04</span>

        <h2>TrainingPeaks Glossary</h2>

    </div>

    <div class="section-content">

        <p>These are the metrics and terms you'll encounter in TrainingPeaks.</p>

        

        <div class="glossary-grid">

{glossary_html}

        </div>

    </div>

</section>

<!-- SECTION 5: SKILLS -->

<section class="section" id="skills">

    <div class="section-header">

        <span class="section-number">05</span>

        <h2>Gravel Skills</h2>

    </div>

    <div class="section-content">

        <p>These skills separate good gravel racers from everyone else.</p>

        

        <div class="skills-grid">

{skills_html}

        </div>

        

        <div class="callout callout-success">

            <div class="callout-title">Practice Recommendations</div>

            <p>Take your gravel bike on MTB trails (green/blue difficulty). Set up obstacle courses in grassy fields. <strong>30 minutes of focused practice builds skills faster than 3 hours of just riding.</strong></p>

        </div>

    </div>

</section>

<!-- SECTION 6: RACE DAY TACTICS -->

<section class="section" id="race-day">

    <div class="section-header">

        <span class="section-number">06</span>

        <h2>Race Day Tactics</h2>

    </div>

    <div class="section-content">

        <p>It turns out racing is much more pleasant if you employ something called "tactics." Tactics just mean having a plan for how you're going to use your energy over the course.</p>

        

        <h3>The Three-Act Structure</h3>

        <p>Every long gravel race follows a predictable three-act structure.</p>

        

        <div class="table-wrapper">

            <table>

                <thead>

                    <tr>

                        <th>Phase</th>

                        <th>When</th>

                        <th>What's Happening</th>

                        <th>Your Job</th>

                    </tr>

                </thead>

                <tbody>

{three_acts_rows}

                </tbody>

            </table>

        </div>

        <hr>

        <h3>Tactical Principles</h3>

        <h4>Be Efficient</h4>

        <p>Keep asking yourself this question:</p>

        

        <div class="callout callout-success">

            <div class="callout-title">The Key Question</div>

            <p style="font-size: 1.2rem; font-weight: 700;">"{tactics['key_quote']}"</p>

        </div>

        <p><strong>The goal of racing, unlike training, is not putting up big power numbers—it's to go from A to B as fast as possible using the least amount of energy.</strong></p>

        {"".join(f'''

        <h4>{tip['name']}</h4>

        <p>{tip['content']}</p>

        ''' for tip in tactics['efficiency_tips'])}

        <h3>The 7-Day Countdown</h3>

        

        <div class="table-wrapper">

            <table>

                <thead>

                    <tr>

                        <th>Day</th>

                        <th>Training</th>

                        <th>Focus</th>

                    </tr>

                </thead>

                <tbody>

{race_week_rows}

                </tbody>

            </table>

        </div>

    </div>

</section>

<!-- FOOTER -->

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

<!-- SCROLL SPY JAVASCRIPT -->

<script>

document.addEventListener('DOMContentLoaded', function() {{

    const sections = document.querySelectorAll('.section');

    const navLinks = document.querySelectorAll('.sticky-nav a');

    

    function updateActiveLink() {{

        let current = '';

        sections.forEach(section => {{

            const sectionTop = section.offsetTop - 100;

            if (scrollY >= sectionTop) {{

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

        print("Usage: python generate_guide.py <input.json> <output.html>")

        print("\nExample:")

        print("  python generate_guide.py guide_data_unbound200_intermediate.json unbound200_guide.html")

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

    print(f"\nOpen {output_file} in a browser to preview.")

if __name__ == "__main__":

    main()


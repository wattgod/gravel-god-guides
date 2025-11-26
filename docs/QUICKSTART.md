# QUICK START GUIDE
## Automated Coaching Plan Generator

### 5-Minute Setup

**1. Prepare Your Files** (Put these in the same directory)
```
/your_project/
├── athlete_analysis_system.py
├── workout_generator.py
├── guide_generator.py
└── master_workflow.py
```

**2. Install Dependencies**
```bash
pip install python-docx pandas
```

**3. Create Your Questionnaire Data**
```python
athlete_data = {
    # REQUIRED FIELDS
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 35,
    'primary_goal': 'Unbound 200',
    'primary_goal_date': '2026-06-06',
    'goal_importance': 5,
    'sport': 'Gravel',
    'experience_years': 8,
    'current_level': 'advanced',  # beginner, intermediate, advanced, pro
    'training_hours_per_week': 12,
    'races_last_year': 4,
    
    # AVAILABILITY (REQUIRED)
    'weekday_hours_available': {
        'Monday': 1.5,
        'Tuesday': 1.5,
        'Wednesday': 1.5,
        'Thursday': 1.5,
        'Friday': 2.0
    },
    'weekend_hours_available': {
        'Saturday': 4.0,
        'Sunday': 3.0
    },
    'preferred_off_days': ['Sunday'],
    'preferred_long_day': 'Saturday',
    
    # OPTIONAL BUT RECOMMENDED
    'strengths': ['Endurance', 'Climbing'],
    'weaknesses': ['Sprinting', 'Recovery'],
    'work_hours_per_week': 40,
    'job_stress_level': 'manageable',
    'sleep_hours': 8.0,
    'day_to_day_feeling': 'good',
    'uses_power_meter': True,
    'uses_hrm': True,
    'strength_frequency': 2
}
```

**4. Run the Generator**
```python
from master_workflow import CoachingPlanGenerator

# Initialize
generator = CoachingPlanGenerator(output_dir="./outputs")

# Generate everything
results = generator.generate_complete_plan(athlete_data)

# Done! Check ./outputs/ for all files
```

---

## What You Get

After running the generator, you'll find in `./outputs/`:

1. **`{Name}_scoring_report.json`** - Detailed system analysis
2. **`{Name}_Executive_Summary.md`** - High-level plan overview
3. **`{Name}_workouts.json`** - Structured workout library
4. **`{Name}_Training_Guide.docx`** - Complete training manual (50+ pages)
5. **`zwo_files/`** - 21+ workout files for Zwift/TrainingPeaks

---

## Typical Output Example

```
✅ COMPLETE! ALL FILES GENERATED SUCCESSFULLY

📦 GENERATED FILES:
  • scoring_report: ./outputs/John_Doe_scoring_report.json
  • executive_summary: ./outputs/John_Doe_Executive_Summary.md
  • workouts_json: ./outputs/John_Doe_workouts.json
  • zwo_files: 21 files in ./outputs/zwo_files
  • training_guide: ./outputs/John_Doe_Training_Guide.docx

🎉 Your personalized training plan is ready!

Recommended System: GOAT (Gravel Optimized Adaptive System)
Score: 9.35/10 (Excellent)
```

---

## Understanding The Scoring

The system scores 13 periodization models across 5 dimensions:

| Score Range | Meaning | Action |
|-------------|---------|--------|
| 9.0-10.0 | Excellent | Highly recommended - proceed with confidence |
| 7.0-8.9 | Good | Recommended with minor compromises |
| 5.5-6.9 | Marginal | Workable but significant limitations |
| <5.5 | Poor | Not recommended - major conflicts |

### The 5 Scoring Dimensions

1. **Time Efficiency** (20%) - Matches available training hours
2. **Recovery Friendly** (25%) - Matches recovery capacity
3. **Event Specificity** (20%) - Develops right capacities for goal
4. **Addresses Weaknesses** (20%) - Targets athlete's limiters
5. **Adaptability** (15%) - Handles life/travel constraints

---

## Customizing For Your Use Case

### Different Event Types

**Ultra-Endurance Events** (Unbound 200, 300, etc.)
```python
'primary_goal': 'Unbound 200',
'sport': 'Gravel',
# System will favor: GOAT, Polarized, Traditional
```

**Time Trials**
```python
'primary_goal': 'Pro Nationals TT',
'sport': 'Road/TT',
# System will favor: GOAT, Sweet Spot, Block Periodization
```

**Stage Racing**
```python
'primary_goal': 'Tour of the Battenkill',
'sport': 'Road',
# System will favor: Block, Critical Power, Traditional
```

**Century Rides**
```python
'primary_goal': 'Century Ride',
'sport': 'Cycling',
# System will favor: Traditional, Polarized, Sweet Spot
```

### Time-Constrained Athletes

```python
'training_hours_per_week': 6,
'weekday_hours_available': {
    'Monday': 0,
    'Tuesday': 1.0,
    'Wednesday': 0,
    'Thursday': 1.0,
    'Friday': 0
},
'weekend_hours_available': {
    'Saturday': 2.5,
    'Sunday': 1.5
}
# System will favor: Sweet Spot, HIIT-Focused, Autoregulated
```

### Recovery-Challenged Athletes

```python
'sleep_hours': 6.5,
'job_stress_level': 'high',
'day_to_day_feeling': 'tired',
'work_hours_per_week': 60,
# System will favor: Polarized, Autoregulated, MAF
# System will avoid: HIIT, Double-Threshold, Block
```

---

## Integration Examples

### Google Forms → Training Plan

```python
import gspread
from master_workflow import CoachingPlanGenerator

# 1. Connect to Google Sheets
gc = gspread.service_account()
sheet = gc.open("Athlete Questionnaires").sheet1

# 2. Get latest response
latest = sheet.get_all_records()[-1]

# 3. Map form fields to questionnaire_data
questionnaire_data = {
    'name': latest['Name'],
    'email': latest['Email'],
    'age': int(latest['Age']),
    'primary_goal': latest['Primary Goal'],
    'primary_goal_date': latest['Goal Date'],
    # ... map all fields
}

# 4. Generate plan
generator = CoachingPlanGenerator()
results = generator.generate_complete_plan(questionnaire_data)

# 5. Email files to athlete
# (your email sending code here)
```

### API Endpoint

```python
from flask import Flask, request, jsonify, send_file
from master_workflow import CoachingPlanGenerator
import os

app = Flask(__name__)

@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    data = request.json
    
    # Generate plan
    generator = CoachingPlanGenerator(output_dir="./temp_outputs")
    results = generator.generate_complete_plan(data)
    
    # Return download links
    return jsonify({
        'status': 'success',
        'athlete': data['name'],
        'recommended_system': generator.recommended_system,
        'score': generator.scoring_report['recommended_score'],
        'downloads': {
            'guide': f"/download/guide/{data['name']}",
            'workouts': f"/download/workouts/{data['name']}",
            'summary': f"/download/summary/{data['name']}"
        }
    })

@app.route('/download/guide/<athlete>')
def download_guide(athlete):
    filepath = f"./temp_outputs/{athlete}_Training_Guide.docx"
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
```

---

## Troubleshooting

### "Module not found" Error
```bash
# Make sure all 4 Python files are in the same directory
ls -l *.py
# Should show:
# athlete_analysis_system.py
# workout_generator.py  
# guide_generator.py
# master_workflow.py
```

### "TypeError: non-default argument follows default argument"
```python
# Check your AthleteProfile dataclass
# All required fields MUST come before optional fields
# Required fields: name, email, age, goal, date, etc.
# Optional fields: those with = default_value
```

### "No such file or directory"
```python
# Create output directory first
import os
os.makedirs("./outputs", exist_ok=True)

# Then run generator with that path
generator = CoachingPlanGenerator(output_dir="./outputs")
```

### Scoring Seems Wrong
```python
# Verify questionnaire data completeness
# Missing fields use defaults which may not be accurate

# Check these key fields:
# - training_hours_per_week
# - weekday/weekend availability
# - strengths and weaknesses
# - day_to_day_feeling
# - job_stress_level

# More complete data = more accurate scoring
```

---

## Advanced Usage

### Generate Only Specific Components

```python
from master_workflow import CoachingPlanGenerator

generator = CoachingPlanGenerator()

# Just load and score
athlete = generator.load_athlete_from_questionnaire(data)
report = generator.analyze_and_score_systems()

# Just generate workouts
workouts = generator.generate_workouts(num_weeks=12)

# Just export to ZWO
zwo_files = generator.export_to_zwo(workouts)

# Just generate guide
guide_path = generator.generate_training_guide()
```

### Custom Number of Workout Weeks

```python
# Generate 12 weeks instead of default 4
workouts = generator.generate_workouts(num_weeks=12)

# This creates 12 weeks × ~6 workouts/week = ~72 workouts
# Useful for longer training blocks
```

### Access Scoring Details

```python
# After analyze_and_score_systems()
report = generator.scoring_report

# Get all scores
for system in report['all_scores']:
    print(f"{system['system_name']}: {system['total_score']:.2f}")
    
    # Get reasoning for each category
    for category, reason in system['reasoning'].items():
        print(f"  {category}: {reason}")

# Get just top 5
top_5 = report['all_scores'][:5]
```

---

## Next Steps

1. **Test with your own data** - Modify the example questionnaire
2. **Review generated files** - Check the outputs directory
3. **Customize as needed** - Edit scoring weights, add systems, modify guide
4. **Integrate into your workflow** - Google Forms, API, manual process
5. **Iterate based on feedback** - Refine scoring algorithm

---

## Support

**Questions?** Check the full README: `README_Coaching_System.md`

**Example Files:** See Tyrel Fuchs test case in `master_workflow.py`

**Need Help?** Email: gravelgodcoaching@gmail.com

---

**You're ready to generate training plans! 🚴💨**

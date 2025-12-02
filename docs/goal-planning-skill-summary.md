# Goal Planning Skill - Summary

## What This Skill Does

The goal-planning skill codifies your Goal → Plan → Execute framework into a reusable tool that helps users:

1. Set SMARRT goals (Specific, Measurable, Achievable, Relevant, Risky, Time-bound)
2. Create comprehensive plans by:
   - Identifying what the goal actually requires across ALL domains
   - Assessing current state honestly
   - Distinguishing limiters from weaknesses
   - Prioritizing what actually matters
   - Designing progression from current state to goal
3. Turn actions into habits through systematic execution

## Key Innovation: Limiters vs Weaknesses

The skill's core contribution is teaching Claude to distinguish between:
- **Weakness**: Something you're not good at
- **Limiter**: A weakness that will ACTUALLY prevent goal achievement

This prevents wasting time on things that don't matter for the specific goal.

## Structure

The skill contains:

### SKILL.md (main file)
- When to use the skill
- Core process overview (Goal → Plan → Execute)
- Detailed framework for each phase
- Critical principles and common mistakes
- Example application (Unbound podium goal)
- Tone guidance

### references/assessment-domains.md
Comprehensive list of domains to assess:
- Physical
- Equipment
- Technical
- Tactical
- Nutritional
- Psychological
- Life Management
- Communication & Social
- Environmental/External
- Coaching Ability
- Competition Preparation

### references/methodology.md
Detailed framework explanation:
- SMARRT goal framework
- Five planning steps (Requirements → Current State → Limiters → Prioritize → Progression)
- Practices vs Actions distinction
- 5-S Formula for actions
- Key principles and common mistakes

## How Claude Uses It

When a user says something like:
- "I want to achieve [goal X]"
- "I'm training but not making progress"
- "Help me create a plan to [accomplish something]"
- "I don't know what to focus on"

Claude will:
1. Load the skill
2. Walk them through the framework systematically
3. Load assessment-domains.md when identifying requirements
4. Load methodology.md when they need deeper explanation
5. Push for comprehensive assessment (not just physical)
6. Emphasize limiter vs weakness distinction
7. Help prioritize ruthlessly
8. Keep the plan simple and actionable

## Use Cases

**Athletic goals**: Training plans, race preparation, performance improvement
**Professional goals**: Career advancement, skill development, project completion
**Personal development**: Health, habits, learning new skills
**Any complex achievement**: Anything requiring systematic planning and execution

## Installation

Upload the `goal-planning.skill` file to Claude via the Skills menu. Claude will then have access to this framework for helping users set and achieve meaningful goals.

## What Makes This Different

Most planning approaches:
- Only consider obvious factors (physical training for athletic goals)
- Treat all weaknesses equally
- Use generic, one-size-fits-all plans
- Skip the honest assessment phase

This framework:
- Assesses comprehensively across ALL relevant domains
- Distinguishes limiters from weaknesses
- Creates individualized plans based on specific gaps
- Requires brutal honesty about current state
- Prioritizes ruthlessly based on what actually prevents goal achievement

The skill makes Claude systematically better at helping people achieve hard things.
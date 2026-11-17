# SupeRR Selector
## Cricket Pressure Performance Intelligence

A Python-based cricket analytics project that identifies players who perform effectively under pressure using ball-by-ball match data.

## Dataset
- Ball-by-ball delivery records
- Match information
- Competition information
- Team and player mappings

Scope: T20 Internationals and IPL matches from 2022 onward.

## Technology
- Python
- Pandas
- NumPy
- Plotly
- Matplotlib
- Seaborn
- Jupyter Notebook

## Workflow
1. Data understanding
2. Data cleaning
3. Data auditing and validation
4. Pressure detection
5. Batting pressure analysis
6. Bowling pressure analysis
7. Player rating generation
8. Interactive dashboard

## Pressure Detection

Pressure is measured before each delivery.

Second innings:
- Required run rate >= 9
- Final 18 legal balls with required run rate >= 7
- Six or more wickets lost with 36 or fewer legal balls remaining

First innings:
- Four or more wickets lost after 70% of available legal balls
- At least 85% of available legal balls completed

Super Overs are excluded from regular rankings.

## Player Rating Methodology

### Batting
- Pressure runs
- Pressure balls faced
- Pressure strike rate
- Expected performance against non-pressure baseline
- Reliability adjustment

### Bowling
- Pressure runs conceded
- Pressure legal balls
- Pressure wickets
- Pressure economy
- Expected performance against non-pressure baseline
- Reliability adjustment

A score of 100 is the baseline reference.

Minimum sample:
- Batters: 30 pressure balls
- Bowlers: 30 pressure legal balls

## Current Results
- Qualified batters: 398
- Qualified bowlers: 322

## Dashboard

Interactive Plotly dashboard:
dashboard/superrr_selector_dashboard.html

Includes top 10 batters, top 10 bowlers, pressure scores and project statistics.

## Project Structure

- data/raw
- data/processed
- notebooks
- src
- visualizations
- dashboard
- reports
- requirements.txt

## Future Improvements
- Player comparison
- Team-level analysis
- Role-based rankings
- Advanced pressure prediction
- Web-based dashboard

## Author
Cricket analytics portfolio project.

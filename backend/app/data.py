"""In-memory placeholder data for the Sensory Lab workspace.

No database yet; this module is the single source of placeholder data that
the backend API serves until persistence is introduced.
"""

SUMMARY = {
    "lab_name": "Sensory Lab",
    "metrics": {
        "active_experiments": 4,
        "tests_this_week": 7,
        "panelists": 24,
        "panels": 5,
    },
    "recent_activity": [
        {"when": "Today 09:12", "what": "Test 'Triangle test — New recipe A' finished", "kind": "test"},
        {"when": "Yesterday 16:40", "what": "Panel 'Texture panel' recruited 3 new panelists", "kind": "panel"},
        {"when": "Yesterday 11:05", "what": "Experiment 'Cracker reformulation' created", "kind": "experiment"},
        {"when": "Mon 10:22", "what": "Attribute set 'Appearance' updated", "kind": "library"},
    ],
    "groups": [
        {"key": "overview", "name": "Overview", "description": "Experiments, projects and individual workloads."},
        {"key": "library", "name": "Library", "description": "Test methods, panelists, panels and attribute sets."},
        {"key": "lab", "name": "Lab", "description": "Run experiments and tests — blind codes and ballots."},
        {"key": "analyze", "name": "Analyze", "description": "ANOVA, correlations, panel performance and trends."},
    ],
}

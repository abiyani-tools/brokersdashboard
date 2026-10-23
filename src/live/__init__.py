"""Live-mode input layer for the broker ADR engine (LIVE_SPEC.md, items E1, E2, E4, E5, E6).

periods    E1  FY / quarter / month ranges from sb_calendar; missing calibration raises.
loader     E2  disclosure facts (reviewed first) and exchange volumes, with source precedence.
guards     E4  "insufficient data" results instead of silent zeros or short windows.
integrity  E5  pre-run checks on the volumes and facts; a blocking issue stops publishing.
db         E6  snapshot reader and Supabase reader (key from SUPABASE_SERVICE_KEY only).

Parity mode does not use this package.
"""

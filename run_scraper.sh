#!/bin/bash
# Vietnam Job Scraper – scheduled runner
# Usage: ./run_scraper.sh

VENV_PYTHON="/home/amrba/job_scraper/venv/bin/python3"
SCRAPER="/home/amrba/job_scraper/vietnam_scraper.py"
LOG="${HOME}/job_scraper/vietnam/scraper.log"

echo "===== Scraper run started: $(date) =====" >> "$LOG"

# Activate venv and run
"$VENV_PYTHON" "$SCRAPER" >> "$LOG" 2>&1
EXIT_CODE=$?

echo "===== Scraper run finished: $(date) | exit=$EXIT_CODE =====" >> "$LOG"
exit $EXIT_CODE

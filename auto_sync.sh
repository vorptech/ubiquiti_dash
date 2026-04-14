#!/bin/bash
cd /workspace/ubiquiti_dash
git add .
git commit -m "auto-sync: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

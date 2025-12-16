#!/bin/bash
# Reddit Digest - Cron Runner Script
# Place this in your WSL server and run via cron

# Configuration - EDIT THESE VALUES
export SUBREDDITS="cfb,nfl,nba,baseball,codcompetetive,soccer,overemployed,MichiganWolverines,DetroitLions,DetroitPistons,BillSimmons"

# Default webhook (fallback for subreddits without specific channel)
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1450208606199877733/WeBNJSX3HdBzGXG30JxKw2itHUhb2YQxo3bl3CPDPVnx8HSKdVrGomj606UMRaoNu-U9"

# Per-subreddit webhooks (JSON format)
export DISCORD_WEBHOOKS='{
  "nba": "https://discord.com/api/webhooks/1450292136221085739/vMVao0B5mOUMS4kDGrSJsA9IpVjM-5p-cYnsqhwgIq2FEnD0rOTq_NsCoiGNwfYIiVtI",
  "cfb": "https://discord.com/api/webhooks/1450292241556963339/6FDHUhYNi0CshJL-vRCwCOtjk6Xg6xPKA8HHpvGRlBm7BABEg7TJPEGBVJi7l4Jn31O5",
  "nfl": "https://discord.com/api/webhooks/1450292473992708186/vGDCNku74DawkojbcbxCpeS3sBVnn-V6btnmmOIh5p_ZAmMPZ6LeOVnq-xFE8PWVtzTI"
}'

# Optional: HTML generation and GitHub push
# export OUTPUT_HTML_PATH="/path/to/Portfolio/reddit-digest.html"
# export GITHUB_PUSH="true"
# export GITHUB_REPO_PATH="/path/to/Portfolio"

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run the script
python3 reddit_digest_scraper.py

# Log completion
echo "[$(date)] Reddit digest completed" >> /var/log/reddit-digest.log

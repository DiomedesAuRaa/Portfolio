# Reddit Daily Digest - GitHub Actions Setup

This project automatically generates a Reddit digest twice daily (4 AM and 4 PM EST) using GitHub Actions and sends it to Discord.

## Features

- Fetches top posts from your favorite subreddits using Reddit's official API
- Sends digest to Discord with per-subreddit webhook support
- Optionally generates HTML page for GitHub Pages
- Runs automatically via GitHub Actions at 4 AM and 4 PM EST

## Setup Instructions

### 1. Get Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in the form:
   - **name**: `Reddit Digest Bot` (or any name you prefer)
   - **App type**: Select **"script"**
   - **description**: Optional
   - **about url**: Optional
   - **redirect uri**: Use `http://localhost:8080` (required but not used)
4. Click "Create app"
5. Note down your credentials:
   - **Client ID**: The string under "personal use script"
   - **Client Secret**: The string next to "secret"

### 2. Set Up GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `REDDIT_CLIENT_ID` | Your Reddit app client ID | `abc123XYZ456` |
| `REDDIT_CLIENT_SECRET` | Your Reddit app client secret | `secret123-abc456` |
| `DISCORD_WEBHOOK_URL` | Default Discord webhook URL (fallback) | `https://discord.com/api/webhooks/...` |
| `DISCORD_WEBHOOKS` | Per-subreddit webhooks (optional, JSON format) | See below |

#### Discord Webhooks Setup

**To create a Discord webhook:**
1. Open Discord and go to your server
2. Right-click the channel → **Edit Channel** → **Integrations** → **Webhooks**
3. Click **New Webhook** → Copy the Webhook URL

**Default webhook** (`DISCORD_WEBHOOK_URL`):
```
https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

**Per-subreddit webhooks** (`DISCORD_WEBHOOKS`, optional):
```json
{
  "nba": "https://discord.com/api/webhooks/ID1/TOKEN1",
  "cfb": "https://discord.com/api/webhooks/ID2/TOKEN2",
  "nfl": "https://discord.com/api/webhooks/ID3/TOKEN3"
}
```

Subreddits not listed will use the default webhook.

### 3. Configure Subreddits

Edit `.github/workflows/reddit-digest.yml` and update the `SUBREDDITS` environment variable:

```yaml
SUBREDDITS: 'cfb,nfl,nba,baseball,soccer,MichiganWolverines,DetroitLions'
```

### 4. Test the Workflow

1. Go to **Actions** tab in your GitHub repository
2. Click **Reddit Daily Digest** workflow
3. Click **Run workflow** → **Run workflow**
4. Check the workflow logs to ensure it runs successfully

### 5. Schedule

The workflow runs automatically at:
- **4:00 AM EST** (9:00 AM UTC)
- **4:00 PM EST** (9:00 PM UTC)

To change the schedule, edit the cron expressions in `.github/workflows/reddit-digest.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'   # 4 AM EST
  - cron: '0 21 * * *'  # 4 PM EST
```

## Optional: HTML Generation

To generate an HTML page and commit it to your repository:

1. Set `OUTPUT_HTML_PATH` in the workflow file:
```yaml
OUTPUT_HTML_PATH: 'reddit-digest.html'
```

2. Enable GitHub Pages:
   - Go to **Settings** → **Pages**
   - Set source to the branch with your HTML file

## Troubleshooting

### "Reddit API credentials not configured"
- Ensure `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` are set in GitHub Secrets
- Double-check the secret names match exactly (case-sensitive)

### "Error fetching posts from r/subreddit"
- Verify the subreddit name is correct
- Ensure your Reddit API credentials are valid
- Check if the subreddit is private or restricted

### Discord messages not sending
- Verify your Discord webhook URLs are correct
- Test the webhook URL using curl or a webhook tester
- Check if the Discord channel still exists

### Workflow not running on schedule
- GitHub Actions schedules can have delays of up to 15 minutes
- Manually trigger the workflow to test functionality
- Check the Actions tab for any errors

## Local Testing

To test locally (requires Reddit API credentials):

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export SUBREDDITS="python,technology"
export DISCORD_WEBHOOK_URL="your_webhook_url"

python3 reddit_digest_scraper.py
```

## Rate Limits

Reddit API rate limits:
- 60 requests per minute for authenticated users
- The script includes sleep delays to stay within limits

Discord webhook rate limits:
- 30 requests per minute per webhook
- 5 requests per second per webhook

## Files

- `.github/workflows/reddit-digest.yml` - GitHub Actions workflow
- `reddit_digest_scraper.py` - Main Python script
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Support

For issues with:
- **Reddit API**: https://www.reddit.com/dev/api
- **PRAW (Python Reddit API Wrapper)**: https://praw.readthedocs.io/
- **Discord Webhooks**: https://discord.com/developers/docs/resources/webhook

#!/usr/bin/env python3
"""
Reddit Daily Digest Generator (API Version)
Fetches top posts from favorite subreddits using Reddit's official API via PRAW
Generates:
1. Discord webhook messages with rich text (supports per-subreddit webhooks with fallback)
2. Static HTML page (optional - for GitHub Pages)

Usage:
    python reddit_digest_scraper.py

Environment Variables:
    REDDIT_CLIENT_ID: Reddit API client ID (required)
    REDDIT_CLIENT_SECRET: Reddit API client secret (required)
    REDDIT_USER_AGENT: Reddit API user agent (optional, defaults to 'RedditDigestBot/1.0')
    SUBREDDITS: Comma-separated list of subreddit names
    DISCORD_WEBHOOK_URL: Default Discord webhook URL (used as fallback)
    DISCORD_WEBHOOKS: JSON object mapping subreddit to webhook URL (optional)
                      Example: {"cfb": "url1", "nfl": "url2"}
    OUTPUT_HTML_PATH: Path to output HTML file (optional - skip HTML generation if not set)
    GITHUB_PUSH: Set to "true" to commit and push HTML to GitHub repo
    GITHUB_REPO_PATH: Path to local git repo (required if GITHUB_PUSH=true)
"""

import os
import sys
import json
import subprocess
import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import html as html_module
import praw

# Configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'RedditDigestBot/1.0')
SUBREDDITS = os.getenv('SUBREDDITS', 'python,technology,news').split(',')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')
DISCORD_WEBHOOKS_JSON = os.getenv('DISCORD_WEBHOOKS', '')
OUTPUT_HTML_PATH = os.getenv('OUTPUT_HTML_PATH', '')
GITHUB_PUSH = os.getenv('GITHUB_PUSH', 'false').lower() == 'true'
GITHUB_REPO_PATH = os.getenv('GITHUB_REPO_PATH', '')
MAX_POSTS_PER_SUB = 5
MAX_COMMENTS_PER_POST = 5

# Parse subreddit-specific webhooks
DISCORD_WEBHOOKS = {}
if DISCORD_WEBHOOKS_JSON:
    try:
        DISCORD_WEBHOOKS = json.loads(DISCORD_WEBHOOKS_JSON)
    except json.JSONDecodeError:
        print("Warning: Could not parse DISCORD_WEBHOOKS JSON, using default webhook")
        DISCORD_WEBHOOKS = {}


class RedditFetcher:
    """Reddit data fetcher using official Reddit API via PRAW"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """Initialize Reddit API connection"""
        if not client_id or not client_secret:
            raise ValueError("Reddit API credentials (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET) are required")
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        print("✓ Connected to Reddit API")
    
    def get_top_posts(self, subreddit: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top posts from a subreddit for the day"""
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            posts = []
            
            for submission in subreddit_obj.top(time_filter='day', limit=limit):
                posts.append({
                    'title': submission.title,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'score': submission.score,
                    'url': f"https://www.reddit.com{submission.permalink}",
                    'selftext': submission.selftext if hasattr(submission, 'selftext') else '',
                    'created_utc': submission.created_utc,
                    'num_comments': submission.num_comments,
                    'id': submission.id,
                    'subreddit': submission.subreddit.display_name,
                    'link_url': submission.url if hasattr(submission, 'url') else '',
                    'is_self': submission.is_self,
                    'upvote_ratio': submission.upvote_ratio,
                })
            
            return posts
            
        except Exception as e:
            print(f"Error fetching posts from r/{subreddit}: {e}")
            return []
    
    def get_top_comments(self, submission_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top comments for a post"""
        try:
            submission = self.reddit.submission(id=submission_id)
            submission.comment_sort = 'top'
            submission.comments.replace_more(limit=0)
            
            comments = []
            for comment in submission.comments[:limit]:
                if hasattr(comment, 'body'):
                    comments.append({
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'body': comment.body,
                        'score': comment.score
                    })
            
            return comments
            
        except Exception as e:
            print(f"Error fetching comments for post {submission_id}: {e}")
            return []
    
    def fetch_all_data(self, subreddits: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch all posts and comments for given subreddits"""
        digest_data = {}
        
        for subreddit in subreddits:
            subreddit = subreddit.strip()
            if not subreddit:
                continue
                
            print(f"\nFetching posts from r/{subreddit}...")
            
            posts = self.get_top_posts(subreddit, MAX_POSTS_PER_SUB)
            
            if not posts:
                print(f"  ✗ No posts found for r/{subreddit}")
                continue
            
            for post in posts:
                print(f"  Fetching comments for: {post['title'][:50]}...")
                comments = self.get_top_comments(post['id'], MAX_COMMENTS_PER_POST)
                post['comments'] = comments
                time.sleep(0.5)
            
            digest_data[subreddit] = posts
            print(f"  ✓ Fetched {len(posts)} posts from r/{subreddit}")
            time.sleep(1)
        
        return digest_data


class DiscordSender:
    """Send messages to Discord via webhook with rich text - supports per-subreddit webhooks"""
    
    def __init__(self, default_webhook_url: str, subreddit_webhooks: Dict[str, str] = None):
        self.default_webhook_url = default_webhook_url
        self.subreddit_webhooks = subreddit_webhooks or {}
    
    def send_digest(self, digest_data: Dict[str, Any]):
        """Send Reddit digest to Discord - each subreddit to its own webhook or fallback"""
        if not self.default_webhook_url and not self.subreddit_webhooks:
            print("Discord webhook URL not configured, skipping Discord message")
            return
        
        date_str = datetime.now().strftime('%B %d, %Y')
        
        for subreddit, posts in digest_data.items():
            # Get webhook for this subreddit (fall back to default)
            webhook_url = self.subreddit_webhooks.get(subreddit, self.default_webhook_url)
            
            if not webhook_url:
                print(f"  ⚠️  No webhook configured for r/{subreddit}, skipping")
                continue
            
            # Indicate which webhook type is being used
            if subreddit in self.subreddit_webhooks:
                print(f"  Sending r/{subreddit} to dedicated channel...")
            else:
                print(f"  Sending r/{subreddit} to default channel...")
            
            # Send header message for this subreddit
            header = f"📰 **r/{subreddit} Daily Digest - {date_str}**\n" + "="*50
            self._send_message(header, webhook_url)
            
            for i, post in enumerate(posts, 1):
                post_msg = self._format_post(i, post)
                self._send_message(post_msg, webhook_url)
                time.sleep(0.5)
            
            # Send footer
            footer = f"\n{'='*50}\n✅ **End of r/{subreddit} digest**"
            self._send_message(footer, webhook_url)
            time.sleep(1)
    
    def _format_post(self, index: int, post: Dict[str, Any]) -> str:
        """Format a post with full details for Discord"""
        msg = f"\n**{index}. {post['title']}**\n"
        msg += f"👤 u/{post['author']} | ⬆️ {post['score']} ({int(post.get('upvote_ratio', 0) * 100)}%) | 💬 {post['num_comments']} comments\n\n"
        
        # Full post content
        if post['selftext']:
            selftext = post['selftext']
            if len(selftext) > 1500:
                selftext = selftext[:1497] + "..."
            msg += f"**Post Content:**\n{selftext}\n\n"
        elif not post['is_self'] and post['link_url']:
            msg += f"**Link:** {post['link_url']}\n\n"
        
        msg += f"**Reddit URL:** {post['url']}\n\n"
        
        # Top comments with full text
        if post['comments']:
            msg += f"**💬 Top {len(post['comments'])} Comments:**\n"
            for j, comment in enumerate(post['comments'], 1):
                comment_body = comment['body']
                if len(comment_body) > 400:
                    comment_body = comment_body[:397] + "..."
                msg += f"\n`{j}.` **u/{comment['author']}** (⬆️ {comment['score']})\n{comment_body}\n"
        
        msg += "\n" + "─"*40
        return msg
    
    def _send_message(self, content: str, webhook_url: str):
        """Send a single message to a specific Discord webhook"""
        if len(content) > 1900:
            chunks = self._smart_split(content, 1900)
            for chunk in chunks:
                self._do_send({'content': chunk}, webhook_url)
                time.sleep(0.5)
        else:
            self._do_send({'content': content}, webhook_url)
    
    def _smart_split(self, text: str, max_length: int) -> List[str]:
        """Split text intelligently on newlines"""
        chunks = []
        current_chunk = ""
        
        for line in text.split('\n'):
            if len(current_chunk) + len(line) + 1 > max_length:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = line
            else:
                if current_chunk:
                    current_chunk += '\n' + line
                else:
                    current_chunk = line
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _do_send(self, payload: Dict, webhook_url: str):
        """Actually send the webhook request"""
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending to Discord: {e}")


class HTMLGenerator:
    """Generate static HTML page with full content"""
    
    def generate(self, digest_data: Dict[str, Any], output_path: str):
        """Generate HTML page with Reddit digest"""
        date_str = datetime.now().strftime('%B %d, %Y')
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reddit Daily Digest - {date_str}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #1a1a1b;
            background: #dae0e6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        header {{
            background: #FF4500;
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        header .date {{
            font-size: 1.2em;
            opacity: 0.95;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .subreddit {{
            margin-bottom: 60px;
        }}
        
        .subreddit-header {{
            background: #FF4500;
            color: white;
            padding: 15px 25px;
            border-radius: 6px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .subreddit-header h2 {{
            font-size: 1.8em;
            font-weight: 600;
        }}
        
        .post {{
            background: #ffffff;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            transition: box-shadow 0.2s;
        }}
        
        .post:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .post-header {{
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #edeff1;
        }}
        
        .post-title {{
            font-size: 1.4em;
            color: #1a1a1b;
            margin-bottom: 10px;
            font-weight: 600;
            line-height: 1.3;
        }}
        
        .post-meta {{
            color: #7c7c7c;
            font-size: 0.85em;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .post-meta span {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        
        .upvote-ratio {{
            color: #FF4500;
            font-weight: 600;
        }}
        
        .post-content {{
            color: #1a1a1b;
            margin: 15px 0;
            line-height: 1.8;
            padding: 15px;
            background: #f6f7f8;
            border-radius: 6px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .post-link {{
            display: inline-block;
            color: #0079D3;
            text-decoration: none;
            font-weight: 600;
            margin: 10px 0;
            padding: 8px 16px;
            background: #f6f7f8;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        
        .post-link:hover {{
            background: #e9eaeb;
            text-decoration: underline;
        }}
        
        .external-link {{
            display: block;
            color: #0079D3;
            text-decoration: none;
            margin: 10px 0;
            word-break: break-all;
            font-size: 0.9em;
        }}
        
        .comments {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #edeff1;
        }}
        
        .comments-header {{
            font-weight: 600;
            color: #1a1a1b;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .comment {{
            background: #f6f7f8;
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 6px;
            border-left: 3px solid #FF4500;
        }}
        
        .comment-meta {{
            color: #7c7c7c;
            font-size: 0.85em;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .comment-author {{
            color: #0079D3;
        }}
        
        .comment-score {{
            color: #FF4500;
        }}
        
        .comment-body {{
            color: #1a1a1b;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        footer {{
            background: #1a1a1b;
            color: white;
            text-align: center;
            padding: 20px;
        }}
        
        footer p {{
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            header {{
                padding: 20px;
            }}
            
            header h1 {{
                font-size: 1.8em;
            }}
            
            .post-title {{
                font-size: 1.2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 Reddit Daily Digest</h1>
            <div class="date">{date_str}</div>
        </header>
        
        <div class="content">
"""
        
        for subreddit, posts in digest_data.items():
            html_content += f"""
            <div class="subreddit">
                <div class="subreddit-header">
                    <h2>r/{html_module.escape(subreddit)}</h2>
                </div>
"""
            
            for i, post in enumerate(posts, 1):
                upvote_pct = int(post.get('upvote_ratio', 0) * 100)
                
                html_content += f"""
                <div class="post">
                    <div class="post-header">
                        <div class="post-title">{i}. {html_module.escape(post['title'])}</div>
                        <div class="post-meta">
                            <span>👤 u/{html_module.escape(post['author'])}</span>
                            <span>⬆️ {post['score']} points</span>
                            <span class="upvote-ratio">{upvote_pct}% upvoted</span>
                            <span>💬 {post['num_comments']} comments</span>
                        </div>
                    </div>
"""
                
                if post['selftext']:
                    html_content += f"""
                    <div class="post-content">{html_module.escape(post['selftext'])}</div>
"""
                elif not post['is_self'] and post['link_url']:
                    html_content += f"""
                    <a href="{html_module.escape(post['link_url'])}" class="external-link" target="_blank">
                        🔗 {html_module.escape(post['link_url'])}
                    </a>
"""
                
                html_content += f"""
                    <a href="{html_module.escape(post['url'])}" class="post-link" target="_blank">
                        View Full Discussion on Reddit →
                    </a>
"""
                
                if post['comments']:
                    html_content += """
                    <div class="comments">
                        <div class="comments-header">💬 Top Comments:</div>
"""
                    for j, comment in enumerate(post['comments'], 1):
                        html_content += f"""
                        <div class="comment">
                            <div class="comment-meta">
                                <span class="comment-author">u/{html_module.escape(comment['author'])}</span>
                                <span class="comment-score">• ⬆️ {comment['score']} points</span>
                            </div>
                            <div class="comment-body">{html_module.escape(comment['body'])}</div>
                        </div>
"""
                    html_content += """
                    </div>
"""
                
                html_content += """
                </div>
"""
            
            html_content += """
            </div>
"""
        
        html_content += f"""
        </div>
        
        <footer>
            <p>Generated automatically via GitHub Actions</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </footer>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML page generated: {output_path}")


def main():
    """Main execution function"""
    print("="*60)
    print("Reddit Daily Digest Generator (API Version)")
    print("="*60)
    
    # Validate Reddit API credentials
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("\nERROR: Reddit API credentials not configured!")
        print("Please set the following environment variables:")
        print("  - REDDIT_CLIENT_ID")
        print("  - REDDIT_CLIENT_SECRET")
        print("\nTo get these credentials:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Create an app (select 'script' type)")
        print("3. Use the client ID and secret in GitHub Secrets")
        sys.exit(1)
    
    subreddits = [s.strip() for s in SUBREDDITS if s.strip()]
    
    if not subreddits:
        print("ERROR: No subreddits configured!")
        print("Please set SUBREDDITS environment variable")
        sys.exit(1)
    
    print(f"\nConfigured subreddits: {', '.join(subreddits)}")
    print(f"Posts per subreddit: {MAX_POSTS_PER_SUB}")
    print(f"Comments per post: {MAX_COMMENTS_PER_POST}")
    
    # Show webhook configuration
    if DISCORD_WEBHOOKS:
        print(f"\nPer-subreddit webhooks configured: {list(DISCORD_WEBHOOKS.keys())}")
    if DISCORD_WEBHOOK_URL:
        print(f"Default webhook: configured (fallback for unconfigured subreddits)")
    
    print("\nInitializing Reddit API client...")
    try:
        fetcher = RedditFetcher(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    digest_data = fetcher.fetch_all_data(subreddits)
    
    if not digest_data:
        print("\n✗ No data fetched. Exiting.")
        sys.exit(1)
    
    print(f"\n✓ Successfully fetched data from {len(digest_data)} subreddits")
    
    # Generate HTML page (optional)
    if OUTPUT_HTML_PATH:
        print("\nGenerating HTML page...")
        html_gen = HTMLGenerator()
        html_gen.generate(digest_data, OUTPUT_HTML_PATH)
        
        # Push to GitHub if configured
        if GITHUB_PUSH and GITHUB_REPO_PATH:
            print("\nPushing to GitHub...")
            push_to_github(GITHUB_REPO_PATH, OUTPUT_HTML_PATH)
    else:
        print("\nSkipping HTML generation (OUTPUT_HTML_PATH not set)")
    
    # Send to Discord
    if DISCORD_WEBHOOK_URL or DISCORD_WEBHOOKS:
        print("\nSending to Discord...")
        discord_sender = DiscordSender(DISCORD_WEBHOOK_URL, DISCORD_WEBHOOKS)
        discord_sender.send_digest(digest_data)
        print("✓ Discord notifications sent")
    else:
        print("\nSkipping Discord (no webhook URL configured)")
    
    print("\n" + "="*60)
    print("✓ Reddit Daily Digest Complete!")
    print("="*60)


def push_to_github(repo_path: str, html_file: str):
    """Commit and push HTML file to GitHub"""
    try:
        import shutil
        # Copy HTML to repo
        dest_path = os.path.join(repo_path, os.path.basename(html_file))
        if html_file != dest_path:
            shutil.copy(html_file, dest_path)
        
        # Git commands
        subprocess.run(['git', '-C', repo_path, 'add', os.path.basename(html_file)], check=True)
        
        # Check if there are changes to commit
        result = subprocess.run(['git', '-C', repo_path, 'diff', '--staged', '--quiet'])
        if result.returncode != 0:
            date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            subprocess.run(['git', '-C', repo_path, 'commit', '-m', f'Update Reddit digest - {date_str}'], check=True)
            subprocess.run(['git', '-C', repo_path, 'push'], check=True)
            print("✓ Pushed to GitHub")
        else:
            print("No changes to commit")
    except Exception as e:
        print(f"Error pushing to GitHub: {e}")


if __name__ == '__main__':
    main()

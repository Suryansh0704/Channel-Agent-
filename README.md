# Channel-Agent-

Fully autonomous YouTube Shorts optimization system for Dark Psychology niche.

## Schedule

- **9:00 AM IST** -- Run 1: Analytics + Evolution + Video #1 Upload
- **6:00 PM IST** -- Run 2: Analytics + Evolution + Video #2 Upload
- **Sunday 9:00 AM** -- Competitor monitoring + Batch script generation

## Setup

### 1. GitHub Secrets

Add these secrets to your Channel-Agent- repo:

| Secret | Source |
|--------|--------|
| YT_API_KEY | Google Cloud Console |
| CHANNEL_ID | Your YouTube channel ID |
| YT_REFRESH_TOKEN | OAuth 2.0 flow |
| YT_CLIENT_ID | Google Cloud Console |
| YT_CLIENT_SECRET | Google Cloud Console |
| PAT_TOKEN | GitHub Personal Access Token (repo scope) |
| GEMINI_API_KEY | Google AI Studio |
| EMAIL_SERVICE_API_KEY | SendGrid / Resend / Gmail |
| EMAIL_FROM_ADDRESS | sender@yourdomain.com |
| EMAIL_TO_ADDRESS | your-email@example.com |

### 2. Update OWNER in push_configs.py

Change `OWNER = 'Suryansh0704'` to your GitHub username.

### 3. Update Repo Names in push_configs.py

Change repo names in REPO_MAP to match your actual repo names.

### 4. Configure Email Service

In `scripts/send_email_report.py`, configure your SMTP or email API settings.

## How It Works

1. **Health Check** -- Verifies all systems before starting
2. **Analytics** -- Collects last 50 videos data from YouTube
3. **Comment Analysis** -- Sentiment analysis on latest video comments
4. **Evolution** -- Compares latest vs last 10, generates optimized configs
5. **Prompt Generation** -- Updates Gemini prompt with small daily changes
6. **Batch Scripts** -- Pre-generates 3 scripts for evening run
7. **Config Push** -- Safely pushes configs to all repos (validated + backup)
8. **Cross-Platform** -- Generates Instagram/TikTok metadata
9. **Email Report** -- Sends detailed report to your email

## Safety Features

- Config-only changes (never touches source code)
- Fallback defaults in every repo
- Statistical significance gate (z-score > 1.96)
- Atomic config updates (backup -> test -> merge)
- Gradual changes only (+/-0.5s cut speed, +/-10 WPM pace)
- Auto-rollback on 2 consecutive DISASTERS
- Prompt versioning (never lose a working prompt)
- Content fatigue detection with pivot mode
- Health check before every run

## File Structure

Channel-Agent-/ |-- .github/workflows/ | |-- channel-intelligence.yml # Main workflow (9 AM & 6 PM) | |-- health-check.yml # Every hour | |-- competitor-monitor.yml # Sundays |-- scripts/ | |-- analytics_collector.py # YouTube data | |-- evolve_configs.py # Compare & evolve | |-- generate_script_prompt.py # Prompt optimization | |-- push_configs.py # Safe config push | |-- comment_analyzer.py # Sentiment analysis | |-- competitor_monitor.py # Trend monitoring | |-- batch_generator.py # Pre-generate scripts | |-- cross_platform_adapter.py # Multi-platform | |-- health_check.py # Health endpoint | |-- send_email_report.py # Email reports | |-- gemini-prompt.json # Current active prompt | |-- validators/ | |-- config_schema.json # JSON schema | |-- validate_config.py # Validation engine |-- config/ | |-- video-generator-config.json | |-- audio-generator-config.json | |-- video-editor-config.json | |-- uploader-config.json | |-- script-prompt-config.json |-- data/ | |-- analytics.json | |-- competitor_trends.json | |-- comment_sentiment.json | |-- cache/ |-- evolution/ | |-- history.json | |-- prompt_versions/ |-- pending_scripts/ |-- temp/ | |-- pending-configs/ |-- logs/ | |-- daily-reports/ | |-- errors/ |-- README.md

## Evolution Tiers

| Tier | Condition | Action |
|------|-----------|--------|
| BREAKTHROUGH | Better than best + z > 1.96 | Amplify winning settings (+15%) |
| IMPROVEMENT | Better than avg + z > 0.5 | Refine current approach (+10%) |
| NEUTRAL | Better than worst only | Small random mutation (+5%) |
| DISASTER | Worse than worst | Full reset to safe defaults |

## Features

- Multi-metric scoring (views + retention + engagement + CTR)
- Hook-specific A/B testing (question vs statement vs story vs number)
- Time-of-day upload optimization
- Competitor/trend monitoring (weekly)
- Auto-thumbnail text suggestions
- Comment sentiment analysis
- Seasonal/day-of-week pattern tracking
- Content fatigue detection with pivot mode
- ActivePieces failure recovery
- Script prompt versioning & rollback
- Audio voice A/B testing (pace, emphasis, volume)
- Auto-hashtag evolution
- Retention curve deep analysis
- Batch pre-generation (3 scripts)
- Cross-platform reuse (Instagram Reels + TikTok)

## Your Current Prompt

Your base prompt is locked in `scripts/gemini-prompt.json`. The system makes small daily optimizations to it but NEVER changes the Dark Psychology niche.

## Support

If something breaks, check:
1. `logs/health_check.json` -- system status
2. `logs/push_log.json` -- config push results
3. `evolution/history.json` -- evolution history
4. `logs/errors/` -- error logs

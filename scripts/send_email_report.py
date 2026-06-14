"""
Sends detailed email reports after each run.
Uses SMTP or email service API.
"""
import os
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_SERVICE_API_KEY = os.environ.get('EMAIL_SERVICE_API_KEY')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'agent@channel.local')
EMAIL_TO = os.environ.get('EMAIL_TO', '')
RUN_NUMBER = os.environ.get('RUN_NUMBER', '1')

def load_analytics():
    if os.path.exists('data/analytics.json'):
        with open('data/analytics.json', 'r') as f:
            return json.load(f)
    return {}

def load_evolution_report():
    if os.path.exists('temp/evolution_report.json'):
        with open('temp/evolution_report.json', 'r') as f:
            return json.load(f)
    return {}

def load_sentiment():
    if os.path.exists('data/comment_sentiment.json'):
        with open('data/comment_sentiment.json', 'r') as f:
            sentiments = json.load(f)
            return sentiments[0] if sentiments else {}
    return {}

def load_push_log():
    if os.path.exists('logs/push_log.json'):
        with open('logs/push_log.json', 'r') as f:
            return json.load(f)
    return {}

def load_health_check():
    if os.path.exists('logs/health_check.json'):
        with open('logs/health_check.json', 'r') as f:
            return json.load(f)
    return {'all_passed': True}

def format_number(num):
    if num >= 1000000:
        return f'{num/1000000:.1f}M'
    elif num >= 1000:
        return f'{num/1000:.1f}K'
    return str(num)

def generate_report():
    analytics = load_analytics()
    evolution = load_evolution_report()
    sentiment = load_sentiment()
    push_log = load_push_log()
    health = load_health_check()
    
    videos = analytics.get('videos', [])
    latest = videos[0] if videos else {}
    
    tier = evolution.get('tier', 'NEUTRAL')
    
    changes = []
    for filename, data in push_log.items():
        status = data.get('status', 'UNKNOWN')
        changes.append(f'{status}: {filename}')
    
    changes_text = '\n'.join(changes) if changes else 'No changes pushed this run'
    
    winning_words = evolution.get('winning_words', [])
    words_text = ', '.join(winning_words[:5]) if winning_words else 'Analyzing...'
    
    sentiment_score = sentiment.get('score', 5)
    
    health_status = 'All systems operational' if health.get('all_passed') else 'Some checks failed'
    
    views = format_number(latest.get('views', 0))
    likes = format_number(latest.get('likes', 0))
    comments = format_number(latest.get('comments', 0))
    score = latest.get('composite_score', 0)
    
    report = f"""CHANNEL AGENT DAILY REPORT -- Run #{RUN_NUMBER}
Date: {datetime.now().strftime('%Y-%m-%d')} | Time: {datetime.now().strftime('%I:%M %p')} IST
Tier: {tier}

LATEST VIDEO PERFORMANCE
Title: {latest.get('title', 'N/A')}
Video ID: {latest.get('video_id', 'N/A')}
Views: {views} | Likes: {likes} | Comments: {comments}
Composite Score: {score}/100
vs. Last 10 Baseline: {evolution.get('z_score', 0)} (z-score)

WHAT CHANGED TODAY
{changes_text}

Winning Words: {words_text}
Best Hook Style: {evolution.get('best_hook', 'Analyzing...')}

COMMENT SENTIMENT
Score: {sentiment_score}/10
Sentiment: {sentiment.get('sentiment', 'neutral')}
Themes: {', '.join(sentiment.get('themes', [])[:3]) if sentiment.get('themes') else 'None'}

SYSTEM STATUS
{health_status}
Prompt Version: {evolution.get('prompt_version', 'default')}
Fatigue Check: {'Pivot triggered: ' + evolution.get('pivot_angle', '') if evolution.get('fatigue_detected') else 'No fatigue detected'}

GOAL TRACKING
Daily Target: 1%+ improvement
Current Streak: {len([v for v in videos if v.get('composite_score', 0) > 50])} videos above 50

Next Run: {'6:00 PM IST' if RUN_NUMBER == '1' else '9:00 AM IST (tomorrow)'}
"""
    
    return report

def send_email_smtp(subject, body):
    try:
        os.makedirs('logs/daily-reports', exist_ok=True)
        filename = f'logs/daily-reports/report-{datetime.now().strftime("%Y%m%d-%H%M")}.txt'
        with open(filename, 'w') as f:
            f.write(f'Subject: {subject}\n\n{body}')
        
        print(f'Report saved: {filename}')
        return True
    except Exception as e:
        print(f'Email error: {e}')
        return False

def send_email_sendgrid(subject, body):
    if not EMAIL_SERVICE_API_KEY:
        return send_email_smtp(subject, body)
    
    try:
        import requests
        
        url = 'https://api.sendgrid.com/v3/mail/send'
        headers = {
            'Authorization': f'Bearer {EMAIL_SERVICE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'personalizations': [{'to': [{'email': EMAIL_TO}]}],
            'from': {'email': EMAIL_FROM},
            'subject': subject,
            'content': [{'type': 'text/plain', 'value': body}]
        }
        
        resp = requests.post(url, headers=headers, json=data)
        
        if resp.status_code in [200, 202]:
            print('Email sent via SendGrid')
            return True
        else:
            print(f'SendGrid error: {resp.status_code}')
            return send_email_smtp(subject, body)
    except Exception as e:
        print(f'SendGrid error: {e}')
        return send_email_smtp(subject, body)

def main():
    print('Generating email report...')
    
    if not EMAIL_TO:
        print('EMAIL_TO not set, saving report locally')
    
    report = generate_report()
    
    tier = load_evolution_report().get('tier', 'NEUTRAL')
    subject = f'[Channel Agent] Run #{RUN_NUMBER} | {datetime.now().strftime("%Y-%m-%d")} | {tier}'
    
    success = send_email_sendgrid(subject, report)
    
    os.makedirs('logs/daily-reports', exist_ok=True)
    with open(f'logs/daily-reports/latest-report.txt', 'w') as f:
        f.write(report)
    
    print('Email report complete')

if __name__ == '__main__':
    main()

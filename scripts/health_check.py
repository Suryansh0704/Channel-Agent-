"""
Health check endpoint for the system.
Verifies GitHub, YouTube API, and email service before each run.
"""
import os
import sys
import json
import requests
from datetime import datetime

PAT_TOKEN = os.environ.get('PAT_TOKEN')
YT_API_KEY = os.environ.get('YT_API_KEY')
EMAIL_SERVICE_API_KEY = os.environ.get('EMAIL_SERVICE_API_KEY')

def check_github_access():
    if not PAT_TOKEN:
        return False, 'PAT_TOKEN not set'
    
    headers = {'Authorization': f'token {PAT_TOKEN}'}
    resp = requests.get('https://api.github.com/user', headers=headers)
    
    if resp.status_code == 200:
        return True, f'Authenticated as {resp.json().get("login", "unknown")}'
    return False, f'GitHub API error: {resp.status_code}'

def check_youtube_api():
    if not YT_API_KEY:
        return False, 'YT_API_KEY not set'
    
    try:
        url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q=test&key={YT_API_KEY}'
        resp = requests.get(url)
        
        if resp.status_code == 200:
            return True, 'YouTube API accessible'
        elif resp.status_code == 403:
            return False, 'YouTube API quota exceeded or invalid key'
        else:
            return False, f'YouTube API error: {resp.status_code}'
    except Exception as e:
        return False, f'YouTube API connection error: {e}'

def check_email_service():
    if not EMAIL_SERVICE_API_KEY:
        return False, 'EMAIL_SERVICE_API_KEY not set (email reports disabled)'
    
    return True, 'Email service configured'

def check_repo_access():
    if not PAT_TOKEN:
        return False, 'PAT_TOKEN not set'
    
    repos = ['Video-generator-', 'Audio-generator-', 'Video-editor-', 'Channel-Agent-']
    headers = {'Authorization': f'token {PAT_TOKEN}'}
    
    failed = []
    for repo in repos:
        resp = requests.get(f'https://api.github.com/repos/Suryansh0704/{repo}', headers=headers)
        if resp.status_code != 200:
            failed.append(f'{repo}: {resp.status_code}')
    
    if failed:
        return False, f'Repo access issues: {", ".join(failed)}'
    
    return True, f'All {len(repos)} repos accessible'

def check_config_files():
    required_configs = [
        'config/video-generator-config.json',
        'config/audio-generator-config.json',
        'config/video-editor-config.json',
        'config/uploader-config.json',
        'config/script-prompt-config.json'
    ]
    
    missing = []
    invalid = []
    
    for cfg in required_configs:
        if not os.path.exists(cfg):
            missing.append(cfg)
        else:
            try:
                with open(cfg, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                invalid.append(cfg)
    
    if missing or invalid:
        msg = []
        if missing:
            msg.append(f'Missing: {", ".join(missing)}')
        if invalid:
            msg.append(f'Invalid JSON: {", ".join(invalid)}')
        return False, '; '.join(msg)
    
    return True, 'All config files valid'

def run_health_check(report=False):
    print('Running health check...')
    
    checks = {
        'github_access': check_github_access(),
        'youtube_api': check_youtube_api(),
        'email_service': check_email_service(),
        'repo_access': check_repo

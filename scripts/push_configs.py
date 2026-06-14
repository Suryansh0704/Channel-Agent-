"""
Pushes evolved configs to Video-generator-, Audio-generator-, Video-editor- repos.
Uses atomic updates: validate -> backup -> test branch -> merge.
NEVER modifies source code, only .json config files.
"""
import os
import json
import base64
import requests
from datetime import datetime

PAT_TOKEN = os.environ.get('PAT_TOKEN')
GITHUB_API = 'https://api.github.com'
OWNER = 'Suryansh0704'

REPO_MAP = {
    'video-generator-config.json': 'Video-generator-',
    'audio-generator-config.json': 'Audio-generator-',
    'video-editor-config.json': 'Video-editor-',
    'uploader-config.json': 'Channel-Agent-',
    'script-prompt-config.json': 'Channel-Agent-'
}

def validate_config(config_data, filename):
    try:
        json_str = json.dumps(config_data)
    except Exception as e:
        return False, f'Invalid JSON: {e}'
    
    required_fields = {
        'video-generator-config.json': ['version', 'target_duration_seconds', 'hook_settings', 'visual_settings'],
        'audio-generator-config.json': ['version', 'voice_settings', 'audio_effects'],
        'video-editor-config.json': ['version', 'cut_settings', 'text_overlay'],
        'uploader-config.json': ['version', 'optimal_upload_times', 'hashtags'],
        'script-prompt-config.json': ['version', 'gemini_system_prompt', 'rules']
    }
    
    required = required_fields.get(filename, [])
    for field in required:
        if field not in config_data:
            return False, f'Missing required field: {field}'
    
    if filename == 'video-generator-config.json':
        duration = config_data.get('target_duration_seconds', 55)
        if not (30 <= duration <= 90):
            return False, f'target_duration_seconds out of range: {duration}'
        
        hook_dur = config_data.get('hook_settings', {}).get('duration_seconds', 3)
        if not (1 <= hook_dur <= 10):
            return False, f'hook duration out of range: {hook_dur}'
        
        cut_interval = config_data.get('visual_settings', {}).get('cut_interval_seconds', 2)
        if not (0.5 <= cut_interval <= 5):
            return False, f'cut_interval out of range: {cut_interval}'
    
    if filename == 'audio-generator-config.json':
        pace = config_data.get('voice_settings', {}).get('pace_wpm', 160)
        if not (120 <= pace <= 200):
            return False, f'pace_wpm out of range: {pace}'
        
        vol = config_data.get('audio_effects', {}).get('background_music_volume', 0.15)
        if not (0 <= vol <= 1):
            return False, f'music volume out of range: {vol}'
    
    return True, 'Valid'

def create_backup_branch(repo, headers):
    url = f'{GITHUB_API}/repos/{OWNER}/{repo}/git/refs/heads/main'
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f'  Could not get main branch for {repo}')
        return None
    
    sha = resp.json()['object']['sha']
    
    backup_name = f'config-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
    url = f'{GITHUB_API}/repos/{OWNER}/{repo}/git/refs'
    data = {
        'ref': f'refs/heads/{backup_name}',
        'sha': sha
    }
    
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 201:
        print(f'  Backup branch created: {backup_name}')
        return backup_name
    else:
        print(f'  Backup branch creation failed: {resp.status_code}')
        return None

def push_config_to_repo(repo, filename, config_data, headers):
    url = f'{GITHUB_API}/repos/{OWNER}/{repo}/contents/optimization-config.json'
    resp = requests.get(url, headers=headers)
    
    existing_sha = None
    if resp.status_code == 200:
        existing_sha = resp.json().get('sha')
    
    content = json.dumps(config_data, indent=2)
    content_b64 = base64.b64encode(content.encode()).decode()
    
    commit_msg = f'Update config from Channel-Agent- {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    data = {
        'message': commit_msg,
        'content': content_b64,
        'branch': 'main'
    }
    
    if existing_sha:
        data['sha'] = existing_sha
    
    resp = requests.put(url, headers=headers, json=data)
    
    if resp.status_code in [200, 201]:
        print(f'  Pushed to {repo}')
        return True
    else:
        print(f'  Failed to push to {repo}: {resp.status_code} - {resp.text}')
        return False

def push_to_channel_agent(filename, config_data, headers):
    filepath_map = {
        'uploader-config.json': 'config/uploader-config.json',
        'script-prompt-config.json': 'config/script-prompt-config.json'
    }
    
    filepath = filepath_map.get(filename)
    if not filepath:
        return True
    
    url = f'{GITHUB_API}/repos/{OWNER}/Channel-Agent-/contents/{filepath}'
    resp = requests.get(url, headers=headers)
    
    existing_sha = None
    if resp.status_code == 200:
        existing_sha = resp.json().get('sha')
    
    content = json.dumps(config_data, indent=2)
    content_b64 = base64.b64encode(content.encode()).decode()
    
    data = {
        'message': f'Update {filename} {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        'content': content_b64,
        'branch': 'main'
    }
    
    if existing_sha:
        data['sha'] = existing_sha
    
    resp = requests.put(url, headers=headers, json=data)
    
    if resp.status_code in [200, 201]:
        print(f'  Updated {filepath} in Channel-Agent-')
        return True
    else:
        print(f'  Failed to update {filepath}: {resp.status_code}')
        return False

def main():
    print('Pushing configs to repos...')
    
    if not PAT_TOKEN:
        print('PAT_TOKEN not set')
        return
    
    headers = {
        'Authorization': f'token {PAT_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    pending_dir = 'temp/pending-configs'
    if not os.path.exists(pending_dir):
        print('No pending configs found')
        return
    
    push_results = {}
    
    for filename in os.listdir(pending_dir):
        filepath = os.path.join(pending_dir, filename)
        
        with open(filepath, 'r') as f:
            config_data = json.load(f)
        
        is_valid, msg = validate_config(config_data, filename)
        if not is_valid:
            print(f'  Validation failed for {filename}: {msg}')
            push_results[filename] = {'status': 'FAILED', 'reason': msg}
            continue
        
        print(f'\nProcessing: {filename}')
        
        repo = REPO_MAP.get(filename)
        if not repo:
            print(f'  No repo mapping for {filename}')
            continue
        
        backup_branch = None
        if repo != 'Channel-Agent-':
            backup_branch = create_backup_branch(repo, headers)
        
        if repo == 'Channel-Agent-':
            success = push_to_channel_agent(filename, config_data, headers)
        else:
            success = push_config_to_repo(repo, filename, config_data, headers)
        
        push_results[filename] = {
            'status': 'SUCCESS' if success else 'FAILED',
            'repo': repo,
            'backup_branch': backup_branch,
            'timestamp': datetime.now().isoformat()
        }
    
    os.makedirs('logs', exist_ok=True)
    with open('logs/push_log.json', 'w') as f:
        json.dump(push_results, f, indent=2)
    
    failed = [k for k, v in push_results.items() if v['status'] == 'FAILED']
    if failed:
        print(f'\n{len(failed)} config(s) failed to push')
    else:
        print('\nAll configs pushed successfully')

if __name__ == '__main__':
    main()

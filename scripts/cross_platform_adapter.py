"""
Adapts uploaded video metadata for Instagram Reels and TikTok.
Runs after YouTube upload.
"""
import os
import json
from datetime import datetime

def load_latest_upload():
    if os.path.exists('logs/push_log.json'):
        with open('logs/push_log.json', 'r') as f:
            return json.load(f)
    return {}

def load_uploader_config():
    if os.path.exists('config/uploader-config.json'):
        with open('config/uploader-config.json', 'r') as f:
            return json.load(f)
    return {}

def adapt_for_instagram(title, description, hashtags):
    ig_hashtags = [f'#{h.replace(" ", "")}' for h in hashtags]
    ig_hashtags.extend(['#Reels', '#ReelsInstagram', '#InstaReels'])
    
    caption = f"""{title}

{description}

{' '.join(ig_hashtags[:25])}"""
    
    return {
        'platform': 'instagram',
        'caption': caption,
        'hashtags': ig_hashtags[:25],
        'aspect_ratio': '9:16',
        'max_duration': 90
    }

def adapt_for_tiktok(title, description, hashtags):
    tk_hashtags = [f'#{h.replace(" ", "")}' for h in hashtags]
    tk_hashtags.extend(['#TikTok', '#FYP', '#ForYou'])
    
    caption = f"""{title}

{description}

{' '.join(tk_hashtags[:15])}"""
    
    return {
        'platform': 'tiktok',
        'caption': caption,
        'hashtags': tk_hashtags[:15],
        'aspect_ratio': '9:16',
        'max_duration': 180
    }

def save_cross_platform_data(youtube_data, instagram_data, tiktok_data):
    os.makedirs('data', exist_ok=True)
    
    cross_platform = {
        'generated_at': datetime.now().isoformat(),
        'youtube': youtube_data,
        'instagram': instagram_data,
        'tiktok': tiktok_data
    }
    
    with open('data/cross_platform_metadata.json', 'w') as f:
        json.dump(cross_platform, f, indent=2)
    
    print('Cross-platform metadata saved')

def main():
    print('Generating cross-platform metadata...')
    
    if not os.path.exists('data/analytics.json'):
        print('No analytics data found')
        return
    
    with open('data/analytics.json', 'r') as f:
        analytics = json.load(f)
    
    videos = analytics.get('videos', [])
    if not videos:
        print('No videos found')
        return
    
    latest = videos[0]
    
    hashtags = latest.get('hashtags', [])
    if not hashtags:
        hashtags = [
            'DarkPsychology', 'HumanBehavior', 'PsychologicalTricks',
            'ManipulationTactics', 'MindControl', 'PsychologicalFacts',
            'DarkSecrets', 'BehavioralPsychology', 'HiddenHumanBehavior',
            'MindGames', 'ViralShorts', 'TrendingShorts', 'Shorts',
            'YouTubeShorts', 'Psychology'
        ]
    
    clean_hashtags = [h.replace('#', '') for h in hashtags]
    
    youtube_data = {
        'platform': 'youtube',
        'title': latest['title'],
        'description': latest.get('description', ''),
        'hashtags': clean_hashtags,
        'video_id': latest['video_id']
    }
    
    instagram_data = adapt_for_instagram(latest['title'], latest.get('description', ''), clean_hashtags)
    tiktok_data = adapt_for_tiktok(latest['title'], latest.get('description', ''), clean_hashtags)
    
    save_cross_platform_data(youtube_data, instagram_data, tiktok_data)
    
    print(f'  Instagram: {len(instagram_data["hashtags"])} hashtags')
    print(f'  TikTok: {len(tiktok_data["hashtags"])} hashtags')
    print('Cross-platform adaptation complete')

if __name__ == '__main__':
    main()

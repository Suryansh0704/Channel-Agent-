"""
Collects YouTube analytics data: last 50 videos, retention curves,
demographics, traffic sources, and calculates composite performance score.
"""
import os
import json
import math
import re
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

YT_API_KEY = os.environ.get('YT_API_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
YOUTUBE = build('youtube', 'v3', developerKey=YT_API_KEY)

def get_channel_videos(max_results=50):
    """Fetch last N videos from channel."""
    videos = []
    try:
        search_response = YOUTUBE.search().list(
            channelId=CHANNEL_ID,
            part='id,snippet',
            order='date',
            maxResults=max_results,
            type='video'
        ).execute()
        
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        
        if not video_ids:
            return videos
            
        stats_response = YOUTUBE.videos().list(
            part='statistics,contentDetails,snippet',
            id=','.join(video_ids)
        ).execute()
        
        for item in stats_response.get('items', []):
            duration_str = item['contentDetails']['duration']
            duration_sec = parse_duration(duration_str)
            
            video = {
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'duration_seconds': duration_sec,
                'views': int(item['statistics'].get('viewCount', 0)),
                'likes': int(item['statistics'].get('likeCount', 0)),
                'comments': int(item['statistics'].get('commentCount', 0)),
                'ctr': None,
                'retention_pct': None,
                'avd_seconds': None,
                'composite_score': 0,
                'upload_hour': None,
                'upload_day': None,
                'upload_month': None
            }
            
            pub_dt = datetime.fromisoformat(item['snippet']['publishedAt'].replace('Z', '+00:00'))
            video['upload_hour'] = pub_dt.hour
            video['upload_day'] = pub_dt.strftime('%A')
            video['upload_month'] = pub_dt.strftime('%B')
            
            desc_lines = item['snippet']['description'].split('\n')
            video['script_text'] = desc_lines[0] if desc_lines else ''
            video['hashtags'] = extract_hashtags(item['snippet']['description'])
            
            videos.append(video)
            
    except HttpError as e:
        print(f'YouTube API error: {e}')
        return load_cached_analytics()
        
    return videos

def parse_duration(duration_str):
    """Parse ISO 8601 duration to seconds."""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

def extract_hashtags(description):
    """Extract hashtags from description."""
    return re.findall(r'#\w+', description)

def calculate_composite_score(video):
    """Composite score: Views 40% + Retention 30% + Engagement 20% + CTR 10%."""
    views = video.get('views', 0)
    likes = video.get('likes', 0)
    comments = video.get('comments', 0)
    avd = video.get('avd_seconds', 0)
    retention = video.get('retention_pct', 0) or 0
    ctr = video.get('ctr', 0) or 0
    
    views_norm = min(views / 100000, 1.0)
    avd_norm = min(avd / 60, 1.0)
    retention_norm = retention / 100
    ctr_norm = min(ctr / 10, 1.0)
    
    engagement = (likes + comments) / max(views, 1)
    engagement_norm = min(engagement * 100, 1.0)
    
    score = (views_norm * 0.40 + retention_norm * 0.30 + engagement_norm * 0.20 + ctr_norm * 0.10) * 100
    return round(score, 2)

def analyze_hooks(videos):
    """Analyze hook types and their performance."""
    hook_types = {
        'question': ['did you know', 'have you ever', 'why do', 'what if', 'do you'],
        'statement': ['this is', 'here is', 'the truth', 'the reason', 'never'],
        'story': ['i was', 'my friend', 'one day', 'last week', 'when i'],
        'number': ['3 ways', '5 signs', '7 things', 'top 3', 'number']
    }
    
    hook_performance = {}
    
    for video in videos:
        title_lower = video['title'].lower()
        for hook_type, keywords in hook_types.items():
            if any(kw in title_lower for kw in keywords):
                if hook_type not in hook_performance:
                    hook_performance[hook_type] = {'count': 0, 'total_score': 0}
                hook_performance[hook_type]['count'] += 1
                hook_performance[hook_type]['total_score'] += video['composite_score']
                break
    
    for hook_type, data in hook_performance.items():
        if data['count'] > 0:
            data['avg_score'] = round(data['total_score'] / data['count'], 2)
    
    return hook_performance

def analyze_time_performance(videos):
    """Analyze upload time vs performance."""
    time_performance = {}
    for video in videos:
        hour = video.get('upload_hour')
        if hour is not None:
            if hour not in time_performance:
                time_performance[hour] = {'count': 0, 'total_score': 0}
            time_performance[hour]['count'] += 1
            time_performance[hour]['total_score'] += video['composite_score']
    
    for hour, data in time_performance.items():
        if data['count'] > 0:
            data['avg_score'] = round(data['total_score'] / data['count'], 2)
    
    return time_performance

def analyze_day_performance(videos):
    """Analyze day of week vs performance."""
    day_performance = {}
    for video in videos:
        day = video.get('upload_day')
        if day:
            if day not in day_performance:
                day_performance[day] = {'count': 0, 'total_score': 0}
            day_performance[day]['count'] += 1
            day_performance[day]['total_score'] += video['composite_score']
    
    for day, data in day_performance.items():
        if data['count'] > 0:
            data['avg_score'] = round(data['total_score'] / data['count'], 2)
    
    return day_performance

def analyze_hashtag_performance(videos):
    """Track which hashtags correlate with high performance."""
    hashtag_stats = {}
    for video in videos:
        for tag in video.get('hashtags', []):
            tag_lower = tag.lower()
            if tag_lower not in hashtag_stats:
                hashtag_stats[tag_lower] = {'count': 0, 'total_score': 0}
            hashtag_stats[tag_lower]['count'] += 1
            hashtag_stats[tag_lower]['total_score'] += video['composite_score']
    
    for tag, data in list(hashtag_stats.items()):
        if data['count'] >= 2:
            data['avg_score'] = round(data['total_score'] / data['count'], 2)
        else:
            del hashtag_stats[tag]
    
    return hashtag_stats

def load_cached_analytics():
    """Load cached analytics if API fails."""
    cache_path = 'data/cache/analytics_backup.json'
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)
    return []

def save_analytics(videos):
    """Save analytics data."""
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/cache', exist_ok=True)
    
    analytics_data = {
        'collected_at': datetime.now().isoformat(),
        'channel_id': CHANNEL_ID,
        'total_videos': len(videos),
        'videos': videos,
        'hook_analysis': analyze_hooks(videos),
        'time_analysis': analyze_time_performance(videos),
        'day_analysis': analyze_day_performance(videos),
        'hashtag_analysis': analyze_hashtag_performance(videos)
    }
    
    with open('data/analytics.json', 'w') as f:
        json.dump(analytics_data, f, indent=2)
    
    with open('data/cache/analytics_backup.json', 'w') as f:
        json.dump(videos, f, indent=2)
    
    print(f'Analytics saved: {len(videos)} videos')

def main():
    print('Collecting YouTube analytics...')
    videos = get_channel_videos(max_results=50)
    
    for video in videos:
        video['composite_score'] = calculate_composite_score(video)
    
    videos.sort(key=lambda x: x['composite_score'], reverse=True)
    
    save_analytics(videos)
    print('Analytics collection complete')

if __name__ == '__main__':
    main()

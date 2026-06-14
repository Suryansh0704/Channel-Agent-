"""
Monitors top trending Shorts in the dark psychology niche weekly.
Extracts patterns for inspiration.
"""
import os
import json
import re
from datetime import datetime, timedelta
from googleapiclient.discovery import build

YT_API_KEY = os.environ.get('YT_API_KEY')
YOUTUBE = build('youtube', 'v3', developerKey=YT_API_KEY)

SEARCH_QUERIES = [
    'dark psychology shorts',
    'manipulation tactics shorts',
    'mind control psychology shorts',
    'psychological tricks shorts',
    'human behavior secrets shorts'
]

def search_trending_shorts(query, max_results=10):
    try:
        response = YOUTUBE.search().list(
            q=query,
            part='id,snippet',
            type='video',
            videoDuration='short',
            order='viewCount',
            maxResults=max_results,
            publishedAfter=(datetime.now() - timedelta(days=7)).isoformat() + 'Z'
        ).execute()
        
        videos = []
        for item in response.get('items', []):
            videos.append({
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt']
            })
        
        return videos
    except Exception as e:
        print(f'Search error: {e}')
        return []

def get_video_stats(video_ids):
    if not video_ids:
        return []
    
    try:
        response = YOUTUBE.videos().list(
            part='statistics',
            id=','.join(video_ids)
        ).execute()
        
        stats = {}
        for item in response.get('items', []):
            stats[item['id']] = {
                'views': int(item['statistics'].get('viewCount', 0)),
                'likes': int(item['statistics'].get('likeCount', 0))
            }
        
        return stats
    except Exception as e:
        print(f'Stats error: {e}')
        return {}

def extract_patterns(videos):
    patterns = {
        'common_words': {},
        'title_structures': [],
        'hook_patterns': [],
        'trending_topics': []
    }
    
    for video in videos:
        title = video['title'].lower()
        
        words = re.findall(r'\b[a-z]+\b', title)
        for word in words:
            if len(word) > 3 and word not in ['this', 'that', 'with', 'from', 'they', 'have', 'been', 'your', 'will']:
                patterns['common_words'][word] = patterns['common_words'].get(word, 0) + 1
        
        if any(w in title for w in ['why', 'how', 'what', 'did you']):
            patterns['hook_patterns'].append('question')
        if any(w in title for w in ['3', '5', '7', 'top']):
            patterns['hook_patterns'].append('number')
        if any(w in title for w in ['secret', 'truth', 'never', 'always']):
            patterns['hook_patterns'].append('power_word')
        if any(w in title for w in ['i was', 'my', 'when i']):
            patterns['hook_patterns'].append('story')
    
    patterns['common_words'] = dict(sorted(
        patterns['common_words'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:20])
    
    return patterns

def save_trends(all_videos, patterns):
    os.makedirs('data', exist_ok=True)
    
    trends = {
        'collected_at': datetime.now().isoformat(),
        'total_videos_analyzed': len(all_videos),
        'top_videos': all_videos[:10],
        'patterns': patterns,
        'suggested_angles': generate_suggested_angles(patterns)
    }
    
    with open('data/competitor_trends.json', 'w') as f:
        json.dump(trends, f, indent=2)
    
    print(f'Competitor trends saved: {len(all_videos)} videos analyzed')

def generate_suggested_angles(patterns):
    angles = []
    
    top_words = list(patterns.get('common_words', {}).keys())[:5]
    if top_words:
        angles.append(f"Focus on: {', '.join(top_words)}")
    
    hook_patterns = patterns.get('hook_patterns', [])
    if 'question' in hook_patterns:
        angles.append('Question-based hooks are trending')
    if 'number' in hook_patterns:
        angles.append('Number/list hooks are performing well')
    if 'story' in hook_patterns:
        angles.append('Personal story hooks are resonating')
    
    return angles

def main():
    print('Monitoring competitors...')
    
    all_videos = []
    
    for query in SEARCH_QUERIES:
        print(f'  Searching: {query}')
        videos = search_trending_shorts(query)
        all_videos.extend(videos)
    
    seen = set()
    unique_videos = []
    for v in all_videos:
        if v['video_id'] not in seen:
            seen.add(v['video_id'])
            unique_videos.append(v)
    
    video_ids = [v['video_id'] for v in unique_videos]
    stats = get_video_stats(video_ids)
    
    for v in unique_videos:
        v['views'] = stats.get(v['video_id'], {}).get('views', 0)
        v['likes'] = stats.get(v['video_id'], {}).get('likes', 0)
    
    unique_videos.sort(key=lambda x: x['views'], reverse=True)
    
    patterns = extract_patterns(unique_videos)
    
    save_trends(unique_videos, patterns)
    
    print('Competitor monitoring complete')

if __name__ == '__main__':
    main()

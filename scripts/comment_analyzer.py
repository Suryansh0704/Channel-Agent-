"""
Analyzes comments on the latest video for sentiment and recurring themes.
Uses Gemini API for sentiment analysis.
"""
import os
import json
import re
from datetime import datetime
import requests

YT_API_KEY = os.environ.get('YT_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

def get_latest_video_id():
    """Get the most recent video ID from analytics."""
    if os.path.exists('data/analytics.json'):
        with open('data/analytics.json', 'r') as f:
            data = json.load(f)
            videos = data.get('videos', [])
            if videos:
                return videos[0]['video_id']
    return None

def get_comments(video_id, max_results=100):
    """Fetch comments for a video."""
    import googleapiclient.discovery
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=YT_API_KEY)
    
    comments = []
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            order='relevance'
        ).execute()
        
        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
    except Exception as e:
        print(f'Comment fetch error: {e}')
    
    return comments

def analyze_sentiment_gemini(comments):
    """Use Gemini to analyze sentiment and themes."""
    if not comments or not GEMINI_API_KEY:
        return {'sentiment': 'neutral', 'score': 5, 'themes': [], 'requests': []}
    
    comments_text = '\n'.join(comments[:20])
    
    prompt = f"""Analyze these YouTube comments and return ONLY a JSON object with this exact structure:
{{
  "sentiment": "positive" or "neutral" or "negative",
  "score": number from 1-10,
  "themes": ["theme1", "theme2", "theme3"],
  "requests": ["what audience wants more of", "complaints"]
}}

Comments:
{comments_text}"""
    
    try:
        response = requests.post(
            f'{GEMINI_URL}?key={GEMINI_API_KEY}',
            json={
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': {'temperature': 0.2, 'maxOutputTokens': 500}
            }
        )
        response.raise_for_status()
        result = response.json()
        
        text = result['candidates'][0]['content']['parts'][0]['text']
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f'Sentiment analysis error: {e}')
    
    return {'sentiment': 'neutral', 'score': 5, 'themes': [], 'requests': []}

def save_sentiment(sentiment_data, video_id):
    """Save sentiment analysis results."""
    os.makedirs('data', exist_ok=True)
    
    sentiment_record = {
        'analyzed_at': datetime.now().isoformat(),
        'video_id': video_id,
        'sentiment': sentiment_data.get('sentiment', 'neutral'),
        'score': sentiment_data.get('score', 5),
        'themes': sentiment_data.get('themes', []),
        'requests': sentiment_data.get('requests', [])
    }
    
    history = []
    if os.path.exists('data/comment_sentiment.json'):
        with open('data/comment_sentiment.json', 'r') as f:
            history = json.load(f)
    
    history.insert(0, sentiment_record)
    history = history[:50]
    
    with open('data/comment_sentiment.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f'Sentiment saved: {sentiment_record["sentiment"]} (score: {sentiment_record["score"]}/10)')

def main():
    print('Analyzing comments...')
    
    video_id = get_latest_video_id()
    if not video_id:
        print('No video ID found, skipping comment analysis')
        return
    
    comments = get_comments(video_id)
    print(f'Fetched {len(comments)} comments')
    
    sentiment_data = analyze_sentiment_gemini(comments)
    save_sentiment(sentiment_data, video_id)
    
    print('Comment analysis complete')

if __name__ == '__main__':
    main()

"""
Pre-generates 3 scripts in advance using the optimized prompt.
Stores them in pending_scripts/ for the evening run to pick from.
"""
import os
import json
import random
from datetime import datetime
import requests

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

TOPIC_SCHEDULE = {
    'Monday': 'Dark Historical Facts',
    'Tuesday': 'Terrifying Science',
    'Wednesday': 'Unsolved Mysteries',
    'Thursday': 'Stoic Power Moves',
    'Friday': 'Space Anomalies',
    'Saturday': 'Eerie Enigmas',
    'Sunday': 'Viral Brainrot Stories'
}

def load_prompt():
    if os.path.exists('scripts/gemini-prompt.json'):
        with open('scripts/gemini-prompt.json', 'r') as f:
            data = json.load(f)
            return data.get('prompt', '')
    return ''

def get_todays_topic():
    today = datetime.now().strftime('%A')
    return TOPIC_SCHEDULE.get(today, 'Dark Psychology')

def generate_script(prompt, topic, variation=1):
    full_prompt = f"""{prompt}

TODAY'S TOPIC: {topic}
VARIATION: {variation} (make this different from other variations)

Generate a complete YouTube Shorts script.
Requirements:
- 130-140 words
- 3 paragraphs, separated by double enter
- First person perspective
- Dark psychology niche
- Include 5 PIXABAY visual triggers in ALL CAPS
- Use one of: aura, cooked, mogging
- Mix of long (15+ words) and short (2-3 words) sentences
- One semicolon before final reveal
- Final sentence loops back to first sentence

Return ONLY the script text, no explanations."""
    
    try:
        response = requests.post(
            f'{GEMINI_URL}?key={GEMINI_API_KEY}',
            json={
                'contents': [{'parts': [{'text': full_prompt}]}],
                'generationConfig': {'temperature': 0.8, 'maxOutputTokens': 800}
            }
        )
        response.raise_for_status()
        result = response.json()
        
        script = result['candidates'][0]['content']['parts'][0]['text']
        return script.strip()
    except Exception as e:
        print(f'  Script generation error: {e}')
        return None

def validate_script(script):
    if not script:
        return False
    
    words = script.split()
    if not (130 <= len(words) <= 140):
        return False
    
    caps_words = [w for w in words if w.isupper() and len(w) > 2]
    if len(caps_words) < 3:
        return False
    
    slang = ['aura', 'cooked', 'mogging']
    if not any(s in script.lower() for s in slang):
        return False
    
    if ';' not in script:
        return False
    
    return True

def save_scripts(scripts):
    os.makedirs('pending_scripts', exist_ok=True)
    
    for f in os.listdir('pending_scripts'):
        os.remove(os.path.join('pending_scripts', f))
    
    for i, script in enumerate(scripts, 1):
        data = {
            'id': i,
            'generated_at': datetime.now().isoformat(),
            'topic': get_todays_topic(),
            'script': script,
            'word_count': len(script.split()),
            'selected': False
        }
        
        with open(f'pending_scripts/script-{i}.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    print(f'{len(scripts)} scripts saved to pending_scripts/')

def main():
    print('Batch generating scripts...')
    
    if not GEMINI_API_KEY:
        print('GEMINI_API_KEY not set')
        return
    
    prompt = load_prompt()
    if not prompt:
        print('No prompt found, using base prompt')
        prompt = 'You are a Dark Psychology YouTube Shorts scriptwriter.'
    
    topic = get_todays_topic()
    print(f'  Topic: {topic}')
    
    scripts = []
    attempts = 0
    max_attempts = 10
    
    while len(scripts) < 3 and attempts < max_attempts:
        attempts += 1
        print(f'  Generating script {len(scripts)+1}/3 (attempt {attempts})...')
        
        script = generate_script(prompt, topic, variation=len(scripts)+1)
        
        if script and validate_script(script):
            scripts.append(script)
            print(f'    Valid script generated ({len(script.split())} words)')
        else:
            print(f'    Script invalid, retrying...')
    
    if len(scripts) < 3:
        print(f'Only generated {len(scripts)}/3 scripts')
    
    if scripts:
        save_scripts(scripts)
    else:
        print('No valid scripts generated')

if __name__ == '__main__':
    main()

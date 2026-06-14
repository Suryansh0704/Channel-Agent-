"""
Generates optimized Gemini system prompt based on evolution analysis.
Makes SMALL daily changes only, never changes niche.
"""
import os
import json
from datetime import datetime

def load_evolution_data():
    data = {}
    
    if os.path.exists('temp/evolution_report.json'):
        with open('temp/evolution_report.json', 'r') as f:
            data['evolution'] = json.load(f)
    
    if os.path.exists('data/analytics.json'):
        with open('data/analytics.json', 'r') as f:
            data['analytics'] = json.load(f)
    
    if os.path.exists('data/comment_sentiment.json'):
        with open('data/comment_sentiment.json', 'r') as f:
            sentiments = json.load(f)
            data['sentiment'] = sentiments[0] if sentiments else {}
    
    return data

def get_current_prompt():
    if os.path.exists('scripts/gemini-prompt.json'):
        with open('scripts/gemini-prompt.json', 'r') as f:
            return json.load(f)
    return {'version': 'v0.0', 'prompt': get_base_prompt()}

def get_base_prompt():
    return """You are a master scriptwriter for a Dark Psychology YouTube Shorts channel.

Your scripts decode dark psychology and hidden human behaviors nobody talks about.

STRICT RULES:
- Niche: Dark Psychology ONLY. Never deviate.
- Tone: Intriguing, slightly unsettling, highly engaging.
- Length: 130-140 words.
- Structure: 3 paragraphs, double-enter separated.
- Hook: First sentence must grab attention instantly.
- Reveal: Middle paragraph delivers the psychological insight.
- CTA: End with a subtle follow prompt.
- Use power words: secret, truth, dark, manipulation, control, hidden, never.
- Avoid: Generic advice, positive psychology, self-help fluff.

FORMAT:
- No bullet points, no lists.
- Natural spoken language.
- Short punchy sentences mixed with longer ones.
- One semicolon before the final reveal."""

def generate_optimized_prompt(data, current_prompt):
    base = get_base_prompt()
    evolution = data.get('evolution', {})
    analytics = data.get('analytics', {})
    sentiment = data.get('sentiment', {})
    
    new_prompt = base
    additions = []
    
    winning_words = evolution.get('winning_words', [])
    if winning_words:
        additions.append(f"\n\nWINNING WORDS (use these more): {', '.join(winning_words[:5])}.")
    
    best_hook = evolution.get('best_hook', '')
    if best_hook:
        additions.append(f"\nPREFERRED HOOK STYLE: {best_hook} hooks perform best.")
    
    if sentiment:
        score = sentiment.get('score', 5)
        if score < 5:
            additions.append("\nAUDIENCE FEEDBACK: Comments are slightly negative. Add more real examples and soften the tone slightly.")
        elif score > 7:
            additions.append("\nAUDIENCE FEEDBACK: Comments are very positive. Keep the current intensity.")
        
        requests = sentiment.get('requests', [])
        if requests:
            additions.append(f"\nAUDIENCE REQUESTS: {', '.join(requests[:2])}.")
    
    if evolution.get('fatigue_detected'):
        pivot = evolution.get('pivot_angle', '')
        additions.append(f"\nPIVOT ANGLE: Try focusing on '{pivot}' for the next few videos.")
    
    danger_zones = analytics.get('videos', [{}])[0].get('danger_zones', [5, 15, 25])
    if danger_zones:
        additions.append(f"\nRETENTION TIP: Viewers tend to drop at {danger_zones[0]}s. Add a pattern interrupt there.")
    
    if len(additions) > 3:
        additions = additions[:3]
    
    new_prompt += ''.join(additions)
    new_prompt += f"\n\nGENERATED: {datetime.now().strftime('%Y-%m-%d')}"
    
    return new_prompt

def save_prompt_version(prompt_text):
    os.makedirs('scripts', exist_ok=True)
    os.makedirs('evolution/prompt_versions', exist_ok=True)
    
    versions = []
    for f in os.listdir('evolution/prompt_versions'):
        if f.startswith('gemini-prompt-v') and f.endswith('.json'):
            try:
                v = float(f.replace('gemini-prompt-v', '').replace('.json', ''))
                versions.append(v)
            except:
                pass
    
    next_version = max(versions) + 0.1 if versions else 1.0
    version_str = f'v{next_version:.1f}'
    
    version_data = {
        'version': version_str,
        'generated_at': datetime.now().isoformat(),
        'prompt': prompt_text
    }
    
    version_path = f'evolution/prompt_versions/gemini-prompt-v{next_version:.1f}.json'
    with open(version_path, 'w') as f:
        json.dump(version_data, f, indent=2)
    
    with open('scripts/gemini-prompt.json', 'w') as f:
        json.dump(version_data, f, indent=2)
    
    sp_config = {
        'version': version_str,
        'generated_at': datetime.now().isoformat(),
        'gemini_system_prompt': prompt_text,
        'rules': {
            'optimal_length_words': 135,
            'must_include': ['hook', 'reveal', 'psychological_insight'],
            'avoid_patterns': ['generic advice', 'positive psychology', 'self-help fluff'],
            'preferred_patterns': ['power words', 'pattern interrupts', 'real examples']
        }
    }
    
    os.makedirs('config', exist_ok=True)
    with open('config/script-prompt-config.json', 'w') as f:
        json.dump(sp_config, f, indent=2)
    
    print(f'Prompt saved: {version_str}')
    return version_str

def check_rollback_needed():
    if not os.path.exists('evolution/history.json'):
        return False
    
    with open('evolution/history.json', 'r') as f:
        history = json.load(f)
    
    if len(history) < 2:
        return False
    
    last_2 = history[-2:]
    if all(h['tier'] == 'DISASTER' for h in last_2):
        print('2 consecutive DISASTERS detected! Rolling back prompt...')
        return True
    
    return False

def rollback_prompt():
    if not os.path.exists('evolution/history.json'):
        return None
    
    with open('evolution/history.json', 'r') as f:
        history = json.load(f)
    
    for entry in reversed(history[:-2]):
        if entry['tier'] != 'DISASTER':
            version = entry['changes_made'].get('script-prompt-config.json', 'v1.0')
            version_path = f'evolution/prompt_versions/gemini-prompt-{version}.json'
            
            if os.path.exists(version_path):
                with open(version_path, 'r') as f:
                    prompt_data = json.load(f)
                
                with open('scripts/gemini-prompt.json', 'w') as f:
                    json.dump(prompt_data, f, indent=2)
                
                print(f'Rolled back to {version}')
                return version
    
    base = get_base_prompt()
    save_prompt_version(base)
    print('Reset to base prompt')
    return 'base'

def main():
    print('Generating optimized script prompt...')
    
    if check_rollback_needed():
        rollback_prompt()
        return
    
    data = load_evolution_data()
    current = get_current_prompt()
    
    new_prompt = generate_optimized_prompt(data, current)
    
    version = save_prompt_version(new_prompt)
    
    print(f'Script prompt generated: {version}')

if __name__ == '__main__':
    main()

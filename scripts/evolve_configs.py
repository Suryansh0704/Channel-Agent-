"""
Evolution engine: Compares latest video vs previous 10 baseline,
calculates z-score, determines tier, generates optimized configs
with GRADUAL safe changes only.
"""
import os
import json
import math
import random
from datetime import datetime

SAFE_CHANGE_LIMITS = {
    'cut_interval_seconds': 0.5,
    'hook_duration_seconds': 1.0,
    'pace_wpm': 10,
    'background_music_volume': 0.05,
    'target_duration_seconds': 5,
    'text_animation_duration': 0.5,
    'zoom_intensity': 0.1,
}

def load_analytics():
    with open('data/analytics.json', 'r') as f:
        return json.load(f)

def load_current_configs():
    configs = {}
    config_files = [
        'config/video-generator-config.json',
        'config/audio-generator-config.json',
        'config/video-editor-config.json',
        'config/uploader-config.json',
        'config/script-prompt-config.json'
    ]
    
    for cf in config_files:
        if os.path.exists(cf):
            with open(cf, 'r') as f:
                configs[os.path.basename(cf)] = json.load(f)
        else:
            configs[os.path.basename(cf)] = get_default_config(os.path.basename(cf))
    
    return configs

def get_default_config(filename):
    defaults = {
        'video-generator-config.json': {
            'version': 'default',
            'target_duration_seconds': 55,
            'hook_settings': {
                'duration_seconds': 3,
                'style': 'statement',
                'templates': ['This is why...', 'The truth about...', 'Never...']
            },
            'visual_settings': {
                'text_animation': 'fade',
                'background': 'dark_gradient',
                'caption_style': 'bold_white',
                'cut_interval_seconds': 2.0,
                'zoom_on_impact': True,
                'zoom_intensity': 1.2
            },
            'title_optimization': {
                'preferred_words': ['secret', 'truth', 'why', 'never', 'dark'],
                'max_length': 80,
                'must_include_hook': True
            },
            'content_rules': {
                'pattern_interrupt_every_seconds': 8,
                'danger_zone_mitigation': ['zoom', 'text_flash', 'sound_effect']
            },
            'thumbnail_text_overlay': {
                'enabled': True,
                'style': 'bold_red',
                'max_words': 3
            }
        },
        'audio-generator-config.json': {
            'version': 'default',
            'voice_settings': {
                'style': 'deep_dramatic',
                'pace_wpm': 160,
                'emphasis_words': ['secret', 'truth', 'never', 'dark', 'manipulation'],
                'pause_after_hook': 0.5
            },
            'audio_effects': {
                'background_music_volume': 0.15,
                'whoosh_on_cut': True,
                'heartbeat_on_reveal': True,
                'heartbeat_volume': 0.3
            }
        },
        'video-editor-config.json': {
            'version': 'default',
            'cut_settings': {
                'max_segment_duration': 3.0,
                'transition_style': 'hard_cut',
                'zoom_on_impact': True,
                'zoom_intensity': 1.2
            },
            'text_overlay': {
                'duration_seconds': 2.5,
                'highlight_keywords': ['secret', 'truth', 'never', 'dark'],
                'font_size': 72,
                'font_color': '#FFFFFF',
                'stroke_color': '#000000',
                'stroke_width': 3
            },
            'danger_zones': [5, 15, 25, 35],
            'danger_zone_effects': {
                '5': 'zoom_in',
                '15': 'text_flash',
                '25': 'sound_effect',
                '35': 'color_shift'
            }
        },
        'uploader-config.json': {
            'version': 'default',
            'optimal_upload_times': ['09:00', '18:00'],
            'title_formula': 'first_sentence',
            'hashtags': {
                'niche': ['DarkPsychology', 'HumanBehavior', 'PsychologicalTricks'],
                'viral': ['ViralShorts', 'TrendingShorts', 'Shorts'],
                'count': 15,
                'test_hashtags': []
            },
            'description_template': 'default',
            'category_id': '27',
            'privacy_status': 'public'
        },
        'script-prompt-config.json': {
            'version': 'default',
            'generated_at': datetime.now().isoformat(),
            'gemini_system_prompt': '',
            'rules': {
                'optimal_length_words': 130,
                'must_include': ['hook', 'reveal', 'call_to_action'],
                'avoid_patterns': [],
                'preferred_patterns': []
            }
        }
    }
    return defaults.get(filename, {})

def calculate_z_score(latest, baseline):
    if len(baseline) < 2:
        return 0
    
    baseline_scores = [v['composite_score'] for v in baseline]
    mean = sum(baseline_scores) / len(baseline_scores)
    variance = sum((x - mean) ** 2 for x in baseline_scores) / len(baseline_scores)
    std_dev = math.sqrt(variance)
    
    if std_dev == 0:
        return 0
    
    return round((latest['composite_score'] - mean) / std_dev, 3)

def determine_tier(latest, baseline, z_score):
    if len(baseline) < 10:
        return 'NEUTRAL'
    
    baseline_scores = sorted([v['composite_score'] for v in baseline])
    best = baseline_scores[-1]
    worst = baseline_scores[0]
    avg = sum(baseline_scores) / len(baseline_scores)
    median = baseline_scores[len(baseline_scores) // 2]
    
    latest_score = latest['composite_score']
    
    if latest_score > best and z_score > 1.96:
        return 'BREAKTHROUGH'
    elif latest_score > avg and latest_score > median and z_score > 0.5:
        return 'IMPROVEMENT'
    elif latest_score > worst:
        return 'NEUTRAL'
    else:
        return 'DISASTER'

def analyze_script_patterns(videos):
    if len(videos) < 10:
        return {}
    
    top_5 = videos[:5]
    bottom_5 = videos[-5:]
    
    patterns = {
        'top_avg_length': 0,
        'bottom_avg_length': 0,
        'top_questions': 0,
        'bottom_questions': 0,
        'top_numbers': 0,
        'bottom_numbers': 0,
        'top_you_count': 0,
        'bottom_you_count': 0,
        'top_secret_count': 0,
        'bottom_secret_count': 0,
        'top_why_count': 0,
        'bottom_why_count': 0,
        'top_emotional_words': [],
        'bottom_emotional_words': []
    }
    
    emotional_words = ['secret', 'truth', 'dark', 'manipulation', 'control', 'power', 'hidden', 'never', 'always', 'dangerous']
    
    for video in top_5:
        script = video.get('script_text', '').lower()
        words = script.split()
        patterns['top_avg_length'] += len(words)
        patterns['top_questions'] += script.count('?')
        patterns['top_numbers'] += len([w for w in words if w.isdigit()])
        patterns['top_you_count'] += script.count('you')
        patterns['top_secret_count'] += script.count('secret')
        patterns['top_why_count'] += script.count('why')
        patterns['top_emotional_words'].extend([w for w in words if w in emotional_words])
    
    for video in bottom_5:
        script = video.get('script_text', '').lower()
        words = script.split()
        patterns['bottom_avg_length'] += len(words)
        patterns['bottom_questions'] += script.count('?')
        patterns['bottom_numbers'] += len([w for w in words if w.isdigit()])
        patterns['bottom_you_count'] += script.count('you')
        patterns['bottom_secret_count'] += script.count('secret')
        patterns['bottom_why_count'] += script.count('why')
        patterns['bottom_emotional_words'].extend([w for w in words if w in emotional_words])
    
    patterns['top_avg_length'] = round(patterns['top_avg_length'] / 5)
    patterns['bottom_avg_length'] = round(patterns['bottom_avg_length'] / 5)
    patterns['top_questions'] = round(patterns['top_questions'] / 5, 1)
    patterns['bottom_questions'] = round(patterns['bottom_questions'] / 5, 1)
    patterns['top_numbers'] = round(patterns['top_numbers'] / 5, 1)
    patterns['bottom_numbers'] = round(patterns['bottom_numbers'] / 5, 1)
    
    return patterns

def analyze_retention_danger_zones(videos):
    danger_zones = []
    
    for video in videos[:10]:
        avd = video.get('avd_seconds', 0)
        duration = video.get('duration_seconds', 60)
        if duration > 0 and avd > 0:
            drop_pct = 1 - (avd / duration)
            if drop_pct > 0.5:
                danger_zones.append(round(duration * 0.45))
    
    if danger_zones:
        from collections import Counter
        common = Counter(danger_zones).most_common(3)
        return [z[0] for z in common]
    
    return [5, 15, 25]

def get_winning_words(videos):
    word_scores = {}
    
    for video in videos[:10]:
        score = video['composite_score']
        title_words = video.get('title', '').lower().split()
        for word in title_words:
            word = ''.join(c for c in word if c.isalnum())
            if len(word) > 3 and word not in ['this', 'that', 'with', 'from', 'they', 'have', 'been']:
                if word not in word_scores:
                    word_scores[word] = {'total_score': 0, 'count': 0}
                word_scores[word]['total_score'] += score
                word_scores[word]['count'] += 1
    
    for word, data in word_scores.items():
        data['avg_score'] = data['total_score'] / data['count']
    
    sorted_words = sorted(word_scores.items(), key=lambda x: x[1]['avg_score'], reverse=True)
    return [w[0] for w in sorted_words[:10]]

def generate_evolved_configs(tier, patterns, danger_zones, winning_words, 
                             hook_analysis, time_analysis, configs, sentiment_data):
    new_configs = json.loads(json.dumps(configs))
    
    for key in new_configs:
        current_version = new_configs[key].get('version', 'default')
        if current_version == 'default':
            new_configs[key]['version'] = 'v1.0'
        else:
            try:
                v_num = float(current_version.replace('v', ''))
                new_configs[key]['version'] = f'v{round(v_num + 0.1, 1)}'
            except:
                new_configs[key]['version'] = 'v1.0'
    
    if tier == 'BREAKTHROUGH':
        mutate_config(new_configs, patterns, danger_zones, winning_words, 
                       hook_analysis, time_analysis, sentiment_data, intensity=0.15)
    elif tier == 'IMPROVEMENT':
        mutate_config(new_configs, patterns, danger_zones, winning_words,
                       hook_analysis, time_analysis, sentiment_data, intensity=0.10)
    elif tier == 'NEUTRAL':
        mutate_config(new_configs, patterns, danger_zones, winning_words,
                       hook_analysis, time_analysis, sentiment_data, intensity=0.05)
    elif tier == 'DISASTER':
        new_configs = reset_to_safe_defaults()
    
    return new_configs

def mutate_config(configs, patterns, danger_zones, winning_words,
                  hook_analysis, time_analysis, sentiment_data, intensity):
    
    vg = configs.get('video-generator-config.json', {})
    if vg:
        current_cut = vg.get('visual_settings', {}).get('cut_interval_seconds', 2.0)
        change = SAFE_CHANGE_LIMITS['cut_interval_seconds'] * intensity
        if patterns.get('top_avg_length', 130) > patterns.get('bottom_avg_length', 130):
            vg['visual_settings']['cut_interval_seconds'] = round(max(1.0, current_cut - change), 1)
        else:
            vg['visual_settings']['cut_interval_seconds'] = round(min(4.0, current_cut + change), 1)
        
        if hook_analysis:
            best_hook = max(hook_analysis.items(), key=lambda x: x[1].get('avg_score', 0))[0]
            vg['hook_settings']['style'] = best_hook
        
        vg['title_optimization']['preferred_words'] = winning_words[:5]
        vg['content_rules']['danger_zone_mitigation'] = ['zoom', 'text_flash', 'sound_effect']
    
    ag = configs.get('audio-generator-config.json', {})
    if ag:
        current_pace = ag.get('voice_settings', {}).get('pace_wpm', 160)
        change = SAFE_CHANGE_LIMITS['pace_wpm'] * intensity
        
        if patterns.get('top_emotional_words'):
            ag['voice_settings']['pace_wpm'] = round(min(180, current_pace + change))
        else:
            ag['voice_settings']['pace_wpm'] = round(max(140, current_pace - change))
        
        ag['voice_settings']['emphasis_words'] = winning_words[:5]
        
        current_vol = ag.get('audio_effects', {}).get('background_music_volume', 0.15)
        change_vol = SAFE_CHANGE_LIMITS['background_music_volume'] * intensity
        ag['audio_effects']['background_music_volume'] = round(
            max(0.05, min(0.3, current_vol + random.uniform(-change_vol, change_vol))), 3
        )
    
    eg = configs.get('video-editor-config.json', {})
    if eg:
        eg['danger_zones'] = danger_zones[:4]
        eg['text_overlay']['highlight_keywords'] = winning_words[:4]
    
    ug = configs.get('uploader-config.json', {})
    if ug:
        if time_analysis:
            best_hour = max(time_analysis.items(), key=lambda x: x[1].get('avg_score', 0))[0]
            if isinstance(best_hour, int):
                best_time = f'{best_hour:02d}:00'
                if best_time not in ug['optimal_upload_times']:
                    ug['optimal_upload_times'].append(best_time)
                    ug['optimal_upload_times'] = ug['optimal_upload_times'][-2:]
        
        if sentiment_data and sentiment_data.get('suggested_rules'):
            for rule in sentiment_data['suggested_rules']:
                if 'example' in rule.lower() and 'example' not in ug['hashtags']['niche']:
                    ug['hashtags']['niche'].append('Examples')
    
    sp = configs.get('script-prompt-config.json', {})
    if sp:
        optimal_len = patterns.get('top_avg_length', 130)
        sp['rules']['optimal_length_words'] = max(120, min(150, optimal_len))
        
        if patterns.get('top_questions', 0) > patterns.get('bottom_questions', 0):
            if 'use_questions' not in sp['rules']['preferred_patterns']:
                sp['rules']['preferred_patterns'].append('use_questions')
        
        if patterns.get('top_numbers', 0) > patterns.get('bottom_numbers', 0):
            if 'use_numbers' not in sp['rules']['preferred_patterns']:
                sp['rules']['preferred_patterns'].append('use_numbers')

def reset_to_safe_defaults():
    defaults = {}
    for filename in ['video-generator-config.json', 'audio-generator-config.json',
                     'video-editor-config.json', 'uploader-config.json',
                     'script-prompt-config.json']:
        defaults[filename] = get_default_config(filename)
        defaults[filename]['version'] = 'reset-v1.0'
        defaults[filename]['reset_reason'] = 'DISASTER detected'
    return defaults

def check_fatigue(history):
    if len(history) < 3:
        return False, None
    
    last_3 = history[-3:]
    poor_results = [h for h in last_3 if h['tier'] in ['NEUTRAL', 'DISASTER']]
    
    if len(poor_results) >= 3:
        pivot_angles = [
            'how to detect manipulation',
            'signs someone is controlling you',
            'dark psychology in relationships',
            'mind games people play',
            'psychological tricks to read people'
        ]
        return True, random.choice(pivot_angles)
    
    return False, None

def save_evolution_history(tier, z_score, latest_video, changes_made):
    os.makedirs('evolution', exist_ok=True)
    
    history_entry = {
        'timestamp': datetime.now().isoformat(),
        'tier': tier,
        'z_score': z_score,
        'latest_video_id': latest_video.get('video_id'),
        'latest_score': latest_video.get('composite_score'),
        'changes_made': changes_made
    }
    
    history = []
    if os.path.exists('evolution/history.json'):
        with open('evolution/history.json', 'r') as f:
            history = json.load(f)
    
    history.append(history_entry)
    
    with open('evolution/history.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    return history

def save_configs(configs):
    os.makedirs('temp/pending-configs', exist_ok=True)
    
    for filename, config in configs.items():
        filepath = f'temp/pending-configs/{filename}'
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        print(f'  Pending config saved: {filename}')

def main():
    print('Starting evolution engine...')
    
    analytics = load_analytics()
    videos = analytics.get('videos', [])
    
    if len(videos) < 2:
        print('Not enough videos for evolution, using defaults')
        configs = {f: get_default_config(f) for f in [
            'video-generator-config.json', 'audio-generator-config.json',
            'video-editor-config.json', 'uploader-config.json',
            'script-prompt-config.json'
        ]}
        save_configs(configs)
        return
    
    latest = videos[0]
    baseline = videos[1:11]
    
    z_score = calculate_z_score(latest, baseline)
    tier = determine_tier(latest, baseline, z_score)
    
    print(f'  Latest video score: {latest["composite_score"]}')
    print(f'  Z-score: {z_score}')
    print(f'  Tier: {tier}')
    
    patterns = analyze_script_patterns(videos)
    danger_zones = analyze_retention_danger_zones(videos)
    winning_words = get_winning_words(videos)
    hook_analysis = analytics.get('hook_analysis', {})
    time_analysis = analytics.get('time_analysis', {})
    
    sentiment_data = {}
    if os.path.exists('data/comment_sentiment.json'):
        with open('data/comment_sentiment.json', 'r') as f:
            sentiments = json.load(f)
            if sentiments:
                sentiment_data = sentiments[0]
    
    configs = load_current_configs()
    
    history = []
    if os.path.exists('evolution/history.json'):
        with open('evolution/history.json', 'r') as f:
            history = json.load(f)
    
    fatigue_detected, pivot_angle = check_fatigue(history)
    if fatigue_detected:
        print(f'  Content fatigue detected! Suggested pivot: {pivot_angle}')
        for key in configs:
            configs[key]['pivot_triggered'] = True
            configs[key]['pivot_angle'] = pivot_angle
    
    new_configs = generate_evolved_configs(
        tier, patterns, danger_zones, winning_words,
        hook_analysis, time_analysis, configs, sentiment_data
    )
    
    save_configs(new_configs)
    
    changes_made = {k: v.get('version') for k, v in new_configs.items()}
    history = save_evolution_history(tier, z_score, latest, changes_made)
    
    report_data = {
        'tier': tier,
        'z_score': z_score,
        'latest_score': latest['composite_score'],
        'fatigue_detected': fatigue_detected,
        'pivot_angle': pivot_angle,
        'winning_words': winning_words,
        'best_hook': max(hook_analysis.items(), key=lambda x: x[1].get('avg_score', 0))[0] if hook_analysis else 'unknown'
    }
    
    with open('temp/evolution_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print('Evolution complete')

if __name__ == '__main__':
    main()

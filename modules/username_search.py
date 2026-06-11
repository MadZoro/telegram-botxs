import aiohttp
import asyncio
import subprocess
import os
import json

async def search_username(username: str) -> list:
    """ПОЛНЫЙ поиск по username: 500+ сайтов, возможные имена, аватарки, история"""
    username = username.lstrip('@')
    results = []
    
    # === 1. ПОИСК ПО 500+ САЙТАМ (через Blackbird) ===
    results.append("🔍 ПОИСК НА 500+ ПЛАТФОРМАХ:")
    
    try:
        # Путь к Blackbird (если установлен)
        blackbird_path = os.path.join(os.path.dirname(__file__), '..', 'blackbird-osint', 'blackbird.py')
        
        if os.path.exists(blackbird_path):
            proc = await asyncio.create_subprocess_exec(
                'python', blackbird_path, '-u', username, '--json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if stdout:
                data = json.loads(stdout)
                found_count = 0
                for site, info in data.items():
                    if info.get('exists', False):
                        url = info.get('url', '')
                        results.append(f"   ✅ {site}: {url}")
                        found_count += 1
                        if found_count >= 15:
                            results.append(f"   ... и ещё много других")
                            break
                if found_count == 0:
                    results.append("   ❌ Аккаунты не найдены")
        else:
            results.append("   ⚠️ Blackbird не установлен (установка: git clone https://github.com/phend0/blackbird-osint.git)")
    except Exception as e:
        results.append(f"   ⚠️ Ошибка Blackbird: {str(e)[:50]}")
    
    results.append("")  # Отступ
    
    # === 2. РУЧНАЯ ПРОВЕРКА ПОПУЛЯРНЫХ ПЛАТФОРМ ===
    results.append("🔍 РУЧНАЯ ПРОВЕРКА ПОПУЛЯРНЫХ ПЛАТФОРМ:")
    
    platforms = [
        ("Telegram", f"https://t.me/{username}"),
        ("Instagram", f"https://instagram.com/{username}"),
        ("Twitter/X", f"https://twitter.com/{username}"),
        ("GitHub", f"https://github.com/{username}"),
        ("Reddit", f"https://reddit.com/user/{username}"),
        ("YouTube", f"https://youtube.com/@{username}"),
        ("TikTok", f"https://tiktok.com/@{username}"),
        ("VK", f"https://vk.com/{username}"),
        ("Facebook", f"https://facebook.com/{username}"),
        ("Pinterest", f"https://pinterest.com/{username}"),
        ("Twitch", f"https://twitch.tv/{username}"),
        ("Steam", f"https://steamcommunity.com/id/{username}"),
        ("Spotify", f"https://open.spotify.com/user/{username}"),
        ("Medium", f"https://medium.com/@{username}"),
        ("Imgur", f"https://imgur.com/user/{username}"),
        ("DeviantArt", f"https://deviantart.com/{username}"),
        ("Behance", f"https://behance.net/{username}"),
        ("Dribbble", f"https://dribbble.com/{username}"),
        ("Flickr", f"https://flickr.com/people/{username}"),
        ("Tumblr", f"https://{username}.tumblr.com"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for platform, url in platforms:
            try:
                async with session.get(url, timeout=5, allow_redirects=True) as response:
                    if response.status == 200:
                        results.append(f"   ✅ {platform}: {url}")
            except:
                pass
    
    results.append("")  # Отступ
    
    # === 3. ВОЗМОЖНЫЕ ИМЕНА (на основе username) ===
    results.append("🔍 ВОЗМОЖНЫЕ ВАРИАНТЫ ИМЕНИ (на основе username):")
    import re
    possible_name = re.sub(r'[._\-0-9]', ' ', username).strip()
    if possible_name and len(possible_name) > 2:
        results.append(f"   • {possible_name.title()}")
        results.append(f"   • {possible_name.capitalize()}")
    
    # === 4. ИСТОРИЯ ИЗМЕНЕНИЙ USERNAME (через Unamer) ===
    results.append("")
    results.append("💡 ДЛЯ ПОЛУЧЕНИЯ ПОЛНЫХ ДАННЫХ И ИСТОРИИ ИСПОЛЬЗУЙТЕ БОТОВ:")
    results.append("   • @SangMata_bot — история смены username и имени")
    results.append("   • @Unamer_bot — поиск по username, история, возможный номер")
    results.append("   • @Usersbox_bot — пробив по нику, email, номеру")
    results.append("   • @PRObivonBot — полный пробив (телефон, ФИО, адреса)")
    
    return results if results else ["❌ Информация не найдена"]

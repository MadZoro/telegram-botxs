import aiohttp
import hashlib
import asyncio

async def search_email(email: str) -> list:
    """ПОЛНЫЙ поиск по email: утечки, аккаунты, имена, пароли"""
    results = []
    
    # === 1. ПРОВЕРКА УТЕЧЕК (BreachDirectory) ===
    results.append("🔍 ПРОВЕРКА УТЕЧЕК ДАННЫХ:")
    
    async with aiohttp.ClientSession() as session:
        try:
            url = f"https://breachdirectory.org/api?email={email}"
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('result') == 'success' and data.get('breaches'):
                        breaches = data['breaches']
                        results.append(f"   🔓 Найден в {len(breaches)} утечках:")
                        for breach in breaches[:5]:
                            name = breach.get('name', 'Неизвестно')
                            date = breach.get('breach_date', 'дата неизвестна')
                            results.append(f"      • {name} ({date})")
                        
                        # Пароли, если есть
                        if 'password' in data and data['password']:
                            results.append(f"   🔑 Возможный пароль: {data['password'][:20]}...")
                    else:
                        results.append("   ✅ Не найден в известных утечках")
                else:
                    results.append(f"   ⚠️ Ошибка API: статус {response.status}")
        except Exception as e:
            results.append(f"   ⚠️ Ошибка: {str(e)[:60]}")
    
    results.append("")  # Отступ
    
    # === 2. ПОИСК АККАУНТОВ ПО EMAIL (Holehe) ===
    results.append("🔍 ПОИСК АККАУНТОВ ПО EMAIL (через Holehe):")
    
    try:
        import holehe
        modules = holehe.modules
        
        # Основные сервисы для проверки
        services = ['facebook', 'instagram', 'twitter', 'github', 'spotify', 
                    'snapchat', 'pinterest', 'tumblr', 'adobe', 'linkedin']
        
        found_services = []
        for service in services:
            try:
                func = getattr(modules, service)
                result = await func(email)
                if result.get('exists'):
                    found_services.append(service.capitalize())
            except:
                pass
        
        if found_services:
            results.append(f"   ✅ Аккаунты найдены на: {', '.join(found_services[:10])}")
        else:
            results.append("   ❌ Аккаунты не найдены или сервисы недоступны")
            
    except ImportError:
        results.append("   ⚠️ Holehe не установлен. Установка: pip install holehe")
    except Exception as e:
        results.append(f"   ⚠️ Ошибка Holehe: {str(e)[:50]}")
    
    results.append("")  # Отступ
    
    # === 3. ВОЗМОЖНЫЕ ИМЕНА (из email) ===
    results.append("🔍 ВОЗМОЖНЫЕ ИМЕНА И ВАРИАНТЫ:")
    local_part = email.split('@')[0]
    import re
    possible_name = re.sub(r'[._\-0-9]', ' ', local_part).strip()
    if possible_name and len(possible_name) > 2:
        results.append(f"   • {possible_name.title()}")
        results.append(f"   • {possible_name.capitalize()}")
    results.append(f"   • Username для поиска: {local_part}")
    
    # === 4. ИНСТРУКЦИЯ ПО ПОЛНОМУ ПРОБИВУ ===
    results.append("")
    results.append("💡 ДЛЯ ПОЛНОГО ПРОБИВА EMAIL ИСПОЛЬЗУЙТЕ:")
    results.append("   • @faizan_bot — поиск по email в утечках с паролями")
    results.append("   • @leak_check_bot — проверка email и username")
    results.append("   • @Usersbox_bot — пробив по email, номеру, нику")
    results.append("   • @PRObivonBot — полный пробив по email (ФИО, адреса)")
    
    return results

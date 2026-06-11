import re
import aiohttp
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from typing import List

async def search_phone(phone: str) -> List[str]:
    """Расширенный поиск информации по номеру телефона"""
    results = []
    
    # Нормализация номера
    phone_clean = re.sub(r'\D', '', phone)
    
    if len(phone_clean) == 10:
        phone_full = "38" + phone_clean
    elif len(phone_clean) == 12 and phone_clean.startswith("38"):
        phone_full = phone_clean
    elif len(phone_clean) == 11 and phone_clean.startswith("8"):
        phone_full = "38" + phone_clean[1:]
    else:
        phone_full = phone_clean
    
    # 1. Информация об операторе и регионе
    try:
        parsed = phonenumbers.parse(phone_full, None)
        operator = carrier.name_for_number(parsed, "ru")
        region = geocoder.description_for_number(parsed, "ru")
        tz = timezone.time_zones_for_number(parsed)
        
        results.append("📡 *Информация о номере:*")
        if operator:
            results.append(f"   • Оператор: {operator}")
        if region:
            results.append(f"   • Регион: {region}")
        if tz:
            results.append(f"   • Часовой пояс: {', '.join(tz)}")
    except Exception as e:
        results.append(f"⚠️ Ошибка определения оператора: {str(e)[:50]}")
    
    # 2. Поиск аккаунтов по номеру в соцсетях
    results.append("\n🔍 *Поиск аккаунтов по номеру:*")
    
    # Формируем поисковые запросы
    search_queries = [
        f"https://google.com/search?q={phone_full}",
        f"https://yandex.ru/search/?text={phone_full}",
        f"https://vk.com/search?c[phone]={phone_full}",
        f"https://www.facebook.com/search/top?q={phone_full}",
        f"https://twitter.com/search?q={phone_full}",
        f"https://www.instagram.com/accounts/web_search/?q={phone_full}",
        f"https://www.ok.ru/search?q={phone_full}",
        f"https://www.tiktok.com/search?q={phone_full}",
        f"https://www.linkedin.com/search/results/all/?keywords={phone_full}",
        f"https://github.com/search?q={phone_full}&type=users",
        f"https://t.me/s/{phone_full}",
        f"https://whatsapp.com/phone/{phone_clean}",
        f"https://www.avito.ru/search?q={phone_full}",
        f"https://www.olx.ua/search/?q={phone_full}",
        f"https://www.prom.ua/search?search_term={phone_full}",
        f"https://www.work.ua/resumes/search/?keywords={phone_full}",
        f"https://rabota.ua/search?query={phone_full}",
        f"https://www.djinni.co/jobs-keyword-{phone_full}/",
        f"https://www.2gis.ru/search/{phone_full}",
        f"https://www.yellowpages.com/search?search_terms={phone_full}",
        f"https://www.truecaller.com/search/{phone_full}",
        f"https://www.spytox.com/search/{phone_full}",
        f"https://www.numberway.com/{phone_full}",
        f"https://www.phonesearch.us/phone/{phone_full}",
        f"https://www.searchpeoplefree.com/phone/{phone_full}",
        f"https://www.whitepages.com/phone/{phone_full}",
        f"https://www.zaba.ru/search/?query={phone_full}",
        f"https://www.rusprofile.ru/search?query={phone_full}",
        f"https://www.list-org.com/search?type=phone&val={phone_full}",
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in search_queries[:15]:  # Ограничиваем для скорости
            try:
                async with session.get(url, timeout=5, allow_redirects=True) as response:
                    if response.status == 200:
                        # Сохраняем ссылку для ручной проверки
                        results.append(f"   • Возможные данные: {url}")
            except:
                pass
    
    # 3. Проверка в базах утечек через публичные API
    breach_results = await check_phone_in_breaches(phone_full)
    if breach_results:
        results.append("\n🔓 *Найден в базах утечек:*")
        results.extend(breach_results)
    
    # 4. Анализ WhatsApp/Telegram
    results.append("\n📱 *Мессенджеры:*")
    results.append(f"   • WhatsApp: https://wa.me/{phone_clean}")
    results.append(f"   • Telegram: https://t.me/{phone_clean}")
    results.append(f"   • Viber: viber://contact?number={phone_clean}")
    results.append(f"   • Signal: https://signal.me/#p/{phone_clean}")
    
    return results

async def check_phone_in_breaches(phone: str) -> List[str]:
    """Проверка номера в открытых базах утечек"""
    results = []
    
    # Проверка через breachdirectory (работает с email, но иногда и с телефоном)
    async with aiohttp.ClientSession() as session:
        try:
            url = f"https://breachdirectory.org/api?phone={phone}"
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('result') == 'success' and data.get('breaches'):
                        for breach in data['breaches'][:3]:
                            name = breach.get('name', 'Неизвестно')
                            date = breach.get('breach_date', 'дата неизвестна')
                            results.append(f"   • {name} ({date})")
        except:
            pass
    
    return results

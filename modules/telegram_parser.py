import os
from telethon import TelegramClient

async def get_telegram_user_info(query: str) -> list:
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    account_phone = os.getenv("PHONE")
    
    if not api_id or not api_hash:
        return ["⚠️ Telegram API не настроен. Укажите API_ID и API_HASH в .env"]
    
    results = []
    
    try:
        client = TelegramClient("temp_session", int(api_id), api_hash)
        await client.start(account_phone)
        
        if query.isdigit():
            entity = await client.get_entity(int(query))
        else:
            username = query.lstrip('@')
            entity = await client.get_entity(username)
        
        results.append(f"👤 ID: {entity.id}")
        results.append(f"📛 Имя: {entity.first_name}")
        
        if hasattr(entity, 'last_name') and entity.last_name:
            results.append(f"🏷️ Фамилия: {entity.last_name}")
        
        if hasattr(entity, 'username') and entity.username:
            results.append(f"🔗 Username: @{entity.username}")
        
        results.append(f"🤖 Бот: {'Да' if entity.bot else 'Нет'}")
        results.append(f"⭐ Premium: {'Да' if getattr(entity, 'premium', False) else 'Нет'}")
        
        await client.disconnect()
        
    except Exception as e:
        results.append(f"❌ Ошибка: {str(e)[:100]}")
    
    return results

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty

def read_keywords(file_name):
    """Читает ключевые слова из файла."""
    with open(file_name, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def save_groups_to_file(groups, filename='groups.txt'):
    """Сохраняет ссылки на группы в текстовый файл."""
    with open(filename, 'w', encoding='utf-8') as f:
        for group in groups:
            username = group.username if group.username else 'нет ссылки'
            f.write(f"{group.title}: https://t.me/{username}\n")
    print(f"Группы сохранены в '{filename}'")

def search_and_save_groups(client, word1_list, word2_list):
    """Ищет группы по ключевым словам и сохраняет их в файл."""
    chats = []
    last_date = None
    size_chats = 200
    
    try:
        result = client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=size_chats,
            hash=0
        ))
        chats.extend(result.chats)
    except Exception as e:
        print(f"Ошибка при получении чатов: {str(e)}")
        return
    
    matched_groups = []

    print(f"Всего чатов: {len(chats)}")

    for chat in chats:
        try:
            if hasattr(chat, 'megagroup') and chat.megagroup:
                if any(word1.lower() in chat.title.lower() and any(word2.lower() in chat.title.lower() for word2 in word2_list) for word1 in word1_list):
                    matched_groups.append(chat)
                    print(f"Найден канал: {chat.title} (https://t.me/{chat.username if chat.username else 'нет ссылки'})")
        except AttributeError as e:
            print(f"Ошибка при обработке чата {chat.id}: {str(e)}")

    if matched_groups:
        save_groups_to_file(matched_groups)
        print(f"Найдено {len(matched_groups)} групп. Сохранено в файл 'groups.txt'")
    else:
        print("Не найдено групп, соответствующих ключевым словам.")

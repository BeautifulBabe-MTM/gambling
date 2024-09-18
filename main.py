from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from defunc import *
from channel_parser import search_and_save_groups
import time
import random
import os

def read_keywords(file_name):
    """Читает ключевые слова из файла."""
    with open(file_name, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def save_groups_to_file(groups):
    """Сохраняет ссылки на группы в текстовый файл."""
    with open('groups.txt', 'w', encoding='utf-8') as f:
        for group in groups:
            username = group.username if group.username else 'нет ссылки'
            f.write(f"{group.title}: https://t.me/{username}\n")
    print("Группы сохранены в 'groups.txt'")

def search_and_save_groups(client, word1_list, word2_list):
    """Ищет группы по ключевым словам и сохраняет их в файл."""
    chats = []
    last_date = None
    size_chats = 200
    
    try:
        # Получаем чаты
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
            # Проверяем наличие атрибутов
            if hasattr(chat, 'megagroup') and chat.megagroup:
                # Проверяем наличие ключевых слов в заголовке чата
                if any(word1.lower() in chat.title.lower() and any(word2.lower() in chat.title.lower() for word2 in word2_list) for word1 in word1_list):
                    matched_groups.append(chat)
                    print(f"Найден канал: {chat.title} (https://t.me/{chat.username if chat.username else 'нет ссылки'})")
        except AttributeError as e:
            print(f"Ошибка при обработке чата {chat.id}: {str(e)}")

    # Проверяем количество найденных групп
    if matched_groups:
        save_groups_to_file(matched_groups)
        print(f"Найдено {len(matched_groups)} групп. Сохранено в файл 'groups.txt'")
    else:
        print("Не найдено групп, соответствующих ключевым словам.")

def send_message_to_groups(client, chats, message):
    """Отправляет сообщение во все группы из списка."""
    for chat in chats:
        try:
            client.send_message(chat, message)
            print(f"Сообщение отправлено в группу: {chat.title}")
        except (PeerFloodError, UserPrivacyRestrictedError) as e:
            print(f"Не удалось отправить сообщение в {chat.title}: {str(e)}")
            time.sleep(1)
        except Exception as e:
            print(f"Ошибка: {str(e)}")
        time.sleep(random.randint(1, 3))

if __name__ == "__main__":
    while True:
        options = getoptions()  # Предполагается, что функция getoptions() загружает конфигурацию
        if not options or options[0] == "NONEID\n" or options[1] == "NONEHASH\n":
            print("Добавьте API_ID и API_HASH")
            time.sleep(2)
            config()  # Предполагается, что функция config() предоставляет возможность настроить параметры
            continue
        
        api_id = int(options[0].replace('\n', ''))
        api_hash = str(options[1].replace('\n', ''))

        user_id = options[2] == 'True\n'
        user_name = options[3] == 'True\n'

        os.system('cls||clear')
        selection = str(input("1 - Настройки\n"
                            "2 - Парсинг\n"
                            "3 - Запустить парсер\n"
                            "4 - Заспамить чаты\n"
                            "5 - Парсинг открытых каналов\n"
                            "e - Выход\n"
                            "Ввод: "))

        if selection == '1':
            config()  # Предполагается, что функция config() предоставляет возможность настроить параметры

        elif selection == '2':
            chats = []
            last_date = None    
            size_chats = 200
            groups = []         

            print("Выберите юзер-бота для парсинга.\n"
                "(Аккаунт который состоит в группах, которые нужно спарсить)\n")

            sessions = [file for file in os.listdir('.') if file.endswith('.session')]

            for i in range(len(sessions)):
                print(f"[{i}] -", sessions[i], '\n')
            i = int(input("Ввод: "))
            
            client = TelegramClient(sessions[i].replace('\n', ''), api_id, api_hash, timeout=60).start(sessions[i].replace('\n', ''))

            result = client(GetDialogsRequest(
                offset_date=last_date,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=size_chats,
                hash=0
            ))
            chats.extend(result.chats)

            for chat in chats:
                try:
                    if chat.megagroup:  # Фильтрация по группам
                        groups.append(chat)         
                except:
                    continue
            
            i = 0
            print('Очистка базы юзеров: clear') 
            print('-----------------------------')
            for g in groups:
                print(str(i) + ' - ' + g.title)
                i += 1
            print(str(i + 1) + ' - ' + 'Спарсить всё')
            g_index = str(input())

            if g_index == 'clear':
                with open('usernames.txt', 'w') as f:
                    pass
                with open('userids.txt', 'w') as f:
                    pass

            elif int(g_index) < i + 1:
                target_group = groups[int(g_index)]
                parsing(client, target_group, user_id, user_name)
                print('Спаршено.')

            elif int(g_index) == i + 1:
                for g_index in groups:
                    parsing(client, g_index, user_id, user_name)
                print('Спаршено.')

        elif selection == '3':
            word1_list = read_keywords('word1.txt')
            word2_list = read_keywords('word2.txt')

            print("Выберите юзер-бота для поиска групп.\n"
                "(Аккаунт, который состоит в группах, где будет выполняться поиск)\n")

            sessions = [file for file in os.listdir('.') if file.endswith('.session')]

            for i in range(len(sessions)):
                print(f"[{i}] -", sessions[i], '\n')
            i = int(input("Ввод: "))
            
            client = TelegramClient(sessions[i].replace('\n', ''), api_id, api_hash).start(sessions[i].replace('\n', ''))

            chats = []
            last_date = None    
            size_chats = 200

            result = client(GetDialogsRequest(
                offset_date=last_date,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=size_chats,
                hash=0
            ))
            chats.extend(result.chats)

            search_and_save_groups(client, word1_list, word2_list)

        elif selection == '4':
            print("Введите сообщение для рассылки: ")
            message = input()

            print("Выберите юзер-бота для рассылки сообщений.\n"
                "(Аккаунт, который состоит в группах, куда будут отправлены сообщения)\n")

            sessions = [file for file in os.listdir('.') if file.endswith('.session')]

            for i in range(len(sessions)):
                print(f"[{i}] -", sessions[i], '\n')
            i = int(input("Ввод: "))
            
            client = TelegramClient(sessions[i].replace('\n', ''), api_id, api_hash).start(sessions[i].replace('\n', ''))

            chats = []
            last_date = None    
            size_chats = 200

            result = client(GetDialogsRequest(
                offset_date=last_date,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=size_chats,
                hash=0
            ))
            chats.extend(result.chats)

            send_message_to_groups(client, chats, message)

        elif selection == '5':
            word1_list = read_keywords('word1.txt')
            word2_list = read_keywords('word2.txt')

            print("Выберите юзер-бота для поиска открытых каналов.\n"
                "(Аккаунт, который состоит в группах, где будет выполняться поиск)\n")

            sessions = [file for file in os.listdir('.') if file.endswith('.session')]

            for i in range(len(sessions)):
                print(f"[{i}] -", sessions[i], '\n')
            i = int(input("Ввод: "))
            
            client = TelegramClient(sessions[i].replace('\n', ''), api_id, api_hash).start(sessions[i].replace('\n', ''))

            search_and_save_groups(client, word1_list, word2_list)

        elif selection == 'e':
            break

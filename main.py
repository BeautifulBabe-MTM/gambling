from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from defunc import *
import time
import random
import os


def read_keywords(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def search_groups(client, chats, word1_list, word2_list):
    matched_groups = []
    for chat in chats:
        for word1 in word1_list:
            for word2 in word2_list:
                keyword = f"{word1} {word2}"
                if keyword.lower() in chat.title.lower(): 
                    matched_groups.append(chat.title)
                    break
    return matched_groups

def send_message_to_groups(client, chats, message):
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
        options = getoptions()
        if not options or options[0] == "NONEID\n" or options[1] == "NONEHASH\n":
            print("Добавьте API_ID и API_HASH")
            time.sleep(2)
            config()
            continue
        
        api_id = int(options[0].replace('\n', ''))
        api_hash = str(options[1].replace('\n', ''))

        if options[2] == 'True\n':
            user_id = True
        else:
            user_id = False
        if options[3] == 'True\n':
            user_name = True
        else:
            user_name = False

        os.system('cls||clear')
        selection = str(input("1 - Настройки\n"
                            "2 - Парсинг\n"
                            "3 - Запустить парсер\n"
                            "4 - Заспамить чаты\n"
                            "e - Выход\n"
                            "Ввод: "))
        

        if selection == '1':
            config()


        elif selection == '2':
            chats = []
            last_date = None    
            size_chats = 200
            groups = []         

            print("Выберите юзер-бота для парсинга.\n"
                "(Аккаунт который состоит в группах, которые нужно спарсить)\n")

            sessions = []
            for file in os.listdir('.'):
                if file.endswith('.session'):
                    sessions.append(file)


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
                    if chat.megagroup is True:
                        groups.append(chat)         
                except:
                    continue
            
            i = 0
            print('Очистка базы юзеров: clear') 
            print('-----------------------------')
            for g in groups:
                print(str(i) + ' - ' + g.title)
                i+=1
            print(str(i + 1) + ' - ' + 'Спарсить всё')
            g_index = str(input())

            if g_index == 'clear':
                f = open('usernames.txt', 'w')
                f.close()
                f = open('userids.txt', 'w')
                f.close

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

            sessions = []
            for file in os.listdir('.'):
                if file.endswith('.session'):
                    sessions.append(file)

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

            matched_groups = search_groups(client, chats, word1_list, word2_list)

            with open('groups.txt', 'w') as f:
                for group in matched_groups:
                    f.write(group + '\n')

            print(f"Найдено групп по ключевым словам: {len(matched_groups)}")
            print("Группы записаны в файл 'groups.txt'")


        elif selection == '4':
            print("Введите сообщение для рассылки: ")
            message = input()

            print("Выберите юзер-бота для рассылки сообщений.\n"
                "(Аккаунт, который состоит в группах, куда будут отправлены сообщения)\n")

            sessions = []
            for file in os.listdir('.'):
                if file.endswith('.session'):
                    sessions.append(file)

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


        elif selection == 'e':
            break

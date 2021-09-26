import telebot
import json
import re
import random
import time
from telebot import types
import requests
from datetime import datetime, timedelta, timezone
########################################
bot_token = '2021306556:AAHhSwrcHJSexPzNiCqUDdw8JOD0fdl2Vro'
bot_username = 'dicefirerobot'
instruction = 't.me/dicefirerobot'
support = 't.me/yankhtop'
game_results = [0, 'vk.com']
qiwitoken = 'a30231d883365add54ad456c2327d560'
minbet = 10
########################################

class Game:
    def __init__(self, bot):
        with open('rooms.json', 'w') as f:
            f.write("{}")
        game_code = 0
        self.bet = 0
        self.bot_username = bot_username
        self.bot = bot
        game = {}
        self.mingame = 0
        self.maxgame = 0
        self.link = ''
        self.refgames = {}
        self.cubes = {'1': 'CAACAgIAAxkBAAECFzBgWQ_yeuIBkkWQ_D696jopNKHwIQAC3MYBAAFji0YMsbUSFEouGv8eBA', '2': 'CAACAgIAAxkBAAECFzJgWRAxouWCfiOGklU4hQOmQNoGkQAC3cYBAAFji0YM608pO-wjAlEeBA', '3': 'CAACAgIAAxkBAAECFzRgWRBHncCwoy9Lwk6XZ1PkyGMvwAAC3sYBAAFji0YMVHH9hav7ILkeBA', '4': 'CAACAgIAAxkBAAECFzZgWRBg_ejUEyYZSzgl69-21Vdw0QAC38YBAAFji0YMHEUTINW7YxceBA', '5': 'CAACAgIAAxkBAAECFzhgWRB1oamDAAEDSjY7G_MAARj7h52QAALgxgEAAWOLRgxIsfP6yP8mqR4E', '6': 'CAACAgIAAxkBAAECFzpgWRCTGsJX03wNEzFNNlOd4DJJEQAC4cYBAAFji0YM75p8zae_tHoeBA'}
    def getKey(self, key):
        try:
            with open('rooms.json', 'r') as f:
                self.data = json.loads(f.read())
            return self.data[str(key)]
        except:
            raise
    def setKey(self, key, value):
        try:
            try:
                with open('rooms.json', 'r') as f:
                    self.data = json.loads(f.read())
            except:
                self.data = {}
            self.data[str(key)] = value
            with open('rooms.json', 'w') as f:
                f.write(json.dumps(self.data))
        except:
            raise
    def deleteKey(self, key):
        try:
            with open('rooms.json', 'r') as f:
                self.data = json.loads(f.read())
            value = self.data[key]
            del self.data[key]
            with open('rooms.json', 'w') as f:
                f.write(json.dumps(self.data))
            try:
                with open('old_rooms.json', 'r') as f:
                    self.data = json.loads(f.read())
            except:
                self.data = {}
            self.data[key] = value
            with open('old_rooms.json', 'w') as f:
                f.write(json.dumps(self.data))
        except:
            raise
    def join_game(self, room_id, user_id, user_name):
        try:
            game = self.getKey(str(room_id))
            if game['guest'] == {}:
                game['guest'] = {'id': user_id,  'name': user_name, 'circles': 0}
                game['player_ids'].append(user_id)
                #print(game['players'])
                self.setKey(str(room_id), game)
                return str(room_id)
            else:
                return 'FULL'
        except:
            return 'NF'
    def join_random_game(self, user_id: int, user_name: str, bet: int):
        try:
            try:
                boolean = True
                errors = ['NF', 'FULL']
                with open('rooms.json', 'r') as f:
                    data = json.loads(f.read())
                games = data.keys()
                num = 0
                if boolean:
                    for i in games:
                        if data[i]['bet'] <= bet and boolean:
                            ans = self.join_game(i, user_id, user_name)
                            if not(ans in errors):
                                boolean = False
                                return i
                        else:
                            if num == len(games)-1:
                                return 'NF'
                        num += 1
            except:
                return 'NF'
        except:
            raise
    def get_game(self, room_id):
        try:
            game = self.getKey(str(room_id))
            return game
        except:
            return None
        
    def end_game(self, room_id, prize):
        data = self.getKey(str(room_id))
        data['prize'] = prize
        self.setKey(str(room_id), data)
        self.deleteKey(str(room_id))

    def get_all_game_data(self, user_id):
        try:
            rooms = {}
            with open('users.json', 'r') as f:
                data = json.loads(f.read())
            games = data[str(user_id)]['games']
            for i in games:
                game = self.get_old_game(str(i))
                rooms[str(i)] = game
            return rooms
        except:
            return []
    
    def get_rooms(self):
        self.mingame = 0
        self.maxgame = 0
        try:
            with open('rooms.json', 'r') as f:
                data = json.loads(f.read())
            for i in data.keys():
                if data[i]['bet'] > self.maxgame:
                    self.maxgame = data[i]['bet']
                    if self.mingame == 0:
                        self.mingame = self.maxgame
                elif data[i]['bet'] < self.mingame:
                    self.mingame = data[i]['bet']
        except:
            self.mingame = 0
            self.maxgame = 0
        return self.mingame, self.maxgame
    
    def create_game(self, bet: int, owner_id: int, owner_name: str):
        game = {}
        game['bet'] = bet 
        game['key'] = random.randint(100000, 999999)
        game['owner'] = {"id": owner_id, "name": owner_name, "circles": 0}
        game['guest'] = {}
        game['player_ids'] = [owner_id]
        game['link'] = f't.me/{self.bot_username}?start=game_{game["key"]}'
        game['winner'] = 0
        game['date'] = datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')
        self.setKey(str(game['key']), game)
        return game["key"], game['link']

    def start_game(self, room_id):
        num = 0
        try:
            game = self.getKey(str(room_id))
            try:
                if game['guest'] != {}:
                    players = ['owner', 'guest']
                    for p in players:
                        player = game[p]
                        for i in game['player_ids']:
                            self.bot.send_message(i, f'👤 <b>{player["name"]}</b> бросил кубик!')
                        time.sleep(2)
                        if p == 'owner':
                            resp = self.bot.send_dice(player["id"])
                        #for i in game['player_ids']:
                            self.bot.forward_message(chat_id=game["guest"]["id"], from_chat_id=player["id"], message_id=resp.message_id)
                        elif p == 'guest':
                            resp = self.bot.send_dice(player["id"])
                            self.bot.forward_message(chat_id=game["owner"]["id"], from_chat_id=player["id"], message_id=resp.message_id)
                        player['circles'] = resp.dice.value
                        time.sleep(4+1/2)
                        for i in game['player_ids']:
                            self.bot.send_message(i, f'🎲 <b>{player["name"]}</b> выпало число <code>{player["circles"]}</code>!')
                        time.sleep(2)
                    #random_value = player['circles']
                    if game['owner']['circles'] > game['guest']['circles']:
                    #print(f"{self.players[0]['name']} победил! В его копилку добавлено {self.bet} рублей!")
                        game['winner'] = game['owner']['id']
                        #print(game['winner'])
                        self.setKey(str(room_id), game)
                        return game['owner']['id'], game['bet'], game['guest']['id']
                    elif game['guest']['circles'] > game['owner']['circles']:
                    #print(f"{self.players[1]['name']} победил! В его копилку добавлено {self.bet} рублей!")
                        game['winner'] = game['guest']['id']
                        #print(game['winner'])
                        self.setKey(str(room_id), game)
                        return game['guest']['id'], game['bet'], game['owner']['id']
                    else:
                        for i in game['player_ids']:
                            self.bot.send_message(i, '〽️ <b>Ничья!</b> \n\n♻️ Повторная игра!')
                        time.sleep(3)
                    #print('Ничья! Попробуем еще разок!')
                        return self.start_game(str(room_id))
                    
                else:
                    return 'Err'
            except:
                raise
        except:
            raise
    def get_old_game(self, room_id):
        try:
            with open('old_rooms.json', 'r') as f:
                data = json.loads(f.read())
            return data[str(room_id)]
        except:
            return 'Err'
            
class Keyboards:
    def __init__(self):
        self.gamepages = {} 
        
    def rm(self):
        keyboard = types.ReplyKeyboardRemove()
        return keyboard
    def accept_applying(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text='✅ Принять', callback_data='начать'))
        return keyboard
    def menu_main(self):
        keyboard = types.ReplyKeyboardMarkup(True, True)
        keyboard.row('🎲 Игра', '👤 Профиль')
        keyboard.row('📄 Информация')
        return keyboard
    
    #def menu_games(self):
        #keyboard = types.InlineKeyboardMarkup(row_width=2)
        #keyboard.add(types.InlineKeyboardButton(text='Создать новую', callback_data='создать_игру'), types.InlineKeyboardButton(text='Случайная комната', callback_data='случайная_игра'), types.InlineKeyboardButton(text='Мои игры', callback_data='мои_игры'), types.InlineKeyboardButton(text='Рейтинг', callback_data='рейтинг'))
        #return keyboard
    def my_games(self):
        pass
    def profile(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(types.InlineKeyboardButton(text='💰 Пополнить баланс', callback_data='пополнить_баланс'), types.InlineKeyboardButton(text='🗣 Пригласи друга', callback_data='партнерка'), types.InlineKeyboardButton(text='☑️ Заказать вывод', callback_data='вывод'))
        return keyboard
    def info(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(types.InlineKeyboardButton(text='ℹИнструкция', url=instruction), types.InlineKeyboardButton(text='⚙️ Поддержка', url=support), types.InlineKeyboardButton(text='📊 Результаты игр', url=game_results[1]))
        return keyboard
    def payment(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)  
        keyboard.add(types.InlineKeyboardButton(text='☑ Готово', callback_data='проверка_оплаты'), types.InlineKeyboardButton(text='🚫 Отмена', callback_data='отмена_оплаты'))
        return keyboard
    def console_menu(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(types.InlineKeyboardButton(text='▪️ Бан', callback_data='бан'), types.InlineKeyboardButton(text='▪️ Разбан', callback_data='разбан'), types.InlineKeyboardButton(text='▪️ Мин.депозит', callback_data='мин.депозит'), types.InlineKeyboardButton(text='▪️ Мин.вывод', callback_data='мин.вывод'), types.InlineKeyboardButton(text='▪️ Доход %', callback_data='%_дохода'))
        keyboard.add(types.InlineKeyboardButton(text='▪️ Реф.бонус', callback_data='реф.бонус'), types.InlineKeyboardButton(text='▪️ Реф. %', callback_data='реферальные_%'))
        keyboard.add(types.InlineKeyboardButton(text='▪️ Изменить баланс пользователя', callback_data='баланс_изменить'))
        return keyboard
    def join_game_by_ref(self, game):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(telebot.types.InlineKeyboardButton(callback_data='присоединиться_реферал', text=f'🎲 Присоединиться к игре - {game["bet"]} RUB'))
        keyboard.add(telebot.types.InlineKeyboardButton(callback_data='главная', text='🚫 Отмена'))
        return keyboard
    def ask_for_pay(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text='💰 Пополнить', callback_data='пополнить_баланс'), types.InlineKeyboardButton(text='↪️ Назад', callback_data='главная'))
        return keyboard
    def back_to_prof(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text='↪️Назад', callback_data='назад_профиль'))
        return keyboard
    def back_to_games(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text='↪️Назад', callback_data='назад_игры'))
        return keyboard
    def menu_games(self, mingame=0, maxgame=0):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        if mingame == 0 and maxgame == 0:
            keyboard.add(types.InlineKeyboardButton(text='➕ Создать комнату', callback_data='создать_игру'), types.InlineKeyboardButton(text='♻️ Обновить', callback_data='обновить_игры'))
            keyboard.add(types.InlineKeyboardButton(text='🎲 Случайная комната', callback_data='случайная_игра'))
            keyboard.add(types.InlineKeyboardButton(text='📝 Мои игры', callback_data='мои_игры'), types.InlineKeyboardButton(text='🏆 Рейтинг', callback_data='рейтинг'))
        elif mingame == maxgame or mingame == 0:
            keyboard.add(types.InlineKeyboardButton(text='➕ Создать комнату', callback_data='создать_игру'), types.InlineKeyboardButton(text='♻️ Обновить', callback_data='обновить_игры'))
            keyboard.add(types.InlineKeyboardButton(text=f'🎲 Присоединиться к игре | {maxgame} RUB', callback_data='случайная_max'))
            keyboard.add(types.InlineKeyboardButton(text='📝 Мои игры', callback_data='мои_игры'), types.InlineKeyboardButton(text='🏆 Рейтинг', callback_data='рейтинг'))
        #elif maxgame == 0:
            #keyboard.add(types.InlineKeyboardButton(text='Создать новую', callback_data='создать_игру'))
            #keyboard.add(types.InlineKeyboardButton(text=f'Присоединиться к игре | {mingame} RUB', callback_data='случайная_min'))
            #keyboard.add(types.InlineKeyboardButton(text='Мои игры', callback_data='мои_игры'), types.InlineKeyboardButton(text='Рейтинг', callback_data='рейтинг'))
        elif mingame > 0 and maxgame > 0:
            keyboard.add(types.InlineKeyboardButton(text='➕ Создать комнату', callback_data='создать_игру'), types.InlineKeyboardButton(text='♻️ Обновить', callback_data='обновить_игры'))
            keyboard.add(types.InlineKeyboardButton(text=f'🎲 Присоединиться к игре | {mingame} RUB', callback_data='случайная_min'))
            keyboard.add(types.InlineKeyboardButton(text=f'🎲 Присоединиться к игре | {maxgame} RUB', callback_data='случайная_max'))
            keyboard.add(types.InlineKeyboardButton(text='📝 Мои игры', callback_data='мои_игры'), types.InlineKeyboardButton(text='🏆 Рейтинг', callback_data='рейтинг'))
        return keyboard
    def back_ref(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text='↪️Назад', callback_data='назад_профиль'))
        return keyboard
    def my_games(self, user_id, lst):
        num = 1
        leng = 10
        try:
            self.gamepages[str(user_id)]
        except:
            self.gamepages[str(user_id)] = 1
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        for i in range(len(lst.keys())):
            try:
                if len(lst.keys()) >= 10:
                    if i % leng == 0 and num == self.gamepages[str(user_id)]:
                        for game in list(lst.keys())[i:i+leng]:
                            if lst[game]['winner'] == int(user_id):
                                keyboard.add(telebot.types.InlineKeyboardButton(callback_data=game, text=f'✅{lst[game]["bet"]}'))
                            else:
                                keyboard.add(telebot.types.InlineKeyboardButton(callback_data=game, text=f'❌{lst[game]["bet"]}'))
                        if not(self.gamepages[str(user_id)] >= len(list(lst.keys()))//leng+1):
                            keyboard.add(telebot.types.InlineKeyboardButton(callback_data='игры_следущая', text=f'Страница {self.gamepages[str(user_id)]+1} ➡️'))
                        if not(self.gamepages[str(user_id)] == 1):
                            keyboard.add(telebot.types.InlineKeyboardButton(callback_data='игры_прошлая', text=f'⬅️ Страница {self.gamepages[str(user_id)]-1}'))
                        break
                    elif i % leng == 0:
                        num += 1
                else:
                    for game in list(lst.keys()):
                        if lst[game]['winner'] == int(user_id):
                            keyboard.add(telebot.types.InlineKeyboardButton(callback_data=game, text=f'✅{lst[game]["prize"]}'))
                        else:
                            keyboard.add(telebot.types.InlineKeyboardButton(callback_data=game, text=f'❌{lst[game]["bet"]}'))
                    break
            except:
                pass
        keyboard.add(telebot.types.InlineKeyboardButton(callback_data='назад_игры', text='↪️ Назад'))
        return keyboard
        
class User:
    def __init__(self):
        try:
            with open('users.json', 'r') as f:
                self.data = json.loads(f.read())
                for i in self.data.keys():
                    self.set_user_in_room(i, False)
        except:
            self.data = {}

    def getKey(self, key):
        try:
            with open('users.json', 'r') as f:
                self.data = json.loads(f.read())
            return self.data[str(key)]
        except:
            return 'Err'
    def setKey(self, key, value):
        try:
            try:
                with open('users.json', 'r') as f:
                    self.data = json.loads(f.read())
            except:
                self.data = {}
            self.data[str(key)] = value
            with open('users.json', 'w') as f:
                f.write(json.dumps(self.data))
        except:
            raise
    def setQiwi(self, user_id, qiwi):
        try:
            data = self.getKey(str(user_id))
            data['QIWI'] = qiwi
            self.setKey(str(user_id), data)
        except:
            raise
    def getQiwi(self, user_id):
        try:
            data = self.getKey(user_id)
            return data['QIWI']
        except:
            raise
    def set_user_in_room(self, user_id, state: bool):
        try:
            data = self.getKey(str(user_id))
            data['in_game'] = state
            self.setKey(str(user_id), data)
        except:
            return 'Err'
    def in_room(self, user_id):
        try:
            return self.getKey(str(user_id))['in_game']
        except:
            data = self.getKey(str(user_id))
            data['in_game'] = False
            self.setKey(str(user_id), data)
            return False
    def get_user(self, user_id):
        data = self.getKey(str(user_id))
        return data
    def get_rating(self):
        users = {}
        def func(value):
            with open('users.json', 'r') as f:
                data = json.loads(f.read())
            return data[value]['balance']
        try:
            with open('users.json', 'r') as f:
                data = json.loads(f.read())
            for i in data.keys():
                users[i] = data[i]['balance']
            lists = sorted(users, reverse=True, key=func)
            return lists
        except:
            return []

    def register_user(self, user_id, name, invited=0):
        regdate = datetime.now(timezone.utc).astimezone().strftime('%d.%m.%Y')
        self.setKey(user_id, {'balance': 5, "name": name, "id": user_id, "invited": invited, 'games': [], 'referals': [], 'games': [], 'regdate': str(regdate), 'banned': False, 'in_game': False, 'QIWI': 0})
    def is_registered(self, user_id):
        if self.getKey(user_id) != 'Err':
            return True
        else:
            return False
    def ban_user(self, user_id):
        try:
            user = self.get_user(user_id)
            user['banned'] = True
            self.setKey(str(user_id), user)
        except:
            return 'Err'
    def unban_user(self, user_id):
        try:
            user = self.get_user(user_id)
            user['banned'] = False
            self.setKey(str(user_id), user)
        except:
            return 'Err'
    def is_banned(self, user_id):
        try:
            return self.getKey(str(user_id))['banned']
        except:
            return False
    def add_to_user_balance(self, user_id: int, amount: int):
        data = self.get_user(user_id)
        data['balance'] += amount
        self.setKey(user_id, data)
    def add_game_to_user(self, user_id: int, room_id: int):
        data = self.get_user(user_id)
        data['games'].append(room_id)
        self.setKey(user_id, data)
    def add_referal_to_user(self, user_id, referal_id):
        data = self.get_user(user_id)
        data['referals'].append(referal_id)
        self.setKey(user_id, data)
    def remove_from_balance(self, user_id: int, amount: int):
        data = self.get_user(user_id)
        data['balance'] -= amount
        self.setKey(user_id, data)
    
class Payments:
    def __init__(self):
        self.qiwitoken = qiwitoken
        self.headers = {'Authorization': 'Bearer ' + self.qiwitoken,
                           'Accept': 'application/json',
                           'Content-Type': 'application/json'}
        self.session = requests.session()
        self.data = {}
    def create_payment(self, user_id, amount: int):
        time = str((datetime.now(timezone.utc) + timedelta(minutes=30)).astimezone()).replace(' ', 'T')
        comment = f'Пополнение счета {bot_username} на сумму {amount} рублей.'
        order_id = random.randint(10000000000, 99999999999)
        params = {'amount': {'value': amount, 'currency': 'RUB'}, 'comment': comment, 'expirationDateTime': time, 'customFields': {}}
        params = json.dumps(params)
        link = self.session.put(f'https://api.qiwi.com/partner/bill/v1/bills/{order_id}', headers=self.headers, data=params)
        link = json.loads(link.text)['payUrl']
        self.data[str(user_id)] = {'link': link, 'sum': amount, 'order_id': order_id}
        return link, order_id, time
    def reject_payment(self, user_id):
        try:
            order_id = self.data[str(user_id)]['order_id']
            self.session.post(f'https://api.qiwi.com/partner/bill/v1/bills/{order_id}/reject', headers=self.headers)
            return True
        except:
            pass
    def get_payment(self, user_id):
        try:
            order_id = self.data[str(user_id)]['order_id']
            data = json.loads(self.session.get(f'https://api.qiwi.com/partner/bill/v1/bills/{order_id}/', headers=self.headers).text)
            return data
        except:
            return 'Err'
    def is_paid(self, user_id):
        try:
            order_id = self.data[str(user_id)]['order_id']
            data = json.loads(self.session.get(f'https://api.qiwi.com/partner/bill/v1/bills/{order_id}/', headers=self.headers).text)
            try:
                if data['status']['value'] == "PAID":
                    return True
                else:
                    return False
            except:
                return False
        except:
            return False
    def get_data(self, user_id):
        return self.data[str(user_id)]
        
class Settings:
    def __init__(self):
        self.addbalance_user = 0
        try:
            with open('settings.json', 'r') as f:
                data = json.loads(f.read())

            try:
                self.percent = data['percent']
            except:
                self.percent = 5.2
            try:
                self.admins = data['admins']
            except:
                self.admins = []
            try:
                self.minwithdrawal = data['minwithdrawal']
            except:
                self.minwithdrawal = 200
            try:
                self.refpercents = data['referalpercents']
            except:
                self.refpercents = 5.0
            try:
                self.refsum = data['referalsum']
            except:
                self.refsum = 0.5
            try:
                self.mindeposit = data['mindeposit']
            except:
                self.mindeposit = 20
        except:
            self.percent = 5.2
            self.admins = []
            self.minwithdrawal = 200
            self.refpercents = 5.0
            self.refsum = 0.5
            self.mindeposit = 20
            with open('settings.json', 'w') as f:
                f.write(json.dumps({'percent': self.percent, 'admins': self.admins, 'minwithdrawal': self.minwithdrawal, 'referalpercents': self.refpercents, 'referalsum': self.refsum, 'mindeposit': self.mindeposit}))
        self.money_today = 0
    def setKey(self, key, value):
        try:
            with open('settings.json', 'r') as f:
                data = json.loads(f.read())
            data[key] = value
            with open('settings.json', 'w') as f:
                f.write(json.dumps(data))
        except:
            return Err
    def getKey(key):
        try:
            with open('settings.json', 'r') as f:
                data = json.loads(f.read())
            return data[key]
        except:
            return 'Err'
    def setRefPerc(self, perc: float):
        self.refpercents = perc
        self.setKey('referalpercents', perc)
    def setRefSum(self, sums):
        self.refsum = sums
        self.setKey('referalsum', sums)
    def setPerc(self, perc: float):
        self.percent = perc
        self.setKey('percent', perc)
    def setMinWithdrawal(self, wit: int):
        self.minwithdrawal = wit
        self.setKey('minwithdrawal', wit)
    def setMinDeposit(self, deposit: int):
        self.mindeposit = deposit
        self.setKey('mindeposit', deposit)
    def addAdmin(self, admin: int):
        try:
            self.admins = self.getKey('admins')
            self.admins.append(admin)
            self.setKey('admins', self.admins)
        except:
            return 'Err'
    def removeAdmin(self, admin: int):
        try:
            self.admins = self.getKey('admins')
            self.admins.remove(admin)
            self.setKey('admins', self.admins)
        except:
            return 'Err'
    def is_admin(self, user_id: int):
        if user_id in self.admins:
            return True
        else:
            return False


#coding: utf-8

import telebot
import re
import settings as config
from threading import Thread
import time
import requests

bot = telebot.TeleBot(token=config.bot_token, parse_mode='html')

k = config.Keyboards()
s = config.User()
g = config.Game(bot)
p = config.Payments()
se = config.Settings()
name = ''
minbet = config.minbet

@bot.message_handler(content_types=['text'])
def start(message):
    try:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1, reply_markup='')
    except:
        pass
    if message.chat.type == 'private' and not(s.is_banned(message.chat.id)):
        global name
        name = message.from_user.first_name
        if re.match('/console', message.text) and se.is_admin(message.chat.id):
            bot.send_message(message.chat.id, f'📝 <b>КОНСОЛЬ</b>\n\n▪️  Заработано сегодня: <code>{se.money_today} RUB</code>\n▪️ Мин.депозит: <code>{se.mindeposit} RUB</code>\n▪️ Мин.вывод: <code>{se.minwithdrawal} RUB</code>\n▪️ Реферальный %: <code>{se.refpercents}%</code>\n▪️ Реферальный бонус: <code>{se.refsum} RUB</code>\n\n<b>Выберите функцию</b>:', reply_markup=k.console_menu())
        if re.match('/start', message.text):
            try: 
                data = message.text.split()[1]
                if re.match('game_', data):
                    if not(s.is_registered(message.chat.id)):
                        s.register_user(message.chat.id, message.from_user.first_name)
                    game = int(data.replace('game_', ''))
                    g.refgames[str(message.chat.id)] = game
                    game = g.get_game(game)
                    bot.send_message(message.chat.id, 'Нажмите на кнопку, чтобы войти в комнату', reply_markup=k.join_game_by_ref(game))
                elif data.isdigit():
                    try:
                        if not(s.is_registered(message.chat.id)) and s.is_registered(int(data)):
                            s.register_user(message.chat.id, message.from_user.first_name, invited=int(data))
                            bot.send_message(message.chat.id, '💵 <b>На Ваш баланс зачислено 5 рублей, как новичку в нашей игре!</b>')
                            s.add_referal_to_user(int(data), message.chat.id)
                            s.add_to_user_balance(int(data), se.refsum)
                            bot.send_message(int(data), f'💵 <b>На Ваш баланс зачислено</b> <code>{se.refsum} RUB</code> <b>за приглашение пользователя в нашу игру!</b>')
                            bot.send_message(config.game_results[0], f'💰 На баланс пользователя <a href="tg://user?id={int(data)}">{s.get_user(int(data))["name"]}</a> было зачислено <code>{se.refsum} RUB</code> за приглашение пользователя!')
                        else:
                            pass
                    except:
                        if not(s.is_registered(message.chat.id)):
                            s.register_user(message.chat.id, message.from_user.first_name)
                            bot.send_message(message.chat.id, '💵 <b>На Ваш баланс зачислено 5 рублей, как новичку в нашей игре!</b>')
                    bot.send_message(message.chat.id, f'🤗 Добро пожаловать в @{config.bot_username}!\n\n▪️ Чтобы принять участие в игре тебе нужно создать новую игровую комнату или подключится к чужой комнате во вкладке <b>🎲 Игра</b>.\n\n⚠️ Но для начала ОБЯЗАТЕЛЬНО ознакомься с полным описанием правил в разделе <b>📄 Информация.</b>', reply_markup=k.menu_main())
            except IndexError:
                if not(s.is_registered(message.chat.id)):
                    s.register_user(message.chat.id, message.from_user.first_name)
                    bot.send_message(message.chat.id, '💵 <b>На Ваш баланс зачислено 5 рублей, как новичку в нашей игре!</b>')
                bot.send_message(message.chat.id, f'🤗 Добро пожаловать в @{config.bot_username}!\n\n▪️ Чтобы принять участие в игре тебе нужно создать новую игровую комнату или подключится к чужой комнате во вкладке <b>🎲 Игра</b>.\n\n⚠️ Но для начала ОБЯЗАТЕЛЬНО ознакомься с полным описанием правил в разделе <b>📄 Информация.</b>', reply_markup=k.menu_main())
            except:
                raise
                
        elif message.text == '👤 Профиль':
            if not(s.is_registered(message.chat.id)):
                s.register_user(message.chat.id, message.from_user.first_name)
                bot.send_message(message.chat.id, '💵 <b>На Ваш баланс зачислено 5 рублей, как новичку в нашей игре!</b>')
            user = s.get_user(message.chat.id)
            with open('images/profile.jpg', 'rb') as f:
                bot.send_photo(message.chat.id, photo=f, caption=f'👤 <b>ПРОФИЛЬ</b>: \n\n🆔 <b>Ваш ID</b>: <code>{message.chat.id}</code>\n📅 <b>Дата регистрации</b>: <code>{user["regdate"]}</code>\n\n💳 <b>Баланс</b>: <code>{user["balance"]} RUB</code>', reply_markup=k.profile())
        elif message.text == '🎲 Игра':
            if not(s.is_registered(message.chat.id)):
                s.register_user(message.chat.id, message.from_user.first_name)
                bot.send_message(message.chat.id, '💵 <b>На Ваш баланс зачислено 5 рублей, как новичку в нашей игре!</b>')
            m, b = g.get_rooms()
            bot.send_message(message.chat.id, '<b>Создайте  новую комнату для игры или заходите в комнаты других игроков!</b>', reply_markup=k.menu_games(m, b))
        elif message.text == '↪️ Назад':
            if not(s.is_registered(message.chat.id)):
                s.register_user(message.chat.id, message.from_user.first_name)
                bot.send_message(message.chat.id, '💵 <b>На Ваш баланс зачислено 5 рублей, как новичку в нашей игре!</b>')
            bot.send_message(message.chat.id, '🚫 <b>Действие отменено!</b>', reply_markup=k.menu_main())
        elif message.text == '📄 Информация':
            if not(s.is_registered(message.chat.id)):
                s.register_user(message.chat.id, message.from_user.first_name)
                bot.send_message(message.chat.id, '💵 <b>На Ваш баланс зачислено 5 рублей, как новчику в нашей игре!</b>')
            bot.send_message(message.chat.id, '⚠️Внимание! Незнание правил не освобождает от ответственности. Ознакомьтесь с ℹ️ <b>Инструкцией.</b>\n\nДля связи с админом перейдите в раздел ⚙️ <b>Поддержки.</b>', reply_markup=k.info())
    elif s.is_banned(message.chat.id):
        bot.send_message(message.chat.id, '🚫 <b>Доступ к боту приостановлен! Вы были внесены в черный список!</b>', reply_markup=k.rm())

def deposit(message):
    try:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1, reply_markup='')
    except:
        pass
    if not(s.is_banned(message.chat.id)):
        amount = message.text
        try:
            #try:
              #  amount = int(amount)
             #   amount = float(amount)
            #except:
            if True:
                amount = int(amount)
            if amount >= se.mindeposit:
                link, order_id, time = p.create_payment(message.chat.id, amount)
                bot.send_message(message.chat.id, f'💳 <b>ПОПОЛНЕНИЕ БАЛАНСА</b>\n\n🆔ID: <code>{order_id}</code>\n\n💳Сумма: <code>{amount} RUB</code>\n\n📝Оплата: {link}\n\n<b>Нажмите на кнопку "Готово" только после оплаты товара, иначе платеж не будет зачислен!</b>', reply_markup=k.payment())
            else:
                bot.send_message(message.chat.id, f'🚫 <b>Минимальная сумма пополнения баланса - </b><code>{se.mindeposit} RUB</code>!', reply_markup=k.menu_main())
        except:
            bot.send_message(message.chat.id, f'🚫 <b>Значение должно быть целым числом, не менее {se.mindeposit}!</b>', reply_markup=k.menu_main())
    else:
        bot.send_message(message.chat.id, '🚫 <b>Доступ к боту приостановлен! Выбыли внесены в черный список!</b>', reply_markup=k.rm())
def perc(message):
    try:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1, reply_markup='')
    except:
        pass
    perc = message.text.replace(' ', '').replace('%', '')
    try:
        perc = float(perc)
        se.setPerc(perc)
        bot.send_message(message.chat.id, '✅ <b>Значение успешно изменено!</b>', reply_markup=k.console_menu())
    except:
        bot.send_message(message.chat.id, '🚫 <b>Ошибка</b>: значение должно быть десятичной дробью')
def mindeposit(message):
    try:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1, reply_markup='')
    except:
        pass
    am = message.text.replace(' ', '')
    try:
        am = int(am)
        se.setMinDeposit(am)
        bot.send_message(message.chat.id, '✅ <b>Значение успешно изменено!</b>', reply_markup=k.console_menu())
    except:
        bot.send_message(message.chat.id, '🚫 <b>Ошибка</b>: значение должно быть целым числом!')
def minwithdrawal(message):
    try:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1, reply_markup='')
    except:
        pass
    am = message.text.replace(' ', '')
    try:
        am = int(am)
        se.setMinWithdrawal(am)
        bot.send_message(message.chat.id, '✅ <b>Значение успешно изменено!</b>', reply_markup=k.console_menu())
    except:
        bot.send_message(message.chat.id, '🚫 <b>Ошибка</b>: значение должно быть целым числом!')
def balance_update_id(message):
    user = message.text
    try:
        if s.is_registered(int(user)):
            user = int(user)
            data = s.get_user(user)
            msg = bot.send_message(message.chat.id, f'👤 <b>Пользователь {data["name"]}</b>:\n\n🆔 ID: {data["id"]}\n💰 Баланс: <code>{data["balance"]} RUB</code>\n\n📝 <b>Введите сумму, которую хотите добавить на баланс пользователя:</b>', reply_markup=k.rm())
            se.addbalance_user = user
            bot.register_next_step_handler(msg, balance_update_sum)
        else:
            bot.send_message(message.chat.id, f'🚫 <b>Пользователь c ID {int(user)} не зарегистрирован в данном боте!</b>', reply_markup=k.console_menu())
    except:
        bot.send_message(message.chat.id, '🚫 <b>Ошибка</b>: значение должно быть целым числом!')
def balance_update_sum(message):
    am = message.text
    try:
        am = int(am)
        #print(am)
        user_id = se.addbalance_user
        data = s.get_user(user_id)
        #print(data)
        s.add_to_user_balance(user_id, am)
        msg = bot.send_message(message.chat.id, f'✅ <b>Средства успешно зачислены пользователю {data["name"]}!</b>', reply_markup=k.console_menu())
    except:
        bot.send_message(message.chat.id, '🚫 <b>Ошибка</b>: значение должно быть целым числом!', reply_markup=k.console_menu())
def referalsum(message):
    try:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1, reply_markup='')
    except:
        pass
    am = message.text.replace(' ', '')
    try:
        am = float(am)
        se.setRefSum(am)
        bot.send_message(message.chat.id, '✅ <b>Значение успешно изменено!</b>', reply_markup=k.console_menu())
    except:
        bot.send_message(message.chat.id, '🚫 <b>Ошибка</b>: значение должно быть целым числом!')
def referalperc(message):
    try:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1, reply_markup='')
    except:
        pass
    perc = message.text.replace(' ', '').replace('%', '')
    try:
        perc = float(perc)
        se.setRefPerc(perc)
        bot.send_message(message.chat.id, '✅ <b>Значение успешно изменено!</b>', reply_markup=k.console_menu())
    except:
        bot.send_message(message.chat.id, '🚫 <b>Ошибка</b>: значение должно быть десятичной дробью!')
def ban(message):
    try:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1, reply_markup='')
    except:
        pass
    user = message.text
    try:
        user = int(user)
        if s.is_registered(user):
            s.ban_user(user)
            bot.send_message(message.chat.id, '✅ <b>Пользователь был успешно заблокирован!</b>', reply_markup=k.console_menu())
        else:
            bot.send_message(message.chat.id, '🚫 <b>Данный пользователь не зарегистрирован в боте!</b>', reply_markup=k.console_menu())
    except:
        bot.send_message(message.chat.id, '🚫 <b>Ошибка</b>: значение должно быть числом!')
def unban(message):
    try:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1, reply_markup='')
    except:
        pass
    user = message.text
    try:
        user = int(user)
        if s.is_registered(user):
            s.unban_user(user)
            bot.send_message(message.chat.id, '✅ <b>Пользователь был успешно разблокирован!</b>', reply_markup=k.console_menu())
        else:
            bot.send_message(message.chat.id, '🚫 <b>Данный пользователь не зарегистрирован в боте!</b>', reply_markup=k.console_menu())
    except:
        bot.send_message(message.chat.id, '🚫 <b>Ошибка</b>: значение должно быть числом!')

def create_game(message):
    try:
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1, reply_markup='')
    except:
        pass
    def players(room_id, message, link):
        bot.send_message(message.chat.id, f'<b>🎲 Ваша комната</b>: \n\n\n📄 <i>Ссылка для друга</i>: {link}\n\nℹ️ Игра запустится автоматически после подключения оппонента к игре.', reply_markup=k.rm())
        while True:
            if g.get_game(str(room_id))['guest'] != {}:
                name = g.get_game(str(room_id))['guest']['name']
                id_owner = g.get_game(str(room_id))["owner"]["id"]
                id_guest = g.get_game(str(room_id))["guest"]["id"]
                players = f'👤 <a href="tg://user?id={id_owner}">{g.get_game(room_id)["owner"]["name"]}</a>\n👤 <a href="tg://user?id={id_guest}">{g.get_game(room_id)["guest"]["name"]}</a>'
                bot.send_message(message.chat.id, f'🎲 <b>Игра #{g.get_game(str(room_id))["key"]}</b>\n\n🥋 <b>Игроки</b>:\n{players}\n\n💰 <b>Ставка</b>: <code>{g.get_game(str(room_id))["bet"]} RUB</code>')
                winner, am, loser = g.start_game(str(room_id))
                bet = (am*2)/100*(100-se.percent)
                bot.send_message(winner, f'✅ <b>Вы победили!</b>\n\n<b>На ваш баланс зачислено {bet} RUB!</b>', reply_markup=k.menu_main())
                bot.send_message(loser, f'🔴 <b>К сожалению, вы проиграли!</b>\n\n<b>Победитель</b>:\n👤 <a href="tg://user?id={s.get_user(winner)["id"]}">{s.get_user(winner)["name"]}</a>', reply_markup=k.menu_main())
                s.add_to_user_balance(winner, bet-am)
                s.add_game_to_user(winner, g.get_game(room_id)['key'])
                s.add_game_to_user(loser, g.get_game(room_id)['key'])
                s.remove_from_balance(loser, am)
                s.set_user_in_room(winner, False)
                s.set_user_in_room(loser, False)
                try:
                    bot.send_message(config.game_results[0], f'🎲 <b>Игра #{g.get_game(str(room_id))["key"]}</b>\n\n🥋 <b>Игроки</b>:\n{players}\n\n💰 <b>Ставка</b>: <code>{g.get_game(str(room_id))["bet"]} RUB</code>\n\n🏆 <b>Победитель</b>:\n👤 <a href="tg://user?id={s.get_user(winner)["id"]}">{s.get_user(winner)["name"]}</a>')
                except:
                    pass
                g.end_game(str(room_id), bet)
                break
            #except KeyError:
                #print('ex')
                #time.sleep(1)
            else:
                time.sleep(1)
    if not(s.is_banned(message.chat.id)):
        bet = message.text
        try:
            bet = int(bet)
            if bet <= s.get_user(message.chat.id)["balance"] and not(s.in_room(message.chat.id)) and bet >= minbet:
                room_id, link = g.create_game(bet, message.chat.id, message.from_user.first_name)
                s.set_user_in_room(message.chat.id, True)
                thread = Thread(target=players, args=(room_id, message, link, ))
                thread.start()
            elif s.in_room(message.chat.id):
                bot.send_message(message.chat.id, '🚫 <b>Вы уже присоединились к игре!</b>')
            elif bet < minbet:
                bot.send_message(message.chat.id, f'🚫 <b>Минимальная сумма ставки - {minbet} рублей!</b>', reply_markup=k.menu_main())
            else:
                bot.send_message(message.chat.id, '🚫 <b>На Вашем балансе недостаточно средств!</b>', reply_markup=k.ask_for_pay())
        except:
            bot.send_message(message.chat.id, f'🚫 <b>Значение должно быть целым числом, не менее {minbet} и не привышающим Ваш баланс.</b>', reply_markup=k.menu_main())
    else:
        bot.send_message(message.chat.id, '🚫 <b>Доступ к боту приостановлен! Выбыли внесены в черный список!</b>', reply_markup=k.rm())
def user_qiwi(message):
    qiwi = message.text.replace('+', '').replace(" ", '')
    if (re.match('79', qiwi) or re.match('38', qiwi) or re.match('375', qiwi)) and qiwi.isdigit():
        s.setQiwi(message.chat.id, int(qiwi))
        try:
            msg = bot.send_message(chat_id=message.chat.id, text='✅ <b>Ваш QIWI номер успешно обновлен!</b>\n\n📝 <b>Введите сумму, которую хотите вывести:</b>', reply_markup=k.rm())#, message_id=message.message_id-1)
            bot.register_next_step_handler(msg, withdrawal)
        except:
            bot.send_message(message.chat.id, '🚫 <b> Данный формат номера не поддерживается! \n\n☑️ Поддерживаются номера:\n▪️ России\n▪️ Украины\n▪️ Белоруссии', reply_markup=k.back_to_prof())

    else:
        bot.send_message(message.chat.id, '🚫 <b> Данный формат номера не поддерживается! \n\n☑️ Поддерживаются номера:\n▪️ России\n▪️ Украины\n▪️ Белоруссии', reply_markup=k.back_to_prof())
def withdrawal(message):
    am = message.text
    try:
        am = int(am)
        if am <= s.get_user(message.chat.id)['balance'] and am >= se.minwithdrawal:
            s.remove_from_balance(message.chat.id, am)
            bot.send_message(message.chat.id, '☑️ <b>Заявка на вывод средств с Вашего баланса отправлена администратору. Он в скором времени свяжется с Вами.</b>', reply_markup=k.menu_main())
            user = s.get_user(message.chat.id)
            for i in se.admins:
                bot.send_message(int(i), f'👤 <b>Заявка на вывод от</b> {user["name"]} | <b>ID</b>: <code>{user["id"]}</code>\n\n💰 <b>Сумма:</b> <code>{am} RUB</code>\n\n💳 <b>QIWI</b>: <code>{s.getQiwi(user["id"])}</code>')
        elif am > s.get_user(message.chat.id)['balance']:
            bot.send_message(message.chat.id, '🚫 <b>На Вашем балансе недостаточно средств для вывода введенной Вами суммы!</b>', reply_markup=k.ask_for_pay())
        else:
            bot.send_message(message.chat.id, f'🚫 <b>Минимальная сумма вывода -</b> <code>{se.minwithdrawal} RUB</code>!', reply_markup=k.menu_main())
    except:
        bot.send_message(message.chat.id, '🚫 <b>Значение должно быть целым числом, не превышающим Ваш баланс!</b>', reply_markup=k.menu_main())
def random_game(message):
    def rangame(message, bet):
        try:
            bet = int(bet)
            errors = ['Err', 'NF', 'FULL']
            bot.send_message(message.chat.id, '🕓 <b>Поиск подходящей комнаты...</b>\n\nИгра запустится сразу же после подключения к комнате.', reply_markup=k.rm())
            for i in range(120):
                game = g.join_random_game(message.chat.id, message.from_user.first_name, bet)
                if not(game in errors) and game != None:
                    if True:
                        id_owner = g.get_game(str(game))["owner"]["id"]
                        id_guest = g.get_game(str(game))["guest"]["id"]
                        players = f'👤 <a href="tg://user?id={id_owner}">{g.get_game(game)["owner"]["name"]}</a>\n👤 <a href="tg://user?id={id_guest}">{g.get_game(game)["guest"]["name"]}</a>'
                        bot.send_message(message.chat.id, f'🎲 <b>Игра #{g.get_game(game)["key"]}</b>\n\n🥋 <b>Игроки</b>:\n{players}\n\n💰 <b>Ставка</b>: <code>{g.get_game(str(game))["bet"]} RUB</code>')
                        break
                    
                else:
                    if i == 119:
                        bot.send_message(message.chat.id, '🚫 <b>К сожалению, комнаты не найдены(!</b>', reply_markup=k.menu_main())
                        break
                    else:
                        time.sleep(1)
        except:
            bot.send_message(message.chat.id, '🚫 <b>Произошла ошибка</b>: попробуйте присоединиться к игре заново, введя команду /start!')
    if not(s.is_banned(message.chat.id)):
        bet = message.text
        try:
            if int(bet) <= s.get_user(message.chat.id)['balance'] and not(s.in_room(message.chat.id)) and int(bet) >= minbet:
                Thread(target=rangame, args=(message, bet,)).start()
            elif s.in_room(message.chat.id):
                bot.send_message(message.chat.id, '🚫 <b>Вы уже присоединились к игре!</b>')
            elif int(bet) < minbet:
                bot.send_message(message.chat.id, f'🚫 <b>Минимальная сумма ставки - {minbet} RUB!</b>', reply_markup=k.menu_main())
            else:
                bot.send_message(message.chat.id, '🚫 <b>На Вашем балансе недостаточно средств!</b>', reply_markup=k.ask_for_pay())
        except:
            bot.send_message(message.chat.id, '🚫 <b>Значение должно быть числом!</b>', reply_markup=k.menu_main())
    else:
        bot.send_message(message.chat.id, '🚫 <b>Доступ к боту приостановлен! Выбыли внесены в черный список!</b>', reply_markup=k.rm())
@bot.callback_query_handler(func=lambda call: True)
def inline(call):
    #if not(call.message.chat.id in s.ban_list()):
    if not(s.is_registered(call.message.chat.id)):
        s.register_user(call.message.chat.id, name)
    if not(s.is_banned(call.message.chat.id)):
        try:
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup='')
        except:
            pass
        if call.data == 'главная':
            bot.send_message(call.message.chat.id, f'🤗 Добро пожаловать в @{config.bot_username}!\n\n▪️ Чтобы принять участие в игре тебе нужно создать новую игровую комнату или подключится к чужой комнате во вкладке <b>🎲 Игра</b>.\n\n⚠️ Но для начала ОБЯЗАТЕЛЬНО ознакомься с полным описанием правил в разделе <b>📄 Информация.</b>', reply_markup=k.menu_main())
        if call.data == 'проверка_оплаты':
            if p.is_paid(call.message.chat.id):
                amount = p.get_data(call.message.chat.id)['sum']
                s.add_to_user_balance(call.message.chat.id, amount)
                se.money_today += amount
                try:
                    inviter = s.get_user(call.message.chat.id)['invited']
                    am = amount/100*se.refpercents
                    s.add_to_user_balance(inviter, am)
                    try:
                        bot.send_message(config.game_results[0], f'💰 На баланс пользователя <a href="tg://user?id={int(inviter)}">{s.get_user(int(inviter))["name"]}</a> было зачислено <code>{am} RUB</code> за пополнение баланса реферала!')
                    except:
                        pass
                    bot.send_message(inviter, '💳 <b>На Ваш баланс зачислено</b> <code>{amount/100*se.refpercents} RUB </code> <b>за покупку приглашенного Вами пользователя!</b>')
                except:
                    pass
                bot.send_message(call.message.chat.id, f'✅ <b>Заказ оплачен! На Ваш счет зачислено</b> <code>{amount} RUB</code>', reply_markup=k.menu_main())
            else:
                p.reject_payment(call.message.chat.id)
                bot.send_message(call.message.chat.id, '🚫 <b>Заказ не оплачен!</b>', reply_markup=k.menu_main())
        elif call.data == 'отмена_оплаты':
            p.reject_payment(call.message.chat.id)
            bot.send_message(call.message.chat.id, '🚫 <b>Заказ отменен!</b>', reply_markup=k.menu_main())
        elif call.data == 'обновить_игры':
            m, b = g.get_rooms()
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=k.menu_games(m, b))
        elif call.data == 'пополнить_баланс':
            try:
                msg = bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,caption='📝 <b>Введите сумму, на которую хотите пополнить баланс: </b>', reply_markup=k.back_to_prof())
            except:
                msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='📝 <b>Введите сумму, на которую хотите пополнить баланс: </b>',reply_markup=k.back_to_prof())

            bot.register_next_step_handler(msg, deposit)
        elif call.data == 'случайная_min':
            def rangame_min(call, bet):
                try:
                    bet = int(bet)
                    errors = ['Err', 'NF', 'FULL']
                    bot.send_message(call.message.chat.id, '🕓 <b>Поиск подходящей комнаты...</b>\n\nИгра запустится сразу же после подключения к комнате.', reply_markup=k.rm())
                    for i in range(120):
                        game = g.join_random_game(call.message.chat.id, s.get_user(call.message.chat.id)['name'], int(bet))
                        if not(game in errors) and game != None:
                            if True:
                                id_owner = g.get_game(str(game))["owner"]["id"]
                                id_guest = g.get_game(str(game))["guest"]["id"]
                                players = f'👤 <a href="tg://user?id={id_owner}">{g.get_game(game)["owner"]["name"]}</a>\n👤 <a href="tg://user?id={id_guest}">{g.get_game(game)["guest"]["name"]}</a>'
                                bot.send_message(call.message.chat.id, f'🎲 <b>Игра #{g.get_game(game)["key"]}</b>\n\n🥋 <b>Игроки</b>:\n{players}\n\n💰 <b>Ставка</b>: <code>{g.get_game(str(game))["bet"]} RUB</code>')
                                break
                            
                        else:
                            if i == 119:
                                bot.send_message(call.message.chat.id, '🚫 <b>К сожалению, комнаты не найдены(!</b>', reply_markup=k.menu_main())
                                break
                            else:
                                time.sleep(1)
                except:
                    bot.send_message(call.message.chat.id, '🚫 <b>Произошла ошибка</b>: попробуйте присоединиться к игре заново, введя команду /start!')

            if not(s.is_banned(call.message.chat.id)):
                bet = g.mingame
                try:
                    if int(bet) <= s.get_user(call.message.chat.id)['balance'] and not(s.in_room(call.message.chat.id)) and int(bet) >= minbet:
                        Thread(target=rangame_min, args=(call, bet,)).start()
                    elif s.in_room(call.message.chat.id):
                        bot.send_message(call.message.chat.id, '🚫 <b>Вы уже присоединились к игре!</b>')
                    elif int(bet) < minbet:
                        bot.send_message(call.message.chat.id, f'🚫 <b>Минимальная сумма ставки - {minbet} RUB!</b>', reply_markup=k.menu_main())
                    else:
                         bot.send_message(call.message.chat.id, '🚫 <b>На Вашем балансе недостаточно средств!</b>', reply_markup=k.ask_for_pay())
                except:
                    bot.send_message(call.message.chat.id, '🚫 <b>Значение должно быть числом!</b>', reply_markup=k.menu_main())
            else:
                bot.send_message(call.message.chat.id, '🚫 <b>Доступ к боту приостановлен! Выбыли внесены в черный список!</b>', reply_markup=k.rm())
        elif call.data == 'случайная_max':
            def rangame_max(call, bet):
                try:
                    bet = int(bet)
                    errors = ['Err', 'NF', 'FULL']
                    bot.send_message(call.message.chat.id, '🕓 <b>Поиск подходящей комнаты...</b>\n\nИгра запустится сразу же после подключения к комнате.', reply_markup=k.rm())
                    for i in range(120):
                        game = g.join_random_game(call.message.chat.id, s.get_user(call.message.chat.id)['name'], int(bet))
                        if not(game in errors) and game != None:
                            if True:
                                id_owner = g.get_game(str(game))["owner"]["id"]
                                id_guest = g.get_game(str(game))["guest"]["id"]
                                players = f'👤 <a href="tg://user?id={id_owner}">{g.get_game(game)["owner"]["name"]}</a>\n👤 <a href="tg://user?id={id_guest}">{g.get_game(game)["guest"]["name"]}</a>'
                                bot.send_message(call.message.chat.id, f'🎲 <b>Игра #{g.get_game(game)["key"]}!</b>\n\n🥋 <b>Игроки</b>:\n{players}\n\n💰 <b>Ставка</b>: <code>{g.get_game(str(game))["bet"]} RUB</code>')
                                break
                            
                        else:
                            if i == 119:
                                bot.send_message(call.message.chat.id, '🚫 <b>К сожалению, комнаты не найдены(!</b>', reply_markup=k.menu_main())
                                break
                            else:
                                time.sleep(1)
                except:
                    bot.send_message(call.message.chat.id, '🚫 <b>Произошла ошибка</b>: попробуйте присоединиться к игре заново, введя команду /start!')
            if not(s.is_banned(call.message.chat.id)):
                bet = g.maxgame
                try:
                    if int(bet) <= s.get_user(call.message.chat.id)['balance'] and not(s.in_room(call.message.chat.id)) and int(bet) >= minbet:
                        Thread(target=rangame_max, args=(call, bet,)).start()
                    elif s.in_room(call.message.chat.id):
                        bot.send_message(call.message.chat.id, '🚫 <b>Вы уже присоединились к игре!</b>')
                    elif int(bet) < minbet:
                        bot.send_message(call.message.chat.id, f'🚫 <b>Минимальная сумма ставки - {minbet} RUB!</b>', reply_markup=k.menu_main())
                    else:
                        bot.send_message(call.message.chat.id, '🚫 <b>На Вашем балансе недостаточно средств!</b>', reply_markup=k.ask_for_pay())
                except:
                    bot.send_message(call.message.chat.id, '🚫 <b>Значение должно быть числом!</b>', reply_markup=k.menu_main())
            else:
                bot.send_message(call.message.chat.id, '🚫 <b>Доступ к боту приостановлен! Выбыли внесены в черный список!</b>', reply_markup=k.rm())
        elif call.data == 'создать_игру':
            if not(s.in_room(call.message.chat.id)):
                msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'🎲 <b>Создать комнату</b>\n\n<i>Минимальная ставка: {minbet} RUB</i>\n\n<b>Введите ставку для игры (целое число):</b>', reply_markup=k.back_to_games())
                bot.register_next_step_handler(msg, create_game)
            else:
                bot.send_message(call.message.chat.id, '🚫 <b>Вы уже присоединились к игре!</b>')
        elif call.data == 'случайная_игра':
            if not(s.in_room(call.message.chat.id)):
                msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='📝 <b>Введите Вашу максимальную ставку:</b>', reply_markup=k.back_to_games())
                bot.register_next_step_handler(msg, random_game)
            else:
                bot.send_message(call.message.chat.id, '🚫 <b>Вы уже присоединились к игре!</b>')
        elif call.data == 'консоль' and se.is_admin(call.message.chat.id):
            bot.send_message(call.message.chat.id, f'<b>КОНСОЛЬ</b>\n\n▪️ Заработано сегодня: <code>{se.money_today} RUB</code>\n▪️ Мин.депозит: <code>{se.mindeposit} RUB</code>\n▪️ Мин.вывод: <code>{se.minwithdrawal} RUB</code>\n▪️ Реферальный %: <code>{s.refpercents}%</code>\n▪️ Реферальный бонус: <code>{se.refsum} RUB</code>\n\n<b>Выберите функцию</b>:', reply_markup=k.console_menu())
        elif call.data == 'баланс_изменить' and se.is_admin(call.message.chat.id):
            msg = bot.send_message(call.message.chat.id, '📝 <b>Введите ID пользователя, баланс которого хотите изменить:</b>', reply_markup=k.rm())
            bot.register_next_step_handler(msg, balance_update_id)
        elif call.data == 'мин.депозит' and se.is_admin(call.message.chat.id):
            msg = bot.send_message(call.message.chat.id, '📝 <b>Введите новое значение:</b>')
            bot.register_next_step_handler(msg, mindeposit)
        elif call.data == 'мин.вывод' and se.is_admin(call.message.chat.id):
            msg = bot.send_message(call.message.chat.id, '📝 <b>Введите новое значение:</b>')
            bot.register_next_step_handler(msg, minwithdrawal)
        elif call.data == 'реф.бонус' and se.is_admin(call.message.chat.id):
            msg = bot.send_message(call.message.chat.id, '📝 <b>Введите новое значение:</b>')
            bot.register_next_step_handler(msg, referalsum)
        elif call.data == 'реферальные_%' and se.is_admin(call.message.chat.id):
            msg = bot.send_message(call.message.chat.id, '📝 <b>Введите новое значение:</b>')
            bot.register_next_step_handler(msg, referalperc)
        elif call.data == '%_дохода' and se.is_admin(call.message.chat.id):
            msg = bot.send_message(call.message.chat.id, '📝 <b>Введите новое значение:</b>')
            bot.register_next_step_handler(msg, perc)
        elif call.data == 'вывод':
            try:
                q = s.getQiwi(call.message.chat.id)
                if q != 0:
                    boole = True
                else:
                    boole = False
            except:
                boole = False
            if boole:
                msg = bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,caption='📝 <b>Введите сумму, которую хотите вывести:</b>', reply_markup=k.back_to_prof())
                bot.register_next_step_handler(msg, withdrawal)
            else:
                msg = bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,caption='📝 <b>Введите номер вашего QIWI Кошелька, его следует ввести только 1 раз за все время:</b>', reply_markup=k.back_to_prof())
                bot.register_next_step_handler(msg, user_qiwi)
        elif call.data == 'бан' and se.is_admin(call.message.chat.id):
            msg = bot.send_message(call.message.chat.id, '📝 <b>Введите ID пользователя, которого хотите заблокировать:</b>', reply_markup=k.rm())
            bot.register_next_step_handler(msg, ban)
        elif call.data == 'разбан' and se.is_admin(call.message.chat.id):
            msg = bot.send_message(call.message.chat.id, '📝 <b>Введите ID пользователя, которого хотите разблокировать:</b>', reply_markup=k.rm())
            bot.register_next_step_handler(msg, unban)
        elif call.data == 'игры_следущая':
            k.gamepages[str(call.message.chat.id)] = k.gamepages[str(call.message.chat.id)] + 1
            lst = g.get_all_game_data(call.message.chat.id)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=k.my_games(call.message.chat.id, lst))
        elif call.data == 'назад_игры':
            try:
                bot.clear_step_handler_by_chat_id(call.message.chat.id)
            except:
                pass
            m, b = g.get_rooms()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Создай новую комнату для игры или заходи в комнаты других игроков!', reply_markup=k.menu_games(m, b))
        elif call.data == 'игры_прошлая':
            k.gamepages[str(call.message.chat.id)] = k.gamepages[str(call.message.chat.id)] - 1
            lst = g.get_all_game_data(call.message.chat.id)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=k.my_games(call.message.chat.id, lst))

        elif call.data in list(map(str, s.get_user(call.message.chat.id)['games'])):
            game = g.get_old_game(call.data)
            if game['winner'] == call.message.chat.id:
                state = '✅ Победа'
            else:
                state = '🔴 Поражение'
            id_owner = game["owner"]['id']
            id_guest = game["guest"]['id']
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'🎲 <b>Игра #{game["key"]}</b> от {game["date"]}\n\n💰 <b>Ставка</b>: <code>{game["bet"]} RUB</code>\n\n🥋 <b>Игроки</b>:\n👤 <a href="tg://user?id={id_owner}">{game["owner"]["name"]}</a>\n👤 <a href="tg://user?id={id_guest}">{game["guest"]["name"]}</a>\n\n<b>Исход</b>:\n{state}', reply_markup=k.back_to_games())
        elif call.data == 'рейтинг':
            msg = '🏆 <b>Рейтинг пользователей</b>\n\n'
            if len(s.get_rating()) != 0:
                for i in s.get_rating()[-10:]:
                    user = s.get_user(i)
                    msg += f'👤 <a href="tg://user?id={user["id"]}">{user["name"]}</a> - <code>{int(user["balance"])} RUB</code>\n'
            else:
                msg += '🚫 Пользователи пока что не зарегистрированы.'
            bot.edit_message_text(chat_id=call.message.chat.id, text=msg, reply_markup=k.back_to_games(), message_id=call.message.message_id)
        elif call.data == 'мои_игры':
            try:
                k.gamepages[str(call.message.chat.id)] = 1
            except:
                pass
            msg = '🎲 <b>Ваши игры:</b>'
            try:
                lst = g.get_all_game_data(call.message.chat.id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text=msg, reply_markup=k.my_games(call.message.chat.id, lst))
            except:
                bot.send_message(message.chat.id, '🚫 <b>Произошла ошибка</b>: попробуйте просмотреть список своих игр позже!')

        elif call.data == 'присоединиться_реферал':
            try:
                game = g.refgames[str(call.message.chat.id)]
                if g.get_game(game) != None and not (call.message.chat.id in g.get_game(game)['player_ids']):
                    user = s.get_user(call.message.chat.id)
                    if user['balance'] >= g.get_game(game)['bet']:
                        if g.join_game(game, call.message.chat.id, user["name"]) != 'FULL':
                            id_owner = g.get_game(game)["owner"]["id"]
                            id_guest = g.get_game(game)["guest"]["id"]
                            players = f'👤 <a href="tg://user?id={id_owner}">{g.get_game(game)["owner"]["name"]}</a>\n👤 <a href="tg://user?id={id_guest}">{g.get_game(game)["guest"]["name"]}</a>'
                            bot.send_message(call.message.chat.id, f'🎲 <b>Игра #{g.get_game(game)["key"]}</b>\n\n🥋 <b>Игроки</b>:\n{players}\n\n💰 Ставка: <code>{g.get_game(str(game))["bet"]} RUB</code>')

                        else:
                            bot.send_message(call.message.chat.id, '<b>Ошибка подключения: комната заполнена или не существует!</b>')
                    else:
                        bot.send_message(call.message.chat.id, '🚫 <b>На Вашем балансе недостаточно средств!</b>', reply_markup=k.ask_for_pay())
                elif call.message.chat.id in g.get_game(game)['player_ids']:
                    pass
            except:
                bot.send_message(call.message.chat.id, f'🚫 <b>Ошибка: комната не найдена!</b>', reply_markup=k.menu_main())
        elif call.data == 'назад_профиль':
            try:
                bot.clear_step_handler_by_chat_id(call.message.chat.id)
            except:
                pass
            user = s.get_user(call.message.chat.id)
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=f'<b>ПРОФИЛЬ</b>: \n\n🆔 <b>Ваш ID</b>: <code>{call.message.chat.id}</code>\n📅 <b>Дата регистрации</b>: <code>{user["regdate"]}</code>\n\n💳 <b>Баланс</b>: <code>{user["balance"]} RUB</code>', reply_markup=k.profile())
        elif call.data == 'партнерка':
            link = f't.me/{config.bot_username}?start={call.message.chat.id}'
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=f'<b>ПАРТНЕРСКАЯ ПРОГРАММА</b>\n\nПоделись своей реферальной ссылкой с  друзьями и получай:\n\n▪️ <b>{se.refsum} RUB</b> за реферала\n▪️ <b>{se.refpercents}%</b> с каждой его оплаты\n\n⤵️ Ваша реферальная ссылка:\n {link}\n\n👥 Рефералов: {len(s.get_user(call.message.chat.id)["referals"])}', reply_markup=k.back_to_prof())
    else:
        bot.send_message(call.message.chat.id, '🚫 <b>Доступ к боту приостановлен! Выбыли внесены в черный список!</b>', reply_markup=k.rm())
while True:
    try:
        bot.polling(none_stop=True)
    except ConnectionError:
        print('Ошибка подключения! Перезапуск бота!')
        time.sleep(2)
    except requests.exceptions.ReadTimeout:
        print('Переподключение...')
        time.sleep(2)

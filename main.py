import telebot
from telebot import types
from telegram_bot_pagination import InlineKeyboardPaginator
import sqlite3
import config
import os
import datetime
from datetime import datetime
import pytz
import math
#Europe/Kyiv

bot = telebot.TeleBot(config.TOKEN)
admin = config.admin #id admin
start_text = config.start_text
stat = config.stat
card_num = config.card_num
pay_t = config.pay_t



conn = sqlite3.connect('napov.db', check_same_thread=False)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS products(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   photo TEXT,
   title TEXT,
   description TEXT,
   price INT
   );
""")
conn.commit()
cur.execute("""CREATE TABLE IF NOT EXISTS taste(
   id INT,
   taste TEXT,
   count INT
   );
""")
cur.execute("""CREATE TABLE IF NOT EXISTS cart(
   id INT,
   uid INT,
   taste TEXT,
   count INT,
   price INT
   );
""")
conn.commit()
cur.execute("""CREATE TABLE IF NOT EXISTS orders(
   or_id INT,
   id INT,
   uid INT,
   taste TEXT,
   count INT,
   price INT,
   delivery_type INT,
   status INT,
   delivery_info TEXT,
   or_date TEXT,
   pay_type INT,
   seller_message TEXT
   );
""")#status 0-нове 1-підтверджений 2-оплачено/наложка 3-виконується 4-Виконаний 9-скасований
    #delivery_type 0-самовивіз(оплата на місці) 1-передача через поштомат(оплата на карту) 2-доставка по НП 3-доставка продавцем(ціна за кілометр/оплата на місці)
conn.commit()


def check(uuid):
    cur.execute(""" SELECT
"main"."cart"."uid",
"main"."cart"."id",
"main"."products"."title",
"main"."cart"."taste",
"main"."cart"."count",
"main"."taste"."count"

FROM "main"."cart", "main"."taste", "main"."products"
WHERE "main"."cart"."count" <= "main"."taste"."count" AND "main"."cart"."uid" = ? AND "main"."cart"."id" = "main"."products"."id" AND "main"."cart"."id" = "main"."taste"."id" AND "main"."cart"."taste" = "main"."taste"."taste"  """,[uuid])

    car = cur.fetchall()
    cur.execute(""" SELECT
"main"."cart"."uid",
"main"."cart"."id",
"main"."products"."title",
"main"."cart"."taste",
"main"."cart"."count",
"main"."taste"."count"

FROM "main"."taste", "main"."cart", "main"."products"
WHERE "main"."cart"."uid" = ? AND "main"."cart"."id" = "main"."taste"."id" AND "main"."cart"."id" = "main"."products"."id" AND "main"."cart"."taste" = "main"."taste"."taste" """,[uuid])
    ct = cur.fetchall()
    result=list(set(car) ^ set(ct))
    return result

@bot.message_handler(commands=['start'])
def start(message):
    try:
        try:
            cid = message.chat.id
        except Exception as e:
            cid = message.message.chat.id
            pass
        uid = message.from_user.id
        user = message.from_user.username
        name = message.from_user.first_name
        print(user," ",uid," ",name)
        markup = types.InlineKeyboardMarkup(row_width=2)
        global msg
        if uid in admin:
            markup.add(
            types.InlineKeyboardButton("Вітрина🔞🚬", callback_data="vitryna"),
            types.InlineKeyboardButton("Корзина🛒",callback_data="carftt"),
            types.InlineKeyboardButton("Мої замовлення📦",callback_data="my_or"),
            types.InlineKeyboardButton("Адмін-панель👨‍💼", callback_data="adm")#,
            #types.InlineKeyboardButton("Налаштування⚙️", callback_data="settings")
            )
            start_photo = open(config.start_photo, 'rb')
            msg = bot.send_photo(cid, start_photo,caption=start_text,reply_markup=markup)
            start_photo.close()
        else:
            markup.add(
            types.InlineKeyboardButton("Вітрина🔞🚬", callback_data="vitryna"),
            types.InlineKeyboardButton("Корзина🛒",callback_data="carftt"),
            types.InlineKeyboardButton("Мої замовлення📦",callback_data="my_or")
            )
            start_photo = open(config.start_photo, 'rb')
            msg = bot.send_photo(cid, start_photo,caption=start_text,reply_markup=markup)
            start_photo.close()
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='character')
def characters_page_callback(call):
    try:
        page = int(call.data.split('#')[1])
        bot.delete_message(call.message.chat.id,call.message.message_id)
        vit(call, page)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='cab_or')
def cab_or_page_callback(call):
    try:
        page = int(call.data.split('#')[1])
        bot.delete_message(call.message.chat.id,call.message.message_id)
        or_cab(call, page)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='u_or')
def u_or_page_callback(call):
    try:
        page = int(call.data.split('#')[1])
        bot.delete_message(call.message.chat.id,call.message.message_id)
        or_list(call, page)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='cab_or')
def cab_or_page_callback(call):
    try:
        page = int(call.data.split('#')[1])
        bot.delete_message(call.message.chat.id,call.message.message_id)
        or_cab(call, page)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='n_back')
def n_back(call):
    try:
        or_id = int(call.data.split('#')[1])
        bot.delete_message(call.message.chat.id,call.message.message_id)
        n_o(call, or_id)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='n_stat')
def n_stat(call):
    try:
        or_id = int(call.data.split('#')[1])
        print("tt")
        bot.delete_message(call.message.chat.id,call.message.message_id)
        new_stat(call, or_id)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='upd_stat')
def upd_stat(call):
    try:
        wtf = call.data.split('#')[1]
        or_id = int(call.data.split('#')[2])
        print(type(or_id))
        cur.execute(""" SELECT * FROM orders WHERE or_id = ? """, [or_id])
        ord = cur.fetchone()
        stann = ord[7]
        d_t = ord[6]
        p_t = ord[10]
        st = stat[stann+1]
        if wtf == "nxt":
            if stann == 1 and d_t == 1:
                masgg = bot.send_message(call.message.chat.id, "Введіть ТТН:")
                bot.register_next_step_handler(masgg, ttn, or_id)
            elif stann == 1 and d_t == 2:
                masgg = bot.send_message(call.message.chat.id, "Введіть ТТН:")
                bot.register_next_step_handler(masgg, ttn, or_id)
            else:
                cur.execute(""" UPDATE orders SET status = status + 1 WHERE or_id = ? """, [or_id])
                conn.commit()
                if (isinstance(st, str)):
                    bot.answer_callback_query(call.id, "Стан замовлення змінено на {}".format(st), show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "Стан замовлення змінено на {}".format(st[p_t]), show_alert=True)
                customer_notice(or_id)
        elif wtf == "skas":
            cancel_or(or_id)

    except Exception as e:
        print(e)

def new_stat(call, or_id):
    try:
        cur.execute(""" SELECT * FROM orders WHERE or_id = ? """, [or_id])
        ord = cur.fetchone()
        if ord[7] != 3:
            nxt_stan = stat[ord[7]+1]
            if (isinstance(nxt_stan, str)):
                staat = nxt_stan
            else:
                staat = nxt_stan[ord[10]]
            mm = types.InlineKeyboardMarkup()
            mm.add(types.InlineKeyboardButton(text="🚫Скасувати замовлення🚫", callback_data="upd_stat#skas#{}".format(or_id)) ,types.InlineKeyboardButton(text="➡️Наступний статус➡️", callback_data="upd_stat#nxt#{}".format(or_id)))
            mm.add(types.InlineKeyboardButton(text="Назад🔙", callback_data="n_back#{}".format(or_id)), types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
            bot.send_message(call.message.chat.id, "Зміна статусу замовлення <code>#{}</code>\nНаступний статус - <b>{}</b>".format(ord[0], staat), parse_mode="html", reply_markup=mm)
        else:
            nxt_stan = stat[ord[7]]
            if (isinstance(nxt_stan, str)):
                staat = nxt_stan
            else:
                staat = nxt_stan[ord[10]]
            mm = types.InlineKeyboardMarkup()
            mm.add(types.InlineKeyboardButton(text="Назад🔙", callback_data="n_back#{}".format(or_id)), types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
            bot.send_message(call.message.chat.id, "Зміна статусу замовлення <code>#{}</code> Неможлива, оскільки статус замовлення - <b>{}</b>".format(ord[0], staat), parse_mode="html", reply_markup=mm)

    except Exception as e:
        print(e)

def ttn(message, or_id):
    try:
        print(or_id)
        text = message.text
        print(text)
        cur.execute(""" UPDATE orders SET seller_message = ?, status = status + 1 WHERE or_id = ? """, (text, or_id))
        conn.commit()
        cur.execute(""" SELECT * FROM orders WHERE or_id = ? """, [or_id])
        ord = cur.fetchone()
        stann = ord[7]
        p_t = ord[10]
        st = stat[stann]
        if (isinstance(st, str)):
            bot.answer_callback_query(call.id, "Стан замовлення змінено на {}".format(st), show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Стан замовлення змінено на {}".format(st[p_t]), show_alert=True)
        customer_notice(or_id)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='bb')
def back_or(call):
    try:
        max_id = call.data.split('#')[1]
        print("bb")
        uuid = call.from_user.id
        cur.execute(""" SELECT * FROM "main"."orders" WHERE "main"."orders"."uid" = ? AND "main"."orders"."or_id" = ? """,(uuid, max_id))
        ordd = cur.fetchall()
        for item in ordd:
            cur.execute(""" UPDATE taste SET count = count + ?
                WHERE "main"."taste"."id" = ?
                AND "main"."taste"."taste" = ? """,(item[4], item[1], item[3]))
            conn.commit()
        bot.delete_message(call.message.chat.id,call.message.message_id)
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        start(call)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='m_o')
def or_list_handler(call):
    try:
        bot.delete_message(call.message.chat.id,call.message.message_id)
        my_or(call)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='n_o')
def new_or_list_handler(call):
    try:
        bot.delete_message(call.message.chat.id,call.message.message_id)
        page = int(call.data.split('#')[2])
        n_o(call, page)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='taste')
def taste_call(call):
    try:
        elec_taste = call.data.split('#')[1]
        elec_id = call.data.split('#')[2]
        uidd = call.from_user.id
        print(elec_taste)
        print(elec_id)
        cur.execute("""
        SELECT "main"."products"."price"
        FROM "main"."taste"
        INNER JOIN "main"."products" ON "main"."taste"."id" = "main"."products"."id"
        WHERE "main"."taste"."id" = ? AND "main"."taste"."taste" = ? """, (elec_id, elec_taste))
        temp_cart = cur.fetchone()
        cur.execute("""
        SELECT "main"."cart"."id",
        "main"."cart"."uid",
        "main"."cart"."taste"
        FROM "main"."cart"
        WHERE "main"."cart"."id" = ? AND "main"."cart"."uid" = ? AND
        "main"."cart"."taste" = ? """, (elec_id, uidd, elec_taste))
        if cur.fetchone() is None:
            cur.execute('INSERT INTO cart VALUES (?,?,?,1,?)', (elec_id, uidd, elec_taste, temp_cart[0]))
            conn.commit()
            bot.answer_callback_query(call.id, "Товар добавлений в корзину🛒")
        else:
            cur.execute("""UPDATE cart SET count = count + 1
            WHERE "main"."cart"."id" = ?
            AND "main"."cart"."uid" = ?
            AND "main"."cart"."taste" = ? """, (elec_id, uidd, elec_taste))
            conn.commit()
            bot.answer_callback_query(call.id, "Товар добавлений в корзину🛒")
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='cart')
def cart_call(call):
    try:
        if call.data.split('#')[1]=='+':
            cur.execute(""" UPDATE cart SET count = count + 1
            WHERE "main"."cart"."id" = ?
            AND "main"."cart"."uid" = ?
            AND "main"."cart"."taste" = ? """, (call.data.split('#')[2], call.from_user.id, call.data.split('#')[3]))
            conn.commit()
            cart_c(call)
        elif call.data.split('#')[1]=='-':

            cur.execute("""UPDATE cart SET count = count - 1
            WHERE "main"."cart"."id" = ?
            AND "main"."cart"."uid" = ?
            AND "main"."cart"."taste" = ? """, (call.data.split('#')[2], call.from_user.id, call.data.split('#')[3]))
            conn.commit()
            cur.execute(""" DELETE FROM cart WHERE "main"."cart"."uid" = ? AND count = 0 """, [call.from_user.id])
            conn.commit()
            cart_c(call)
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='buy')
def bbuy(call):
    cart_price = call.data.split('#')[1]
    bot.delete_message(call.message.chat.id,call.message.message_id)
    buy_elf(call, cart_price)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='order')
def order_call(call):
    try:
        cart_price = call.data.split('#')[2]
        dt = call.data.split('#')[1]
        bot.delete_message(call.message.chat.id,call.message.message_id)
        pay_type(call, cart_price, dt)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='pay_type')
def p_t(call):
    try:
        bot.delete_message(call.message.chat.id,call.message.message_id)
        pay_type = call.data.split('#')[1]
        cart_price = call.data.split('#')[2]
        dt = call.data.split('#')[3]
        if pay_type == 1 or "1":
            pay = types.InlineKeyboardMarkup()
            pay.add(types.InlineKeyboardButton("Підтвердити оплату", callback_data="card_succes#{}#{}#{}".format(pay_type, dt, cart_price)))
            pay.add(types.InlineKeyboardButton("Скасувати❌", callback_data="back"))
            bot.send_message(call.message.chat.id, "Оплатіть <b>{}</b> грн. на цю карту <code>{}</code>".format(cart_price, card_num), parse_mode="html", reply_markup=pay)
        else:
            order(call, pay_type, dt, cart_price)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='card_succes')
def card_ss(call):
    try:
        pay_type = call.data.split('#')[1]
        dt = call.data.split('#')[2]
        cart_price = call.data.split('#')[3]
        bot.delete_message(call.message.chat.id,call.message.message_id)
        order(call, pay_type, dt, cart_price)
    except Exception as e:
        print(e)

def pay_type(call, cart_price, dt):
    try:
        or_type = int(call.data.split('#')[1])
        if or_type == 1:
            nn = types.InlineKeyboardMarkup()
            nn.add(types.InlineKeyboardButton("Готівка💵",callback_data="pay_type#0#{}#{}".format(cart_price, dt)))
            nn.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
            bot.send_message(call.message.chat.id, "Виберіть спосіб оплати:", reply_markup=nn)
        else:
            nn = types.InlineKeyboardMarkup()
            nn.add(types.InlineKeyboardButton("Готівка💵",callback_data="pay_type#0#{}#{}".format(cart_price, dt)),types.InlineKeyboardButton("Безготівковий💳",callback_data="pay_type#1#{}#{}".format(cart_price, dt)))
            nn.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
            bot.send_message(call.message.chat.id, "Виберіть спосіб оплати:", reply_markup=nn)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='amm')
def pay_check(call):
    try:
        bot.delete_message(call.message.chat.id,call.message.message_id)
        p = call.data.split('#')[1]
        or_id = call.data.split('#')[2]
        print(or_id)
        print(type(int(or_id)))
        if p == "1":
            cur.execute(""" UPDATE orders SET status = 1 WHERE or_id = ? """, [int(or_id)])
            conn.commit()
        else:
            cancel_or(or_id)

    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='ttt')
def ttt(call):
    bot.delete_message(call.message.chat.id,call.message.message_id)
    page = int(call.data.split('#')[1])
    tt = int(call.data.split('#')[2])
    next_prvs = call.data.split('#')[3]
    max_tt = int(call.data.split('#')[4])
    if tt == 1 and next_prvs == "-":
        vit(call, page, tt)
    elif tt == max_tt and next_prvs == "+":
        vit(call, page, tt)
    elif next_prvs == "+":
        vit(call, page, tt+1)
    elif next_prvs == "-":
        vit(call, page, tt-1)

def cancel_or(or_id):
    try:
        cur.execute("""  UPDATE orders SET status = 9 WHERE or_id = ? """, [or_id])
        conn.commit()
        cur.execute(" SELECT * FROM orders WHERE or_id = ? ", [or_id])
        orr = cur.fetchall()
        for item in orr:
            print(item)
            cur.execute(""" UPDATE taste SET count = count + ?
                WHERE "main"."taste"."id" = ?
                AND "main"."taste"."taste" = ? """,(item[4], item[1], item[3]))
            conn.commit()
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='edit')
def edit_call(call):
    try:
        id = int(call.data.split('#')[1])
        edit_second_stage(call, id)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='edit_page')
def edit_page(call):
    try:
        page = int(call.data.split()[1])
        next_prvs = call.data.split()[2]
        max_page = int(call.data.split()[3])
        bot.delete_message(call.message.chat.id,call.message.message_id)
        if page == 1 and next_prvs == "-":
            edit_napov(call, page=page)
        elif page == max_page and next_prvs == "+":
            edit_napov(call, page=page)
        elif next_prvs == "+":
            edit_napov(call, page=page+1)
        elif next_prvs == "-":
            edit_napov(call, page=page-1)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='aback')
def aback(call):
    try:
        page = int(call.data.split('#')[1])
        bot.delete_message(call.message.chat.id,call.message.message_id)
        or_cab(call, page)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == "vitryna":
            bot.delete_message(call.message.chat.id,call.message.message_id)
            vit(call)
        elif call.data == "adm":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if call.message.chat.id in admin:
                addm(call)
            else:
                start(call)
        elif call.data == "admin_n":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if call.message.chat.id in admin:
                napov(call)
            else:
                start(call)
        elif call.data == "admin_old":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if call.message.chat.id in admin:
                edit_napov(call)
            else:
                start(call)
        elif call.data == "back":
            bot.delete_message(call.message.chat.id,call.message.message_id)
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            start(call)
        elif call.data == "carftt":
            bot.delete_message(call.message.chat.id,call.message.message_id)
            cart(call)
        elif call.data == "or_cab":
            #bot.delete_message(call.message.chat.id,call.message.message_id)
            if call.message.chat.id in admin:
                print(call.data)
                or_cab(call)
            else:
                start(call)
        elif call.data == "my_or":
            bot.delete_message(call.message.chat.id,call.message.message_id)
            or_list(call)
        elif call.data == "bback":
            bot.delete_message(call.message.chat.id,call.message.message_id)
            or_list(call)
        elif call.data == "back_edit":
            bot.delete_message(call.message.chat.id,call.message.message_id)
            if call.message.chat.id in admin:
                addm(call)
            else:
                start(call)
        elif call.data == "clear":
            bot.delete_message(call.message.chat.id,call.message.message_id)
    except Exception as e:
        print(e)
#adm
def addm(call):
    try:
        am = types.InlineKeyboardMarkup(row_width=2)
        am.add(types.InlineKeyboardButton(text="Нова позиція товару🆕", callback_data="admin_n"), types.InlineKeyboardButton(text="Оновити позиції🔄", callback_data="admin_old"), types.InlineKeyboardButton("Нові Замовлення📜",callback_data="or_cab"), types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
        bot.send_message(call.message.chat.id, "Доброго дня <b>{}</b>, чим я можу вам допомогти?".format(call.from_user.first_name), reply_markup=am, parse_mode="html")

    except Exception as e:
        print(e)
#adm
def edit_napov(call, page=1):
    try:
        cur.execute(""" SELECT id FROM products ORDER BY id DESC LIMIT 1 """)
        max_id = cur.fetchone()
        temp_edit = []
        i=1
        while i <= max_id[0]:
            cur.execute("""
            SELECT
            "main"."products"."id",
            "main"."products"."photo",
            "main"."products"."title",
            "main"."products"."price",
            "main"."taste"."taste",
            "main"."taste"."count",
            "main"."products"."description"
            FROM "main"."taste"
            INNER JOIN "main"."products" ON "main"."taste"."id" = "main"."products"."id"
            WHERE "main"."products"."id" = ? """, [i])
            ucheck = cur.fetchall()
            if ucheck == None or len(ucheck) == 0:
                i=i+1
            else:
                temp_edit.append(ucheck)
                i=i+1
        l = len(temp_edit)/9
        buttons_list = []
        i = 9*page
        b = i-8
        while b<=i:
            try:
                item=temp_edit[b-1]
                buttons_list.append(types.InlineKeyboardButton(text=item[0][2], callback_data="edit#{}".format(item[0][0])))
                b=b+1
            except Exception as e:
                b=b+1
                pass
        mm = types.InlineKeyboardMarkup(row_width=3)
        mm.add(*buttons_list)
        if math.ceil(l) > 1:
            mm.add(types.InlineKeyboardButton("⬅️", callback_data="edit_page#{}#-#{}".format(page, math.ceil(l))), types.InlineKeyboardButton("{}/{}".format(page, math.ceil(l)), callback_data="gfd"), types.InlineKeyboardButton("➡️", callback_data="edit_page#{}#+#{}".format(page, math.ceil(l))))
        mm.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"), types.InlineKeyboardButton("Назад🔙",callback_data="back_edit"))
        bot.send_message(call.message.chat.id, "Панове, який саме продукт ви бажаєте відредагувати?📝", reply_markup=mm)
    except Exception as e:
        print(e)
#adm
def edit_second_stage(call, id, page=1):
    try:
        cur.execute("""
        SELECT
        "main"."products"."id",
        "main"."products"."photo",
        "main"."products"."title",
        "main"."products"."price",
        "main"."taste"."taste",
        "main"."taste"."count",
        "main"."products"."description"
        FROM "main"."taste"
        INNER JOIN "main"."products" ON "main"."taste"."id" = "main"."products"."id"
        WHERE "main"."products"."id" = ?
        ORDER BY "main"."taste"."count" """, [id])
        ucheck = cur.fetchall()
        print(ucheck)
        text_d = ["<b>Всі відомості про цю позицію:</b>\n"]
        for item in ucheck:
            text_d.append("-----{}-----\n")
        temp_photo = open(ucheck[0][1], 'rb')
        text = ''.join(text_d)
        bot.send_photo(call.message.chat.id, temp_photo, caption=text, parse_mode='html')
        temp_photo.close()
    except Exception as e:
        print(e)
#adm
def or_cab(call, page=1):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        cur.execute(""" SELECT * FROM orders GROUP BY or_id ORDER BY or_id DESC, status DESC """)
        cus_or = cur.fetchall()
        print(cus_or)
        if cus_or is None or len(cus_or)==0:
            nn = types.InlineKeyboardMarkup()
            nn.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"), types.InlineKeyboardButton("Назад🔙",callback_data="back_edit"))
            bot.send_message(cid, "😥На жаль у вас ще немає замовлень", reply_markup=nn)
        else:
            buttons_list = []
            l = len(cus_or)/10
            paginator = InlineKeyboardPaginator(
                math.ceil(l),
                current_page=page,
                data_pattern='cab_or#{page}'
            )

            i = 10*page
            b = i-9
            while b<=i:
                try:
                    stan = stat[cus_or[b-1][7]]
                    if (isinstance(stan, str)):
                        p = types.InlineKeyboardButton(text="#{} | {} | {}".format(cus_or[b-1][0], stat[cus_or[b-1][7]], cus_or[b-1][9]), callback_data='n_o#{}#{}'.format(cus_or[b-1][0], page))
                    else:
                        pay_type = cus_or[b-1][10]
                        p = types.InlineKeyboardButton(text="#{} | {} | {}".format(cus_or[b-1][0], stat[cus_or[b-1][7]][pay_type], cus_or[b-1][9]), callback_data='n_o#{}#{}'.format(cus_or[b-1][0], page))
                    paginator.add_before(p)
                    b=b+1
                    print(b)
                except Exception as e:
                    b=b+1
                    pass
            paginator.add_after(types.InlineKeyboardButton('↩️На головну↩️', callback_data='back'), types.InlineKeyboardButton("Назад🔙",callback_data="back_edit"))
            bot.send_message(cid, text="📦 Замовлення:", reply_markup=paginator.markup)

    except Exception as e:
        print(e)
#adm
def n_o(call, page):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        or_id = call.data.split('#')[1]
        cur.execute(""" SELECT * FROM orders WHERE or_id = ? ORDER BY or_id ASC""",[or_id])
        cus_or = cur.fetchall()
        print(cus_or)
        pay_type = cus_or[0][10]
        delivery = {0:"Самовивіз", 1:"Пункт передачі НП", 2:"Доставка по НП", 3:"Доставка продавцем"}
        or_price = 0
        stan = stat[cus_or[0][7]]
        temp_text = []
        for item in cus_or:
            coun = item[4]
            price = item[5]
            taste = item[3]
            id = item[1]
            cur.execute("""SELECT title FROM products WHERE id = ? """, [id])
            title = cur.fetchone()[0]
            cur_price = price*coun
            or_price = or_price+cur_price
            temp_text.append("<code>{} | {} | {} шт.</code>\n".format(title, taste, coun))
        orr = types.InlineKeyboardMarkup()
        orr.add(types.InlineKeyboardButton("Оновити статус",callback_data="n_stat#{}".format(or_id, cus_or[0][7], cus_or[0][6], cus_or[0][10])))
        orr.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"), types.InlineKeyboardButton("🔙Назад",callback_data="aback#{}".format(page)))
        if cus_or[0][11] == "  ":
            if (isinstance(stan, str)):
                bot.send_message(cid, text="📦 <b>Інформація про замовлення:</b>\n\n<b>Номер замовлення:</b> #{}\n<b>Статус:</b> {}\n<b>Тип достаки:</b> {}\n<b>Тип оплати:</b> {} \n<b>Сума замовлення:</b> {} грн.\n<b>Дата:</b> {}\n<b>Вміст замовлення:</b>\n {}".format(cus_or[0][0], stat[cus_or[0][7]], delivery[cus_or[0][6]], pay_t[pay_type], or_price, cus_or[0][9], ''.join(temp_text)), parse_mode="html", reply_markup=orr)
            else:
                bot.send_message(cid, text="📦 <b>Інформація про замовлення:</b>\n\n<b>Номер замовлення:</b> #{}\n<b>Статус:</b> {}\n<b>Тип достаки:</b> {}\n<b>Тип оплати:</b> {} \n<b>Сума замовлення:</b> {} грн.\n<b>Дата:</b> {}\n<b>Вміст замовлення:</b>\n {}".format(cus_or[0][0], stat[cus_or[0][7]][pay_type], delivery[cus_or[0][6]], pay_t[pay_type], or_price, cus_or[0][9], ''.join(temp_text)), parse_mode="html", reply_markup=orr)
        else:
            if (isinstance(stan, str)):
                bot.send_message(cid, text="📦 <b>Інформація про замовлення:</b>\n\n<b>Номер замовлення:</b> #{}\n<b>Статус:</b> {}\n<b>Тип достаки:</b> {}\n<b>ТТН:</b> <code>{}</code>\n<b>Тип оплати:</b> {} \n<b>Сума замовлення:</b> {} грн.\n<b>Дата:</b> {}\n<b>Вміст замовлення:</b>\n {}".format(cus_or[0][0], stat[cus_or[0][7]], delivery[cus_or[0][6]], cus_or[0][11], pay_t[pay_type], or_price, cus_or[0][9], ''.join(temp_text)), parse_mode="html", reply_markup=orr)
            else:
                bot.send_message(cid, text="📦 <b>Інформація про замовлення:</b>\n\n<b>Номер замовлення:</b> #{}\n<b>Статус:</b> {}\n<b>Тип достаки:</b> {}\n<b>ТТН:</b> <code>{}</code>\n<b>Тип оплати:</b> {} \n<b>Сума замовлення:</b> {} грн.\n<b>Дата:</b> {}\n<b>Вміст замовлення:</b>\n {}".format(cus_or[0][0], stat[cus_or[0][7]][pay_type], delivery[cus_or[0][6]], cus_or[0][11], pay_t[pay_type], or_price, cus_or[0][9], ''.join(temp_text)), parse_mode="html", reply_markup=orr)


    except Exception as e:
        print(e)
#all
def or_list(call, page=1):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        cur.execute(""" SELECT * FROM orders WHERE uid = ? GROUP BY or_id ORDER BY or_id DESC, status DESC """,[uid])
        cus_or = cur.fetchall()
        print(cus_or)
        if cus_or is None or len(cus_or)==0:
            nn = types.InlineKeyboardMarkup()
            nn.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
            bot.send_message(cid, "😥На жаль у вас ще немає замовлень", reply_markup=nn)
        else:
            buttons_list = []
            l = len(cus_or)/10
            paginator = InlineKeyboardPaginator(
                math.ceil(l),
                current_page=page,
                data_pattern='u_or#{page}'
            )

            i = 10*page
            b = i-9
            while b<=i:
                try:
                    stan = stat[cus_or[b-1][7]]
                    if (isinstance(stan, str)):
                        p = types.InlineKeyboardButton(text="#{} | {} | {}".format(cus_or[b-1][0], stat[cus_or[b-1][7]], cus_or[b-1][9]), callback_data='m_o#{}'.format(cus_or[b-1][0]))
                    else:
                        pay_type = cus_or[b-1][10]
                        p = types.InlineKeyboardButton(text="#{} | {} | {}".format(cus_or[b-1][0], stat[cus_or[b-1][7]][pay_type], cus_or[b-1][9]), callback_data='m_o#{}'.format(cus_or[b-1][0]))
                    paginator.add_before(p)
                    b=b+1
                    print(b)
                except Exception as e:
                    b=b+1
                    pass
            paginator.add_after(types.InlineKeyboardButton('↩️На головну↩️', callback_data='back'))
            bot.send_message(cid, text="📦 Ваші замовлення:", reply_markup=paginator.markup)


    except Exception as e:
        print(e)
#all
def my_or(call):
    try:
        uid = call.from_user.id
        cid = call.message.chat.id
        or_id = call.data.split('#')[1]
        cur.execute(""" SELECT * FROM orders WHERE or_id = ? ORDER BY or_id ASC""",[or_id])
        cus_or = cur.fetchall()
        print(cus_or)
        pay_type = cus_or[0][10]
        delivery = {0:"Самовивіз", 1:"Пункт передачі НП", 2:"Доставка по НП", 3:"Доставка продавцем"}
        or_price = 0
        stan = stat[cus_or[0][7]]
        temp_text = []
        for item in cus_or:
            coun = item[4]
            price = item[5]
            taste = item[3]
            id = item[1]
            cur.execute("""SELECT title FROM products WHERE id = ? """, [id])
            title = cur.fetchone()[0]
            cur_price = price*coun
            or_price = or_price+cur_price
            temp_text.append("<code>{} | {} | {} шт.</code>\n".format(title, taste, coun))
        orr = types.InlineKeyboardMarkup()
        orr.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"), types.InlineKeyboardButton("🔙Назад",callback_data="bback"))
        if cus_or[0][11] == "  ":
            if (isinstance(stan, str)):
                bot.send_message(cid, text="📦 <b>Інформація про замовлення:</b>\n\n<b>Номер замовлення:</b> #{}\n<b>Статус:</b> {}\n<b>Тип достаки:</b> {}\n<b>Сума замовлення:</b> {} грн.\n<b>Дата:</b> {}\n<b>Вміст замовлення:</b>\n {}".format(cus_or[0][0], stat[cus_or[0][7]], delivery[cus_or[0][6]], or_price, cus_or[0][9], ''.join(temp_text)), parse_mode="html", reply_markup=orr)
            else:
                bot.send_message(cid, text="📦 <b>Інформація про замовлення:</b>\n\n<b>Номер замовлення:</b> #{}\n<b>Статус:</b> {}\n<b>Тип достаки:</b> {}\n<b>Сума замовлення:</b> {} грн.\n<b>Дата:</b> {}\n<b>Вміст замовлення:</b>\n {}".format(cus_or[0][0], stat[cus_or[0][7]][pay_type], delivery[cus_or[0][6]], or_price, cus_or[0][9], ''.join(temp_text)), parse_mode="html", reply_markup=orr)
        else:
            if (isinstance(stan, str)):
                bot.send_message(cid, text="📦 <b>Інформація про замовлення:</b>\n\n<b>Номер замовлення:</b> #{}\n<b>Статус:</b> {}\n<b>Тип достаки:</b> {}\n<b>ТТН:</b> <code>{}</code>\n<b>Сума замовлення:</b> {} грн.\n<b>Дата:</b> {}\n<b>Вміст замовлення:</b>\n {}".format(cus_or[0][0], stat[cus_or[0][7]], delivery[cus_or[0][6]], cus_or[0][11], or_price, cus_or[0][9], ''.join(temp_text)), parse_mode="html", reply_markup=orr)
            else:
                bot.send_message(cid, text="📦 <b>Інформація про замовлення:</b>\n\n<b>Номер замовлення:</b> #{}\n<b>Статус:</b> {}\n<b>Тип достаки:</b> {}\n<b>ТТН:</b> <code>{}</code>\n<b>Сума замовлення:</b> {} грн.\n<b>Дата:</b> {}\n<b>Вміст замовлення:</b>\n {}".format(cus_or[0][0], stat[cus_or[0][7]][pay_type], delivery[cus_or[0][6]], cus_or[0][11], or_price, cus_or[0][9], ''.join(temp_text)), parse_mode="html", reply_markup=orr)


    except Exception as e:
        print(e)

def cart_c(message):
    try:
        uidd = message.from_user.id
        print(uidd)
        cart = types.InlineKeyboardMarkup(row_width=3)
        print(message.message.message_id)
        cur.execute("""SELECT "main"."cart"."id", "main"."cart"."taste", "main"."cart"."price", "main"."cart"."count" FROM "main"."cart" WHERE "main"."cart"."count" > 0 AND "main"."cart"."uid" = ? """, [uidd])
        a = cur.fetchall()
        if a is None or len(a)==0:
            cart.add(types.InlineKeyboardButton("Вітрина🔞🚬", callback_data="vitryna"), types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
            bot.edit_message_text("На жаль ваша корзина Пуста\nАле ви завжди можете її доповнити!",chat_id=message.message.chat.id,message_id=message.message.message_id,reply_markup=cart)
        else:
            cur.execute("""SELECT "main"."cart"."id", "main"."cart"."taste", "main"."cart"."price", "main"."cart"."count" FROM "main"."cart" WHERE "main"."cart"."count" > 0 AND "main"."cart"."uid" = ? """, [uidd])
            buttons = cur.fetchall()
            print(buttons)
            print('cartc')
            buttons_list = []
            text = ['*Ваша корзина:*🛒\n\n']
            i=1
            cart_price = 0
            for item in buttons:
                taste = str(item[1])
                coun = int(item[3])
                price = int(item[2])
                id = item[0]
                cur_price = price*coun
                cart_price = cart_price+cur_price
                cur.execute("""SELECT title FROM products WHERE id = ? """, [id])
                title = cur.fetchone()
                text.append('{}. *{}* {} *(грн/шт)* {} ({}шт.) - {} грн\n'.format(i, title[0],price , taste.replace('_', ' '), coun, cur_price))
                cart.add(types.InlineKeyboardButton(text="➖", callback_data='cart#-#{}#{}'.format(item[0], item[1])), types.InlineKeyboardButton(text="{}. ({} шт.)".format(i, coun), callback_data=' '), types.InlineKeyboardButton(text="➕", callback_data="cart#+#{}#{}".format(item[0], item[1])))
                i=i+1
            text.append("\n Сума: {} *Грн*".format(cart_price))
            cart.add(types.InlineKeyboardButton("Оформити замовлення",callback_data="buy#{}".format(cart_price)),types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
            bot.edit_message_text(text=''.join(text),chat_id=message.message.chat.id,message_id=message.message.message_id,reply_markup=cart, parse_mode="Markdown")
    except Exception as e:
        print(e)

def cart(message):
    try:
        uidd = message.from_user.id
        print(uidd)
        cart = types.InlineKeyboardMarkup(row_width=3)
        print(message.message.message_id)
        cur.execute("""SELECT "main"."cart"."id",
  "main"."cart"."uid",
  "main"."cart"."taste",
  "main"."cart"."count",
  "main"."cart"."price"
FROM "main"."cart"
WHERE "main"."cart"."uid" = ? AND "main"."cart"."count" > 0 """, [uidd])
        a = cur.fetchall()
        if a is None or len(a)==0:
            cart.add(types.InlineKeyboardButton("Вітрина🔞🚬", callback_data="vitryna"), types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
            bot.send_message(message.message.chat.id, "На жаль ваша корзина Пуста\nАле ви завжди можете її доповнити!",reply_markup=cart)
        else:
            cur.execute("""SELECT "main"."cart"."id", "main"."cart"."taste", "main"."cart"."price", "main"."cart"."count" FROM "main"."cart" WHERE "main"."cart"."count" > 0 AND "main"."cart"."uid" = ?  """, [uidd])
            buttons = cur.fetchall()
            print(buttons)
            print('cart')
            buttons_list = []
            text = ['*Ваша корзина:*🛒\n\n']
            i=1
            cart_price = 0
            for item in buttons:
                taste = str(item[1])
                coun = int(item[3])
                price = int(item[2])
                id = item[0]
                cur_price = price*coun
                cart_price = cart_price+cur_price
                cur.execute("""SELECT title FROM products WHERE id = ? """, [id])
                title = cur.fetchone()
                text.append('{}. *{}* {} *(грн/шт)* {} ({}шт.) - {} грн\n'.format(i, title[0],price , taste.replace('_', ' '), coun, cur_price))
                cart.add(types.InlineKeyboardButton(text="➖", callback_data='cart#-#{}#{}'.format(item[0], item[1])), types.InlineKeyboardButton(text="{}. ({} шт.)".format(i, coun), callback_data=' '), types.InlineKeyboardButton(text="➕", callback_data="cart#+#{}#{}".format(item[0], item[1])))
                i=i+1
            text.append("\n Сума: {} *Грн*".format(cart_price))
            cart.add(types.InlineKeyboardButton("Оформити замовлення",callback_data="buy#{}".format(cart_price)),types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
            bot.send_message(message.message.chat.id, ''.join(text),reply_markup=cart, parse_mode="Markdown")
    except Exception as e:
        print(e)

def vit(message, page=1, tt=1):   #вивід вітрини
    try:
        cur.execute(""" SELECT id FROM products ORDER BY id DESC LIMIT 1 """)
        max_id = cur.fetchone()
        temp_vit = []
        i=1
        while i <= max_id[0]:

            cur.execute("""
            SELECT
            "main"."products"."id",
            "main"."products"."photo",
            "main"."products"."title",
            "main"."products"."price",
            "main"."taste"."taste",
            "main"."taste"."count",
            "main"."products"."description"
            FROM "main"."taste"
            INNER JOIN "main"."products" ON "main"."taste"."id" = "main"."products"."id"
            WHERE "main"."products"."id" = ? AND "main"."taste"."count" > 0 """, [i])
            ucheck = cur.fetchall()
            if ucheck == None or len(ucheck) == 0:
                i=i+1
            else:
                temp_vit.append(ucheck)
                i=i+1
        l = len(temp_vit[page-1])/5
        paginator = InlineKeyboardPaginator(
            len(temp_vit),
            current_page=page,
            data_pattern='character#{page}'
        )
        cur_taste = []
        for temp_taste in temp_vit[page-1]:
            cur_taste.append(temp_taste[4])
        i = 5*tt
        b = i-4
        while b<=i:
            try:
                item = cur_taste[b-1]
                p = types.InlineKeyboardButton(text="{}".format(item.replace('_', ' ')), callback_data='taste#{}#{}'.format(item, temp_vit[page-1][0][0]))
                paginator.add_before(p)
                b=b+1
            except Exception as e:
                b=b+1
                pass
        print("bbbb")
        if math.ceil(l) > 1:
            paginator.add_before(types.InlineKeyboardButton("⬅️", callback_data="ttt#{}#{}#-#{}".format(page, tt, math.ceil(l))), types.InlineKeyboardButton("{}/{}".format(tt, math.ceil(l)), callback_data="gfd"), types.InlineKeyboardButton("➡️", callback_data="ttt#{}#{}#+#{}".format(page, tt, math.ceil(l))))
        print("fdf")
        paginator.add_after(types.InlineKeyboardButton('↩️На головну↩️', callback_data='back'))
        temp_photo = open(temp_vit[page-1][0][1], 'rb')
        if temp_vit[page-1][0][6] == "-":
            temp_text = temp_vit[page-1][0][2],"\n*Ціна:*",str(temp_vit[page-1][0][3])," грн."
        else:
            temp_text = temp_vit[page-1][0][2],"\n",temp_vit[page-1][0][6],"\n\n*Ціна:*",str(temp_vit[page-1][0][3])," грн."
        bot.send_photo(message.message.chat.id,temp_photo,caption=''.join(temp_text),reply_markup=paginator.markup,parse_mode='Markdown')
        temp_photo.close()
    except Exception as e:
        print(e)

def buy_elf(message, cart_price):
    try:
        result = check(message.from_user.id)
        if result is None or len(result)==0:
            text = ["Настав час вибрати як і де ви отримаєте все що ви вибрали!\n\n"]
            i=1
            buy_keyboard = types.InlineKeyboardMarkup(row_width=2)
            for index, value in enumerate(config.delivery):
                print(list((index, value)))
                if value == True and index==0:
                    print('ok')
                    buy_keyboard.add(types.InlineKeyboardButton("Самовивіз", callback_data="order#0#{}".format(cart_price)))
                    text.append(str(i)+'.'+config.delivery_description[index]+"\n")
                    i=i+1
                elif value == True and index==1:
                    print('ok')
                    buy_keyboard.add(types.InlineKeyboardButton("Пункт передачі", callback_data="order#1#{}".format(cart_price)))
                    text.append(str(i)+'.'+config.delivery_description[index]+"\n")
                    i=i+1
                elif value == True and index==2:
                    print('ok')
                    buy_keyboard.add(types.InlineKeyboardButton("Доставка по НП", callback_data="order#2#{}".format(cart_price)))
                    text.append(str(i)+'.'+config.delivery_description[index]+"\n")
                    i=i+1
                elif value == True and index==3:
                    print('ok')
                    buy_keyboard.add(types.InlineKeyboardButton("Доставка продавцем", callback_data="order#3#{}".format(cart_price)))
                    text.append(str(i)+'.'+config.delivery_description[index]+"\n")
                    i=i+1
            buy_keyboard.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
            bot.send_message(message.message.chat.id, text=''.join(text), reply_markup=buy_keyboard)
        else:
            text = ['На жаль, зараз неможливо оформити замовлення, оскільки у вас в корзині вибрана більша кількість, ніж є у наявності\n\n']
            for item in result:
                text.append("*{}* — *{}* \nУ вас в корзині (*{}* шт.), але доступно —(*{}* шт.)\n".format(item[2],item[3],item[4],item[5]))
            buy_keyboard = types.InlineKeyboardMarkup(row_width=2)
            buy_keyboard.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"), types.InlineKeyboardButton("Корзина🛒",callback_data="carftt"))
            bot.send_message(message.message.chat.id, text=''.join(text), reply_markup=buy_keyboard, parse_mode="Markdown")

    except Exception as e:
        print(e)

def order(call, pay, dt, cart_price):
    num = int(dt)
    uuid = call.from_user.id
    status=0
    result = check(uuid)
    if result is None or len(result)==0:
        print("ok")
        cur.execute(""" SELECT * FROM "main"."cart" WHERE "main"."cart"."uid" = ? """,[uuid])
        cart = cur.fetchall()
        cur.execute(""" SELECT or_id FROM orders ORDER BY or_id DESC LIMIT 1 """)
        max_id = cur.fetchone()
        mx_id=0
        if max_id is None:
            mx_id=1
        else:
            mx_id=max_id[0]+1
        print(max_id)
        del_info = " "
        message_seller = "  "
        country_time_zone = pytz.timezone('Europe/Kyiv')
        today = datetime.now(country_time_zone)
        temp_or = [str(today.day),".",str(today.month),".",str(today.year)," ",str(today.hour),":",str(today.minute),":",str(today.second)]
        for item in cart:
            print(item)
            cur.execute(""" INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?) """,(mx_id, item[0], item[1], item[2], item[3], item[4], num, status, del_info, ''.join(temp_or), pay, message_seller))
            conn.commit()
            cur.execute(""" UPDATE taste SET count = count - ?
                WHERE "main"."taste"."id" = ?
                AND "main"."taste"."taste" = ? """,(item[3], item[0], item[2]))
            conn.commit()
        if pay == 1 or "1":
            pay_verification(mx_id, cart_price)
        if num == 0:
            print("fff")
            buy_keyboard = types.InlineKeyboardMarkup()
            buy_keyboard.add(types.InlineKeyboardButton("❌Відмінити❌", callback_data="bb#{}".format(mx_id)))
            msgs = bot.send_message(call.message.chat.id, "Введіть будь ласка номер телефону та ваше ім'я':", reply_markup=buy_keyboard)
            bot.register_next_step_handler(msgs, get_num)
        elif num == 1:
            msgs = bot.send_message(call.message.chat.id, "Введіть будь ласка ваше Прізвище Ім'я По батькові, номер телефону та адресою бажаного поштомату або номером:\nЗверніть увагу, що потрібно вводити через кому(Приклад: Іван Сидоренко Іванович, 0680000000, Адреса поштомату або його номер),а також, що вам потрібно мати програму нової пошти")
        elif num == 2:
            msgs = bot.send_message(call.message.chat.id, "Введіть будь ласка ваше Прізвище Ім'я По батькові, номер телефону, адресу відділення та номер:\nЗверніть увагу, що потрібно вводити через кому(Приклад: Іван Сидоренко Іванович, 0680000000, Область Місто/село номер-відділення)")
        elif num == 3:
            msgs = bot.send_message(call.message.chat.id, "Введіть будь ласка ваше ім'я, номер телефону та Адресу:\n Зверніть увагу, що потрібно записувати через кому—Приклад(Іван, 0680000000, Вул Наукова 55Б)")
        #bot.register_next_step_handler()

    else:
        text = ['На жаль, зараз неможливо оформити замовлення, оскільки у вас в корзині вибрана більша кількість, ніж є у наявності\n\n']
        for item in result:
            text.append("*{}* — *{}* \nУ вас в корзині (*{}* шт.), але доступно — (*{}* шт.)\n".format(item[2],item[3],item[4],item[5]))
        buy_keyboard = types.InlineKeyboardMarkup()
        buy_keyboard.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
        bot.send_message(call.message.chat.id, text=''.join(text), reply_markup=buy_keyboard, parse_mode="Markdown")

def pay_verification(or_id, cart_price):
    try:
        verify = types.InlineKeyboardMarkup()
        verify.add(types.InlineKeyboardButton("Оплачений", callback_data="amm#1#{}".format(or_id)), types.InlineKeyboardButton("Неоплачений", callback_data="amm#0#{}".format(or_id)))
        for ad in admin:
            bot.send_message(chat_id=ad, text="<b>Підтвердження оплати</b> <code>#{}</code>,<b>Вартість - </b><code>{}</code> ".format(or_id, cart_price), parse_mode="html", reply_markup=verify)
    except Exception as e:
        print(e)

def get_num(message):
    prvs = message.message_id-1
    bot.delete_message(message.chat.id, prvs)
    cur.execute(""" SELECT * FROM orders WHERE uid = ? ORDER BY or_id DESC LIMIT 1""",[message.from_user.id])
    ord = cur.fetchone()
    if ord[8] == " ":
        max_or_id = ord[0]
        print(max_or_id)
        text = message.text
        print(text)
        cur.execute(""" UPDATE orders SET delivery_info = ? WHERE or_id = ? """, (text, max_or_id))
        conn.commit()
        get_num = types.InlineKeyboardMarkup()
        get_num.add(types.InlineKeyboardButton("↩️На головну↩️",callback_data="back"))
        bot.send_message(message.chat.id, "Ваше замовлення успішно оформлене, скоро з вами зв'яжеться продавець!", reply_markup=get_num)
        notice_new_or(message)
    else:
        print("okk")

def notice_new_or(message):
    try:
        cur.execute(""" SELECT * FROM orders WHERE uid = ? ORDER BY or_id DESC LIMIT 1""",[message.from_user.id])
        ord = cur.fetchone()
        num = ord[6]
        if num==0:
            typ = "Самовивіз"
        elif num==1:
            typ = "Пункт передачі"
        elif num==2:
            typ = "Доставка по НП"
        elif num==3:
            typ = "Доставка продавцем"
        for ad in admin:
            notice = types.InlineKeyboardMarkup()
            notice.add(types.InlineKeyboardButton("Приховати",callback_data="clear"))
            bot.send_message(chat_id=ad, text="<b>У вас нове замовлення</b> <code>#{}</code>,<b>Тип доставки - </b><code>{}</code> ".format(ord[0],typ), parse_mode="html")
    except Exception as e:
        print(e)

def customer_notice(or_id):
    try:
        cur.execute(""" SELECT * FROM orders WHERE or_id = ? """, [or_id])
        ord = cur.fetchone()
        uid = ord[2]
        stan = stat[ord[7]]
        p_t = ord[10]
        notice = types.InlineKeyboardMarkup()
        notice.add(types.InlineKeyboardButton("Приховати",callback_data="clear"))
        if (isinstance(stan, str)):
            bot.send_message(uid, "У вашого замовлення новий статус:{}".format(stan), reply_markup=notice)
        else:
            bot.send_message(uid, "У вашого замовлення новий статус:{}".format(stan[p_t]), reply_markup=notice)
    except Exception as e:
        print(e)

def napov(message):
    try:
        back_markup = types.InlineKeyboardMarkup()
        back_markup.add(types.InlineKeyboardButton("❌Відмінити❌", callback_data="back_edit"))
        msgsg = bot.send_message(message.message.chat.id, "Введіть назву товару (Наприклад ElfBar 1500 ElfBar BC4000)",reply_markup=back_markup)
        m_id = msgsg.message_id
        bot.register_next_step_handler(msgsg, description, m_id)
    except Exception as e:
        print(e)

def description(message, m_id):
    try:

        cid = message.chat.id
        title = message.text
        bot.delete_message(cid, m_id)
        back_markup = types.InlineKeyboardMarkup()
        back_markup.add(types.InlineKeyboardButton("❌Відмінити❌", callback_data="back_edit"))
        msgsg = bot.send_message(cid, 'Надішліть опис товару(Якщо без опису то надішліть <code>-</code>):',reply_markup=back_markup, parse_mode='html')
        mm_id = msgsg.message_id
        bot.register_next_step_handler(msgsg, process_title_step, title, mm_id)
    except Exception as e:
        bot.reply_to(message, e)

def process_title_step(message, title, mm_id):
    try:
        cid = message.chat.id
        description = message.text
        bot.delete_message(cid, mm_id)
        back_markup = types.InlineKeyboardMarkup()
        back_markup.add(types.InlineKeyboardButton("❌Відмінити❌", callback_data="back_edit"))
        msgsg = bot.send_message(cid, 'Надішліть фото товару:',reply_markup=back_markup)
        m_id = msgsg.message_id
        bot.register_next_step_handler(msgsg, get_photo, title, description, m_id)
    except Exception as e:
        bot.reply_to(message, e)

def get_photo(message, title, description, m_id):
    try:
        print(message.photo)
        uid = message.from_user.id
        cid = message.chat.id
        bot.delete_message(cid, m_id)
        if message.photo != None:
            file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            src='img/'+file_info.file_path;
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            back_markup = types.InlineKeyboardMarkup()
            back_markup.add(types.InlineKeyboardButton("❌Відмінити❌", callback_data="back_edit"))
            msgsg = bot.send_message(cid,"Введіть ціну за 1 одиницю:",reply_markup=back_markup)
            mm_id = msgsg.message_id
            bot.register_next_step_handler(msgsg, get_price, title, description, src, mm_id)
        else:
            cid = message.chat.id
            back_markup = types.InlineKeyboardMarkup()
            back_markup.add(types.InlineKeyboardButton("❌Відмінити❌", callback_data="back_edit"))
            msgsg = bot.send_message(cid, 'Надішліть фото товару:',reply_markup=back_markup)
            mmm_id = msgsg.message_id
            bot.register_next_step_handler(msgsg, get_photo, title, description, mmm_id)
    except Exception as e:
        bot.reply_to(message, e)

def get_price(message, title, description, src, mm_id):
    try:
        cid = message.chat.id
        price = message.text
        bot.delete_message(cid, mm_id)
        back_markup = types.InlineKeyboardMarkup()
        back_markup.add(types.InlineKeyboardButton("❌Відмінити❌", callback_data="back_edit"))
        msgsg = bot.send_message(cid, 'Надішліть смаки та кількість як на прикладі\n(🍇grape🍇 12, 🍑peach_ice🍑 10)\n в назві смаку не ставте пробіл та не використовуйте дужки',reply_markup=back_markup)
        m_id = msgsg.message_id
        bot.register_next_step_handler(msgsg, get_taste, title, description, src, price, m_id)
    except Exception as e:
        bot.reply_to(message, e)

def get_taste(message, title, description, src, price, m_id):
    try:
        cur.execute('INSERT INTO products(description, photo, price, title) VALUES (?,?,?,?)', (description, src, price, title))
        conn.commit()
        cur.execute("SELECT max(id) FROM products;")
        cur_id = cur.fetchall()
        curr_id = cur_id[0]
        cid = message.chat.id
        count_taste = message.text
        taste_count = count_taste.split(",")
        ttast = []
        for ta_coo in taste_count:
            ta_co = ta_coo.split()
            ttast = [int(curr_id[0]), ta_co[0], int(ta_co[1])]
            cur.execute('INSERT INTO taste VALUES (?,?,?)', (ttast[0], ttast[1], ttast[2]))
            conn.commit()
        bot.delete_message(cid, m_id)
        start(message)
    except Exception as e:
        bot.reply_to(message, e)


bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()


bot.polling(none_stop=True)

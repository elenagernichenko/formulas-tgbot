import telebot
import sqlite3
import difflib
import config
from formulas_info import x

class App:
    def __init__(self):
        self.bot = telebot.TeleBot(config.token)
        self.base = sqlite3.connect('formulas.db', check_same_thread=False)
        self.cur = self.base.cursor()
        self.conc = ['Формула','Единица измерения','Формулировка','Все сведения','По номеру понятия', 'Список понятий']
        self.comma = ['/start','/help']
        
    def similarity(self, s1, s2):
        normalized1 = s1.lower()
        normalized2 = s2.lower()
        matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
        return matcher.ratio()

    def database(self):
        self.cur.execute('''DROP TABLE IF EXISTS formulas''')
        self.base.commit()

        self.cur.execute('''CREATE TABLE IF NOT EXISTS formulas(id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        formulation TEXT,
        unit TEXT,
        formula TEXT)
        ''')
        self.base.commit()

        self.cur.executemany('''INSERT INTO formulas (name, formulation, unit, formula) VALUES(?, ?, ?, ?)''', (x))
        self.base.commit()

        self.cur.execute('''SELECT name FROM formulas''')
        self.info = self.cur.fetchall()

        self.cur.execute('''SELECT id FROM formulas''')
        self.num = self.cur.fetchall()

    def router(self):
        @self.bot.message_handler(commands=['start', 'help', 'send'])
        def start_help_command(message):
            if message.text == '/start':
                keyboard_repl = telebot.types.ReplyKeyboardMarkup()
                keyboard_repl.add('Формула', 'Единица измерения', 'Формулировка', 'Все сведения', 'По номеру понятия', 'Список понятий')
                
                self.bot.send_message(message.from_user.id, 'Привет! Здесь ты можешь получить формулу/формулировку' +
                    'закона/единицу измерения по своему запросу!\n' +
                    'Пропиши /help для получения инструкции по составлению корректного запроса.', reply_markup=keyboard_repl)
                
            elif message.text == '/help':
                keyboard_inl = telebot.types.InlineKeyboardMarkup()
                keyboard_inl.add((telebot.types.InlineKeyboardButton('Написать разработчице', url = 'https://t.me/failure_l')),
                             (telebot.types.InlineKeyboardButton('Список понятий', callback_data="/send")))
                
                
                self.bot.send_message(message.from_user.id, 'Для получения конкретного параметра укажите его на\
        клавиатуре, а затем введите название интересующего Вас понятия. Также, можно увидеть полный список понятий ниже\
        и указав "По номеру понятия" получить информацию о нем.', reply_markup=keyboard_inl)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_q(call):
            if call.data == '/send':
                k = 1
                arr = []
                for name in self.info:
                    name = str(name[0])
                    arr.append('{}. {}'.format(k, name))
                    k += 1
            text = '\n'.join(arr)
            self.bot.send_message(call.from_user.id, text)

        @self.bot.message_handler(content_types=['text'])
        def check(message):
            
            if 'Формула' in message.text and message.text.isdigit() == False:
                msg1 = self.bot.send_message(
                          message.from_user.id, 'Введите название понятия.')
                self.bot.register_next_step_handler(msg1, formula)
                
            elif 'Формулировка' in message.text and message.text.isdigit() == False:
                msg2 = self.bot.send_message(
                              message.from_user.id, 'Введите название понятия.')
                self.bot.register_next_step_handler(msg2, formulation)
                
            elif 'Единица измерения' in message.text and message.text.isdigit() == False:
                msg3 = self.bot.send_message(
                          message.from_user.id, 'Введите название понятия.')
                self.bot.register_next_step_handler(msg3, unit)
                
            elif 'Все сведения' in message.text and message.text.isdigit() == False:
                msg4 = self.bot.send_message(
                          message.from_user.id, 'Введите название понятия.')
                self.bot.register_next_step_handler(msg4, all_concepts)
            elif 'По номеру понятия' in message.text:
                msg5 = self.bot.send_message(
                          message.from_user.id, 'Введите цифру, под которой находится понятие.')
                self.bot.register_next_step_handler(msg5, by_digit)
            elif 'Список понятий' in message.text and message.text.isdigit() == False:
                arr_conc(message)
            else:
                self.bot.send_message(
                          message.from_user.id, 'Не был введен запрос.')

        def formula(message):
            request = message.text
            request_1 = message
            wr_1 = 0
            for msg in self.info:
                msg = str(msg[0])
                if self.similarity(msg, request) > 0.8:
                    self.cur.execute('''SELECT formula FROM formulas WHERE name=?''', [msg])
                    formulas = self.cur.fetchone()
                      
                    photo = open('E:/python/project/tg_bot/{}.png'.format(formulas[0]), 'rb')
                    self.bot.send_photo(message.from_user.id, photo)
                    file_id = 'form'
                    self.bot.send_photo(message.from_user.id, file_id)
                    wr_1 += 1
            if wr_1 == 0 and message.text not in self.conc and message.text not in self.comma:
                wrong = self.bot.send_message(
                    message.from_user.id, 'Формул не найдено или Ваш запрос некорректный, повторите ввод(по тому же параметру).')
                self.bot.register_next_step_handler(wrong, formula)
            elif request in self.conc:
                
                check(request_1)
            elif request in self.comma:
                start_help_command(message)
                

        def formulation(message):
            request = message.text
            wr_2 = 0
            for msg in self.info:
                msg = str(msg[0])
                if self.similarity(msg, request) > 0.8:
                    self.cur.execute('''SELECT formulation FROM formulas WHERE name=?''', [msg])
                    formulation_1 = self.cur.fetchone()
                    self.bot.send_message(
                        message.from_user.id, '- Формулировка: {}'.format(formulation_1[0]))
                    wr_2 += 1
            if wr_2 == 0 and message.text not in self.conc and message.text not in self.comma:
                wrong = self.bot.send_message(
                    message.from_user.id, 'Формул не найдено или Ваш запрос некорректный, повторите ввод(по тому же параметру).')
                self.bot.register_next_step_handler(wrong, formulation)
            elif message.text in self.conc:
                check(message)
            elif message.text in self.comma:
                start_help_command(message)
            

        def unit(message):
            request = message.text
            wr_3 = 0
            for msg in self.info:
                msg = str(msg[0])
                if self.similarity(msg, request) > 0.8:
                    self.cur.execute('''SELECT unit FROM formulas WHERE name=?''', [msg])
                    unit_1 = self.cur.fetchone()
                    self.bot.send_message(
                        message.from_user.id, '- Единица измерения: {}'.format(unit_1[0]))
                    wr_3 += 1
            if wr_3 == 0 and message.text not in self.conc and message.text not in self.comma:
                wrong = self.bot.send_message(
                    message.from_user.id, 'Формул не найдено или Ваш запрос некорректный, повторите ввод(по тому же параметру).')
                self.bot.register_next_step_handler(wrong, unit)
            elif message.text in self.conc:
                check(message)
            elif message.text in self.comma:
                start_help_command(message)

        def all_concepts(message):
            request = message.text
            wr_4 = 0
            for msg in self.info:
                msg = str(msg[0])
              
                if self.similarity(msg, request) > 0.8:
                    self.cur.execute('''SELECT * FROM formulas WHERE name=?''', [msg])
                    all_info = self.cur.fetchall()
                    form = 'Держи: \n- Понятие: {} \n - Формулировка: {} \n - Единица измерения: {}'.format(all_info[0][1],all_info[0][2],
                                                                                                                        all_info[0][3])

                    photo = open('E:/python/project/tg_bot/{}.png'.format(all_info[0][4]), 'rb')
                    self.bot.send_photo(message.from_user.id, photo, form)
                    wr_4 += 1
            if wr_4 == 0 and message.text not in self.conc and message.text not in self.comma:
                wrong = self.bot.send_message(
                    message.from_user.id, 'Формул не найдено или Ваш запрос некорректный, повторите ввод(по тому же параметру).')
                self.bot.register_next_step_handler(wrong, all_concepts)
            elif message.text in self.conc:
                check(message)
            elif message.text in self.comma:
                start_help_command(message)

        def by_digit(message):
            wr_5 = 0
            if message.text.isdigit() == True:
                for n in self.num:
                    n_str = str(n[0])
                    if message.text == n_str:
                        self.cur.execute('''SELECT * FROM formulas WHERE id=?''', n)
                        all_info_1 = self.cur.fetchall()

                        form_1 = 'Держи: \n- Понятие: {} \n - Формулировка: {} \n - Единица измерения: {}'.format(all_info_1[0][1],all_info_1[0][2],
                                                                                                                              all_info_1[0][3])

                        photo_1 = open('E:/python/project/tg_bot/{}.png'.format(all_info_1[0][4]), 'rb')
                        self.bot.send_photo(message.from_user.id, photo_1, form_1)
                        wr_5 += 1
            if (wr_5 == 0 or message.text.isdigit() == False) and message.text not in self.conc  and message.text not in self.comma:
                wrong = self.bot.send_message(
                message.from_user.id, 'Формул не найдено или Ваш запрос некорректный, повторите ввод(по тому же параметру).')
                self.bot.register_next_step_handler(wrong, by_digit)
            elif message.text in self.conc:
                check(message)
            elif message.text in self.comma:
                start_help_command(message)

        def arr_conc(message):
            k = 1
            arr = []
            for name in self.info:
                name = str(name[0])
                arr.append('{}. {}'.format(k, name))
                k += 1
            text = '\n'.join(arr)
            self.bot.send_message(message.from_user.id, text)
            
                
    def start(self):
        self.database()
        self.router()
        self.bot.polling(none_stop=True)

        
app = App()
app.start()


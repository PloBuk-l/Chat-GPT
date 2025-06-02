import sys
import os
import pickle  # Импортируем библиотеку для сериализации
from datetime import datetime
from openai import OpenAI
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QGraphicsDropShadowEffect, QLineEdit, QScrollArea, QMessageBox, QComboBox,
    QListWidget, QSplitter
)
from PyQt5.QtGui import QFont, QIcon, QColor, QTextCursor, QTextDocument
from PyQt5.QtCore import Qt, QPropertyAnimation, QThread, pyqtSignal, QTimer, QRect
import markdown
from markdown.extensions import codehilite, fenced_code

# Путь для хранения API ключа
API_KEY_FILE = "api_key.txt" 
SESSIONS_FILE = "sessions.pkl"  # Файл для хранения сессий

# Функция для загрузки API ключа из файла
def load_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            return f.read().strip()
    return ""

# Функция для сохранения API ключа в файл
def save_api_key_to_file(key):
    with open(API_KEY_FILE, "w") as f:
        f.write(key)

# Функция для сохранения сессий в файл
def save_sessions_to_file(sessions):
    with open(SESSIONS_FILE, "wb") as f:
        pickle.dump(sessions, f)

# Функция для загрузки сессий из файла
def load_sessions_from_file():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "rb") as f:
            return pickle.load(f)
    return []

class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ввод API ключа")
        self.resize(400, 250)
        self.setStyleSheet(""" 
            QWidget {
                background-color: #121212;
                color: #FFFFFF;
            }
            QLineEdit {
                background-color: #1E1E1E;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 8px;
                color: #FFFFFF;
                font-family: Helvetica;
                font-size: 14px;
            }
            QLabel {
                font-family: Helvetica;
                font-size: 16px;
                margin-bottom: 10px;
            }
            QPushButton {
                background-color: #3A86FF;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 16px;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)  # Выровнить всё по центру
        
        label = QLabel("Введите ваш API ключ")
        label.setAlignment(Qt.AlignCenter)  # Выровнить текст по центру
        layout.addWidget(label)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API ключ")
        self.api_key_input.setFixedWidth(200)  # Установить ширину поля ввода
        self.api_key_input.setAlignment(Qt.AlignCenter)  # Выровнить текст внутри по центру
        layout.addWidget(self.api_key_input, alignment=Qt.AlignHCenter)

        self.save_button = GlowingButton("Сохранить")
        self.save_button.setFixedWidth(100)  # Узкая ширина кнопки
        self.save_button.clicked.connect(self.save_api_key)
        layout.addWidget(self.save_button, alignment=Qt.AlignHCenter)

        link_label = QLabel('<br><b><a href="https://telegra.ph/NexoraAI-05-29">Инструкция</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setStyleSheet("QLabel { font-family: Helvetica; font-size: 16px; color: #3A86FF; }")
        layout.addWidget(link_label, alignment=Qt.AlignHCenter)

        link_label1 = QLabel('<b><a>При использовании</a><br><a>вы соглашаетесь с</a><br><a href="https://telegra.ph/NexoraAI-05-29-2">пользовательским соглашением</a>')
        link_label1.setOpenExternalLinks(True)
        link_label1.setAlignment(Qt.AlignCenter)
        link_label1.setStyleSheet("QLabel { font-family: Helvetica; font-size: 16px; color: #3A86FF; }")
        layout.addWidget(link_label1, alignment=Qt.AlignHCenter)

        self.setLayout(layout)
        
        # Если есть сохранённый ключ — подставляем
        saved_key = load_api_key()
        if saved_key:
            self.api_key_input.setText(saved_key)
    
    def save_api_key(self):
        api = self.api_key_input.text().strip()
        if not api:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите API ключ.")
            return
        client.api_key = api
        save_api_key_to_file(api)
        second_window.close()  # Закрываем окно ввода ключа
        window.show()  # Показываем основное окно

# Инициализация клиента с загруженным API ключом
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=load_api_key(),
)

class ApiWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, user_text, model_name):
        super().__init__()
        self.user_text = user_text
        self.model_name = model_name  # Сохраняем модель

    def run(self):
        try:
            # Prepare the messages for the API request
            completion = client.chat.completions.create(
                model=self.model_name,  # Используем модель
                messages=self.user_text,  # Используем полную историю сообщений
            )
            response = completion.choices[0].message.content
            self.finished.emit(response)  # Передаём ответ обратно в основной поток
        except Exception as e:
            self.error.emit(str(e))  # Передача ошибок



class GlowingButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(0)
        self.shadow_effect.setOffset(0, 0)
        self.shadow_effect.setColor(Qt.cyan)
        self.setGraphicsEffect(self.shadow_effect)

        # Создаём анимацию свечения для кнопки
        self.animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(25)

    def enterEvent(self, event):
        # При наведении на кнопку активируется эффект свечения
        self.animation.setDirection(QPropertyAnimation.Forward)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        # При уходе курсора эффект свечения исчезает
        self.animation.setDirection(QPropertyAnimation.Backward)
        self.animation.start()
        super().leaveEvent(event)

class CopyButton(QPushButton):
    def __init__(self, text="Копировать"):
        super().__init__(text)
        # Создаем эффект свечения
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setColor(Qt.cyan)
        self.shadow_effect.setBlurRadius(0)
        self.shadow_effect.setOffset(0)
        self.setGraphicsEffect(self.shadow_effect)

        # Создаем анимацию свечения
        self.animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(20)

    def enterEvent(self, event):
        # При наведении кнопки эффект свечения увеличивается
        self.animation.setDirection(QPropertyAnimation.Forward)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        # При уходе эффект свечения исчезает
        self.animation.setDirection(QPropertyAnimation.Backward)
        self.animation.start()
        super().leaveEvent(event)

class NexoraAI_Interface(QWidget):
    def __init__(self):
        super().__init__()
        self.model_map = {
            "Deepseek-R1-free": "deepseek/deepseek-r1:free",
            "Liama-4-scout-free": "meta-llama/llama-4-scout:free",
            "Gemini-2.0-flash-exp-free": "google/gemini-2.0-flash-exp:free"
        }
        self.selected_model = self.model_map["Deepseek-R1-free"]
        self.setWindowTitle("NexoraAI Client")
        self.resize(1100, 650)  # Установлен размер окна
        self.chat_history = []  # (роль, текст, время)
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_dots)
        self.loading_index = 0
        self.loading_chars = ['⠁','⠂','⠄','⡀','⢀','⠠','⠐','⠈']
        self.chat_sessions = load_sessions_from_file()  # Загружаем сессии из файла
        self.current_session_index = -1  # индекс текущей сессии
        self.dark_mode = True  # Start in dark mode
        self.setup_ui()
        self.add_new_session("Новый чат")
        self.chat_sessions = load_sessions_from_file()  # Загружаем сессии из файла
        self.load_sessions_into_list()


    def setup_ui(self):
        main_layout = QHBoxLayout()  # Horizontal layout for chat history and chat area

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(280)

        buttons_top_layout = QHBoxLayout()
        buttons_top_layout.setSpacing(10)

        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.on_session_selected)
        left_layout.addWidget(self.session_list, stretch=1)

        self.delete_session_button = GlowingButton("Удалить чат")
        self.delete_session_button.clicked.connect(self.delete_current_session)
        buttons_top_layout.addWidget(self.delete_session_button)

        self.delete_sessions_button = GlowingButton("Удалить всё")
        self.delete_sessions_button.clicked.connect(self.delete_all_sessions)
        buttons_top_layout.addWidget(self.delete_sessions_button)

        left_layout.addLayout(buttons_top_layout)

        self.new_session_button_left = GlowingButton("Новый чат")
        self.new_session_button_left.clicked.connect(self.add_new_session)
        self.new_session_button_left.setFixedHeight(40)
        left_layout.addWidget(self.new_session_button_left)


        main_layout.addWidget(left_panel)

        # --- Right part of the interface ---
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        self.chat_layout = QVBoxLayout()
        right_layout.addLayout(self.chat_layout)

        # Timer for bot response
        self.bot_response_timer = QTimer()
        self.bot_response_timer.timeout.connect(self.update_bot_timer)

        # Combo box for model selection
        self.select_list = QComboBox()
        self.select_list.addItems(["Deepseek-R1-free", "Liama-4-scout-free", "Gemini-2.0-flash-exp-free"])
        self.select_list.currentIndexChanged.connect(self.on_select_change)
        self.select_list.currentIndexChanged.connect(self.on_model_change)

        # Create a horizontal layout for the combo box and clear chat button
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.select_list)

        # Clear chat button
        self.clear_button = GlowingButton("Очистить чат")
        self.clear_button.clicked.connect(self.clear_chat)
        top_layout.addStretch()  # This will push the clear chat button to the right
        top_layout.addWidget(self.clear_button)  # Add the button after the stretch

        self.chat_layout.addLayout(top_layout)

        title_label = QLabel("NexoraAI Client")
        title_font = QFont("Helvetica", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        self.chat_layout.addWidget(title_label)

        # Scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setFixedSize(800, 450)  # Set size for message area
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 4px solid #555;
                border-radius: 8px;
                background-color: #1E1E1E;
                color: #191970;
            }
        """)
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_container.setLayout(self.messages_layout)
        self.scroll_area.setWidget(self.messages_container)
        self.chat_layout.addWidget(self.scroll_area)

        # Input field and send button
        input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setFixedHeight(45)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border: 2px solid #555;
                border-radius: 10px;
                padding: 8px;
                font-family: Helvetica;
                font-size: 16px;
            }
            QTextEdit:hover {
                border-color: #888;
            }
            QTextEdit:focus {
                border-color: #3A86FF;
                outline: none;
            }
        """)
        self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        input_layout.addWidget(self.input_field)

        self.send_button = GlowingButton("Отправить")
        self.send_button.setFixedSize(160, 45)  # Set button size
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3A86FF;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 16px;
                font-family: Helvetica;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.send_button.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_button)
        self.chat_layout.addLayout(input_layout)

        # Original keyPressEvent
        self.original_keyPressEvent = self.input_field.keyPressEvent
        self.input_field.keyPressEvent = self.custom_keyPressEvent

        main_layout.addWidget(right_widget)
        self.setLayout(main_layout)

        self.apply_theme()
        self.input_field.setFocus()

    def delete_current_session(self):
        index = self.current_session_index
        if index >= 0 and index < len(self.chat_sessions):
            # Удаляем выбранную сессию
            del self.chat_sessions[index]
            # Обновляем список сессий в интерфейсе
            self.load_sessions_into_list()
            # Если остались сессии, выбираем первую или следующую
            if self.chat_sessions:
                self.current_session_index = 0
                self.chat_history = self.chat_sessions[0]
                self.session_list.setCurrentRow(0)
            else:
                # Если сессий больше нет, создаем новую
                self.add_new_session(f"Чат 1")
            self.update_chat_display()

    def on_select_change(self, index):
        # при изменении выбранного элемента, очищаем чат
        self.clear_chat()

    def toggle_theme(self, state):
        self.dark_mode = state  # тут важно
        self.apply_theme()

    def update_loading_dots(self):
        self.loading_dots_count = (getattr(self, 'loading_dots_count', 0) + 1) % 4
        dots = '.' * self.loading_dots_count
        if self.chat_history and self.chat_history[-1][0] == "bot":
            self.chat_history[-1] = ("bot", f"ИИ думает{dots}")
            self.update_chat_display()

    def load_sessions_into_list(self):
        self.session_list.clear()
        for i, session in enumerate(self.chat_sessions):
            display_title = f"Чат {i + 1}"
            self.session_list.addItem(display_title)
        if self.chat_sessions:
            self.current_session_index = 0
            self.chat_history = self.chat_sessions[0]
            self.session_list.setCurrentRow(0)
            self.update_chat_display()
        else:
            self.current_session_index = -1
            self.chat_history = []

    def apply_theme(self):
        if True:
            # Dark theme styles
            self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #FFFFFF;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
                font-family: Helvetica;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3A86FF;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QLabel {
                color: #FFFFFF;
            }
            QScrollArea {
                border: 4px solid #555;
                border-radius: 8px;
                background-color: #1E1E1E;
            }
            QScrollBar:vertical {
                background: #D3D3D3;
                width: 10px;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical {
                background: #3A86FF;
                min-height: 20px;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5A99FF;
            }
            QComboBox {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 10px 4px 8px;
                min-width: 150px;
            }
            QComboBox QAbstractItemView {
                background-color: #1E1E1E;
                color: #FFFFFF;
                selection-background-color: #3A86FF;
                border: 1px solid #555;
                border-radius: 4px;
            }
            """)
            
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    
    def add_new_session(self, title=None):
        # Создаём новую сессию с пустой историей
        self.chat_sessions.append([])
        self.current_session_index = len(self.chat_sessions) - 1
        # Добавляем элемент в список сессий
        display_title = title or f"Чат {self.current_session_index + 1}"
        self.session_list.addItem(display_title)
        self.session_list.setCurrentRow(self.current_session_index)
        self.chat_history = self.chat_sessions[self.current_session_index]
        self.update_chat_display()
    
    def delete_all_sessions(self):
        self.chat_sessions.clear()
        self.current_session_index = -1
        self.chat_history.clear()
        self.session_list.clear()
        self.update_chat_display()
        save_sessions_to_file(self.chat_sessions)  # Записать пустой список в файл

    def on_session_selected(self, item):
        index = self.session_list.currentRow()
        if index < 0 or index >= len(self.chat_sessions):
            return
        self.current_session_index = index
        self.chat_history = self.chat_sessions[index]
        self.update_chat_display()

    def clear_chat(self):
        if self.current_session_index >= 0:
            self.chat_sessions[self.current_session_index].clear()
            self.chat_history = self.chat_sessions[self.current_session_index]
        else:
            self.chat_history.clear()
        self.update_chat_display()

    def closeEvent(self, event):
        # Сохраняем сессии перед закрытием приложения
        save_sessions_to_file(self.chat_sessions)
        event.accept()  # Принять событие закрытия


    def on_model_change(self, index):
        item_text = self.select_list.itemText(index)
        self.selected_model = self.model_map.get(item_text, "deepseek/deepseek-r1:free")
    
    def clear_chat(self):
        # Очистка истории сообщений чата
        self.chat_history.clear()
        self.update_chat_display()

    def custom_keyPressEvent(self, event):
        # Обработка нажатий клавиш в текстовом поле
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if not (event.modifiers() & Qt.ShiftModifier):
                self.handle_send()
                event.accept()
            else:
                self.original_keyPressEvent(event)
        else:
            self.original_keyPressEvent(event)

    def update_chat_display(self):
        for i in reversed(range(self.messages_layout.count())):
            widget = self.messages_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        for item in self.chat_history:
            if item[0] == "user":
                if len(item) == 3:
                    role, text, time_str = item
                else:
                    role, text = item
                    time_str = ""
                message_widget = QWidget()
                h_layout = QHBoxLayout()
                message_widget.setLayout(h_layout)
                text_label = QLabel()
                text_label.setWordWrap(True)
                formatted_text = '\n'.join([text[i:i + 75] for i in range(0, len(text), 75)])
                text_label.setText(f'<b>Вы [{time_str}]:</b> {formatted_text}')
                text_label.setStyleSheet("border-radius:8px; padding:8px; background-color:#222; color: #FFFFFF;")
                h_layout.addWidget(text_label)
            elif item[0] == "bot":
                if len(item) == 3:
                    role, text, time_str = item
                else:
                    role, text = item[0], item[1]
                    time_str = ""
                message_widget = QWidget()
                h_layout = QHBoxLayout()
                message_widget.setLayout(h_layout)
                text_label = QLabel()
                text_label.setWordWrap(True)
                html = markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
                text_label.setText(f'<b>NexoraAI [{time_str}]:</b><br>{html}')
                text_label.setTextFormat(Qt.RichText)
                text_label.setStyleSheet("border-radius:8px; padding:8px; background-color:#333; color: #FFFFFF;")
                copy_button = CopyButton("Копировать")
                copy_button.setFixedSize(100, 30)
                copy_button.clicked.connect(lambda checked, t=text: self.copy_text(t))
                h_layout.addWidget(text_label)
                h_layout.addWidget(copy_button)
                h_layout.setStretch(0, 1)
                h_layout.setStretch(1, 0)
            else:
                continue
            self.messages_layout.addWidget(message_widget)
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def copy_text(self, text):
        QApplication.clipboard().setText(text)

    def handle_send(self):
        user_text = self.input_field.toPlainText().strip()
        if not user_text:
            return
        if not client.api_key:
            QMessageBox.warning(self, "Ошибка", "API ключ не установлен. Пожалуйста, введите ключ.")
            return
        timestamp = datetime.now().strftime("%H:%M:%S")

        if self.current_session_index == -1:
            self.add_new_session()

        # Добавляем новое сообщение пользователя
        self.chat_sessions[self.current_session_index].append(("user", user_text, timestamp))
        self.chat_sessions[self.current_session_index].append(("bot", "ИИ думает..."))
        self.chat_history = self.chat_sessions[self.current_session_index]

        # Извлечь первые три слова пользовательского запроса для названия чата
        words = user_text.split()
        new_title = " ".join(words[:3]) if len(words) >= 3 else " ".join(words)
        if not new_title.strip():
            new_title = f"Чат {self.current_session_index + 1}"

        # Обновить название сессии в QListWidget
        self.session_list.item(self.current_session_index).setText(new_title)

        self.update_chat_display()
        self.input_field.clear()
        self.send_button.setEnabled(False)
        self.loading_dots_count = 0
        self.loading_timer.start(300)
        self.bot_response_timer.start(1000)

        messages = []
        # Формируем сообщения для API
        for role, text, *rest in self.chat_history[:-2]:
            if role == "user":
                messages.append({
                    "role": "user",
                    "content": f"Это старое сообщение пользователя для контекста, не отвечай на него: {text}"
                })
            elif role == "bot":
                messages.append({
                    "role": "bot",
                    "content": f"Это старое сообщение бота для контекста, не отвечай на него: {text}"
                })

        messages.append({
            "role": "user",
            "content": user_text
        })

        self.worker = ApiWorker(messages, self.selected_model)
        self.worker.finished.connect(self.on_response)
        self.worker.start()
        self.input_field.setFocus()




    def update_bot_timer(self):
        if self.chat_history and self.chat_history[-1][0] == "bot":
            self.chat_history[-1] = ("bot", "ИИ думает...")
            self.update_chat_display()

    def on_response(self, response):
        self.loading_timer.stop()
        self.bot_response_timer.stop()
        html_content = markdown.markdown(response)
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.chat_history and self.chat_history[-1][0] == "bot":
            self.chat_history[-1] = ("bot", html_content, timestamp)
        else:
            self.chat_history.append(("bot", html_content, timestamp))
        # Обновляем сессию
        if self.current_session_index >= 0:
            self.chat_sessions[self.current_session_index] = self.chat_history
        self.update_chat_display()
        self.send_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NexoraAI_Interface()
    window.setWindowIcon(QIcon('icon.ico'))
    window.hide()
    second_window = SecondWindow()
    second_window.setWindowIcon(QIcon('icon.ico'))
    second_window.show()
    sys.exit(app.exec_())
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
SETTINGS_FILE = "settings.pkl"  # Файл для хранения настроек

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

# Функция для сохранения настроек
def save_settings(settings):
    with open(SETTINGS_FILE, "wb") as f:
        pickle.dump(settings, f)

# Функция для загрузки настроек
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "rb") as f:
                return pickle.load(f)
        except:
            return {"dark_mode": True}
    return {"dark_mode": True}

class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Загружаем настройки темы
        self.settings = load_settings()
        self.dark_mode = self.settings.get("dark_mode", True)
        
        self.setWindowTitle("NexoraAI - API ключ")
        self.resize(480, 320)
        self.apply_theme()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок
        title_label = QLabel("Добро пожаловать в NexoraAI")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Введите ваш API ключ для начала работы")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(subtitle_label)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-your-api-key-here...")
        self.api_key_input.setFixedWidth(320)
        self.api_key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.api_key_input, alignment=Qt.AlignHCenter)

        # Кнопка показать/скрыть пароль
        show_hide_layout = QHBoxLayout()
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedSize(180, 40)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        show_hide_layout.addStretch()
        show_hide_layout.addWidget(self.show_password_btn)
        show_hide_layout.addStretch()
        layout.addLayout(show_hide_layout)

        self.save_button = GlowingButton("Сохранить и продолжить")
        self.save_button.setFixedWidth(250)
        self.save_button.clicked.connect(self.save_api_key)
        layout.addWidget(self.save_button, alignment=Qt.AlignHCenter)

        # Ссылки
        links_layout = QVBoxLayout()
        links_layout.setSpacing(8)
        
        link_label = QLabel('<a href="https://telegra.ph/NexoraAI-05-29" style="text-decoration: none;">📖 Инструкция по получению API ключа</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(Qt.AlignCenter)
        links_layout.addWidget(link_label)

        agreement_label = QLabel('<a href="https://telegra.ph/NexoraAI-05-29-2" style="text-decoration: none;">📋 Пользовательское соглашение</a>')
        agreement_label.setOpenExternalLinks(True)
        agreement_label.setAlignment(Qt.AlignCenter)
        links_layout.addWidget(agreement_label)
        
        layout.addLayout(links_layout)

        self.setLayout(layout)
        
        # Если есть сохранённый ключ — подставляем
        saved_key = load_api_key()
        if saved_key:
            self.api_key_input.setText(saved_key)
    
    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet(""" 
                QWidget {
                    background: #0F0F23;
                    color: #FFFFFF;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QLineEdit {
                    background: rgba(255, 255, 255, 0.05);
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 16px 20px;
                    color: #FFFFFF;
                    font-size: 14px;
                    font-weight: 400;
                }
                QLineEdit:focus {
                    border: 2px solid #6366F1;
                    background: rgba(255, 255, 255, 0.08);
                }
                QLineEdit:hover {
                    background: rgba(255, 255, 255, 0.07);
                }
                QLabel {
                    font-size: 16px;
                    font-weight: 500;
                    margin-bottom: 8px;
                    color: #E5E7EB;
                }
                QPushButton {
                    background: #6366F1;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #5B5BD6;
                }
                QPushButton:pressed {
                    background: #4F46E5;
                }
            """)
        else:
            self.setStyleSheet(""" 
                QWidget {
                    background: #FAFAFA;
                    color: #1F2937;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QLineEdit {
                    background: rgba(255, 255, 255, 0.9);
                    border: 2px solid rgba(229, 231, 235, 0.8);
                    border-radius: 12px;
                    padding: 16px 20px;
                    color: #1F2937;
                    font-size: 14px;
                    font-weight: 400;
                }
                QLineEdit:focus {
                    border: 2px solid #FBBF24;
                    background: rgba(255, 255, 255, 1);
                }
                QLineEdit:hover {
                    background: rgba(255, 255, 255, 1);
                }
                QLabel {
                    font-size: 16px;
                    font-weight: 500;
                    margin-bottom: 8px;
                    color: #374151;
                }
                QPushButton {
                    background: #FBBF24;
                    color: #1F2937;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #F59E0B;
                }
                QPushButton:pressed {
                    background: #D97706;
                }
            """)
    
    def toggle_password_visibility(self):
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("👁")
    
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
        self.setStyleSheet("""
            QPushButton {
                background: #6366F1;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #5B5BD6;
            }
            QPushButton:pressed {
                background: #4F46E5;
            }
        """)

class CopyButton(QPushButton):
    def __init__(self, text="Копировать", dark_mode=True):
        super().__init__(text)
        self.dark_mode = dark_mode
        self.update_theme()
        
    def update_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(139, 92, 246, 0.2);
                    border: 1px solid rgba(139, 92, 246, 0.3);
                    border-radius: 8px;
                    font-size: 12px;
                    color: #FFFFFF;
                    padding: 8px 16px;
                    text-align: center;
                    min-width: 80px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    background: rgba(139, 92, 246, 0.3);
                    color: #FFFFFF;
                }
                QPushButton:pressed {
                    background: rgba(139, 92, 246, 0.4);
                    color: #FFFFFF;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(251, 191, 36, 0.2);
                    border: 1px solid rgba(251, 191, 36, 0.4);
                    border-radius: 8px;
                    font-size: 12px;
                    color: #1F2937;
                    padding: 8px 16px;
                    text-align: center;
                    min-width: 80px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    background: rgba(251, 191, 36, 0.3);
                    color: #1F2937;
                }
                QPushButton:pressed {
                    background: rgba(251, 191, 36, 0.4);
                    color: #1F2937;
                }
            """)

class ThemeToggle(QWidget):
    theme_changed = pyqtSignal(bool)  # True for dark, False for light
    
    def __init__(self, is_dark=True):
        super().__init__()
        self.is_dark = is_dark
        self.setFixedSize(60, 30)
        self.setStyleSheet("background: transparent;")
        
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QBrush, QPen
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Рисуем фон переключателя
        if self.is_dark:
            bg_color = QColor(99, 102, 241)  # Синий для темной темы
        else:
            bg_color = QColor(251, 191, 36)  # Желтый для светлой темы
            
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(bg_color))
        painter.drawRoundedRect(0, 0, 60, 30, 15, 15)
        
        # Рисуем переключатель
        circle_color = QColor(255, 255, 255)
        painter.setBrush(QBrush(circle_color))
        painter.setPen(QPen(circle_color))
        
        if self.is_dark:
            painter.drawEllipse(32, 3, 24, 24)  # Справа для темной темы
        else:
            painter.drawEllipse(4, 3, 24, 24)   # Слева для светлой темы
    
    def mousePressEvent(self, event):
        self.is_dark = not self.is_dark
        self.theme_changed.emit(self.is_dark)
        self.update()  # Перерисовываем виджет

class NexoraAI_Interface(QWidget):
    def __init__(self):
        super().__init__()
        self.model_map = {
            "Deepseek-R1": "deepseek/deepseek-r1:free",
            "Llama-4": "meta-llama/llama-4-scout:free",
            "Gemini-2.0": "google/gemini-2.0-flash-exp:free"
        }
        self.selected_model = self.model_map["Deepseek-R1"]
        self.setWindowTitle("NexoraAI Client")
        self.resize(1200, 750)
        self.chat_history = []  # (роль, текст, время)
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_dots)
        self.loading_index = 0
        self.loading_chars = ['⠁','⠂','⠄','⡀','⢀','⠠','⠐','⠈']
        self.chat_sessions = load_sessions_from_file()
        self.current_session_index = -1
        
        # Загружаем настройки темы
        self.settings = load_settings()
        self.dark_mode = self.settings.get("dark_mode", True)
        
        self.setup_ui()
        self.add_new_session("Новый чат")
        self.chat_sessions = load_sessions_from_file()
        self.load_sessions_into_list()

    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Левая панель
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(16)
        left_layout.setContentsMargins(24, 24, 24, 24)
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(320)

        # Заголовок боковой панели
        self.sidebar_title = QLabel("Чаты")
        self.sidebar_title.setStyleSheet("""
            font-size: 18px; 
            font-weight: 700; 
            color: #FFFFFF; 
            margin-bottom: 16px;
        """)
        left_layout.addWidget(self.sidebar_title)

        # Кнопка нового чата
        self.new_session_button_left = GlowingButton("+ Новый чат")
        self.new_session_button_left.clicked.connect(self.add_new_session)
        self.new_session_button_left.setFixedHeight(48)
        left_layout.addWidget(self.new_session_button_left)

        # Список сессий
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.on_session_selected)
        left_layout.addWidget(self.session_list, stretch=1)

        # Кнопки управления
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(8)

        self.delete_session_button = GlowingButton("🗑 Удалить чат")
        self.delete_session_button.clicked.connect(self.delete_current_session)
        buttons_layout.addWidget(self.delete_session_button)

        self.delete_sessions_button = GlowingButton("🗑 Очистить всё")
        self.delete_sessions_button.clicked.connect(self.delete_all_sessions)
        buttons_layout.addWidget(self.delete_sessions_button)

        left_layout.addLayout(buttons_layout)

        main_layout.addWidget(left_panel)

        # Правая панель
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(24)
        right_layout.setContentsMargins(32, 32, 32, 32)
        right_widget.setLayout(right_layout)

        # Верхняя панель
        top_layout = QHBoxLayout()
        top_layout.setSpacing(16)

        # Заголовок
        title_label = QLabel("NexoraAI")
        title_label.setStyleSheet("""
            font-size: 28px; 
            font-weight: 800; 
            color: #6366F1;
        """)
        top_layout.addWidget(title_label)

        # Переключатель темы
        theme_container = QWidget()
        theme_layout = QHBoxLayout()
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(8)
        
        self.theme_label = QLabel("🌙" if self.dark_mode else "☀️")
        self.theme_label.setStyleSheet("font-size: 16px; color: #9CA3AF;")
        theme_layout.addWidget(self.theme_label)
        
        self.theme_toggle = ThemeToggle(self.dark_mode)
        self.theme_toggle.theme_changed.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_toggle)
        
        theme_container.setLayout(theme_layout)
        top_layout.addWidget(theme_container)

        top_layout.addStretch()

        # Выбор модели
        model_label = QLabel("🤖 Модель:")
        model_label.setStyleSheet("font-size: 14px; color: #9CA3AF; font-weight: 500;")
        top_layout.addWidget(model_label)

        self.select_list = QComboBox()
        self.select_list.addItems(["Deepseek-R1", "Llama-4", "Gemini-2.0"])
        self.select_list.currentIndexChanged.connect(self.on_select_change)
        self.select_list.currentIndexChanged.connect(self.on_model_change)
        top_layout.addWidget(self.select_list)

        # Кнопка очистки чата
        self.clear_button = GlowingButton("🧹 Очистить")
        self.clear_button.clicked.connect(self.clear_chat)
        top_layout.addWidget(self.clear_button)

        right_layout.addLayout(top_layout)

        # Область сообщений
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(16)
        self.messages_layout.setContentsMargins(16, 16, 16, 16)
        self.messages_container.setLayout(self.messages_layout)
        self.scroll_area.setWidget(self.messages_container)
        right_layout.addWidget(self.scroll_area, stretch=1)

        # Поле ввода
        input_container = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_container.setLayout(input_layout)

        self.input_field = QTextEdit()
        self.input_field.setFixedHeight(60)
        self.input_field.setPlaceholderText("Введите ваше сообщение...")
        self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        input_layout.addWidget(self.input_field)

        self.send_button = GlowingButton("➤")
        self.send_button.setFixedSize(60, 60)
        self.send_button.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_button)

        right_layout.addWidget(input_container)

        # Оригинальный keyPressEvent
        self.original_keyPressEvent = self.input_field.keyPressEvent
        self.input_field.keyPressEvent = self.custom_keyPressEvent

        main_layout.addWidget(right_widget)
        self.setLayout(main_layout)

        self.apply_theme()
        self.input_field.setFocus()

    def apply_theme(self):
        if self.dark_mode:
            # Темная тема
            self.setStyleSheet("""
                QWidget {
                    background: #0F0F23;
                    color: #FFFFFF;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                /* Список сессий */
                QListWidget {
                    background: transparent;
                    border: none;
                    outline: none;
                    color: #E5E7EB;
                    font-size: 14px;
                }
                QListWidget::item {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                    border: 1px solid transparent;
                    color: #E5E7EB;
                }
                QListWidget::item:hover {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(99, 102, 241, 0.3);
                    color: #FFFFFF;
                }
                QListWidget::item:selected {
                    background: rgba(99, 102, 241, 0.2);
                    border: 1px solid #6366F1;
                    color: #FFFFFF;
                }
                
                /* Область сообщений */
                QScrollArea {
                    background: rgba(255, 255, 255, 0.02);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 16px;
                }
                
                /* Полоса прокрутки */
                QScrollBar:vertical {
                    background: rgba(255, 255, 255, 0.05);
                    width: 8px;
                    border-radius: 4px;
                    margin: 0;
                }
                QScrollBar::handle:vertical {
                    background: rgba(99, 102, 241, 0.6);
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: rgba(99, 102, 241, 0.8);
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
                
                /* Поле ввода */
                QTextEdit {
                    background: rgba(255, 255, 255, 0.05);
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: 16px;
                    padding: 12px 20px;
                    color: #FFFFFF;
                    font-size: 16px;
                    font-weight: 400;
                }
                QTextEdit:focus {
                    border: 2px solid #6366F1;
                    background: rgba(255, 255, 255, 0.08);
                }
                
                /* Кнопки */
                QPushButton {
                    background: #6366F1;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #5B5BD6;
                }
                QPushButton:pressed {
                    background: #4F46E5;
                }
                
                /* Выпадающий список */
                QComboBox {
                    background: rgba(255, 255, 255, 0.9);
                    color: #1F2937;
                    border: 1px solid rgba(229, 231, 235, 0.8);
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                    min-width: 120px;
                }
                QComboBox:hover {
                    background: rgba(255, 255, 255, 1);
                    border: 1px solid rgba(251, 191, 36, 0.5);
                }
                QComboBox::drop-down {
                    border: none;
                    background: transparent;
                    width: 0px;
                }
                QComboBox::down-arrow {
                    image: none;
                    background: transparent;
                    border: none;
                    width: 0px;
                    height: 0px;
                }
                QComboBox QAbstractItemView {
                    background: #FFFFFF;
                    color: #1F2937;
                    selection-background-color: #FBBF24;
                    border: 1px solid rgba(229, 231, 235, 0.8);
                    border-radius: 8px;
                    padding: 4px;
                }
            """)
            # Обновляем стиль заголовка боковой панели для темной темы
            self.sidebar_title.setStyleSheet("""
                font-size: 18px; 
                font-weight: 700; 
                color: #FFFFFF; 
                margin-bottom: 16px;
            """)
        else:
            # Светлая тема
            self.setStyleSheet("""
                QWidget {
                    background: #FAFAFA;
                    color: #1F2937;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                /* Список сессий */
                QListWidget {
                    background: transparent;
                    border: none;
                    outline: none;
                    color: #374151;
                    font-size: 14px;
                }
                QListWidget::item {
                    background: rgba(255, 255, 255, 0.8);
                    border-radius: 12px;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                    border: 1px solid rgba(229, 231, 235, 0.8);
                    color: #374151;
                }
                QListWidget::item:hover {
                    background: rgba(249, 250, 251, 1);
                    border: 1px solid rgba(251, 191, 36, 0.5);
                    color: #1F2937;
                }
                QListWidget::item:selected {
                    background: rgba(251, 191, 36, 0.1);
                    border: 1px solid #FBBF24;
                    color: #1F2937;
                }
                
                /* Область сообщений */
                QScrollArea {
                    background: rgba(255, 255, 255, 0.7);
                    border: 1px solid rgba(229, 231, 235, 0.8);
                    border-radius: 16px;
                }
                
                /* Полоса прокрутки */
                QScrollBar:vertical {
                    background: rgba(229, 231, 235, 0.3);
                    width: 8px;
                    border-radius: 4px;
                    margin: 0;
                }
                QScrollBar::handle:vertical {
                    background: rgba(251, 191, 36, 0.6);
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: rgba(251, 191, 36, 0.8);
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
                
                /* Поле ввода */
                QTextEdit {
                    background: rgba(255, 255, 255, 0.9);
                    border: 2px solid rgba(229, 231, 235, 0.8);
                    border-radius: 16px;
                    padding: 12px 20px;
                    color: #1F2937;
                    font-size: 16px;
                    font-weight: 400;
                }
                QTextEdit:focus {
                    border: 2px solid #FBBF24;
                    background: rgba(255, 255, 255, 1);
                }
                
                /* Кнопки */
                QPushButton {
                    background: #FBBF24;
                    color: #1F2937;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #F59E0B;
                }
                QPushButton:pressed {
                    background: #D97706;
                }
                
                /* Выпадающий список */
                QComboBox {
                    background: rgba(255, 255, 255, 0.9);
                    color: #1F2937;
                    border: 1px solid rgba(229, 231, 235, 0.8);
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                    min-width: 120px;
                }
                QComboBox:hover {
                    background: rgba(255, 255, 255, 1);
                    border: 1px solid rgba(251, 191, 36, 0.5);
                }
                QComboBox::drop-down {
                    border: none;
                    background: transparent;
                    width: 0px;
                }
                QComboBox::down-arrow {
                    image: none;
                    background: transparent;
                    border: none;
                    width: 0px;
                    height: 0px;
                }
                QComboBox QAbstractItemView {
                    background: #FFFFFF;
                    color: #1F2937;
                    selection-background-color: #FBBF24;
                    border: 1px solid rgba(229, 231, 235, 0.8);
                    border-radius: 8px;
                    padding: 4px;
                }
            """)
            # Обновляем стиль заголовка боковой панели для светлой темы
            self.sidebar_title.setStyleSheet("""
                font-size: 18px; 
                font-weight: 700; 
                color: #1F2937; 
                margin-bottom: 16px;
            """)
        
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def update_chat_display(self):
        # Очищаем предыдущие сообщения
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
                if self.dark_mode:
                    message_widget.setStyleSheet("""
                        background: rgba(99, 102, 241, 0.1);
                        border-radius: 20px;
                        border: 1px solid rgba(99, 102, 241, 0.2);
                        padding: 16px;
                        margin: 8px;
                    """)
                    header_color = "#9CA3AF"
                    text_color = "#FFFFFF"
                else:
                    message_widget.setStyleSheet("""
                        background: rgba(251, 191, 36, 0.1);
                        border-radius: 20px;
                        border: 1px solid rgba(251, 191, 36, 0.3);
                        padding: 16px;
                        margin: 8px;
                    """)
                    header_color = "#6B7280"
                    text_color = "#1F2937"
                
                layout = QVBoxLayout()
                layout.setContentsMargins(20, 16, 20, 16)
                
                header = QLabel(f"👤 Вы • {time_str}")
                header.setStyleSheet(f"font-size: 12px; color: {header_color}; margin-bottom: 8px; font-weight: 500;")
                layout.addWidget(header)
                
                text_label = QLabel(text)
                text_label.setWordWrap(True)
                text_label.setStyleSheet(f"font-size: 15px; color: {text_color}; line-height: 1.5;")
                layout.addWidget(text_label)
                
                message_widget.setLayout(layout)
                self.messages_layout.addWidget(message_widget)
                
            elif item[0] == "bot":
                if len(item) == 3:
                    role, text, time_str = item
                else:
                    role, text = item[0], item[1]
                    time_str = ""
                    
                message_widget = QWidget()
                if self.dark_mode:
                    message_widget.setStyleSheet("""
                        background: rgba(255, 255, 255, 0.03);
                        border-radius: 20px;
                        border: 1px solid rgba(255, 255, 255, 0.08);
                        padding: 16px;
                        margin: 8px;
                    """)
                    header_color = "#9CA3AF"
                    text_color = "#E5E7EB"
                else:
                    message_widget.setStyleSheet("""
                        background: rgba(255, 255, 255, 0.9);
                        border-radius: 20px;
                        border: 1px solid rgba(229, 231, 235, 0.8);
                        padding: 16px;
                        margin: 8px;
                    """)
                    header_color = "#6B7280"
                    text_color = "#374151"
                
                layout = QVBoxLayout()
                layout.setContentsMargins(20, 16, 20, 16)
                
                header_layout = QHBoxLayout()
                header_label = QLabel(f"🤖 NexoraAI • {time_str}")
                header_label.setStyleSheet(f"font-size: 12px; color: {header_color}; font-weight: 500;")
                header_layout.addWidget(header_label)
                
                header_layout.addStretch()
                
                copy_button = CopyButton(dark_mode=self.dark_mode)
                copy_button.clicked.connect(lambda checked, t=text: self.copy_text(t))
                header_layout.addWidget(copy_button)
                
                layout.addLayout(header_layout)
                
                html = markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
                text_label = QLabel(html)
                text_label.setWordWrap(True)
                text_label.setTextFormat(Qt.RichText)
                text_label.setStyleSheet(f"""
                    font-size: 15px; 
                    color: {text_color}; 
                    line-height: 1.6;
                    margin-top: 8px;
                """)
                layout.addWidget(text_label)
                
                message_widget.setLayout(layout)
                self.messages_layout.addWidget(message_widget)
        
        # Прокручиваем вниз
        scrollbar = self.scroll_area.verticalScrollBar()
        QTimer.singleShot(50, lambda: scrollbar.setValue(scrollbar.maximum()))

    def copy_text(self, text):
        QApplication.clipboard().setText(text)

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

    def closeEvent(self, event):
        # Сохраняем сессии перед закрытием приложения
        save_sessions_to_file(self.chat_sessions)
        event.accept()  # Принять событие закрытия

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

        # Таймер для ответа бота
        self.bot_response_timer = QTimer()
        self.bot_response_timer.timeout.connect(self.update_bot_timer)
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
        if hasattr(self, 'bot_response_timer'):
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

    def on_model_change(self, index):
        item_text = self.select_list.itemText(index)
        self.selected_model = self.model_map.get(item_text, "deepseek/deepseek-r1:free")
    
    def clear_chat(self):
        # Очистка истории сообщений чата
        if self.current_session_index >= 0:
            self.chat_sessions[self.current_session_index].clear()
            self.chat_history = self.chat_sessions[self.current_session_index]
        else:
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

    def on_theme_changed(self, is_dark):
        self.dark_mode = is_dark
        self.settings["dark_mode"] = is_dark
        save_settings(self.settings)
        
        # Обновляем иконку рядом с переключателем
        self.theme_label.setText("🌙" if is_dark else "☀️")
        
        # Применяем новую тему
        self.apply_theme()
        # Обновляем отображение сообщений с новыми цветами
        self.update_chat_display()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NexoraAI_Interface()
    window.setWindowIcon(QIcon('icon.ico'))
    window.hide()
    second_window = SecondWindow()
    second_window.setWindowIcon(QIcon('icon.ico'))
    second_window.show()
    sys.exit(app.exec_())
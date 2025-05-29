import sys
import os
from datetime import datetime
from openai import OpenAI
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QGraphicsDropShadowEffect, QLineEdit, QScrollArea, QMessageBox, QCheckBox
)
from PyQt5.QtGui import QFont, QIcon, QColor, QTextCursor, QTextDocument
from PyQt5.QtCore import Qt, QPropertyAnimation, QThread, pyqtSignal, QTimer, QRect
import markdown
from markdown.extensions import codehilite, fenced_code

# Путь для хранения API ключа
API_KEY_FILE = "api_key.txt"

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
                font-family: Arial;
                font-size: 14px;
            }
            QLabel {
                font-family: Arial;
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
        self.api_key_input.setFixedWidth(200)  # Сделать поле шириной 200 пикселей
        self.api_key_input.setAlignment(Qt.AlignCenter)  # Выровнить текст внутри по центру
        layout.addWidget(self.api_key_input, alignment=Qt.AlignHCenter)

        self.save_button = GlowingButton("Сохранить")
        self.save_button.setFixedWidth(100)  # Сделать кнопку шириной 100 пикселей
        self.save_button.clicked.connect(self.save_api_key)
        layout.addWidget(self.save_button, alignment=Qt.AlignHCenter)

        link_label = QLabel('<br><b><a href="https://telegra.ph/Kak-polzovatsya-programmoj-Chat-GPT-05-27">Инструкция</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setStyleSheet("QLabel { font-family: Arial; font-size: 16px; color: #3A86FF; }")
        layout.addWidget(link_label, alignment=Qt.AlignHCenter)

        self.setLayout(layout)
        
        # Если есть сохраненный ключ — подставляем
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
        second_window.close()
        window.show()

# Инициализация клиента с пустым ключом
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=load_api_key(),
)

class ApiWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, user_text):
        super().__init__()
        self.user_text = user_text

    def run(self):
        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=[{"role": "user", "content": self.user_text}],
            )
            response = completion.choices[0].message.content
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))

class GlowingButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(0)
        self.shadow_effect.setOffset(0, 0)
        self.shadow_effect.setColor(Qt.cyan)
        self.setGraphicsEffect(self.shadow_effect)

        self.animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(25)

    def enterEvent(self, event):
        self.animation.setDirection(QPropertyAnimation.Forward)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.setDirection(QPropertyAnimation.Backward)
        self.animation.start()
        super().leaveEvent(event)

class ToggleSwitch(QWidget):
    def __init__(self, label_on="Светлая тема", label_off="Темная тема"):
        super().__init__()
        self.is_on = False
        self.label_on = label_on
        self.label_off = label_off

        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.label = QLabel(self.label_off)
        self.label.setStyleSheet("color: #FFFFFF; font-family: Arial; font-size: 16px;")
        self.layout.addWidget(self.label)

        self.switch_bg = QWidget()
        self.switch_bg.setFixedSize(60, 30)
        self.switch_bg.setStyleSheet("""
            background-color: #696969;
            border-radius: 15px;
        """)

        self.switch_circle = QWidget(self.switch_bg)
        self.switch_circle.setGeometry(3, 3, 24, 24)
        self.switch_circle.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
        """)

        self.layout.addWidget(self.switch_bg)
        self.setLayout(self.layout)

        self.switch_bg.mousePressEvent = self.toggle
        self.label.mousePressEvent = self.toggle

        self.anim = QPropertyAnimation(self.switch_circle, b"geometry")
        self.anim.setDuration(200)

    def toggle(self, event):
        self.is_on = not self.is_on
        self.update_switch()

    def update_switch(self):
        if self.is_on:
            self.label.setText(self.label_on)
            self.label.setStyleSheet("color: #000; font-family: Arial; font-size: 16px;")
            self.anim.setStartValue(QRect(3, 3, 24, 24))
            self.anim.setEndValue(QRect(33, 3, 24, 24))
            self.anim.start()
            self.emit_toggle_signal(True)
        else:
            self.label.setText(self.label_off)
            self.label.setStyleSheet("color: #FFFFFF; font-family: Arial; font-size: 16px;")
            self.anim.setStartValue(QRect(33, 3, 24, 24))
            self.anim.setEndValue(QRect(3, 3, 24, 24))
            self.anim.start()
            self.emit_toggle_signal(False)

    def emit_toggle_signal(self, state):
        if self.parent():
            self.parent().toggle_theme(state)


class CopyButton(QPushButton):
    def __init__(self, text="Копировать"):
        super().__init__(text)
        # Создаем эффект свечения
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setColor(Qt.cyan)
        self.shadow_effect.setBlurRadius(0)
        self.shadow_effect.setOffset(0)
        self.setGraphicsEffect(self.shadow_effect)

        # Анимация для свечения
        self.animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(20)

    def enterEvent(self, event):
        self.animation.setDirection(QPropertyAnimation.Forward)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.setDirection(QPropertyAnimation.Backward)
        self.animation.start()
        super().leaveEvent(event)

class ChatGPTInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT")
        self.resize(800, 600)
        self.chat_history = []  # (role, text, timestamp)
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_dots)
        self.loading_index = 0
        self.loading_chars = ['⠁','⠂','⠄','⡀','⢀','⠠','⠐','⠈']

        # New timer for the bot response
        self.bot_response_timer = QTimer()
        self.bot_response_timer.timeout.connect(self.update_bot_timer)

        self.dark_mode = True
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()  # Переместили сюда объявление main_layout

        # Добавил переключатель темы
        self.toggle_switch = ToggleSwitch()
        main_layout.addWidget(self.toggle_switch, alignment=Qt.AlignRight)

        # Кнопка очистить чат
        self.clear_button = GlowingButton("Очистить чат")
        self.clear_button.clicked.connect(self.clear_chat)
        main_layout.addWidget(self.clear_button, alignment=Qt.AlignRight)

        title_label = QLabel("ChatGPT Client")
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Создаем ScrollArea с фиксированной высотой (например, 400 пикселей)
        self.scroll_area = QScrollArea()
        self.scroll_area.setFixedSize(780, 400)  # фиксированная высота по желанию
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

        main_layout.addWidget(self.scroll_area)

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
                font-family: Arial;
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
        self.send_button.setFixedSize(140, 45)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3A86FF;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 16px;
                font-family: Arial;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        # стиль и подключение
        self.send_button.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

        # Сохраняем оригинальный метод keyPressEvent
        self.original_keyPressEvent = self.input_field.keyPressEvent
        # Переопределяем keyPressEvent
        self.input_field.keyPressEvent = self.custom_keyPressEvent

        self.setLayout(main_layout)
        self.apply_theme()
        self.input_field.setFocus()



    def toggle_theme(self, state):
        self.dark_mode = not state  # True если выключен переключатель (Темная тема)
        self.apply_theme()

    def update_loading_dots(self):
        self.loading_dots_count = (self.loading_dots_count + 1) % 4
        dots = '.' * self.loading_dots_count
        # Update the last "bot" message
        if self.chat_history and self.chat_history[-1][0] == "bot":
            self.chat_history[-1] = ("bot", f"ИИ думает{dots}")
            self.update_chat_display()

    def apply_theme(self):
        if self.dark_mode:
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
                font-family: Arial;
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
                border-radius: 8px; /* Закругленные углы для ScrollArea */
                background-color: #1E1E1E; /* Цвет фона ScrollArea */
            }
            QScrollBar:vertical {
                background: #D3D3D3; /* Серый цвет фона ползунка */
                width: 10px; /* Ширина вертикального ползунка */
                border-radius: 8px; /* Закругленные углы */
            }
            QScrollBar::handle:vertical {
                background: #3A86FF; /* Цвет ползунка */
                min-height: 20px; /* Минимальная высота ползунка */
                border-radius: 8px; /* Закругление углов ползунка */
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none; /* Убираем стрелки */
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none; /* Убираем стрелки */
            }
            QScrollBar::handle:vertical:hover {
                background: #5A99FF; /* Цвет ползунка при наведении */
            }
            QScrollBar:horizontal {
            background: #D3D3D3; /* Серый фон */
            height: 10px;
            border-radius: 8px;
            }
            QScrollBar::handle:horizontal {
                background: #3A86FF;
                min-width: 20px;
                border-radius: 8px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #5A99FF;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
            }
            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                background: none;
            }
        """)
        else:
            self.setStyleSheet("""
                QWidget { background-color: #FFFFFF; color: #000000; }
                QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
                font-family: Arial;
                font-size: 14px;
                }
                QPushButton {
                    background-color: #3A86FF;
                    color: #FFFFFF;
                    border-radius: 8px;
                    padding: 8px 16px;
                }
                QLabel { color: #000000; }
                QScrollArea { background-color: #F0F0F0; }
                QScrollArea {
                border: 4px solid #555;
                border-radius: 8px; /* Закругленные углы для ScrollArea */
                background-color: #1E1E1E; /* Цвет фона ScrollArea */
                }
                QScrollBar:vertical {
                    background: #D3D3D3; /* Серый цвет фона ползунка */
                    width: 10px; /* Ширина вертикального ползунка */
                    border-radius: 8px; /* Закругленные углы */
                }
                QScrollBar::handle:vertical {
                    background: #3A86FF; /* Цвет ползунка */
                    min-height: 20px; /* Минимальная высота ползунка */
                    border-radius: 8px; /* Закругление углов ползунка */
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none; /* Убираем стрелки */
                }
                QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                    background: none; /* Убираем стрелки */
                }
                QScrollBar::handle:vertical:hover {
                    background: #5A99FF; /* Цвет ползунка при наведении */
                }
                QScrollBar:horizontal {
                background: #D3D3D3; /* Серый фон */
                height: 10px;
                border-radius: 8px;
                }
                QScrollBar::handle:horizontal {
                    background: #3A86FF;
                    min-width: 20px;
                    border-radius: 8px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #5A99FF;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    background: none;
                }
                QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                    background: none;
                }
            """)

    def clear_chat(self):
        self.chat_history.clear()
        self.update_chat_display()

    def custom_keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if not (event.modifiers() & Qt.ShiftModifier):
                self.handle_send()
                event.accept()
            else:
                # Если Shift+Enter, вставляем перенос строки
                self.original_keyPressEvent(event)
        else:
            # Для всех остальных клавиш вызываем оригинальный метод
            self.original_keyPressEvent(event)

    def update_chat_display(self):
        # очищаем старые сообщения
        for i in reversed(range(self.messages_layout.count())):
            widget = self.messages_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # добавляем новые сообщения
        for item in self.chat_history:
            if item[0] == "user":
                # user сообщения имеют 3 элемента
                if len(item) == 3:
                    role, text, time_str = item
                else:
                    # на случай, если нет времени
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
                # bot сообщения имеют 3 элемента: role, text, timestamp
                if len(item) == 3:
                    role, text, time_str = item
                else:
                    # если вдруг есть 2, игнорируем время
                    role, text = item[0], item[1]
                    time_str = ""

                message_widget = QWidget()
                h_layout = QHBoxLayout()
                message_widget.setLayout(h_layout)

                text_label = QLabel()
                text_label.setWordWrap(True)

                html = markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
                text_label.setText(f'<b>ChatGPT [{time_str}]:</b><br>{html}')  # Include the timestamp
                text_label.setTextFormat(Qt.RichText)
                text_label.setStyleSheet("border-radius:8px; padding:8px; background-color:#333; color: #FFFFFF;")

                copy_button = CopyButton("Копировать")
                copy_button.setFixedSize(100, 30)
                copy_button.clicked.connect(lambda checked, t=text: self.copy_text(t))

                def copy_button_def(self, btn=copy_button):
                    btn.setText("Скопировано")
                    QTimer.singleShot(0, lambda: btn.setFixedSize(120, 30))
                    QTimer.singleShot(2000, lambda: btn.setText("Копировать"))
                    QTimer.singleShot(2000, lambda: btn.setFixedSize(100, 30))

                copy_button.clicked.connect(copy_button_def)

                h_layout.addWidget(text_label)
                h_layout.addWidget(copy_button)
                h_layout.setStretch(0, 1)
                h_layout.setStretch(1, 0)

            else:
                # если роль неизвестна — пропускаем
                continue

            self.messages_layout.addWidget(message_widget)

        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())




    def copy_text(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def handle_send(self):
        user_text = self.input_field.toPlainText().strip()
        if not user_text:
            return

        if not client.api_key:
            QMessageBox.warning(self, "Ошибка", "API ключ не установлен. Пожалуйста, введите ключ.")
            return

        # Add user message with timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_history.append(("user", user_text, timestamp))
        # Add "bot is thinking..." message without timestamp
        self.chat_history.append(("bot", "ИИ думает..."))
        self.update_chat_display()

        self.input_field.clear()
        self.send_button.setEnabled(False)

        # Show "bot is thinking..."
        self.loading_dots_count = 0
        self.loading_timer.start(300)

        # Start the bot response timer
        self.bot_response_timer.start(1000)  # Update every second

        # Start the worker thread for the request
        self.worker = ApiWorker(user_text)
        self.worker.finished.connect(self.on_response)
        self.worker.start()
        self.input_field.setFocus()


    def update_bot_timer(self):
        # Update the bot's timer display (if needed)
        if self.chat_history and self.chat_history[-1][0] == "bot":
            self.chat_history[-1] = ("bot", "ИИ думает...")
            self.update_chat_display()

    def on_response(self, response):
        self.loading_timer.stop()
        self.bot_response_timer.stop()  # Stop the bot's response timer

        html_content = markdown.markdown(response)
        timestamp = datetime.now().strftime("%H:%M:%S")  # Capture the current time

        if self.chat_history and self.chat_history[-1][0] == "bot":
            self.chat_history[-1] = ("bot", html_content, timestamp)  # Add timestamp to bot's message
        else:
            self.chat_history.append(("bot", html_content, timestamp))  # Append with timestamp

        self.update_chat_display()
        self.send_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGPTInterface()
    window.setWindowIcon(QIcon('icon.ico'))
    window.hide()

    second_window = SecondWindow()
    second_window.setWindowIcon(QIcon('icon.ico'))
    second_window.show()

    sys.exit(app.exec_())

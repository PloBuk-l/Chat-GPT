import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QThread, pyqtSignal, QTimer
from openai import OpenAI

# Инициализация клиента OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

class ApiWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, user_text):
        super().__init__()
        self.user_text = user_text

    def run(self):
        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=[
                    {"role": "user", "content": self.user_text}
                ],
            )
            response = completion.choices[0].message.content
        except Exception as e:
            response = f"Ошибка при запросе: {e}"
        self.finished.emit(response)

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

class ChatGPTInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Client")
        self.resize(800, 600)
        self.chat_history = []  # список кортежей (role, text)

        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_dots)
        self.loading_dots_count = 0

        self.setup_ui()

    def setup_ui(self):
        dark_style = """
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
        """
        self.setStyleSheet(dark_style)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        title_label = QLabel("ChatGPT Client")
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display)

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
        input_layout.addWidget(self.input_field)

        self.send_button = GlowingButton("Отправить")
        self.send_button.setFixedSize(140, 45)
        font = QFont("Arial", 12)
        font.setBold(True)
        self.send_button.setFont(font)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3A86FF;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 16px;
            }
        """)
        self.send_button.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

    def update_chat_display(self):
        self.chat_display.clear()
        for role, text in self.chat_history:
            if role == "user":
                self.chat_display.append(f'<b><span style="font-size:16px;">Вы:</span></b> <span style="font-size:16px;">{text}</span>')
            elif role == "bot":
                self.chat_display.append(f'<div style="margin-top:10px;"><b><span style="font-size:16px;">ChatGPT:</span></b> <span style="font-size:16px;">{text}</span></div>')

    def handle_send(self):
        user_text = self.input_field.toPlainText().strip()
        if not user_text:
            return

        # Добавляем сообщение пользователя в историю
        self.chat_history.append(("user", user_text))
        # Добавляем сообщение "бот думает..."
        self.chat_history.append(("bot", ""))  # будет обновляться в процессе
        self.update_chat_display()

        self.input_field.clear()
        self.send_button.setEnabled(False)

        # Запускаем анимацию с точками
        self.loading_dots_count = 0
        self.loading_timer.start(300)

        # Запускаем поток для асинхронного запроса
        self.worker = ApiWorker(user_text)
        self.worker.finished.connect(self.on_response)
        self.worker.start()

    def update_loading_dots(self):
        # Циклично меняем количество точек 0-3
        self.loading_dots_count = (self.loading_dots_count + 1) % 4
        dots = '.' * self.loading_dots_count
        # Обновляем последнее сообщение "бот"
        if self.chat_history and self.chat_history[-1][0] == "bot":
            self.chat_history[-1] = ("bot", f"ИИ думает{dots}")
            self.update_chat_display()

    def on_response(self, response):
        # Останавливаем таймер
        self.loading_timer.stop()

        # Заменяем последнее сообщение "бот" на ответ
        if self.chat_history and self.chat_history[-1][0] == "bot":
            self.chat_history[-1] = ("bot", response)
        else:
            self.chat_history.append(("bot", response))
        self.update_chat_display()
        self.send_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGPTInterface()
    window.show()
    sys.exit(app.exec_())
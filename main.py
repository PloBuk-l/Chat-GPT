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
from PyQt5.QtCore import Qt, QPropertyAnimation


class ChatGPTInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Client")
        self.resize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        # Общий стиль для тёмной темы
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
            QPushButton:hover {
                /* Можно оставить пустым или добавить стиль */
            }
            QLabel {
                color: #FFFFFF;
            }
        """

        self.setStyleSheet(dark_style)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Заголовок
        title_label = QLabel("ChatGPT Interface")
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Область для диалога
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display)

        # Поле для ввода и кнопка
        input_layout = QHBoxLayout()

        self.input_field = QTextEdit()
        self.input_field.setFixedHeight(45)
        
        # Стиль для поля ввода
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #2C2C2C; /* чуть светлее фона */
                color: #FFFFFF;
                border: 2px solid #555; /* граница */
                border-radius: 10px; /* закругленные углы */
                padding: 8px; /* внутренние отступы */
                font-family: Bold;
                font-size: 16px;
            }
            QTextEdit:hover {
                border-color: #888; /* при наведении чуть ярче граница */
            }
            QTextEdit:focus {
                border-color: #3A86FF; /* при фокусе выделение */
                outline: none; /* убрать стандартный outline */
            }
        """)

        
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Отправить")
        self.send_button.setFixedSize(120, 45)  # увеличил ширину

        # Создаем шрифт для кнопки
        font = QFont("Arial", 12)
        font.setBold(True)
        self.send_button.setFont(font)
        # Стиль кнопки (без hover эффектов)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3A86FF;
                color: #DCDCDC;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                /* Можно оставить пустым или добавить стиль */
            }
        """)

        self.send_button.clicked.connect(self.handle_send)

        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

        # Создаем эффект свечения (тень) для кнопки
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(0)   # изначально без свечения
        self.shadow_effect.setColor(Qt.cyan)   # цвет свечения
        self.shadow_effect.setOffset(0)       # без смещения

        self.send_button.setGraphicsEffect(self.shadow_effect)

        # Создаем анимацию для изменения радиуса размытия тени
        self.animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        
    def handle_send(self):
        user_text = self.input_field.toPlainText().strip()
        if user_text:
            # Добавляем сообщение пользователя
            self.chat_display.append(f"<b>Вы:</b> {user_text}")
            self.input_field.clear()

            # Здесь можно вставить логику взаимодействия с API
            response = "Это пример ответа от модели."
            
            # Добавляем ответ с небольшим отступом сверху (можно через HTML)
            self.chat_display.append(f'<div style="margin-top:10px;"><b>ChatGPT:</b> {response}</div>')

    def enterEvent(self, event):
        super().enterEvent(event)

    def leaveEvent(self, event):
        super().leaveEvent(event)

# Обработчики наведения на кнопку для свечения
def setup_hover_effects(widget, animation):
    def on_enter(event):
        animation.stop()
        animation.setStartValue(widget.graphicsEffect().blurRadius())
        animation.setEndValue(15)  # уровень свечения при наведении
        animation.start()

    def on_leave(event):
        animation.stop()
        animation.setStartValue(widget.graphicsEffect().blurRadius())
        animation.setEndValue(0)   # исчезновение свечения при уходе
        animation.start()

    widget.enterEvent = on_enter
    widget.leaveEvent = on_leave


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGPTInterface()

    setup_hover_effects(window.send_button, window.animation)

    window.show()
    sys.exit(app.exec_())



#Потом добавлю модель
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="", #API ключ сюда
)

completion = client.chat.completions.create(
    model="deepseek/deepseek-r1:free", # Здесь выбираешь любую модель
    messages=[
        {
            "role": "user",
            "content": "Что такое Иван Золо?"
        }
    ],    
)

print(completion.choices[0].message.content)
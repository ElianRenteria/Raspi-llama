import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont


class ChatBotWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Raspi-llama")
        self.setGeometry(100, 100, 600, 700)

        # Set up the central widget and layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # Chat display area
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont('Roboto', 12))
        self.layout.addWidget(self.chat_display)

        # Input area
        self.input_area = QLineEdit(self)
        self.input_area.setFont(QFont('Roboto', 12))
        self.input_area.returnPressed.connect(self.handle_user_input)
        self.layout.addWidget(self.input_area)

        # Send button
        self.send_button = QPushButton("Send", self)
        self.send_button.setFont(QFont('Roboto', 12))
        self.send_button.clicked.connect(self.handle_user_input)
        self.layout.addWidget(self.send_button)

        self.setCentralWidget(self.central_widget)

        # Typing animation
        self.typing_animation_timer = QTimer()
        self.typing_animation_timer.timeout.connect(self.update_typing_animation)
        self.typing_dots = ""
        self.typing_colors = ['#000080', '#00008B', '#0000CD', '#0000FF']
        self.current_color_index = 0

    def handle_user_input(self):
        user_input = self.input_area.text().strip()
        if user_input:
            self.display_message("User", user_input, "black")
            self.input_area.clear()
            self.input_area.setEnabled(False)
            self.send_button.setEnabled(False)
            self.start_typing_animation()
            self.get_bot_response(user_input)

    def display_message(self, sender, message, color):
        if sender == "Raspi-llama":
            sender_text = "Raspi-llama 🐑"
        else:
            sender_text = sender
        self.chat_display.append(
            f'<span style="color:{color}; font-family:Roboto;"><b>{sender_text}:</b> {message}</span>')

    def get_bot_response(self, user_input):
        self.bot_thread = BotResponseThread(user_input)
        self.bot_thread.response_received.connect(self.handle_bot_response)
        self.bot_thread.start()

    def handle_bot_response(self, bot_response):
        self.stop_typing_animation()
        self.display_message("Raspi-llama", bot_response, "darkblue")
        self.input_area.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_area.setFocus()

    def start_typing_animation(self):
        self.typing_dots = ""
        self.typing_animation_timer.start(500)
        self.chat_display.append("Raspi-llama 🐑 is typing")

    def stop_typing_animation(self):
        self.typing_animation_timer.stop()
        self.chat_display.undo()

    def update_typing_animation(self):
        if len(self.typing_dots) < 4:
            self.typing_dots += "."
        else:
            self.typing_dots = ""

        self.current_color_index = (self.current_color_index + 1) % len(self.typing_colors)
        color = self.typing_colors[self.current_color_index]

        self.chat_display.undo()
        self.chat_display.append(
            f'<span style="color:{color}; font-family:Roboto;">Raspi-llama 🐑 is typing{self.typing_dots}</span>')


class BotResponseThread(QThread):
    response_received = pyqtSignal(str)

    def __init__(self, user_input):
        super().__init__()
        self.user_input = user_input

    def run(self):
        url = 'https://elianrenteria.me/chat'
        data = {'message': self.user_input}
        response = requests.post(url=url, json=data).json()
        bot_response = response.get('response', 'Sorry, I did not understand that.')
        self.response_received.emit(bot_response)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatBotWindow()
    window.show()
    sys.exit(app.exec_())

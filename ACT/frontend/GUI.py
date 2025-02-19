from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QSizePolicy, QLabel
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

#load the environment variables
env_vars = dotenv_values('.env')
Assistant_name = env_vars.get('assistant_name')
current_dir = os.getcwd()
old_chat_msg = ''
TempDirPath = rf"{current_dir}\frontend\files"
GraphicsDirPath = rf"{current_dir}\frontend\graphics"

#Function to modify the answer
def ModifyAnswer(Answer):
    lines = Answer.split('\n') # split into lines
    non_empty_lines = [line for line in lines if line.strip()] # remove empty lines
    modified_lines = "\n".join(non_empty_lines) # join the clean lines
    return modified_lines

# function to modify query for proper punctuation and formating
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    questions_words = ["how", "why", "where", "where's", "when", "when's", "who", "whom", "whose", "how's", "can you", "what", "which"]

    #check if a query is a question and add question mrk if necessary
    if any(word + "" in new_query for word in questions_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '?'
        else:
            new_query += '?'
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()

def SetMicStatus(command):
    with open(rf"{TempDirPath}/Mic.data", "w", encoding='utf-8') as file:
        file.write(command)

def GetMicStatus():
    with open(rf"{TempDirPath}/Mic.data", "r", encoding='utf-8') as file:
        status = file.read()
    return status

def SetAssistantStatus(status):
    with open(rf"{TempDirPath}/status.data", "w", encoding='utf-8') as file:
        file.write(status)

def GetAssistantStatus():
    with open(rf"{TempDirPath}/status.data", "r", encoding='utf-8') as file:
        status = file.read()
    return status

def MicButtonInitialized():
    SetMicStatus("False")

def MicButtonDisabled():
    SetMicStatus("True")

def TempWorkingDirectory(Filename):
    path = rf"{TempDirPath}/{Filename}"
    return path

def GraphicsWorkingDirectory(Filename):
    path = rf"{GraphicsDirPath}/{Filename}"
    return path

def ShowTexttOScreen(text):
    with open(rf"{TempDirPath}/responses.data", "w", encoding='utf-8') as file:
        file.write(text)

class ChatSection(QWidget):

    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        text_color= QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsWorkingDirectory('ACT.gif'))
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)

        movie.start()
        layout.addWidget(self.gif_label)
        self.label = QLabel("")
        
        self.label.setStyleSheet("color: white; font-size:14px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        layout.addWidget(self.gif_label)
        font = QFont()
        font.setPointSize(13)
        
        self.chat_text_edit.setFont(font)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
              QScrollBar:vertical {
              border: none;
              background: black;
              width: 10px;
              margin: 0px 0px 0px 0px;
              }     
              
              QScrollBar::handle:vertical { 
              background: white;
              min-height: 20px;
              }
                           
              QScrollBar::add-line:vertical {
              background: black;
              subcontrol-position: bottom;
              subcontrol-origin: margin;
              height: 10px;
              }

              QScrollBar::sub-line:vertical {
              background: black;
              subcontrol-position: top;
              subcontrol-origin: margin;
              height: 10px;
              }
                           
              QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical{
              border: none;
              background: none;
              color: none;             
              }
                           
              QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{
              background: none;
              }
        """)

    def loadMessages(self):
        
        global old_chat_msg

        with open(TempWorkingDirectory('responses.data'), "r", encoding='utf-8') as file:
            messages = file.read()

        if None == messages:
            pass

        elif len(messages) <= 1:
            pass

        elif str(old_chat_msg) == str(messages):
            pass

        else:
            self.addMessage(message=messages, color="White")
            old_chat_msg = messages

    def SpeechRecogText(self):
        with open(TempWorkingDirectory('status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def loadIcons(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggleIcons(self, event=None):
        if self.toggled:
            self.loadIcons(GraphicsWorkingDirectory('voice.png'), 60, 60)
            MicButtonInitialized()
        else:
            self.loadIcons(GraphicsWorkingDirectory('mic.png'), 60, 60)
            MicButtonDisabled()

        self.toggled = not self.toggled

    def addMessage(self, message, color):
        
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin (10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        desktop= QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setAlignment(Qt.AlignCenter)

        gif_label = QLabel()
        movie = QMovie(GraphicsWorkingDirectory('ACT.gif'))
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()

        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icon_label = QLabel()

        pixmap = QPixmap(GraphicsWorkingDirectory('mic_on.png'))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggleIcons()
        self.icon_label.mousePressEvent = self.toggleIcons

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; margin-bottom:0;")
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        with open(TempWorkingDirectory('status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def loadIcons(self, path, width=65, height=65):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggleIcons(self, event=None):
        if self.toggled:
            self.loadIcons(GraphicsWorkingDirectory('mic_on.png'), 72, 72)
            MicButtonInitialized()
        else:
            self.loadIcons(GraphicsWorkingDirectory('mic_off.png'), 72, 72)
            MicButtonDisabled()

        self.toggled = not self.toggled

class MessageScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):

    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        
        self.setFixedHeight(75)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        home_button = QPushButton()
        home_icon= QIcon (GraphicsWorkingDirectory("home.png"))
        home_button.setIcon(home_icon)
        home_button.setStyleSheet("width: 40px; height: 40px; background-color: black; color: white; margin-right: -8px;")

        message_button = QPushButton()
        message_icon = QIcon(GraphicsWorkingDirectory("chats.png"))
        message_button.setIcon(message_icon)
        message_button.setStyleSheet("width: 26px; background-color: black; color: white; margin-left: 10px;")

        minimize_button = QPushButton()
        minimize_icon= QIcon(GraphicsWorkingDirectory('minimize-2.png'))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color: black")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsWorkingDirectory('Maximize.png'))
        self.restore_icon = QIcon(GraphicsWorkingDirectory('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color: black; margin-left: 6px;")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_icon= QIcon(GraphicsWorkingDirectory('close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color: black; margin-left: 6px;")
        close_button.clicked.connect(self.closeWindow)

        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape (QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet ("border-color: black")

        act_icon = QIcon(GraphicsWorkingDirectory("act_icon.png"))
        act_btn = QPushButton()
        act_btn.setIcon(act_icon)
        act_btn.setStyleSheet("width: 40px; height:40px")

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        layout.addWidget(act_btn)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)

        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter()
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def MousePos(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMovePos(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalpos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen 

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)

        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()


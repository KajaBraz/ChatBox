import markupsafe
from flask import Flask, render_template

from src import enums

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/home/', methods=['GET'])
def open_chatbox():
    return render_template('home.html')


@app.route('/chat/', methods=['GET'])
@app.route('/chat/<chat>', methods=['GET'])
def enter_chat(chat=enums.Constants.DEFAULT_CHAT_NAME):
    requested_chat = markupsafe.escape(chat)
    return render_template('index.html', requestedChatName=requested_chat)


if __name__ == '__main__':
    app.run()

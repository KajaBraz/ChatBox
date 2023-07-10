import markupsafe
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/<chat>', methods=['GET'])
def open_chatbox(chat='WelcomeInChatBox'):
    requested_chat = markupsafe.escape(chat)
    print('chat:', requested_chat)
    return render_template('index.html', requestedChatName=requested_chat)


if __name__ == '__main__':
    app.run()

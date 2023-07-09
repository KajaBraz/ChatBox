from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def open_chatbox():
    if request.method == 'GET':
        args = request.args
        chat_room_name = args.get('chat')
        print(args)
        print('chat:', chat_room_name)
        return render_template('index.html')

    # todo fix no sound on messages (files treated as a GET request: "GET /sheep-122256.mp3 HTTP/1.1" 404 -)


if __name__ == '__main__':
    app.run()

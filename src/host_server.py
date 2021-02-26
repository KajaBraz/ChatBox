from flask import Flask, request, render_template
from src.database import add_user, db_name, db_login, db_password

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('user_login')
        password = request.form.get('user_password')
        add_user(db_name, db_login, db_password, login, password)
        return f'You are now successfully registered!'
    return render_template('registration.html')


if __name__ == '__main__':
    app.run()

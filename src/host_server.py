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

# @app.route('/')
# def ciao():
#     return '<html><body><h1>tyuio</h1></body></html>'
#
# @app.route('/register')
# def register():
#     return '<html><body><h1>register</h1></body></html>'
#
# @app.route('/login',methods=['GET','POST'])
# def login():
#     if request.method=='POST':
#         return do_the_login()
#     else:
#         return show_the_login_form()

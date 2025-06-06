from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import os
import bcrypt

local_db = "users_db.db"

app = Flask(__name__)
app.secret_key = os.urandom(24)
# app.config['SESSION_COOKIE_SECURE'] = True
# app.config['SESSION_COOKIE_HTTPONLY'] = True
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


@app.route('/')
@app.route('/home')
def home_page():
    if 'user_name' in session:
        users_data = data_query()
        return render_template('home_page.html', users_data=users_data)
    else:
        return redirect(url_for('login'))

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.html')
    else:
        user_details = (
            request.form['user_name'],
            request.form['firstname'],
            request.form['surname'],
            request.form['password']
        )
        if not is_user(user_details[0]):
            insert_user(user_details)
            return render_template('sign_up_success.html')
        return render_template('sign_up_failed.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['user_name']
        password = request.form['password']
        auth_result = authenticate_user(username, password)
        if auth_result == "user not exist":
            return redirect(url_for('sign_up'))
        elif auth_result:
            session['user_name'] = username
            return render_template('login_success.html', username=username)
        return render_template('login_failed.html')


@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect(url_for('login'))


@app.route('/my_profile')
def my_profile():
    if 'user_name' in session:
        user_data = user_query(session['user_name'])
        return render_template('my_profile.html', user_data=user_data)
    else:
        return redirect(url_for('login'))


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_name' in session:
        if request.method == 'GET':
            user_data = user_query(session['user_name'])
            return render_template('edit_profile.html', user_data=user_data)
        else:
            current_pass = request.form['current_password']
            new_pass = request.form['new_password']

            if authenticate_user(session['user_name'], current_pass):
                if new_pass:
                    password = new_pass
                else:
                    password = current_pass

                new_user_details = (
                    request.form['user_name'],
                    request.form['firstname'],
                    request.form['surname'],
                    password,
                    session['user_name']
                )

                if not is_user(new_user_details[0]) or new_user_details[0] == session['user_name']:
                    update_user(new_user_details)
                    return render_template('update_success.html', new_user_details= new_user_details)
                else:
                    user_data = user_query(session['user_name'])
                    return render_template('edit_profile_failed.html', user_data=user_data, text_error="THIS USERNAME IS ALREADY IN USE, PLEASE TRY AGAIN")
            else:
                user_data = user_query(session['user_name'])
                return render_template('edit_profile_failed.html', user_data= user_data, text_error= "INCORRECT PASSWORD, PLEASE TRY AGAIN.")
    else:
        return redirect(url_for('login'))


def data_query():
    connection = sqlite3.connect(local_db)
    cursor = connection.cursor()
    cursor.execute("""
    SELECT * FROM users_table
    """)
    users_data = cursor.fetchall()
    return users_data


def user_query(user_name):
    connection = sqlite3.connect(local_db)
    cursor = connection.cursor()
    sql_execute_string = "SELECT * FROM users_table WHERE user_name = ?"
    cursor.execute(sql_execute_string, (user_name,))
    user_data = cursor.fetchall()
    return user_data


def authenticate_user(user_name_input, password_input):
    connection = sqlite3.connect(local_db)
    cursor = connection.cursor()
    sql_execute_string = "SELECT password FROM users_table WHERE user_name = ?"
    cursor.execute(sql_execute_string, (user_name_input,))
    user_data = cursor.fetchall()
    if user_data:
        stored_hashed_password = user_data[0][0]
        return bcrypt.checkpw(password_input.encode(), stored_hashed_password)
    return "user not exist"


def insert_user(user_details):
    connection = sqlite3.connect(local_db)
    cursor = connection.cursor()
    hashed_password = bcrypt.hashpw(user_details[3].encode(), bcrypt.gensalt())
    user_details = (user_details[0], user_details[1], user_details[2], hashed_password)
    sql_execute_string = 'INSERT INTO users_table (user_name, firstname, surname, password) VALUES (?, ?, ?, ?)'
    cursor.execute(sql_execute_string, user_details)
    connection.commit()
    connection.close()


def update_user(new_details):
    connection = sqlite3.connect(local_db)
    cursor = connection.cursor()
    sql_execute_string = 'UPDATE users_table SET user_name = ?, firstname = ?, surname = ?, password = ? WHERE user_name = ?'
    hashed_password = bcrypt.hashpw(new_details[3].encode(), bcrypt.gensalt())
    new_details = (new_details[0], new_details[1], new_details[2], hashed_password, new_details[4])
    cursor.execute(sql_execute_string, new_details)
    connection.commit()
    connection.close()

def is_user(user_name_input):
    connection = sqlite3.connect(local_db)
    cursor = connection.cursor()
    sql_execute_string = "SELECT * FROM users_table WHERE user_name = ?"
    cursor.execute(sql_execute_string, (user_name_input,))
    user_data = cursor.fetchall()
    if user_data:
        return True
    return False

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))

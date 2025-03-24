from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import os

local_db = "users_db.db"

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
@app.route('/home')
def home_page():
    if 'user_name' in session:
        users_data = data_query()
        return render_template('home_page.html', users_data=users_data)
    else:
        return redirect(url_for('login'))


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        return render_template('sign_in.html')
    else:
        user_details = (
            request.form['user_name'],
            request.form['firstname'],
            request.form['surname'],
            request.form['password']
        )
        insert_user(user_details)
        return render_template('sign_in_success.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['user_name']
        password = request.form['password']
        auth_result = authenticate_user(username, password)
        if auth_result == "user not exist":
            return redirect(url_for('sign_in'))
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
            new_user_details = (
                request.form['user_name'],
                request.form['firstname'],
                request.form['surname'],
                request.form['new_password'],
                session['user_name']
            )
            update_user(new_user_details)
            return render_template('update_success.html', new_user_details= new_user_details)
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
        user_password = user_data[0][0]
        return user_password == password_input
    return "user not exist"


def insert_user(user_details):
    connection = sqlite3.connect(local_db)
    cursor = connection.cursor()
    sql_execute_string = 'INSERT INTO users_table (user_name, firstname, surname, password) VALUES (?, ?, ?, ?)'
    cursor.execute(sql_execute_string, user_details)
    connection.commit()
    connection.close()


def update_user(new_details):
    print(new_details)
    connection = sqlite3.connect(local_db)
    cursor = connection.cursor()
    sql_execute_string = 'UPDATE users_table SET user_name = ?, firstname = ?, surname = ?, password = ? WHERE user_name = ?'
    cursor.execute(sql_execute_string, new_details)
    connection.commit()
    connection.close()


if __name__ == '__main__':
    app.run()


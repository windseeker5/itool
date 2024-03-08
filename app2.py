from flask import Flask, request, redirect, url_for, session, render_template

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Hardcoded username and password (for demonstration purposes)
USERNAME = 'admin'
PASSWORD = 'password'

@app.route('/')
def home():
    if 'username' in session:
        return f'Logged in as {session["username"]}<br><a href="/logout">Logout</a>'
    return 'You are not logged in<br><a href="/login">Login</a>'




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['username'] = username
            return redirect(url_for('home'))
        return 'Invalid username or password'
    return render_template('login.html')





@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

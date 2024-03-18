from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# Mock user database (replace this with a real user database)
users = {'admin': 'password'}

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')



@app.route('/login', methods=['POST','GET'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if users.get(username) == password:
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', message='Invalid credentials')



@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)

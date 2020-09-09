from flask import Flask, render_template, url_for, request, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskprueba'
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template("index.html" )


@app.route('/registro')
def registro():
    return render_template("registro.html" )


@app.route('/login')
def login():
    return render_template("login.html" )

@app.route('/principal')
def principal():
    return render_template("principal.html" )

@app.route('/evento')
def evento():
    return render_template("evento.html" )


if __name__ == '__main__':
    app.run(debug=True)
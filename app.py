from flask import Flask, render_template, url_for, request, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_agend'
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template("index.html" )

@app.route('/terminos_y_condiciones')
def terminos():
    return render_template("terminos.html")

@app.route('/registro')
def registro():
    return render_template("registro.html" )

@app.route('/crear_registro', methods=["POST"] )
def crear_registro():
    if request.method == 'POST':
        nombre = request.form['nombre'] 
        email = request.form['email'] 
        usuario = request.form['usuario'] 
        contrasena = request.form['contrasena']
        validar = request.form['validar']
        if contrasena == validar:
            cur = mysql.connection.cursor()
            try:
                cur.execute("INSERT INTO usuario (nombre,email,usuario,contrasena) VALUES (%s,%s,%s,%s)",(nombre,email,usuario,generate_password_hash(contrasena, method="sha256")))
                mysql.connection.commit()
                flash("Sus datos fueron registrados exitosamente", "exito")
                return redirect(url_for("registro"))
            except:
                flash("Ese usuario ya se encuantra en uso", "info")
                return  redirect(url_for("registro"))
        else:
            flash("Las contraseñas ingresadas no coinciden entre ellas", "error")
            return redirect(url_for("registro"))

    else:
        return redirect(url_for("registro"))

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
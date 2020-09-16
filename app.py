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
usuario1 = 0

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
                cur.close()
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
    return render_template("login.html")

@app.route('/login_datos', methods=['POST'])
def login_datos():
    global usuario1
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM usuario WHERE usuario = %s", (usuario,))
            datos = cur.fetchall()
            cur.close()
            for i in datos:
                iid = i[0]
                contra = i[4]
                if datos and check_password_hash(contra, contrasena):
                    usuario1 = iid
                    return redirect(url_for("principal"))
                else:
                    flash("El usuario o contraseña son incorrectos", "error")
                    return redirect(url_for("login"))
            else:
                flash("El usuario o contraseña son incorrectos", "error")
                return redirect(url_for("login"))
        except:
            flash("El usuario o contraseña son incorrectos", "error")
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

@app.route('/principal')
def principal():
    if usuario1 > 0:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM evento WHERE id_usuario = %s ORDER BY id DESC",(usuario1,))
        eventos = cur.fetchall()
        cur.close()
        return render_template("principal.html", eventos=eventos)
    else:
        return redirect(url_for("login"))

@app.route('/salir')
def salir():
    global usuario1
    usuario1 = 0
    return redirect(url_for("index"))
    
@app.route('/evento')
def evento():
    if usuario1 > 0:
        return render_template("evento.html")
    else:
        return redirect(url_for("login"))

      
@app.route('/crear_evento', methods=["POST"])
def crear_evento():
    if request.method == 'POST':
        titulo = request.form['titulo'] 
        fecha = request.form['fecha'] 
        descripcion = request.form['descripcion'] 
        hora = request.form['hora'] 
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO evento (id_usuario,titulo,fecha,descripcion,hora) VALUES (%s,%s,%s,%s,%s)",(usuario1,titulo,fecha,descripcion,hora))
        mysql.connection.commit()
        cur.close()
        flash("El evento fue registrado exitosamente", "exito")
        return redirect(url_for("principal"))

@app.route("/busqueda", methods=["POST"])
def busqueda():
    if request.method == "POST":
        if usuario1 > 0:
            busqueda = "%" + request.form["busqueda"] + "%"
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM evento WHERE descripcion LIKE %s and id_usuario = %s ORDER BY id DESC",(busqueda,usuario1,))
            eventos = cur.fetchall()
            cur.close()
            return render_template("principal.html", eventos=eventos)
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
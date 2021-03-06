from flask import Flask, render_template, url_for, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import random, smtplib
from email.message import EmailMessage

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
                session['usuario'] = usuario
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
                    session['usuario'] = usuario
                    session['id'] = iid
                    session['logged_in'] = True
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

@app.route('/recuperar', methods=['POST'])
def recuperar():
    if request.method == 'POST':
        correo = request.form['email']
        session['correo'] = correo
        cur = mysql.connection.cursor()  
        try:
            cur.execute("SELECT * FROM usuario WHERE email = %s", (session['correo'],))    
            datos = cur.fetchall()
            cur.close()
            for i in datos:
                correo = i[2]
                ccs = random.randint(000000000,100000001)
                session['recovery'] = True
                session['validar'] = ccs
                msg = EmailMessage()
                msg.set_content(f"Su codigo es {session['validar']}")

                msg['Subject'] = 'Cambio de contraseña'
                msg['From'] = "codegroup787@gmail.com"
                msg['To'] = correo

                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login("codegroup787@gmail.com", "codegroup787..")
                server.send_message(msg)
                server.quit()
                return redirect(url_for("recovery"))
            else:
                flash("El correo no corresponde a un usuario registrado", "error")
                return redirect(url_for("login"))
        except:
            flash("El correo no corresponde a un usuario registrado", "error")
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

@app.route('/recovery')
def recovery():
    if session.get('recovery') == True:
        return render_template("cambio.html")
    else:
        return redirect(url_for("login"))

@app.route('/recovery2', methods=['POST'])
def recovery2():
    if request.method == 'POST':
        codigo = request.form['codigo']
        if session.get('recovery') == True:
            if session['validar'] == int(codigo):
                contrasena = request.form['contrasena']
                validar = request.form['validar']
                if contrasena == validar:
                    cur = mysql.connection.cursor()
                    cur.execute("UPDATE usuario SET contrasena = %s where email = %s", (generate_password_hash(contrasena, method="sha256"),session['correo'],))
                    mysql.connection.commit()
                    cur.close()
                    session.clear()
                    flash("La contraseña se cambio con éxito", "exito")
                    return redirect(url_for("login"))
                else:
                    flash("Las contraseñas ingresadas no coinciden", "info")
                    return redirect(url_for("recovery"))
            else:
                flash("El codigo que acaba de ingresar es incorrecto", "error")
                return redirect(url_for("recovery"))
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for("principal"))


@app.route('/principal')
def principal():
    if session.get('logged_in') == True:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM evento WHERE id_usuario = %s ORDER BY id DESC",(session['id'],))
        eventos = cur.fetchall()
        cur.close()
        return render_template("principal.html", eventos=eventos)
    else:
        return redirect(url_for('login'))


@app.route("/borrar/<id>")
def borrar(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM evento WHERE id=%s",(id,))
    mysql.connection.commit()
    cur.close()
    flash("El evento fue borrado exitosamente", "exito")
    return redirect(url_for('principal'))

@app.route("/editar/<id>")
def editar(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM evento WHERE id=%s",(id,))
    evento = cur.fetchall()
    cur.close()
    return render_template("editar.html", evento=evento[0])

@app.route("/editar_evento/<id>", methods=["POST"])
def editar_evento(id):
    titulo = request.form["titulo"]
    fecha = request.form["fecha"]
    descripcion = request.form["descripcion"]
    hora = request.form["hora"]
    cur = mysql.connection.cursor()
    cur.execute("UPDATE evento SET titulo = %s, descripcion = %s, fecha = %s, hora = %s WHERE id = %s ",(titulo,descripcion,fecha,hora,id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("principal"))

@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for("index"))
    
@app.route('/evento')
def evento():
    if session.get('logged_in') == True:
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
        cur.execute("INSERT INTO evento (id_usuario,titulo,fecha,descripcion,hora) VALUES (%s,%s,%s,%s,%s)",(session['id'],titulo,fecha,descripcion,hora))
        mysql.connection.commit()
        cur.close()
        flash("El evento fue registrado exitosamente", "exito")
        return redirect(url_for("principal"))

@app.route("/busqueda", methods=["POST"])
def busqueda():
    if session.get('logged_in') == True:
        if request.method == "POST":
            busqueda = "%" + request.form["busqueda"] + "%"
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM evento WHERE descripcion LIKE %s and id_usuario = %s ORDER BY id DESC",(busqueda,session['id'],))
            eventos = cur.fetchall()
            cur.close()
            return render_template("principal.html", eventos=eventos)
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))

@app.route("/busqueda_avanzada", methods=["POST"])
def busqueda_avanzada():
    if request.method == "POST":
        ba_titulo = request.form["ba_titulo"]
        ba_fecha = request.form["ba_fecha"] 
        ba_hora = request.form["ba_hora"]
        ba_fecha2 = request.form["ba_fecha2"]
        ba_fecha3 = request.form["ba_fecha3"]
        ba_hora2 = request.form["ba_hora2"]
        ba_hora3 = request.form["ba_hora3"]
        if ba_titulo != "":
            if ba_fecha != "": 
                if ba_fecha2 != "" or ba_fecha3 != "":
                    flash("Escoja si desea ver por una fecha exacta o por filtros pero no ambas", "info")
                    return redirect(url_for("principal"))
                elif ba_hora != "":
                    if ba_hora2 != "" or ba_hora3 != "":
                        flash("Escoja si desea ver por una hora exacta o por filtros pero no ambas", "info")
                        return redirect(url_for("principal"))
                    else:
                        cur = mysql.connection.cursor()
                        cur.execute("SELECT * FROM evento WHERE id_usuario = %s and titulo LIKE %s and fecha LIKE %s and hora LIKE %s ORDER BY id ASC",(session['id'],"%" + ba_titulo + "%",ba_fecha,"%" + ba_hora + "%",))
                        eventos = cur.fetchall()
                        cur.close()
                        return render_template("principal.html", eventos=eventos)
                elif ba_hora2 != "":
                    if ba_hora3 != "":
                        cur = mysql.connection.cursor()
                        cur.execute("SELECT * FROM evento WHERE id_usuario = %s and titulo LIKE %s and fecha LIKE %s and (hora >= %s and hora <= %s) ORDER BY id ASC",(session['id'],"%" + ba_titulo + "%",ba_fecha,ba_hora2,ba_hora3,))
                        eventos = cur.fetchall()
                        cur.close()
                        return render_template("principal.html", eventos=eventos) 
                    else:
                        flash("Si desea hacer un filtro de la hora porfavor llene ambos campos", "info")
                        return redirect(url_for("principal"))
                elif ba_hora3 != "":
                    flash("Si desea hacer un filtro de la hora porfavor llene ambos campos", "info")
                    return redirect(url_for("principal"))
                else:
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM evento WHERE id_usuario = %s and titulo LIKE %s and fecha LIKE %s ORDER BY id ASC",(session['id'],"%" + ba_titulo + "%",ba_fecha,))
                    eventos = cur.fetchall()
                    cur.close()
                    return render_template("principal.html", eventos=eventos)
            elif ba_hora != "": #ya
                if ba_hora2 != "" or ba_hora3 != "":
                    flash("Escoja si desea ver por una hora exacta o por filtros pero no ambas", "info")
                    return redirect(url_for("principal"))
                elif ba_fecha2 != "":
                    if ba_fecha3 != "":
                        cur = mysql.connection.cursor()
                        cur.execute("SELECT * FROM evento WHERE id_usuario = %s and titulo LIKE %s and hora LIKE %s and fecha BETWEEN CAST(%s AS DATE) AND CAST(%s AS DATE) ORDER BY id ASC",(session['id'],"%" + ba_titulo + "%","%" + ba_hora + "%",ba_fecha2,ba_fecha3,))
                        eventos = cur.fetchall()
                        cur.close()
                        return render_template("principal.html", eventos=eventos) 
                    else:
                        flash("Si desea hacer un filtro de la fecha porfavor llene ambos campos", "info")
                        return redirect(url_for("principal"))
                elif ba_fecha3 !="":
                    flash("Si desea hacer un filtro de la fecha porfavor llene ambos campos", "info")
                    return redirect(url_for("principal"))
                else:
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM evento WHERE id_usuario = %s and titulo LIKE %s and hora LIKE %s ORDER BY id ASC",(session['id'],"%" + ba_titulo + "%","%" + ba_hora + "%",))
                    eventos = cur.fetchall()
                    cur.close()
                    return render_template("principal.html", eventos=eventos)
            elif ba_fecha2 != "":
                if ba_fecha3 != "":
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM evento WHERE id_usuario = %s and titulo LIKE %s and fecha BETWEEN CAST(%s AS DATE) AND CAST(%s AS DATE) ORDER BY id ASC",(session['id'],"%" + ba_titulo + "%",ba_fecha2,ba_fecha3,))
                    eventos = cur.fetchall()
                    cur.close()
                    return render_template("principal.html", eventos=eventos) 
                else:
                    flash("Si desea hacer un filtro de la fecha porfavor llene ambos campos", "info")
                    return redirect(url_for("principal"))
            elif ba_fecha3 != "":
                flash("Si desea hacer un filtro de la fecha porfavor llene ambos campos", "info")
                return redirect(url_for("principal"))
            elif ba_hora2 != "":
                if ba_hora3 != "":
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM evento WHERE id_usuario = %s and titulo LIKE %s and (hora >= %s and hora <= %s) ORDER BY id ASC",(session['id'],"%" + ba_titulo + "%",ba_hora2,ba_hora3,))
                    eventos = cur.fetchall()
                    cur.close()
                    return render_template("principal.html", eventos=eventos) 
                else:
                    flash("Si desea hacer un filtro de la hora porfavor llene ambos campos", "info")
                    return redirect(url_for("principal"))
            elif ba_hora3 != "":
                flash("Si desea hacer un filtro de la hora porfavor llene ambos campos", "info")
                return redirect(url_for("principal"))
            else:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM evento WHERE id_usuario = %s and titulo LIKE %s ORDER BY id ASC",(session['id'],"%" + ba_titulo + "%",))
                eventos = cur.fetchall()
                cur.close()
                return render_template("principal.html", eventos=eventos)
        elif ba_fecha != "": #ya terminado
            if ba_fecha2 != "" or ba_fecha3 != "":
                flash("Escoja si desea ver por una fecha exacta o por filtros pero no ambas", "info")
                return redirect(url_for("principal"))
            elif ba_hora != "": 
                if ba_hora2 != "" or ba_hora3 != "":
                    flash("Escoja si desea ver por una hora exacta o por filtros pero no ambas", "info")
                    return redirect(url_for("principal"))
                else:
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM evento WHERE id_usuario = %s and fecha LIKE %s and hora LIKE %s ORDER BY id ASC",(session['id'],ba_fecha,"%" + ba_hora + "%",))
                    eventos = cur.fetchall()
                    cur.close()
                    return render_template("principal.html", eventos=eventos) 
            elif ba_hora2 != "":
                if ba_hora3 != "":
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM evento WHERE id_usuario = %s and fecha LIKE %s and (hora >= %s and hora <= %s) ORDER BY id ASC",(session['id'],ba_fecha,ba_hora2,ba_hora3,))
                    eventos = cur.fetchall()
                    cur.close()
                    return render_template("principal.html", eventos=eventos)  
                else:
                    flash("Si desea hacer un filtro de la fecha porfavor llene ambos campos", "info")
                    return redirect(url_for("principal"))
            elif ba_hora3 != "":
                flash("Si desea hacer un filtro de la fecha porfavor llene ambos campos", "info")
                return redirect(url_for("principal"))
            else:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM evento WHERE id_usuario = %s and fecha LIKE %s ORDER BY id ASC",(session['id'],ba_fecha,))
                eventos = cur.fetchall()
                cur.close()
                return render_template("principal.html", eventos=eventos)
        elif ba_hora != "": 
            if ba_hora2 != "" or ba_hora3 != "":
                flash("Escoja si desea ver por una hora exacta o por filtros pero no ambas", "info")
                return redirect(url_for("principal"))
            elif ba_fecha2 != "":
                if ba_fecha3 != "":
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM evento WHERE id_usuario = %s and hora LIKE %s and fecha BETWEEN CAST(%s AS DATE) AND CAST(%s AS DATE) ORDER BY id ASC",(session['id'],"%" + ba_hora + "%",ba_fecha2,ba_fecha3,))
                    eventos = cur.fetchall()
                    cur.close()
                    return render_template("principal.html", eventos=eventos) 
                else:
                    flash("Si desea hacer un filtro de la fecha porfavor llene ambos campos", "info")
                    return redirect(url_for("principal"))
            elif ba_fecha3 != "":
                flash("Si desea hacer un filtro de la fecha porfavor llene ambos campos", "info")
                return redirect(url_for("principal"))
            else:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM evento WHERE id_usuario = %s and hora LIKE %s ORDER BY id ASC",(session['id'],"%" + ba_hora + "%",))
                eventos = cur.fetchall()
                cur.close()
                return render_template("principal.html", eventos=eventos)
        elif ba_fecha2 != "":
            if ba_fecha3 != "":
                if ba_hora2 != "":
                    if ba_hora3 != "":
                        cur = mysql.connection.cursor()
                        cur.execute("SELECT * FROM evento WHERE id_usuario = %s and fecha BETWEEN CAST(%s AS DATE) AND CAST(%s AS DATE) and (hora >= %s and hora <= %s) ORDER BY id ASC",(session['id'],ba_fecha2,ba_fecha3,ba_hora2,ba_hora3,))
                        eventos = cur.fetchall()
                        cur.close()
                        return render_template("principal.html", eventos=eventos) 
                    else:
                        flash("Si desea hacer un filtro de la fecha con la hora porfavor llene ambos campos", "info")
                        return redirect(url_for("principal"))
                elif ba_hora3 != "":
                    flash("Si desea hacer un filtro de la fecha con la hora porfavor llene ambos campos", "info")
                    return redirect(url_for("principal"))
                else:
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM evento WHERE id_usuario = %s and fecha BETWEEN CAST(%s AS DATE) AND CAST(%s AS DATE) ORDER BY id ASC",(session['id'],ba_fecha2,ba_fecha3,))
                    eventos = cur.fetchall()
                    cur.close()
                    return render_template("principal.html", eventos=eventos) 
            else:
                flash("Si desea hacer un filtro de la fecha porfavor llene ambos campos", "info")
                return redirect(url_for("principal"))
        elif ba_fecha3 != "":
            flash("Si desea hacer un filtro de la fecha porfavor llene ambos campos", "info")
            return redirect(url_for("principal"))
        elif ba_hora2 != "":
            if ba_hora3 != "":
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM evento WHERE id_usuario = %s and (hora >= %s and hora <= %s) ORDER BY id ASC",(session['id'],ba_hora2,ba_hora3,))
                eventos = cur.fetchall()
                cur.close()
                return render_template("principal.html", eventos=eventos) 
            else:
                flash("Si desea hacer un filtro de la hora porfavor llene ambos campos", "info")
                return redirect(url_for("principal"))
        elif ba_hora3 != "":
            flash("Si desea hacer un filtro de la hora porfavor llene ambos campos", "info")
            return redirect(url_for("principal"))
        elif ba_titulo == "" and ba_hora == "" and ba_fecha == "":
            flash("Usted no ingresó ningun dato a buscar por favor llene almenos 1 de los campos", "info")
            return redirect(url_for("principal"))

if __name__ == '__main__': 
    app.run(debug=True)
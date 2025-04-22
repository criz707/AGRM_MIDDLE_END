from flask import Flask, request, jsonify
from flask import render_template, session, current_app
from flask_bcrypt import Bcrypt
import pymysql.cursors
from Config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Configuración de la conexión a la base de datos
connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor

)
app.connection = connection

# Regsitramso los blueprints aqui:
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login",methods=["get","post"])
def login():

    #Llamamos el primer elemento de labase de datos
    connection =  current_app.connection
    #Bcrypt - sele tiene que PASAR LA APP COMO CONTEXTO
    #en el archivo principal
    bcrypt = Bcrypt(app)
    if request.method == "POST":

        correo=request.form.get("correo")
        contrasena = request.form.get("contrasena")
        #Realizamos la verificacion
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT CONTRASENA FROM perfil WHERE CORREO=%s", (correo,))
                result = cursor.fetchone()
                #Verificamos la contrasena con encriptacion
                # (contraseña encriptada, contraseña sin encriptar)
                es_valida = bcrypt.check_password_hash(result["CONTRASENA"] , contrasena)
                #Verificamos que sea valida la contrasenia
                if es_valida:
                    #print("¡Contraseña correcta!")
                    #Si la contraseña en valida en alguno de los
                    #Verificamos si existe algun registro:
                        #Obtenemos el id del perfil
                        cursor.execute("SELECT ID_PERFIL FROM perfil WHERE correo=%s", (correo,))
                        
                        id_perfil = cursor.fetchone()
                        #Verificamos si existealgun registro:
                        if id_perfil:
                            #Con el id de perfil vmos a verificar si esta registrado como 
                            # administrador o como usuario

                            cursor.execute("SELECT ID_ADMINISTRADOR FROM administrador WHERE ID_PERFIL=%s", (id_perfil["ID_PERFIL"],))
                            admin = cursor.fetchone()
                            if admin:
                                # Guardar el email del usuario en la sesión de flask
                                session['correo'] = correo
                                return render_template("Admin/Inicio_a.html")
                            else:
                                #Usamos el id_perfil que obtuvimos arriba
                                cursor.execute("SELECT ID_USUARIO FROM usuario WHERE ID_PERFIL=%s", (id_perfil["ID_PERFIL"],))
                                usuario = cursor.fetchone()
                                if usuario["ID_USUARIO"]:
                                    # Guardar el email del usuario en la sesión de flask
                                    session['correo'] = correo
                                    return render_template("Usuario/Home_u.html")

                                else:
                                    return render_template("Login.html")
                            
                            return render_template("Login.html")

                        else:
                            
                            return "No hay perfiles registrados con esos datos"
                else:

                    #print("Contraseña incorrecta")
                    bcrypt = Bcrypt()
                    hashed = bcrypt.generate_password_hash("123").decode("utf-8")

                    return f'hashed : {hashed} , verificacion: {str(bcrypt.check_password_hash(hashed, "123"))}'

                
        except Exception as e:
            return str(e)
    elif request.method == "GET":
        return render_template("Login.html")


@app.route("/Inicio")
def incio():
    role="admin"
    if role == "admin":
        return render_template("Admin/Inicio_a.html",role=role)

    elif role == "usuario":
        return render_template("Usuario/Home_u.html",role=role)
    return render_template("index.html",role=role)

@app.route("/contacto",methods=["get","post"]) 
def contact():
    if request.method == 'POST':
        
        return "Formualrio enviado correctamente"

    return "pagina contacto :D"
from flask import Blueprint, render_template, current_app, request
from flask_bcrypt import Bcrypt

user_bp = Blueprint('user_bp', __name__)
bcrypt = Bcrypt()


@user_bp.route("/registro",methods=["get","post"])
def registro():
    if request.method == "POST":
        #Coneccion con la base de datos
        connection =  current_app.connection
        #Bcrypt
        bcrypt = Bcrypt()

        rol = request.form.get("ROL")

        nombre = request.form.get("NOMBRE")
        correo = request.form.get("CORREO")
        contrasena = request.form.get("CONTRASENA")
        contrasena  = bcrypt.generate_password_hash(contrasena).decode('utf-8')
        
        try:
            with connection.cursor() as cursor:
                if rol == "administrador":

                    cursor.execute("INSERT INTO perfil(NOMBRE,CORREO,CONTRASENA) VALUES (%s,%s,%s)",(nombre,correo,contrasena,))
                    #Sacamos el id del perfil
                    cursor.execute("SELECT ID_PERFIL FROM perfil WHERE NOMBRE=%s AND CORREO=%s",(nombre,correo))
                    id_perfil_admin = cursor.fetchone()
                    id_perfil_admin = id_perfil_admin["ID_PERFIL"]
                    #Tomamos el id del perfil y le asignamos un id de administrador:
                    cursor.execute("INSERT INTO administrador(ID_PERFIL) VALUES (%s)", (id_perfil_admin,))
                    #Este comando guarda LOS CAMBIOS EN LA BASE DE DATOS
                    connection.commit()

                    return render_template("index.html")
                if rol == "usuario":
                    #Insertamos el perfil
                    cursor.execute("INSERT INTO perfil(NOMBRE,CORREO,CONTRASENA) VALUES (%s,%s,%s)",(nombre,correo,contrasena,))
                    
                    #Sacamos el id del perfil
                    cursor.execute("SELECT ID_PERFIL FROM perfil WHERE NOMBRE=%s AND CORREO=%s",(nombre,correo))
                    id_perfil_usuario = cursor.fetchone()
                    id_perfil_usuario = id_perfil_usuario["ID_PERFIL"]
                    #Tomamos el id del perfil y le asignamos un id de administrador:
                    cursor.execute("INSERT INTO usuario(ID_PERFIL) VALUES (%s)", (id_perfil_usuario,))
                    #Este comando guarda LOS CAMBIOS EN LA BASE DE DATOS
                    connection.commit()

                    return render_template("index.html")

        except Exception as e:
            return str(e)


        return render_template("Registro.html")

    
    if request.method == "GET":
        return render_template("Registro.html")

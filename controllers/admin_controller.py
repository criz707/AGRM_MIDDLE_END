from flask import Blueprint, render_template, current_app, request, redirect,url_for
from flask_bcrypt import Bcrypt
admin_bp = Blueprint('admin_bp', __name__)
bcrypt = Bcrypt()


@admin_bp.route("/crud")
def crud():
    return render_template("Admin/Crud.html")


@admin_bp.route("/crud/usuarios")
def inicio_usuarios():
    connection = current_app.connection
    try:

        with connection.cursor() as cursor:
            cursor.execute("SELECT u.ID_USUARIO,p.ID_PERFIL,p.NOMBRE,p.CORREO FROM usuario u INNER JOIN perfil p ON u.ID_PERFIL = p.ID_PERFIL ")
            usuarios = cursor.fetchall()
            return render_template("Admin/usuario/Admin_menu_u.html", usuarios=usuarios)
    except Exception as e:
        return f"Error al obtener usuarios: {e}"
    return render_template("Admin/usuario/Admin_menu_u.html")

#Botones de volver

@admin_bp.route("/volver")
def volver():
    return redirect(url_for('admin_bp.inicio_usuarios'))

@admin_bp.route("/volver_crud")
def volver_crud():
    return render_template("Admin/Crud.html")



@admin_bp.route("/cerrar_sesion")
def cerrar_sesion():
    return render_template("index.html")


@admin_bp.route("/volver_menu")
def volver_menu():
    return render_template("Admin/Inicio_a.html")

@admin_bp.route("/crud/perfil/<int:id_perfil>", methods=["get","post"])
def perfil_usuario(id_perfil):
    connection = current_app.connection
    
    # Cargar la data del perfil
    if request.method == "GET":
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT p.ID_PERFIL, p.NOMBRE, p.CORREO,p.CONTRASENA
                    FROM perfil p
                    WHERE p.ID_PERFIL = %s
                """, (id_perfil,))
                perfil = cursor.fetchone()
                return render_template("Admin/usuario/Editar_u.html", perfil=perfil)
        except Exception as e:
            return f"Error al obtener perfil: {e}"
    # edita la data del perfil dependiendo del boton
    elif request.method == "POST":

        accion = request.form.get("accion")
        if accion == "actualizar":
            actualizar_perfil(id_perfil)
        elif accion == "eliminar":
            eliminar(id_perfil)

        # Luego de actualizar o eliminar, redirigimos o cargamos la lista
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT u.ID_USUARIO,p.ID_PERFIL,p.NOMBRE,p.CORREO FROM usuario u INNER JOIN perfil p ON u.ID_PERFIL = p.ID_PERFIL ")
                usuarios = cursor.fetchall()
                return render_template("Admin/usuario/Admin_menu_u.html", usuarios=usuarios)
        except Exception as e:
            return f"Error al obtener usuarios: {e}"

    # Por si acaso no entra en ninguna condición
    return "Método no válido"



def actualizar_perfil(id):
    connection = current_app.connection
    if request.method == "POST":
        
        #Obtenemos los datos del formulario, por el nombre del input
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")
        #Encriptamos la contraseña
        contrasena = bcrypt.generate_password_hash(contrasena).decode('utf-8')
        #En base al id, actualizamos los campos
        try:
            with connection.cursor() as cursor:
                #tomamos lso valores de la funcion
                cursor.execute("UPDATE perfil SET NOMBRE=%s,CORREO=%s, CONTRASENA=%s WHERE ID_PERFIL=%s",(nombre,correo,contrasena,id))
                #Actualizamos en la base de datos
                connection.commit()
        except Exception as e:

            return str(e)

def eliminar(id):
    #Eliminamos de la base de datos
    connection = current_app.connection
    #En base al id, actualizamos los campos
    try:
            with connection.cursor() as cursor:

                #Como tienen una relacion uno(perfil) a muchos(usuario), primero elimianrmos
                #  el perfil de la tabla usuarios
                cursor.execute("DELETE FROM usuario WHERE ID_PERFIL=%s",(id))
                #Luego al eliminamos de los perfiles
                cursor.execute("DELETE FROM perfil WHERE ID_PERFIL=%s",(id))
                #actualizamos en la base de datos
                connection.commit()

    except Exception as e:
            return str(e)
@admin_bp.route("/crud/perfil/crear", methods=["get","post"])
def crear_usuario():

    #Eliminamos de la base de datos
    connection = current_app.connection
    if request.method == "POST":
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")
        #Encriptamos la contrasena
        contrasena = bcrypt.generate_password_hash(contrasena).decode('utf-8')

        if not nombre or not correo or not contrasena:
            return "Faltan datos", 400

        try:

            with connection.cursor() as cursor:
                # Ya sabemos que es un usuario, asi ue hacemos el INSERT en perfiles primero

                # y luego tomaos el id_perfil y lo añadimos a usuario
                cursor.execute("INSERT INTO perfil(NOMBRE,CORREO,CONTRASENA) VALUES (%s,%s,%s)",(nombre,correo,contrasena,))
                cursor.execute("SELECT ID_PERFIL FROM perfil WHERE NOMBRE=%s AND CORREO=%s",(nombre,correo))
                id_perfil = cursor.fetchone()
                id_perfil = id_perfil["ID_PERFIL"]
                cursor.execute("INSERT INTO usuario(ID_PERFIL) VALUES (%s)",(id_perfil,))
                # actualizamos en la base de datos
                connection.commit()
                #Lo retornamos al usuario
                return redirect(url_for('admin_bp.inicio_usuarios'))
                
                
        except Exception as e:
                return str(e)
    #Retornamos la pantalla por default
    return render_template("Admin/usuario/Admin_crear_u.html")
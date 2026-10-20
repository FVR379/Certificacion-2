from datetime import date
from functools import wraps
import re

from flask import Flask, flash, redirect, render_template, request, session, url_for

from controllers.usuario import Usuario
from controllers.viaje import Viaje

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "67"


def obtener_fechas(formulario):
    try:
        fecha_inicio = date.fromisoformat(formulario.get("fecha_inicio", ""))
        fecha_fin = date.fromisoformat(formulario.get("fecha_fin", ""))
    except ValueError:
        return None, None
    if fecha_inicio < date.today() or fecha_fin < fecha_inicio:
        return None, None
    return fecha_inicio, fecha_fin


def requiere_sesion(vista):
    @wraps(vista)
    def vista_protegida(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Inicia sesión para continuar.")
            return redirect(url_for("index"))
        return vista(*args, **kwargs)

    return vista_protegida


@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect(url_for("viajes"))
    return render_template("registro.html")


@app.route("/registro", methods=["POST"])
def registro():
    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "apellido": request.form.get("apellido", "").strip(),
        "email": request.form.get("email", "").strip().lower(),
        "password": request.form.get("password", ""),
    }
    confirmacion = request.form.get("confirm_password", "")

    if not all(datos.values()):
        flash("Completa todos los campos.")
        return redirect(url_for("index"))
    if len(datos["nombre"]) < 2 or len(datos["apellido"]) < 2:
        flash("El nombre y el apellido deben tener al menos 2 caracteres.")
        return redirect(url_for("index"))
    if datos["password"] != confirmacion:
        flash("Las contraseñas no coinciden.")
        return redirect(url_for("index"))
    if Usuario.get_by_email(datos["email"]):
        flash("Ya existe una cuenta con ese correo electrónico.")
        return redirect(url_for("index"))

    usuario_id = Usuario.save(datos)
    if not usuario_id:
        flash("No se pudo crear la cuenta. Inténtalo nuevamente.")
        return redirect(url_for("index"))

    session["usuario_id"] = usuario_id
    session["usuario_nombre"] = datos["nombre"]
    return redirect(url_for("viajes"))


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    usuario = Usuario.validate_login(email, password)
    if not usuario:
        flash("Correo electrónico o contraseña incorrectos.")
        return redirect(url_for("index"))

    session["usuario_id"] = usuario.id
    session["usuario_nombre"] = usuario.nombre
    return redirect(url_for("viajes"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/viajes")
@requiere_sesion
def viajes():
    return render_template(
        "bienvenida.html",
        usuario=session.get("usuario_nombre", ""),
        viajes=Viaje.get_all(),
    )


@app.route("/viajes/nuevo", methods=["GET", "POST"])
@requiere_sesion
def nuevo_viaje():
    if request.method == "GET":
        return render_template("nuevo_viaje.html", today=date.today().isoformat())

    fecha_inicio, fecha_fin = obtener_fechas(request.form)
    destino = request.form.get("destino", "").strip()
    itinerario = request.form.get("itinerario", "").strip()
    if not destino or not itinerario or not fecha_inicio or not fecha_fin:
        flash("Completa el itinerario y verifica que las fechas sean válidas y futuras.")
        return redirect(url_for("nuevo_viaje"))

    viaje_id = Viaje.save(
        {
            "destino": destino,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "itinerario": itinerario,
            "usuario_id": session["usuario_id"],
        }
    )
    if not viaje_id:
        flash("No se pudo guardar el viaje. Inténtalo nuevamente.")
        return redirect(url_for("nuevo_viaje"))
    return redirect(url_for("ver_viaje", viaje_id=viaje_id))


@app.route("/viajes/<int:viaje_id>")
@requiere_sesion
def ver_viaje(viaje_id):
    viaje = Viaje.get_one({"id": viaje_id})
    if not viaje:
        flash("No se encontró ese viaje.")
        return redirect(url_for("viajes"))
    return render_template(
        "ver_viaje.html",
        viaje=viaje,
        es_organizador=viaje.usuario_id == session["usuario_id"],
        esta_unido=Viaje.has_traveler(viaje_id, session["usuario_id"]),
    )


@app.route("/viajes/<int:viaje_id>/unirse", methods=["POST"])
@requiere_sesion
def unirse_viaje(viaje_id):
    viaje = Viaje.get_one({"id": viaje_id})
    if not viaje:
        flash("No se encontró ese viaje.")
        return redirect(url_for("viajes"))
    if viaje.usuario_id == session["usuario_id"]:
        flash("Quien organiza el viaje ya está registrado como organizador.")
    elif Viaje.has_traveler(viaje_id, session["usuario_id"]):
        flash("Ya estás unido a este viaje.")
    elif not Viaje.add_traveler(viaje_id, session["usuario_id"]):
        flash("No se pudo unir al viaje. Inténtalo nuevamente.")
    return redirect(url_for("ver_viaje", viaje_id=viaje_id))


@app.route("/viajes/<int:viaje_id>/cancelar", methods=["POST"])
@requiere_sesion
def cancelar_viaje(viaje_id):
    viaje = Viaje.get_one({"id": viaje_id})
    if not viaje:
        flash("No se encontró ese viaje.")
        return redirect(url_for("viajes"))
    if viaje.usuario_id == session["usuario_id"]:
        flash("El organizador no puede cancelar su propio viaje.")
    elif Viaje.has_traveler(viaje_id, session["usuario_id"]):
        Viaje.remove_traveler(viaje_id, session["usuario_id"])
    return redirect(url_for("ver_viaje", viaje_id=viaje_id))


@app.route("/viajes/<int:viaje_id>/editar", methods=["GET", "POST"])
@requiere_sesion
def editar_viaje(viaje_id):
    viaje = Viaje.get_one({"id": viaje_id})
    if not viaje:
        flash("No se encontró ese viaje.")
        return redirect(url_for("viajes"))
    if viaje.usuario_id != session["usuario_id"]:
        flash("Solo quien organizó el viaje puede editarlo.")
        return redirect(url_for("ver_viaje", viaje_id=viaje_id))
    if request.method == "GET":
        return render_template(
            "editar_viaje.html", viaje=viaje, today=date.today().isoformat()
        )

    fecha_inicio, fecha_fin = obtener_fechas(request.form)
    destino = request.form.get("destino", "").strip()
    itinerario = request.form.get("itinerario", "").strip()
    if not destino or not itinerario or not fecha_inicio or not fecha_fin:
        flash("Completa el itinerario y verifica que las fechas sean válidas y futuras.")
        return redirect(url_for("editar_viaje", viaje_id=viaje_id))

    actualizado = Viaje.update(
        {
            "id": viaje_id,
            "destino": destino,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "itinerario": itinerario,
        }
    )
    if actualizado is False:
        flash("No se pudo actualizar el viaje.")
        return redirect(url_for("editar_viaje", viaje_id=viaje_id))
    return redirect(url_for("ver_viaje", viaje_id=viaje_id))


@app.route("/viajes/<int:viaje_id>/eliminar", methods=["POST"])
@requiere_sesion
def eliminar_viaje(viaje_id):
    viaje = Viaje.get_one({"id": viaje_id})
    if not viaje:
        flash("No se encontró ese viaje.")
        return redirect(url_for("viajes"))
    if viaje.usuario_id != session["usuario_id"]:
        flash("Solo quien organizó el viaje puede eliminarlo.")
        return redirect(url_for("ver_viaje", viaje_id=viaje_id))

    eliminado = Viaje.delete({"id": viaje_id})
    if eliminado is False:
        flash("No se pudo eliminar el viaje.")
    return redirect(url_for("viajes"))


if __name__ == "__main__":
    app.run()
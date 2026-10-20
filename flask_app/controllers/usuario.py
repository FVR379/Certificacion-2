from config.mysqlconnection import connectToMySQL
from werkzeug.security import check_password_hash, generate_password_hash

class Usuario:
    def __init__(self, data):
        self.id = data.get('id')
        self.nombre = data.get('nombre')
        self.apellido = data.get('apellido')
        self.email = data.get('email')
        self.password = data.get('password')

    @classmethod
    def save(cls, datos):
        query = "INSERT INTO usuarios (nombre, apellido, `e-mail`, `password`, created_at, updated_at) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s, NOW(), NOW());"
        datos_guardar = dict(datos)
        datos_guardar['password'] = generate_password_hash(datos['password'])
        return connectToMySQL('certificaion-2').query_db(query, datos_guardar)

    @classmethod
    def get_by_email(cls, email):
        query = "SELECT id, nombre, apellido, `e-mail` AS email, `password` AS password FROM usuarios WHERE `e-mail` = %(email)s;"
        resultados = connectToMySQL('certificaion-2').query_db(query, {'email': email})
        return cls(resultados[0]) if resultados else None

    @classmethod
    def validate_login(cls, email, password):
        usuario = cls.get_by_email(email)
        if usuario:
            try:
                contraseña_valida = check_password_hash(usuario.password, password)
            except (TypeError, ValueError):
                contraseña_valida = usuario.password == password
            if contraseña_valida:
                return usuario
        return None

    @classmethod
    def get_all(cls):
        query = " SELECT * FROM usuarios;"
        resultados_query = connectToMySQL('certificaion-2').query_db(query)

        usuarios = []
        
        for elemento in resultados_query:
            usuarios.append(cls(elemento))
        return usuarios

    @classmethod
    def get_one(cls,datos):
        query = "SELECT * FROM usuarios WHERE id = %(id)s;"
        usuario_en_db = connectToMySQL('certificaion-2').query_db(query,datos)
        return cls(usuario_en_db[0]) if usuario_en_db else None

    @classmethod
    def update(cls, datos):
        query = "UPDATE usuarios SET nombre=%(nombre)s, apellido=%(apellido)s, `e-mail`=%(email)s, updated_at=NOW() WHERE id = %(id)s;"
        return connectToMySQL('certificaion-2').query_db(query, datos)

    @classmethod
    def delete(cls, datos):
        query = "DELETE FROM usuarios WHERE id = %(id)s;"
        return connectToMySQL('certificaion-2').query_db(query, datos)
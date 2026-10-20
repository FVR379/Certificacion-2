from config.mysqlconnection import connectToMySQL

class Viaje:
    def __init__(self, data):
        self.id = data.get('id')
        self.destino = data.get('destino')
        self.fecha_inicio = data.get('fecha_inicio')
        self.fecha_fin = data.get('fecha_fin')
        self.itinerario = data.get('itinerario')
        self.usuario_id = data.get('usuario_id')
        self.usuario = data.get('usuario')
        self.viajeros = data.get('viajeros', [])

    @classmethod
    def save(cls, datos):
        query = "INSERT INTO viajes (destino, fecha_inicio, fecha_fin, `Itinerario`, usuarios_id, created_at, updated_at) VALUES (%(destino)s, %(fecha_inicio)s, %(fecha_fin)s, %(itinerario)s, %(usuario_id)s, NOW(), NOW());"
        return connectToMySQL('certificaion-2').query_db(query, datos)

    @classmethod
    def get_all(cls):
        query = "SELECT viajes.id, viajes.destino, viajes.fecha_inicio, viajes.fecha_fin, viajes.`Itinerario` AS itinerario, viajes.usuarios_id AS usuario_id, CONCAT(usuarios.nombre, ' ', usuarios.apellido) AS usuario FROM viajes JOIN usuarios ON viajes.usuarios_id = usuarios.id ORDER BY viajes.fecha_inicio;"
        resultados_query = connectToMySQL('certificaion-2').query_db(query)
        return [cls(elemento) for elemento in resultados_query]

    @classmethod
    def get_one(cls,datos):
        query = "SELECT viajes.id, viajes.destino, viajes.fecha_inicio, viajes.fecha_fin, viajes.`Itinerario` AS itinerario, viajes.usuarios_id AS usuario_id, CONCAT(usuarios.nombre, ' ', usuarios.apellido) AS usuario FROM viajes JOIN usuarios ON viajes.usuarios_id = usuarios.id WHERE viajes.id = %(id)s;"
        viaje_en_db = connectToMySQL('certificaion-2').query_db(query,datos)
        if not viaje_en_db:
            return None
        viaje = cls(viaje_en_db[0])
        viaje.viajeros = cls.get_travelers(viaje.id)
        return viaje

    @classmethod
    def get_travelers(cls, viaje_id):
        query = "SELECT usuarios.id, usuarios.nombre, usuarios.apellido FROM viajes_usuarios JOIN usuarios ON viajes_usuarios.usuario_id = usuarios.id WHERE viajes_usuarios.viaje_id = %(viaje_id)s ORDER BY usuarios.nombre, usuarios.apellido;"
        return connectToMySQL('certificaion-2').query_db(query, {'viaje_id': viaje_id})

    @classmethod
    def has_traveler(cls, viaje_id, usuario_id):
        query = "SELECT usuario_id FROM viajes_usuarios WHERE viaje_id = %(viaje_id)s AND usuario_id = %(usuario_id)s;"
        resultado = connectToMySQL('certificaion-2').query_db(
            query, {'viaje_id': viaje_id, 'usuario_id': usuario_id}
        )
        return bool(resultado)

    @classmethod
    def add_traveler(cls, viaje_id, usuario_id):
        query = "INSERT INTO viajes_usuarios (viaje_id, usuario_id, created_at) VALUES (%(viaje_id)s, %(usuario_id)s, NOW());"
        return connectToMySQL('certificaion-2').query_db(
            query, {'viaje_id': viaje_id, 'usuario_id': usuario_id}
        )

    @classmethod
    def remove_traveler(cls, viaje_id, usuario_id):
        query = "DELETE FROM viajes_usuarios WHERE viaje_id = %(viaje_id)s AND usuario_id = %(usuario_id)s;"
        return connectToMySQL('certificaion-2').query_db(
            query, {'viaje_id': viaje_id, 'usuario_id': usuario_id}
        )

    @classmethod
    def update(cls, datos):
        query = "UPDATE viajes SET destino=%(destino)s, fecha_inicio=%(fecha_inicio)s, fecha_fin=%(fecha_fin)s, `Itinerario`=%(itinerario)s, updated_at=NOW() WHERE id = %(id)s;"
        return connectToMySQL('certificaion-2').query_db(query, datos)

    @classmethod
    def delete(cls, datos):
        query = "DELETE FROM viajes WHERE id = %(id)s;"
        return connectToMySQL('certificaion-2').query_db(query, datos)
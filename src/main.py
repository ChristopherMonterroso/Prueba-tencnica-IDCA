from flask import Flask, request, jsonify
from models import Persona
import pyodbc
app = Flask(__name__)

def connect_db():
    try:
        db = pyodbc.connect('Driver={SQL Server};'
                            'Server=DESKTOP-E8GKA5B\SQLEXPRESS;'
                            'Database=pruebaTecnica;'
                            'Trusted_Connection=yes;')
        return db
    except Exception as e:
          return  jsonify({'error': str(e)}), 500

db = connect_db()
@app.route('/api/persona', methods=['POST'])
def add_persona():
    data = request.get_json()

    # se valida que dentro del json existan los campos requeridos para agregar una nueva persona 
    required_fields = ['Nombres', 'Apellidos', 'FechaNacimiento', 'Genero', 'Direccion', 'EstadoCivil', 'DPI']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Falta el campo {field} en el JSON'}), 400

    nueva_persona = Persona(
        nombres=data['Nombres'],
        apellidos=data['Apellidos'],
        fecha_nacimiento=data['FechaNacimiento'],
        genero=data['Genero'],
        direccion=data['Direccion'],
        estado_civil=data['EstadoCivil'],
        dpi=data['DPI']
    )

    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Personas (Nombres, Apellidos, FechaNacimiento, Genero, Direccion, EstadoCivil, DPI) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            nueva_persona.nombres, nueva_persona.apellidos, nueva_persona.fecha_nacimiento,
            nueva_persona.genero, nueva_persona.direccion, nueva_persona.estado_civil, nueva_persona.dpi
        )

        db.commit()
        cursor.close()
        return jsonify({'message': 'Persona agregada correctamente'}), 201
    except pyodbc.IntegrityError as e:
        return jsonify({'error': f'Error de integridad: {e}'}), 400


@app.route('/api/personas', methods=['GET'])
def get_personas():
    try:
        # Se obtienen todas las personas de la base de datos
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Personas")
        personas = cursor.fetchall()
        cursor.close()
        personas_list = []
        for persona in personas:
            persona_dict = {
                'ID': persona[0],
                'Nombres': persona[1],
                'Apellidos': persona[2],
                'FechaNacimiento': persona[3],  
                'Genero': persona[4],
                'Direccion': persona[5],
                'EstadoCivil': persona[6],
                'DPI': persona[7]
            }
            personas_list.append(persona_dict)

        return jsonify(personas_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/persona/<dpi>', methods=['PUT'])
def update_persona(dpi):
    if len(dpi) != 13:
        return jsonify({'error': 'El DPI debe tener 13 dígitos'}), 400

    data = request.get_json()
    # Se busca la persona en la base de datos
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Personas WHERE DPI = ?", dpi)
    persona = cursor.fetchone()
    cursor.close()
    if not persona:
        return jsonify({'error': 'La persona no existe'}), 404
    # Se actualiza la persona en la db
    try:
        cursor = db.cursor()
        for key, value in data.items():
            cursor.execute(f"UPDATE Personas SET {key}=? WHERE DPI=?", value, dpi)

        db.commit()
        cursor.close()
        return jsonify({'message': 'Persona actualizada correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/persona/<dpi>', methods=['DELETE'])
def delete_persona(dpi):
    if len(dpi) != 13:
        return jsonify({'error': 'El DPI debe tener 13 dígitos'}), 400

    # Se busca la persona en la base de datos
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Personas WHERE DPI = ?", dpi)
    persona = cursor.fetchone()

    if not persona:
        cursor.close()
        return jsonify({'error': 'La persona no existe'}), 404

    # Se elimina la persona de la db
    try:
        cursor.execute("DELETE FROM Personas WHERE DPI = ?", dpi)
        db.commit()
        cursor.close()
        return jsonify({'message': 'Persona eliminada correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


    





if __name__ == '__main__':
    app.run(debug=True, port=5000)

from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta, date
import sqlite3
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turnos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para la base de datos
class CirujanosTurno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    nombre_turno = db.Column(db.String(50), nullable=False)
    cirujano1 = db.Column(db.String(100), nullable=False)
    cirujano2 = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Turno {self.fecha} {self.nombre_turno}>'

# Función para inicializar la base de datos con los datos por defecto
def inicializar_db():
    with app.app_context():
        db.create_all()
        
        # Verificar si ya hay datos
        if CirujanosTurno.query.first() is None:
            # Datos iniciales de cirujanos por turno
            datos_iniciales = {
                "Turno miércoles": ["Dr. Pérez", "Dr. González"],
                "Turno jueves": ["Dr. Rodríguez", "Dr. Sánchez"],
                "Volante 1": ["Dr. López", "Dr. Martínez"],
                "Volante 2": ["Dr. García", "Dr. Torres"],
                "Turno lunes": ["Dr. Díaz", "Dr. Ruiz"],
                "Turno martes": ["Dr. Morales", "Dr. Castro"]
            }
            
            # Crear registros para todo 2025 y 2026
            for año in [2025, 2026]:
                for mes in range(1, 13):
                    for dia in range(1, 32):
                        try:
                            fecha = datetime(año, mes, dia).date()
                            # Obtener el turno para esta fecha usando la lógica existente
                            turno = get_turno_for_date(fecha, TURNOS)
                            if turno:
                                nuevo_turno = CirujanosTurno(
                                    fecha=fecha,
                                    nombre_turno=turno['nombre'],
                                    cirujano1=datos_iniciales[turno['nombre']][0],
                                    cirujano2=datos_iniciales[turno['nombre']][1]
                                )
                                db.session.add(nuevo_turno)
                        except ValueError:
                            # Ignorar fechas inválidas (ej. 31 de abril)
                            continue
            
            db.session.commit()

# Modificar la ruta de actualización de cirujanos
@app.route('/actualizar_cirujanos', methods=['POST'])
def actualizar_cirujanos():
    try:
        data = request.get_json()
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        nombre_turno = data['nombreTurno']
        aplicar_futuro = data['aplicarFuturo']
        
        if aplicar_futuro:
            # Actualizar todos los turnos del mismo tipo desde la fecha en adelante
            turnos = CirujanosTurno.query.filter(
                CirujanosTurno.fecha >= fecha,
                CirujanosTurno.nombre_turno == nombre_turno
            ).all()
            
            for turno in turnos:
                turno.cirujano1 = data['cirujano1']
                turno.cirujano2 = data['cirujano2']
        else:
            # Actualizar solo el turno seleccionado
            turno = CirujanosTurno.query.filter_by(fecha=fecha).first()
            if turno:
                turno.cirujano1 = data['cirujano1']
                turno.cirujano2 = data['cirujano2']
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Diccionario de colores para los turnos
COLORES_TURNOS = {
    "Turno miércoles": "lightblue",
    "Turno jueves": "plum",
    "Volante 1": "khaki",
    "Volante 2": "salmon",
    "Turno lunes": "pink",
    "Turno martes": "lightgreen"
}

def generar_calendario_año(año):
    calendario = {}
    for mes in range(1, 13):
        for dia in range(1, 32):
            try:
                fecha = datetime(año, mes, dia).date()
                turno_db = CirujanosTurno.query.filter_by(fecha=fecha).first()
                if turno_db:
                    calendario[fecha] = {
                        'nombre': turno_db.nombre_turno,
                        'color': COLORES_TURNOS[turno_db.nombre_turno],
                        'cirujanos': [turno_db.cirujano1, turno_db.cirujano2]
                    }
            except ValueError:
                continue
    return calendario

# Constantes
DIAS_POR_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
NOMBRES_MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

class TurnoCiclo:
    def __init__(self, nombre, color, fecha_inicial, semana_inicial):
        self.nombre = nombre
        self.color = color
        self.fecha_inicial = fecha_inicial if isinstance(fecha_inicial, date) else fecha_inicial.date()
        self.semana_inicial = semana_inicial
        self.ciclo_dias = 42  # 6 semanas

    def get_turno_para_fecha(self, fecha):
        fecha = fecha if isinstance(fecha, date) else fecha.date()
        dias_desde_inicio = (fecha - self.fecha_inicial).days
        ciclo_actual = (dias_desde_inicio // self.ciclo_dias)
        dia_en_ciclo = dias_desde_inicio % self.ciclo_dias
        semana_en_ciclo = (dia_en_ciclo // 7 + self.semana_inicial) % 6
        
        if semana_en_ciclo == 0:
            semana_en_ciclo = 6

        dia_semana = fecha.weekday()
        dia_turno = {
            "Turno lunes": 0,
            "Turno martes": 1,
            "Turno miércoles": 2,
            "Turno jueves": 3
        }[self.nombre]

        if semana_en_ciclo <= 3:
            return dia_semana == dia_turno
        elif semana_en_ciclo == 4:
            return dia_semana == dia_turno or dia_semana == 6
        elif semana_en_ciclo == 5:
            return dia_semana == 5
        else:  # semana_en_ciclo == 6
            return dia_semana == 4

class TurnoVolante:
    def __init__(self, nombre, color, fecha_inicial):
        self.nombre = nombre
        self.color = color
        self.fecha_inicial = fecha_inicial if isinstance(fecha_inicial, date) else fecha_inicial.date()

    def get_turno_para_fecha(self, fecha):
        fecha = fecha if isinstance(fecha, date) else fecha.date()
        if self.nombre == "Volante 1":
            dias_desde_v1 = (fecha - datetime(2025, 1, 3).date()).days
            return dias_desde_v1 >= 0 and dias_desde_v1 % 6 == 0
        else:  # Volante 2
            dias_desde_v2 = (fecha - datetime(2025, 1, 4).date()).days
            return dias_desde_v2 >= 0 and dias_desde_v2 % 6 == 0

# Configuración de turnos con fechas consistentes
TURNOS = {
    "Turno miércoles": TurnoCiclo("Turno miércoles", "lightblue", 
                                 datetime(2025, 1, 1).date(), 3),  # Convertir a date
    "Turno jueves": TurnoCiclo("Turno jueves", "plum", 
                              datetime(2025, 1, 2).date(), 4),    # Convertir a date
    "Volante 1": TurnoVolante("Volante 1", "khaki", 
                             datetime(2025, 1, 3).date()),        # Convertir a date
    "Volante 2": TurnoVolante("Volante 2", "salmon", 
                             datetime(2025, 1, 4).date()),        # Convertir a date
    "Turno lunes": TurnoCiclo("Turno lunes", "pink", 
                             datetime(2025, 1, 6).date(), 2),     # Convertir a date
    "Turno martes": TurnoCiclo("Turno martes", "lightgreen", 
                              datetime(2025, 1, 7).date(), 3)     # Convertir a date
}

def get_turno_for_date(fecha, turnos):
    fecha = fecha if isinstance(fecha, date) else fecha.date()
    
    for turno_name, turno in turnos.items():
        if turno.get_turno_para_fecha(fecha):
            return {"nombre": turno.nombre, "color": turno.color}
    return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Calendario de Turnos 2025-2026</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        .year-container {
            margin-bottom: 50px;
        }
        .year-title {
            text-align: center;
            font-size: 24px;
            margin: 20px 0;
            padding: 10px;
            background-color: #333;
            color: white;
            border-radius: 5px;
        }
        .calendar-container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .mes {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: black;
            text-align: center;
        }
        .dias-container {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 5px;
        }
        .dia {
            min-height: 80px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            align-items: center;
            color: black;
        }
        .dia span {
            margin-top: 5px;
            padding: 5px;
            border-radius: 3px;
            width: 90%;
            text-align: center;
            font-size: 12px;
        }
        .weekday {
            font-weight: bold;
            text-align: center;
            padding: 5px;
            background-color: #f0f0f0;
            color: black;
        }
        
        /* Estilos para el modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 1;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.4);
        }
        
        .modal-content {
            background-color: #fefefe;
            margin: 15% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 300px;
            border-radius: 5px;
        }
        
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .turno-info {
            cursor: pointer;
            padding: 5px;
            border-radius: 3px;
        }
        
        .cirujanos {
            font-size: 11px;
            margin-top: 3px;
        }
        
        .modal input {
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .modal button {
            width: 100%;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
        }
        
        .modal button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <!-- Modal para editar cirujanos -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <h3>Editar Cirujanos</h3>
            
            <div class="form-group">
                <label>Fecha del turno:</label>
                <input type="text" id="fechaMostrada" readonly>
            </div>
            
            <div class="form-group">
                <label>Cirujano 1:</label>
                <input type="text" id="cirujano1" placeholder="Nombre del primer cirujano">
            </div>
            
            <div class="form-group">
                <label>Cirujano 2:</label>
                <input type="text" id="cirujano2" placeholder="Nombre del segundo cirujano">
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="aplicarFuturo" name="aplicarFuturo">
                <label for="aplicarFuturo">Cambio definitivo</label>
            </div>
            
            <input type="hidden" id="fechaTurno">
            <input type="hidden" id="nombreTurno">
            
            <div class="button-group">
                <button class="secondary" onclick="cerrarModal()">Cancelar</button>
                <button onclick="guardarCambios()">Guardar</button>
            </div>
        </div>
    </div>

    <div class="calendar-container">
        {% for año in [2025, 2026] %}
        <h1>Calendario de Turnos {{ año }}</h1>
        {% for mes in range(12) %}
        <div class="mes">
            <h2>{{ nombres_meses[mes] }}</h2>
            <div class="dias-container">
                {% for dia in ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"] %}
                    <div class="weekday">{{ dia }}</div>
                {% endfor %}
                
                {% set primer_dia = datetime(año, mes + 1, 1).weekday() %}
                {% for _ in range(primer_dia) %}
                    <div class="dia"></div>
                {% endfor %}
                
                {% for dia in range(1, dias_por_mes[mes] + 1) %}
                    {% set fecha = datetime(año, mes + 1, dia).date() %}
                    <div class="dia">
                        {{ dia }}
                        {% if fecha in calendarios[año] %}
                            <div class="turno-info" 
                                 onclick="editarTurno('{{ fecha }}', '{{ calendarios[año][fecha].cirujanos[0] }}', '{{ calendarios[año][fecha].cirujanos[1] }}', '{{ calendarios[año][fecha].nombre }}')"
                                 style="background-color: {{ calendarios[año][fecha].color }}">
                                {{ calendarios[año][fecha].nombre }}
                                <div class="cirujanos">
                                    {{ calendarios[año][fecha].cirujanos[0] }}<br>
                                    {{ calendarios[año][fecha].cirujanos[1] }}
                                </div>
                            </div>
                        {% endif %}
                    </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
        {% endfor %}
    </div>

    <script>
        const modal = document.getElementById('editModal');
        const span = document.getElementsByClassName('close')[0];

        function editarTurno(fecha, cirujano1, cirujano2, nombreTurno) {
            const [year, month, day] = fecha.split('-');
            const fechaObj = new Date(year, month - 1, day);
            const fechaFormateada = fechaObj.toLocaleDateString('es-ES', {
                day: '2-digit',
                month: 'long',
                year: 'numeric'
            });
            
            document.getElementById('fechaTurno').value = fecha;
            document.getElementById('fechaMostrada').value = fechaFormateada;
            document.getElementById('cirujano1').value = cirujano1;
            document.getElementById('cirujano2').value = cirujano2;
            document.getElementById('nombreTurno').value = nombreTurno;
            document.getElementById('aplicarFuturo').checked = false;
            modal.style.display = "block";
        }

        function guardarCambios() {
            const fecha = document.getElementById('fechaTurno').value;
            const cirujano1 = document.getElementById('cirujano1').value;
            const cirujano2 = document.getElementById('cirujano2').value;
            const nombreTurno = document.getElementById('nombreTurno').value;
            const aplicarFuturo = document.getElementById('aplicarFuturo').checked;
            
            fetch('/actualizar_cirujanos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fecha: fecha,
                    cirujano1: cirujano1,
                    cirujano2: cirujano2,
                    nombreTurno: nombreTurno,
                    aplicarFuturo: aplicarFuturo
                })
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    location.reload();
                } else {
                    alert('Error al guardar los cambios: ' + data.error);
                }
            });
            
            modal.style.display = "none";
        }

        function cerrarModal() {
            modal.style.display = "none";
        }

        span.onclick = cerrarModal;
        window.onclick = function(event) {
            if (event.target == modal) {
                cerrarModal();
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def show_calendar():
    calendarios = {
        2025: generar_calendario_año(2025),
        2026: generar_calendario_año(2026)
    }
    
    return render_template_string(
        HTML_TEMPLATE,
        datetime=datetime,
        calendarios=calendarios,
        dias_por_mes=DIAS_POR_MES,
        nombres_meses=NOMBRES_MESES
    )

if __name__ == '__main__':
    # Instalar las dependencias necesarias:
    # pip install flask-sqlalchemy
    inicializar_db()
    app.run(debug=True, port=8080)

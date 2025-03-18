from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class TurnoPattern:
    """Define el patrón de un turno fijo."""
    name: str
    designated_day: int  # 0=Lunes, 6=Domingo
    cycle_start: datetime  # Fecha de inicio del ciclo

def generate_fixed_turno(pattern: TurnoPattern, end_date: datetime) -> List[Tuple[datetime, str]]:
    """
    Genera las asignaciones para un turno fijo siguiendo el patrón de 6 semanas:
    - Semanas 1-4: turno en día designado
    - Semana 4: turno adicional en domingo
    - Semana 5: solo sábado
    - Semana 6: solo viernes
    """
    assignments = []
    current_cycle_start = pattern.cycle_start
    
    while current_cycle_start <= end_date:
        # Obtener el primer día designado del ciclo
        current = current_cycle_start
        while current.weekday() != pattern.designated_day:
            current += timedelta(days=1)
        
        # Semanas 1-4: turnos en día designado
        for week in range(4):
            assignment_date = current + timedelta(weeks=week)
            if assignment_date <= end_date:
                assignments.append((assignment_date, pattern.name))
        
        # Semana 4: turno adicional en domingo
        week4_start = current + timedelta(weeks=3)
        sunday_extra = week4_start
        while sunday_extra.weekday() != 6:  # Avanzar hasta el domingo
            sunday_extra += timedelta(days=1)
        if sunday_extra <= end_date:
            assignments.append((sunday_extra, pattern.name))
        
        # Semana 5: turno en sábado
        saturday = sunday_extra + timedelta(days=6)
        if saturday <= end_date:
            assignments.append((saturday, pattern.name))
        
        # Semana 6: turno en viernes
        friday = saturday + timedelta(days=6)
        if friday <= end_date:
            assignments.append((friday, pattern.name))
        
        # Siguiente ciclo comienza después del viernes
        # Calculamos exactamente 42 días (6 semanas) desde el inicio del ciclo actual
        current_cycle_start = current_cycle_start + timedelta(days=42)
    
    return assignments

def generate_volantes(start_date: datetime, end_date: datetime) -> List[Tuple[datetime, str]]:
    """
    Genera las asignaciones para los turnos volante.
    Volante 1 comienza el día especificado y retrocede un día cada semana.
    Volante 2 va siempre el día siguiente a Volante 1.
    """
    assignments = []
    current = start_date
    current_weekday = start_date.weekday()  # Comenzar en el día especificado
    
    while current <= end_date:
        if current <= end_date:
            assignments.append((current, "Volante 1"))
            next_day = current + timedelta(days=1)
            if next_day <= end_date:
                assignments.append((next_day, "Volante 2"))
        
        # Retroceder un día para la siguiente semana
        current_weekday = (current_weekday - 1) % 7
        current += timedelta(days=6)  # Avanzar a la siguiente semana
        while current.weekday() != current_weekday:
            current += timedelta(days=1)
    
    return assignments

def generate_annual_schedule(year: int) -> Dict[datetime.date, str]:
    """
    Genera el calendario completo para el año especificado.
    """
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    # Configurar fechas de inicio según febrero 2025
    # El turno lunes comienza el 3 de febrero
    # El turno martes comienza el 4 de febrero
    # El turno miércoles comienza el 5 de febrero
    # El turno jueves comienza el 6 de febrero
    # Los volantes comienzan el 1 y 2 de febrero
    
    # Primero generamos los volantes para asegurarnos de cubrir el inicio de febrero
    volante_start = datetime(year, 2, 1)  # Volante 1 comienza el 1 de febrero
    volante_assignments = generate_volantes(volante_start, end_date)
    
    patterns = [
        TurnoPattern("Turno lunes", 0, datetime(year, 2, 3)),    # Primer lunes de febrero
        TurnoPattern("Turno martes", 1, datetime(year, 2, 4)),   # Primer martes de febrero
        TurnoPattern("Turno miércoles", 2, datetime(year, 2, 5)), # Primer miércoles de febrero
        TurnoPattern("Turno jueves", 3, datetime(year, 2, 6))    # Primer jueves de febrero
    ]
    
    # Generar todas las asignaciones de turnos fijos
    all_assignments = []
    for pattern in patterns:
        assignments = generate_fixed_turno(pattern, end_date)
        all_assignments.extend(assignments)
    
    # Agregar las asignaciones de volantes
    all_assignments.extend(volante_assignments)
    
    # Convertir a diccionario y verificar conflictos
    schedule = {}
    conflicts = []
    for date, turno in sorted(all_assignments):
        day = date.date()
        if day in schedule:
            conflicts.append(f"CONFLICTO: {day} tiene asignado {schedule[day]} y {turno}")
        schedule[day] = turno
    
    # Verificar días sin asignación
    missing_days = []
    current = start_date.date()
    while current <= end_date.date():
        if current not in schedule:
            missing_days.append(current)
        current += timedelta(days=1)
    
    # Reportar problemas
    if conflicts:
        print("\nConflictos encontrados:")
        for conflict in conflicts:
            print(conflict)
    
    if missing_days:
        print("\nDías sin asignación:")
        for day in missing_days:
            print(f"- {day}")
    
    # Verificación específica para febrero 2025
    print("\nVerificación de febrero 2025:")
    start_feb = datetime(year, 2, 1).date()
    end_feb = datetime(year, 2, 28).date()
    current = start_feb
    while current <= end_feb:
        if current in schedule:
            print(f"{current}: {schedule[current]}")
        else:
            print(f"{current}: SIN ASIGNACIÓN")
        current += timedelta(days=1)
    
    return schedule

def generate_html_calendar(schedule: Dict[datetime.date, str]) -> str:
    """
    Genera una representación HTML del calendario de turnos.
    """
    # Definir colores para cada tipo de turno
    COLORS = {
        "Turno lunes": "#FFB6C1",     # Rosa claro
        "Turno martes": "#98FB98",    # Verde claro
        "Turno miércoles": "#87CEFA", # Azul claro
        "Turno jueves": "#DDA0DD",    # Púrpura claro
        "Volante 1": "#F0E68C",       # Amarillo claro
        "Volante 2": "#FFA07A"        # Salmón
    }
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Calendario de Turnos 2025</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f0f0f0;
            }
            .calendar {
                max-width: 1200px;
                margin: 0 auto;
            }
            .month {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .month-title {
                font-size: 24px;
                margin-bottom: 15px;
                color: #333;
            }
            .calendar-grid {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 5px;
            }
            .day-header {
                text-align: center;
                font-weight: bold;
                padding: 5px;
                background: #333;
                color: white;
            }
            .day {
                min-height: 80px;
                padding: 5px;
                border: 1px solid #ddd;
                text-align: left;
            }
            .day-number {
                font-weight: bold;
                margin-bottom: 5px;
            }
            .turno {
                font-size: 12px;
                padding: 2px 4px;
                border-radius: 3px;
                margin-bottom: 2px;
            }
            .empty {
                background: #f9f9f9;
            }
            .legend {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 20px 0;
                padding: 10px;
                background: white;
                border-radius: 5px;
            }
            .legend-item {
                display: flex;
                align-items: center;
                margin-right: 15px;
            }
            .legend-color {
                width: 20px;
                height: 20px;
                margin-right: 5px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
    <div class="calendar">
        <h1>Calendario de Turnos 2025</h1>
        
        <div class="legend">
    """
    
    # Agregar leyenda
    for turno, color in COLORS.items():
        html += f"""
            <div class="legend-item">
                <div class="legend-color" style="background: {color}"></div>
                <div>{turno}</div>
            </div>
        """
    
    html += "</div>"
    
    # Agrupar por meses
    months = {}
    for date, turno in schedule.items():
        if date.year == 2025:
            month = date.month
            if month not in months:
                months[month] = []
            months[month].append((date, turno))
    
    # Nombres de los meses en español
    MONTH_NAMES = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    
    # Nombres de los días en español
    DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # Generar calendario por mes
    for month in sorted(months.keys()):
        html += f'<div class="month"><div class="month-title">{MONTH_NAMES[month]}</div>'
        html += '<div class="calendar-grid">'
        
        # Agregar encabezados de días
        for day in DAY_NAMES:
            html += f'<div class="day-header">{day}</div>'
        
        # Obtener el primer día del mes
        first_day = datetime(2025, month, 1).date()
        # Ajustar el índice del día de la semana (0 = Lunes, 6 = Domingo)
        first_weekday = first_day.weekday()
        
        # Agregar días vacíos al principio
        for _ in range(first_weekday):
            html += '<div class="day empty"></div>'
        
        # Agregar los días del mes
        for date, turno in sorted(months[month]):
            color = COLORS.get(turno, "#ffffff")
            html += f"""
                <div class="day">
                    <div class="day-number">{date.day}</div>
                    <div class="turno" style="background: {color}">{turno}</div>
                </div>
            """
        
        html += '</div></div>'
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

def save_calendar_to_html(schedule: Dict[datetime.date, str], filename: str = "calendario_turnos_2025.html"):
    """
    Guarda el calendario en un archivo HTML.
    """
    html_content = generate_html_calendar(schedule)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Calendario guardado en {filename}")

# Generar y guardar el calendario
if __name__ == "__main__":
    schedule_2025 = generate_annual_schedule(2025)
    save_calendar_to_html(schedule_2025)

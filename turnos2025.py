from datetime import datetime, timedelta

def generate_volantes(start_date, end_date):
    """
    Genera las asignaciones para los turnos volante:
      - "Volante 1" se asigna en la fecha de inicio.
      - "Volante 2" se asigna el día siguiente.
      - Se repite cada 6 días.
    """
    assignments = []
    current = start_date
    while current <= end_date:
        assignments.append((current, "Volante 1"))
        next_day = current + timedelta(days=1)
        if next_day <= end_date:
            assignments.append((next_day, "Volante 2"))
        current += timedelta(days=6)
    return assignments

def get_sunday_of_week(date):
    """
    Dado un 'date', devuelve el domingo de esa semana.
    (Considerando Monday=0, Sunday=6)
    """
    days_to_sunday = 6 - date.weekday()
    return date + timedelta(days=days_to_sunday)

def generate_fixed_turno(cycle_start, turno_name, end_date):
    """
    Genera el calendario para un turno fijo según el patrón:
      - Semana 1: Asigna el turno en el día designado (fecha 'cycle_start').
      - Semana 2: +7 días.
      - Semana 3: +14 días.
      - Semana 4: +21 días (en este día se asigna el turno designado) y se añade extra el domingo de esa semana.
      - Semana 5 (adelanto): 6 días después del turno extra, se asigna el turno en sábado.
      - Semana 6 (adelanto): 6 días después del sábado, se asigna el turno en viernes.
      - Nuevo ciclo: Comienza 6 días después del turno adelantado al viernes.
    """
    assignments = []
    current_cycle_start = cycle_start
    while current_cycle_start <= end_date:
        # Semana 1: turno designado
        week1 = current_cycle_start
        if week1 <= end_date:
            assignments.append((week1, turno_name, "designado"))
        # Semana 2:
        week2 = current_cycle_start + timedelta(days=7)
        if week2 <= end_date:
            assignments.append((week2, turno_name, "designado"))
        # Semana 3:
        week3 = current_cycle_start + timedelta(days=14)
        if week3 <= end_date:
            assignments.append((week3, turno_name, "designado"))
        # Semana 4: turno designado y extra el domingo
        week4_designado = current_cycle_start + timedelta(days=21)
        if week4_designado <= end_date:
            assignments.append((week4_designado, turno_name, "designado"))
        extra_sunday = get_sunday_of_week(week4_designado)
        if extra_sunday <= end_date:
            assignments.append((extra_sunday, turno_name, "extra domingo"))
        # Semana 5: adelanto al sábado (6 días después del extra domingo)
        adv_sabado = extra_sunday + timedelta(days=6)
        if adv_sabado <= end_date:
            assignments.append((adv_sabado, turno_name, "adelanto sábado"))
        # Semana 6: adelanto al viernes (6 días después del sábado)
        adv_viernes = adv_sabado + timedelta(days=6)
        if adv_viernes <= end_date:
            assignments.append((adv_viernes, turno_name, "adelanto viernes"))
        # Nuevo ciclo inicia 6 días después del adelanto al viernes
        next_cycle_start = adv_viernes + timedelta(days=6)
        current_cycle_start = next_cycle_start
    return assignments

# Rango de proyección para todo el 2025
start_2025 = datetime(2025, 1, 1)
end_2025   = datetime(2025, 12, 31)

# --- Turnos Volante ---
# Según la realidad, Volante 1 inicia el 2 de febrero de 2025.
volante_start = datetime(2025, 2, 2)
volantes = generate_volantes(volante_start, end_2025)

# --- Turnos Fijos ---
# Se consideran los inicios reales de ciclo:
# Turno lunes: ciclo inicia el 10 de febrero de 2025.
lunes_cycle_start = datetime(2025, 2, 10)
turno_lunes = generate_fixed_turno(lunes_cycle_start, "Turno lunes", end_2025)

# Turno martes: ciclo inicia el 4 de febrero de 2025.
martes_cycle_start = datetime(2025, 2, 4)
turno_martes = generate_fixed_turno(martes_cycle_start, "Turno martes", end_2025)

# Turno miércoles: ciclo inicia el 29 de enero de 2025.
miercoles_cycle_start = datetime(2025, 1, 29)
turno_miercoles = generate_fixed_turno(miercoles_cycle_start, "Turno miércoles", end_2025)

# Turno jueves: ciclo inicia el 23 de enero de 2025.
jueves_cycle_start = datetime(2025, 1, 23)
turno_jueves = generate_fixed_turno(jueves_cycle_start, "Turno jueves", end_2025)

# --- Integración de todos los turnos ---
all_assignments = volantes + turno_lunes + turno_martes + turno_miercoles + turno_jueves
all_assignments.sort(key=lambda x: x[0])

print("Calendario de turnos 2025:")
for item in all_assignments:
    date_str = item[0].strftime("%Y-%m-%d")
    # Los volantes tienen dos elementos; los fijos, tres (incluyendo la fase)
    if len(item) == 2:
        print(f"{date_str}: {item[1]}")
    else:
        print(f"{date_str}: {item[1]} ({item[2]})")

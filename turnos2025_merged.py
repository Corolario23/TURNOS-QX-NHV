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
    Dado una fecha 'date', devuelve el domingo de esa semana
    (considerando que Monday=0 y Sunday=6).
    """
    days_to_sunday = 6 - date.weekday()
    return date + timedelta(days=days_to_sunday)

def generate_fixed_turno(cycle_start, turno_name, end_date):
    """
    Genera una lista de asignaciones para un turno fijo siguiendo el patrón:
      - Semana 1: asigna el turno en el día designado (fecha 'cycle_start').
      - Semana 2: +7 días.
      - Semana 3: +14 días.
      - Semana 4: +21 días (se asigna en la fecha designada) y se añade
                  un turno extra el domingo de esa semana.
      - Semana 5 (adelanto): 6 días después del turno extra (se asigna en sábado).
      - Semana 6 (adelanto): 6 días después del sábado (se asigna en viernes).
      - Nuevo ciclo: comienza 6 días después del adelanto del viernes.
    Devuelve una lista de tuplas con (fecha, turno_name, fase).
    """
    assignments = []
    current_cycle_start = cycle_start
    while current_cycle_start <= end_date:
        # Semana 1
        week1 = current_cycle_start
        if week1 <= end_date:
            assignments.append((week1, turno_name, "designado"))
        # Semana 2
        week2 = current_cycle_start + timedelta(days=7)
        if week2 <= end_date:
            assignments.append((week2, turno_name, "designado"))
        # Semana 3
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
        # Nuevo ciclo: 6 días después del adelanto al viernes
        next_cycle_start = adv_viernes + timedelta(days=6)
        current_cycle_start = next_cycle_start
    return assignments

# ––– Rango de proyección para el 2025 –––
start_2025 = datetime(2025, 1, 1)
end_2025   = datetime(2025, 12, 31)

# ––– Generación de Turnos Volante –––
# (Estos se generan de forma independiente y se dejan como están.)
volante_start = datetime(2025, 2, 2)  # Según lo real, Volante 1 inicia el 2 de febrero de 2025.
volantes = generate_volantes(volante_start, end_2025)

# ––– Generación de Turnos Fijos –––
# Usamos las fechas reales de inicio de ciclo:
lunes_cycle_start   = datetime(2025, 2, 10)  # Turno lunes
martes_cycle_start  = datetime(2025, 2, 4)   # Turno martes
miercoles_cycle_start = datetime(2025, 1, 29) # Turno miércoles
jueves_cycle_start  = datetime(2025, 1, 23)  # Turno jueves

turno_lunes     = generate_fixed_turno(lunes_cycle_start, "Turno lunes", end_2025)
turno_martes    = generate_fixed_turno(martes_cycle_start, "Turno martes", end_2025)
turno_miercoles = generate_fixed_turno(miercoles_cycle_start, "Turno miércoles", end_2025)
turno_jueves    = generate_fixed_turno(jueves_cycle_start, "Turno jueves", end_2025)

# ––– Fusionar asignaciones fijas en un diccionario para garantizar que
# cada día tenga máximo una asignación fija.
# Definimos una prioridad: (menor valor = mayor prioridad)
priority = {
    "Turno jueves": 1,
    "Turno miércoles": 2,
    "Turno martes": 3,
    "Turno lunes": 4
}

fixed_assignments = {}  # clave: fecha (date), valor: (turno, fase)
for turno_list in [turno_lunes, turno_martes, turno_miercoles, turno_jueves]:
    for (fecha, turno, fase) in turno_list:
        # Convertir a fecha (sin hora)
        day = fecha.date()
        if day in fixed_assignments:
            # Si ya existe asignación, conservar la de mayor prioridad
            existing_turno = fixed_assignments[day][0]
            if priority[turno] < priority[existing_turno]:
                fixed_assignments[day] = (turno, fase)
        else:
            fixed_assignments[day] = (turno, fase)

# ––– Combinar asignaciones volantes y fijas en un diccionario global –––
# Para cada día del 2025, se mostrará la asignación fija (si existe)
# y la asignación de volante (si existe).
global_calendar = {}

# Agregar asignaciones fijas:
for day, (turno, fase) in fixed_assignments.items():
    global_calendar[day] = {"Fijo": f"{turno} ({fase})"}

# Agregar asignaciones de volantes (pueden convivir, ya que son otro grupo)
for (fecha, vol) in volantes:
    day = fecha.date()
    # Si ya hay asignación de volante en ese día, concatenar; de lo contrario, crear la entrada.
    if day in global_calendar:
        global_calendar[day]["Volante"] = vol
    else:
        global_calendar[day] = {"Volante": vol}

# ––– Imprimir el calendario (ordenado por fecha) –––
print("Calendario de turnos 2025:")
for day in sorted(global_calendar.keys()):
    entry = global_calendar[day]
    date_str = day.strftime("%Y-%m-%d")
    fijo = entry.get("Fijo", "—")
    volante = entry.get("Volante", "—")
    print(f"{date_str}: Fijo -> {fijo} | Volante -> {volante}")

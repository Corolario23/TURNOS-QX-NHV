from datetime import date, timedelta

# Clase que mantiene el estado de cada equipo
class TeamState:
    def __init__(self, name, cycle_start, pattern, cycle_length):
        """
        name: nombre del turno (p.ej., "Turno lunes")
        cycle_start: fecha de inicio del ciclo actual (date)
        pattern: lista de offsets (en días) para asignaciones dentro del ciclo
        cycle_length: duración total del ciclo (en días)
        """
        self.name = name
        self.cycle_start = cycle_start
        self.pattern = pattern
        self.cycle_length = cycle_length
        self.index = 0  # índice del offset actual

    def next_date(self):
        # Devuelve la fecha de la próxima asignación para este equipo
        return self.cycle_start + timedelta(days=self.pattern[self.index])

    def update(self):
        # Se asignó el turno en la fecha actual; se avanza en el ciclo
        self.index += 1
        if self.index >= len(self.pattern):
            self.cycle_start = self.cycle_start + timedelta(days=self.cycle_length)
            self.index = 0

# Inicializamos los estados usando los datos reales de febrero 2025
# Separamos los equipos fijos y los volantes

# Equipos fijos
teams_fixed = []
teams_fixed.append(TeamState("Turno lunes", date(2025, 2, 1), [0, 6, 9, 16, 23], 30))
teams_fixed.append(TeamState("Turno martes", date(2025, 2, 4), [0, 7, 14, 21, 26], 31))
teams_fixed.append(TeamState("Turno miércoles", date(2025, 2, 5), [0, 7, 14, 18], 24))
teams_fixed.append(TeamState("Turno jueves", date(2025, 2, 6), [0, 7, 10, 16, 22], 28))

# Equipos volantes
teams_volante = []
teams_volante.append(TeamState("Volante 1", date(2025, 2, 2), [0], 6))
teams_volante.append(TeamState("Volante 2", date(2025, 2, 3), [0], 6))

# Definimos el rango de simulación: del 1 de febrero al 31 de diciembre de 2025
start_day = date(2025, 2, 1)
end_day = date(2025, 12, 31)
schedule = {}

current_day = start_day
while current_day <= end_day:
    assigned_team = None
    # Primero, consultamos los turnos fijos:
    for team in teams_fixed:
        if team.next_date() == current_day:
            if assigned_team is not None:
                raise Exception(f"Conflict on {current_day} among fixed teams: already assigned {assigned_team} and trying to assign {team.name}")
            assigned_team = team.name
            team.update()  # actualizamos el estado del equipo asignado
    # Si no hay asignación fija, consultamos los volantes:
    if assigned_team is None:
        for team in teams_volante:
            if team.next_date() == current_day:
                if assigned_team is not None:
                    raise Exception(f"Conflict on {current_day} among volantes: already assigned {assigned_team} and trying to assign {team.name}")
                assigned_team = team.name
                team.update()
    if assigned_team is None:
        raise Exception(f"No assignment for {current_day}")
    schedule[current_day] = assigned_team
    current_day += timedelta(days=1)

# Imprimimos el calendario final ordenado por fecha
print("Calendario de turnos 2025 (del 1 de febrero al 31 de diciembre):")
for day in sorted(schedule.keys()):
    print(f"{day}: {schedule[day]}")

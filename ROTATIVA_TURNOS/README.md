# Calendario de Turnos Rotativos

Sistema de calendario para gestionar turnos rotativos con ciclos de 6 semanas.

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
   ```python
   python -m venv .venv
   ```
3. Activar el entorno virtual:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Instalar dependencias:
   ```python
   pip install -r requirements.txt
   ```

## Uso

1. Ejecutar el servidor:
   ```python
   python app.py
   ```
2. Abrir en el navegador: http://localhost:8080

## Estructura de Turnos

- Turnos fijos (Lunes, Martes, Miércoles, Jueves)
  - Ciclo de 6 semanas
  - 3 semanas en su día
  - 4ta semana: día normal + domingo
  - 5ta semana: sábado
  - 6ta semana: viernes

- Volantes (1 y 2)
  - Ciclo de 6 días
  - Volante 1 comienza 3 de enero
  - Volante 2 comienza 4 de enero
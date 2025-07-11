import json
import os

TAREAS_FILE = 'tareas.json'

def convertir_tareas():
    if not os.path.exists(TAREAS_FILE):
        print("No existe el archivo tareas.json")
        return

    with open(TAREAS_FILE, 'r', encoding='utf-8') as f:
        try:
            tareas = json.load(f)
        except json.JSONDecodeError:
            print("Archivo JSON vacío o inválido")
            tareas = []

    # Si ya son diccionarios, no hacer nada
    if tareas and isinstance(tareas[0], dict):
        print("Las tareas ya están en formato actualizado.")
        return

    nuevas_tareas = [{"texto": tarea, "completada": False} for tarea in tareas]

    with open(TAREAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(nuevas_tareas, f, indent=2, ensure_ascii=False)
    print("Archivo convertido correctamente.")

if __name__ == "__main__":
    convertir_tareas()

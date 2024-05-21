import sqlite3
import time
from pynput import keyboard, mouse
from queue import Queue
from threading import Thread

# Conexão com o banco de dados SQLite
def db_worker(queue):
    conn = sqlite3.connect('atividade.db')
    cursor = conn.cursor()

    # Criação da tabela de registros de ociosidade
    cursor.execute('''CREATE TABLE IF NOT EXISTS ociosidade (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     inicio_ociosidade TEXT,
                     fim_ociosidade TEXT)''')
    conn.commit()

    while True:
        item = queue.get()
        if item is None:
            break
        inicio_ociosidade, fim_ociosidade = item
        cursor.execute('INSERT INTO ociosidade (inicio_ociosidade, fim_ociosidade) VALUES (?, ?)',
                       (inicio_ociosidade, fim_ociosidade))
        conn.commit()
        queue.task_done()

    conn.close()

# Variáveis de controle
tempo_inatividade = 0
inicio_ociosidade = None
event_queue = Queue()

# Inicia a thread do banco de dados
db_thread = Thread(target=db_worker, args=(event_queue,))
db_thread.start()

def reset_tempo_inatividade():
    global tempo_inatividade, inicio_ociosidade
    if inicio_ociosidade:
        fim_ociosidade = time.strftime('%Y-%m-%d %H:%M:%S')
        event_queue.put((inicio_ociosidade, fim_ociosidade))
        inicio_ociosidade = None
    tempo_inatividade = 0

# Funções de callback para os eventos de teclado e mouse
def on_press(key):
    reset_tempo_inatividade()

def on_click(x, y, button, pressed):
    reset_tempo_inatividade()

# Inicia os listeners para teclado e mouse
listener_teclado = keyboard.Listener(on_press=on_press)
listener_mouse = mouse.Listener(on_click=on_click)
listener_teclado.start()
listener_mouse.start()

try:
    while True:
        time.sleep(1)
        tempo_inatividade += 1
        if tempo_inatividade > 2:  # Configurar o tempo de ociosidade desejado (em segundos)
            print(f'Oscioso as {time.strftime('%Y-%m-%d %H:%M:%S')}')
            if not inicio_ociosidade:
                inicio_ociosidade = time.strftime('%Y-%m-%d %H:%M:%S')
except KeyboardInterrupt:
    listener_teclado.stop()
    listener_mouse.stop()
    event_queue.put(None)
    db_thread.join()

import sqlite3

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('atividade.db')
cursor = conn.cursor()

# Consulta para selecionar todos os registros de ociosidade
cursor.execute('SELECT * FROM ociosidade')

# Recupera todos os registros
registros = cursor.fetchall()

# Exibe os registros
print("Registros de ociosidade:")
print("ID | Início da Ociosidade | Fim da Ociosidade")
print("-" * 40)
for registro in registros:
    print(f"{registro[0]} | {registro[1]} | {registro[2]}")

# Fecha a conexão com o banco de dados
conn.close()


import sqlite3
import os

def migrate(db_path):
    if not os.path.exists(db_path):
        print(f"Banco {db_path} não encontrado, pulando...")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Iniciando migração no banco: {db_path}")

    # Colunas para Celula
    try:
        cursor.execute("ALTER TABLE celula ADD COLUMN dia_reuniao TEXT")
        print("Coluna dia_reuniao adicionada")
    except sqlite3.OperationalError:
        print("Coluna dia_reuniao já existe")

    try:
        cursor.execute("ALTER TABLE celula ADD COLUMN horario_reuniao TEXT")
        print("Coluna horario_reuniao adicionada")
    except sqlite3.OperationalError:
        print("Coluna horario_reuniao já existe")

    conn.commit()
    conn.close()
    print("Migração concluída!")

if __name__ == "__main__":
    migrate('igreja.db')
    migrate('instance/igreja.db')

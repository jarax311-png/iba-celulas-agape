import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('instance/igreja.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("ALTER TABLE membro ADD COLUMN rede_id INTEGER REFERENCES rede(id)")
            print("Coluna rede_id adicionada.")
        except Exception as e:
            print(f"Erro rede_id: {e}")

        try:
            cursor.execute("ALTER TABLE membro ADD COLUMN geracao_id INTEGER REFERENCES geracao(id)")
            print("Coluna geracao_id adicionada.")
        except Exception as e:
            print(f"Erro geracao_id: {e}")

        conn.commit()
        conn.close()
        print("Migração concluída.")
    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == "__main__":
    migrate()

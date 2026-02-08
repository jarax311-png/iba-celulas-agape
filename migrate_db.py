import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('instance/igreja.db')
        cursor = conn.cursor()
        
        # Verifica se coluna já existe
        cursor.execute("PRAGMA table_info(celula)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'lider_treinamento' not in columns:
            print("Adicionando coluna lider_treinamento...")
            cursor.execute("ALTER TABLE celula ADD COLUMN lider_treinamento VARCHAR(100)")
            conn.commit()
            print("Coluna adicionada com sucesso.")
        else:
            print("Coluna lider_treinamento já existe.")
            
        conn.close()
    except Exception as e:
        print(f"Erro na migração: {e}")

if __name__ == "__main__":
    migrate()

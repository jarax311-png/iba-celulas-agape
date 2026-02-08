import sqlite3
import os

def migrate_bio_foto():
    db_path = os.path.join('instance', 'igreja.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(membro)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'biografia' not in columns:
            print("Adicionando coluna biografia...")
            cursor.execute("ALTER TABLE membro ADD COLUMN biografia VARCHAR(500)")
            
        if 'foto_url' not in columns:
            print("Adicionando coluna foto_url...")
            cursor.execute("ALTER TABLE membro ADD COLUMN foto_url VARCHAR(200)")
            
        conn.commit()
        print("Migracao concluida com sucesso!")
        conn.close()
    except Exception as e:
        print(f"Erro na migração: {e}")

if __name__ == "__main__":
    migrate_bio_foto()

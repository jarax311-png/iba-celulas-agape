
import sqlite3
import time

def seed():
    schools = [
        ("Escola de Líderes", "Formação para novos líderes de célula.", "Terça 20h"),
        ("Maturidade no Espírito", "Curso de crescimento espiritual e fundamentos.", "Domingo 09h"),
        ("Seminário de Batalha Espiritual", "Aprenda a guerrear no espírito.", "Sábado 14h"),
        ("Curso de Casais", "Fortalecendo o matrimônio à luz da palavra.", "Quinta 20h"),
        ("Mestres de Vida", "Para homens que desejam ser sacerdotes do lar.", "Segunda 20h"),
        ("Mulheres que Vencem", "Curso exclusivo para o público feminino.", "Quarta 19h30"),
        ("Discipulado Pessoal", "Acompanhamento um a um.", "A combinar"),
        ("Liderança Avançada", "Para supervisores e pastores.", "Sexta 20h")
    ]

    try:
        conn = sqlite3.connect('igreja.db', timeout=10)
        cursor = conn.cursor()
        
        # Check if empty
        cursor.execute("SELECT count(*) FROM escola")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"Tabela vazia. Inserindo {len(schools)} escolas...")
            for nome, desc, horario in schools:
                cursor.execute("INSERT INTO escola (nome, descricao, dia_horario) VALUES (?, ?, ?)", (nome, desc, horario))
            conn.commit()
            print("Escolas inseridas com sucesso!")
        else:
            print(f"Tabela já tem {count} escolas. Nenhuma ação necessária.")
            
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    seed()

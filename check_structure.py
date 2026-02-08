from app import app, Rede, Geracao, Celula

with app.app_context():
    print("\n--- REDES ---")
    redes = Rede.query.all()
    if not redes: print("Nenhuma rede encontrada.")
    for r in redes:
        print(f"ID: {r.id} | Nome: {r.nome} | Líder: {r.lider_nome}")

    print("\n--- GERAÇÕES ---")
    geracoes = Geracao.query.all()
    if not geracoes: print("Nenhuma geração encontrada.")
    for g in geracoes:
        print(f"ID: {g.id} | Nome: {g.nome} | Rede ID: {g.rede_id}")

    print("\n--- CÉLULAS ---")
    celulas = Celula.query.all()
    if not celulas: print("Nenhuma célula encontrada.")
    for c in celulas:
        print(f"ID: {c.id} | Nome: {c.nome} | Rede ID: {c.rede_id} | Geração ID: {c.geracao_id}")

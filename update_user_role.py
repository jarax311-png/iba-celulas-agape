from app import app, db, Membro

email_alvo = "pinheirojunior31@gmail.com"

with app.app_context():
    user = Membro.query.filter_by(email=email_alvo).first()
    if user:
        user.tipo = 'Lider'
        db.session.commit()
        print(f"Sucesso! Usuario {user.nome} ({user.email}) agora e Lider.")
    else:
        print(f"Erro: Usuario com email {email_alvo} nao encontrado.")

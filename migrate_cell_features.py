from app import app, db, Aviso, PedidoOracao, Testemunho

with app.app_context():
    db.create_all()
    print("Tabelas de Célula (Aviso, Pedido, Testemunho) verificadas/criadas com sucesso!")

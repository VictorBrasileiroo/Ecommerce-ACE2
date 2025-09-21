#!/usr/bin/env python3
"""
Script para recriar o banco de dados com a nova estrutura
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine
from backend.models import Base, Usuario, Produto, Venda
from backend.auth import get_password_hash
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def recreate_database():
    print("🗑️ Tentando remover banco antigo...")
    try:
        os.remove("db.sqlite3")
        print("✅ Banco antigo removido")
    except (FileNotFoundError, PermissionError) as e:
        print(f"ℹ️ Não foi possível remover banco antigo: {e}")
        print("🔄 Continuando com criação da nova estrutura...")
    
    print("🏗️ Criando nova estrutura do banco...")
    Base.metadata.create_all(bind=engine)
    print("✅ Estrutura criada com sucesso!")
    
    # Criar usuário admin
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    print("👤 Criando usuário admin...")
    admin_user = Usuario(
        email="admin@admin.com",
        senha_hash=get_password_hash("admin")
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print("✅ Usuário admin criado!")
    
    # Criar alguns produtos de exemplo
    print("📦 Criando produtos de exemplo...")
    produtos_exemplo = [
        {"nome": "Notebook Dell", "categoria": "Eletrônicos", "preco": 2500.00},
        {"nome": "Mouse Logitech", "categoria": "Periféricos", "preco": 150.00},
        {"nome": "Teclado Mecânico", "categoria": "Periféricos", "preco": 300.00},
        {"nome": "Monitor Samsung", "categoria": "Eletrônicos", "preco": 800.00},
        {"nome": "Headset Gamer", "categoria": "Periféricos", "preco": 200.00}
    ]
    
    for produto_data in produtos_exemplo:
        produto = Produto(**produto_data)
        db.add(produto)
    
    db.commit()
    print("✅ Produtos de exemplo criados!")
    
    # Criar algumas vendas de exemplo para o admin
    print("💰 Criando vendas de exemplo...")
    produtos = db.query(Produto).all()
    vendas_exemplo = [
        {"data": datetime(2024, 1, 15).date(), "produto_id": produtos[0].id, "quantidade": 2, "valor_total": 5000.00},
        {"data": datetime(2024, 1, 20).date(), "produto_id": produtos[1].id, "quantidade": 5, "valor_total": 750.00},
        {"data": datetime(2024, 2, 10).date(), "produto_id": produtos[2].id, "quantidade": 3, "valor_total": 900.00},
        {"data": datetime(2024, 2, 15).date(), "produto_id": produtos[3].id, "quantidade": 1, "valor_total": 800.00},
        {"data": datetime(2024, 3, 5).date(), "produto_id": produtos[4].id, "quantidade": 4, "valor_total": 800.00},
        {"data": datetime(2024, 3, 12).date(), "produto_id": produtos[0].id, "quantidade": 1, "valor_total": 2500.00},
        {"data": datetime(2024, 3, 20).date(), "produto_id": produtos[1].id, "quantidade": 3, "valor_total": 450.00},
        {"data": datetime(2024, 4, 2).date(), "produto_id": produtos[2].id, "quantidade": 2, "valor_total": 600.00},
        {"data": datetime(2024, 4, 8).date(), "produto_id": produtos[3].id, "quantidade": 2, "valor_total": 1600.00},
        {"data": datetime(2024, 4, 15).date(), "produto_id": produtos[4].id, "quantidade": 6, "valor_total": 1200.00}
    ]
    
    for venda_data in vendas_exemplo:
        venda = Venda(
            **venda_data,
            usuario_id=admin_user.id  # Associar ao admin
        )
        db.add(venda)
    
    db.commit()
    print("✅ Vendas de exemplo criadas!")
    
    db.close()
    print("\n🎉 Banco de dados recriado com sucesso!")
    print("👤 Login admin: admin@admin.com / admin")
    print("📊 10 vendas de exemplo criadas")

if __name__ == "__main__":
    recreate_database()

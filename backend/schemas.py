from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional

# Schemas de Request
class UserCreate(BaseModel):
    email: str = Field(..., example="novo@exemplo.com", description="Email do usuário")
    password: str = Field(..., example="senha123", min_length=4, description="Senha (mínimo 4 caracteres)")

# Schemas de Response
class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", example="bearer")

class MessageResponse(BaseModel):
    message: str = Field(..., example="Usuário criado com sucesso")
    email: Optional[str] = Field(None, example="novo@exemplo.com")

class ImportResponse(BaseModel):
    status: str = Field(..., example="Importação realizada")

class MetricsMonth(BaseModel):
    mes: str = Field(..., example="2024-01", description="Mês no formato YYYY-MM")
    receita: float = Field(..., example=5000.0, description="Receita do mês")

class TopProduto(BaseModel):
    nome: str = Field(..., example="Notebook Dell")
    receita: float = Field(..., example=5000.0)
    quantidade: int = Field(..., example=2)

class VendasCategoria(BaseModel):
    categoria: Optional[str] = Field(None, example="Eletrônicos")
    receita: float = Field(..., example=5000.0)
    num_vendas: int = Field(..., example=1)

class MetricsResponse(BaseModel):
    receita_total: float = Field(..., example=12500.5, description="Receita total do usuário")
    ticket_medio: float = Field(..., example=250.01, description="Valor médio por venda")
    produto_mais_vendido: Optional[str] = Field(None, example="Mouse Logitech", description="Nome do produto com mais vendas")
    evolucao_mensal: List[MetricsMonth] = Field(default_factory=list, description="Evolução da receita por mês")
    top_produtos: List[TopProduto] = Field(default_factory=list, description="Top 5 produtos por receita")
    vendas_categoria: List[VendasCategoria] = Field(default_factory=list, description="Vendas agrupadas por categoria")
    total_vendas: int = Field(..., example=9, description="Total de vendas do usuário")
    produtos_unicos: int = Field(..., example=3, description="Quantidade de produtos únicos vendidos")

    class Config:
        schema_extra = {
            "example": {
                "receita_total": 12500.5,
                "ticket_medio": 250.01,
                "produto_mais_vendido": "Mouse Logitech",
                "evolucao_mensal": [
                    {"mes": "2024-01", "receita": 5000.0},
                    {"mes": "2024-02", "receita": 7500.5}
                ],
                "top_produtos": [
                    {"nome": "Notebook Dell", "receita": 5000.0, "quantidade": 2},
                    {"nome": "Mouse Logitech", "receita": 750.0, "quantidade": 5}
                ],
                "vendas_categoria": [
                    {"categoria": "Eletrônicos", "receita": 5000.0, "num_vendas": 1},
                    {"categoria": "Periféricos", "receita": 8250.5, "num_vendas": 8}
                ],
                "total_vendas": 9,
                "produtos_unicos": 3
            }
        }

class ForecastOut(BaseModel):
    produto_id: int = Field(..., example=1)
    produto_nome: Optional[str] = Field(None, example="Notebook Dell")
    data_prevista: date = Field(..., example="2025-01-01", description="Data da previsão")
    qtd_prevista: float = Field(..., example=3000.0, description="Receita prevista para o produto")
    intervalo_conf: Optional[str] = Field(None, example="[2500.0,3500.0]", description="Intervalo de confiança da previsão")

    class Config:
        schema_extra = {
            "example": {
                "produto_id": 1,
                "produto_nome": "Notebook Dell",
                "data_prevista": "2025-01-01",
                "qtd_prevista": 3000.0,
                "intervalo_conf": "[2500.0,3500.0]"
            }
        }

class MLResponse(BaseModel):
    status: str = Field(..., example="success", description="Status da execução: 'success' ou 'error'")
    message: str = Field(..., example="ML executado com sucesso", description="Mensagem detalhada do resultado")

    class Config:
        schema_extra = {
            "examples": {
                "success": {
                    "summary": "Execução bem-sucedida",
                    "value": {
                        "status": "success",
                        "message": "ML executado com sucesso"
                    }
                },
                "error": {
                    "summary": "Erro na execução",
                    "value": {
                        "status": "error",
                        "message": "Erro: ModuleNotFoundError: No module named 'numpy'"
                    }
                }
            }
        }

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Mensagem de erro detalhada")

    class Config:
        schema_extra = {
            "examples": {
                "validation_error": {
                    "summary": "Erro de validação",
                    "value": {"detail": "Arquivo deve ser CSV"}
                },
                "auth_error": {
                    "summary": "Erro de autenticação",
                    "value": {"detail": "Não foi possível validar as credenciais"}
                },
                "duplicate_error": {
                    "summary": "Email já existe",
                    "value": {"detail": "Email já está em uso"}
                }
            }
        }
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .models import Usuario
from .database import get_db
from .schemas import UserCreate, Token, MessageResponse, ErrorResponse
import os
import hashlib
from datetime import datetime, timedelta

SECRET_KEY = os.getenv('SECRET_KEY', 'secret')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()

def verify_password(plain_password, hashed_password):
    return get_password_hash(plain_password) == hashed_password

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user or not verify_password(password, user.senha_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/auth/login",
            response_model=Token,
            summary="Fazer login no sistema",
            description="""Autenticação de usuário via OAuth2 Password Flow.
            
            **Formato da requisição**: application/x-www-form-urlencoded
            - username: email do usuário
            - password: senha do usuário
            
            **Credenciais padrão para teste**:
            - Email: admin@admin.com
            - Senha: admin
            
            Retorna um token JWT válido por 60 minutos.""",
            responses={
                200: {
                    "description": "Login realizado com sucesso",
                    "content": {
                        "application/json": {
                            "example": {
                                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                "token_type": "bearer"
                            }
                        }
                    }
                },
                400: {
                    "description": "Credenciais inválidas",
                    "model": ErrorResponse,
                    "content": {
                        "application/json": {
                            "example": {"detail": "Usuário ou senha inválidos"}
                        }
                    }
                }
            })
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha inválidos")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/register",
            response_model=MessageResponse,
            summary="Cadastrar novo usuário",
            description="""Cria uma nova conta de usuário no sistema.
            
            **Validações**:
            - Email deve ser único (não pode já existir)
            - Senha deve ter pelo menos 4 caracteres
            - Email deve ter formato válido
            
            A senha é criptografada usando SHA256 antes de ser salva.""",
            responses={
                200: {
                    "description": "Usuário criado com sucesso",
                    "content": {
                        "application/json": {
                            "example": {
                                "message": "Usuário criado com sucesso",
                                "email": "novo@exemplo.com"
                            }
                        }
                    }
                },
                400: {
                    "description": "Erro na validação",
                    "model": ErrorResponse,
                    "content": {
                        "application/json": {
                            "examples": {
                                "email_exists": {
                                    "summary": "Email já cadastrado",
                                    "value": {"detail": "Email já está em uso"}
                                },
                                "validation_error": {
                                    "summary": "Dados inválidos",
                                    "value": {"detail": "Senha deve ter pelo menos 4 caracteres"}
                                }
                            }
                        }
                    }
                }
            })
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Verificar se email já existe
    existing_user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já está em uso")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = Usuario(email=user_data.email, senha_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Usuário criado com sucesso", "email": new_user.email}

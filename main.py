from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from datetime import datetime, timedelta, timezone
import string
import random

# IMPORT NOVO: As ferramentas do Rate Limiter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# INICIALIZANDO O LIMITER: Ele identifica os usuários pelo endereço IP
limiter = Limiter(key_func=get_remote_address)

# A sua conexão blindada (IPv4) com o Supabase
DATABASE_URL = "postgresql://postgres.kkpzdyktojytzksygmpt:S5BC7A9IQMP1YxR2@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class URLModel(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True) 

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CONFIGURAÇÃO NOVA: Registrando o Limiter no app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def gerar_codigo(tamanho=6):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

@app.get("/")
def home():
    return {"mensagem": "API de Encurtador de URL está online e blindada!"}

# ROTA PROTEGIDA: Limite de 5 criações por minuto por IP
@app.post("/encurtar")
@limiter.limit("5/minute")
def encurtar_url(request: Request, url: str, dias_validos: int = 7, db: Session = Depends(get_db)):
    codigo = gerar_codigo()
    
    data_expiracao = datetime.now(timezone.utc) + timedelta(days=dias_validos)
    
    nova_url = URLModel(
        original_url=url, 
        short_code=codigo, 
        expires_at=data_expiracao
    )
    
    db.add(nova_url)
    db.commit()
    db.refresh(nova_url)
    
    return {
        "link_curto": f"http://localhost:8000/{codigo}",
        "original": url,
        "expira_em": data_expiracao.strftime("%d/%m/%Y %H:%M")
    }

@app.get("/{codigo}")
def redirecionar(codigo: str, db: Session = Depends(get_db)):
    db_url = db.query(URLModel).filter(URLModel.short_code == codigo).first()
    
    if db_url:
        if db_url.expires_at and db_url.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="Este link expirou e não está mais disponível!")
            
        db_url.clicks += 1
        db.commit()
        
        return RedirectResponse(url=db_url.original_url)
        
    raise HTTPException(status_code=404, detail="Link não encontrado no sistema.")

# ROTA NOVA: Relatório e Estatísticas do Link
@app.get("/estatisticas/{codigo}")
def ver_estatisticas(codigo: str, db: Session = Depends(get_db)):
    db_url = db.query(URLModel).filter(URLModel.short_code == codigo).first()
    
    if not db_url:
        raise HTTPException(status_code=404, detail="Link não encontrado no sistema.")
        
    # Checa se o link ainda está valendo para te avisar no relatório
    status = "🟢 Ativo"
    if db_url.expires_at and db_url.expires_at < datetime.now(timezone.utc):
        status = "🔴 Expirado"
        
    return {
        "link_original": db_url.original_url,
        "link_curto": f"http://localhost:8000/{codigo}",
        "cliques_totais": db_url.clicks,
        "status": status,
        "criado_em": db_url.created_at.strftime("%d/%m/%Y %H:%M")
    }
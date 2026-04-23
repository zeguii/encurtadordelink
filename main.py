from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
# IMPORT ATUALIZADO: Adicionamos o 'timezone'
from datetime import datetime, timedelta, timezone
import string
import random

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
    return {"mensagem": "API de Encurtador de URL está online!"}

@app.post("/encurtar")
def encurtar_url(url: str, dias_validos: int = 7, db: Session = Depends(get_db)):
    codigo = gerar_codigo()
    
    # CORREÇÃO: Agora dizemos explicitamente para usar o fuso horário UTC
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
        # CORREÇÃO: Comparando a data do banco com a data atual (também em UTC)
        if db_url.expires_at and db_url.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="Este link expirou e não está mais disponível!")
            
        db_url.clicks += 1
        db.commit()
        
        # CORREÇÃO: Agora ele faz o redirecionamento real da página!
        return RedirectResponse(url=db_url.original_url)
        
    raise HTTPException(status_code=404, detail="Link não encontrado no sistema.")
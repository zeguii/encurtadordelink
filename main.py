from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from datetime import datetime
import string
import random

DATABASE_URL = "postgresql://postgres:S5BC7A9IQMP1YxR2@db.kkpzdyktojytzksygmpt.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class URLModel(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

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

@app.post("/encurtar")
def encurtar_url(url: str, db: Session = Depends(get_db)):
    codigo = gerar_codigo()
    nova_url = URLModel(original_url=url, short_code=codigo)
    db.add(nova_url)
    db.commit()
    db.refresh(nova_url)
    return {"link_curto": f"http://localhost:8000/{codigo}"}

@app.get("/{codigo}")
def redirecionar(codigo: str, db: Session = Depends(get_db)):
    db_url = db.query(URLModel).filter(URLModel.short_code == codigo).first()
    if db_url:
        db_url.clicks += 1
        db.commit()
        return {"redirecionando_para": db_url.original_url, "cliques_totais": db_url.clicks}
    raise HTTPException(status_code=404, detail="URL não encontrada")
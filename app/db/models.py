from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped 
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    pass

class ParserData(Base):
    __tablename__ = "parser_data"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    url:Mapped[str] = mapped_column(unique=True)
    theme: Mapped[str] = mapped_column(String(50),nullable=True)
    header: Mapped[str] = mapped_column(String(200))
    text: Mapped[str] = mapped_column()
    author: Mapped[str] = mapped_column(String(50), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable= True)
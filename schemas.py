"""
Database Schemas for Nakama OS

Each Pydantic model = one MongoDB collection (lowercased class name).
These schemas are used for validation when creating documents.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Core user
class Nakama(BaseModel):
    username: str = Field(..., description="Unique handle for the nakama")
    rank: str = Field("Rookie", description="Crew rank: Rookie, Supernova, Shichibukai, Yonko")
    belly: int = Field(0, ge=0, description="Utility token balance ($BELLY)")
    nakamas: int = Field(0, ge=0, description="Governance score / $NAKAMAS snapshot")
    last_active_ts: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Last activity timestamp")

# Den Den Messenger
class Chat_Room(BaseModel):
    name: str
    topic: Optional[str] = None
    is_private: bool = False

class Chat_Message(BaseModel):
    room_id: str
    sender: str
    text: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Pacto_Contrato(BaseModel):
    title: str
    party_a: str
    party_b: str
    amount_nakamas: Optional[int] = 0
    escrow_address: Optional[str] = None
    status: str = Field("draft", description="draft|deployed|released|cancelled")

# Diario de Bitácora
class Mision(BaseModel):
    title: str
    description: Optional[str] = None
    reward_belly: int = 0

class Nakama_Mision(BaseModel):
    nakama: str
    mision_id: str
    status: str = Field("En Progreso", description="En Progreso|Completada|Fallida")

class Logro(BaseModel):
    name: str
    icon: Optional[str] = None

class Nakama_Logro(BaseModel):
    nakama: str
    logro_id: str
    obtained_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

# Mercado de Sabaody (DAO)
class Proyecto(BaseModel):
    title: str
    description: Optional[str] = None
    vibe_css: Optional[str] = Field(None, description="Custom CSS to inject on project page")
    vibe_music_url: Optional[str] = None

class Inversion_Proyecto(BaseModel):
    proyecto_id: str
    investor: str
    amount_belly: int

class DAO_Propuesta(BaseModel):
    proyecto_id: Optional[str] = None
    proposer: str
    title: str
    details: Optional[str] = None
    stake_nakamas: int = 0

# Arcade de Jaya
class Arcade_Juego(BaseModel):
    title: str
    embed_url: str
    thumbnail: Optional[str] = None

class Peticion_Juego(BaseModel):
    title: str
    requested_by: str
    total_belly_votado: int = 0

# Isla del Sonido (TUNOVA)
class Cancion(BaseModel):
    title: str
    artist: Optional[str] = None
    audio_file_url: str
    cassette_art: Optional[str] = None

class Mechero_Voto(BaseModel):
    cancion_id: str
    voter: str
    belly_spent: int = 0
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

# Asalto de Habilidades
class Sala_Chat_Juego(BaseModel):
    name: str
    description: Optional[str] = None

class Nakama_Status_Juego(BaseModel):
    nakama: str
    sala_id: str
    stamina: int = 100
    pi_score: int = 0

class Habilidad(BaseModel):
    codigo: str = Field(..., description="/gomu_gomu_pistol, etc.")
    stamina_cost: int = 10
    effect: Optional[str] = None

# i18n
class Ecos_Globales(BaseModel):
    string_id: str
    eco_es: str
    eco_en: str
    eco_ja: str

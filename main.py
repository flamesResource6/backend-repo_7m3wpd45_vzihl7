import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
import schemas as s

app = FastAPI(title="Nakama OS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!", "service": "Nakama OS API"}

@app.get("/api/ping")
def ping():
    return {"pong": True}

@app.get("/schema")
def get_schema() -> Dict[str, Any]:
    """Expose Pydantic schemas for the database viewer and tooling"""
    def model_schema(model: BaseModel) -> Dict[str, Any]:
        return model.model_json_schema()

    models = {
        "nakama": model_schema(s.Nakama),
        "chat_room": model_schema(s.Chat_Room),
        "chat_message": model_schema(s.Chat_Message),
        "pacto_contrato": model_schema(s.Pacto_Contrato),
        "mision": model_schema(s.Mision),
        "nakama_mision": model_schema(s.Nakama_Mision),
        "logro": model_schema(s.Logro),
        "nakama_logro": model_schema(s.Nakama_Logro),
        "proyecto": model_schema(s.Proyecto),
        "inversion_proyecto": model_schema(s.Inversion_Proyecto),
        "dao_propuesta": model_schema(s.DAO_Propuesta),
        "arcade_juego": model_schema(s.Arcade_Juego),
        "peticion_juego": model_schema(s.Peticion_Juego),
        "cancion": model_schema(s.Cancion),
        "mechero_voto": model_schema(s.Mechero_Voto),
        "sala_chat_juego": model_schema(s.Sala_Chat_Juego),
        "nakama_status_juego": model_schema(s.Nakama_Status_Juego),
        "habilidad": model_schema(s.Habilidad),
        "ecos_globales": model_schema(s.Ecos_Globales),
    }
    return {"models": models}

# --- Minimal API examples (backend-first) ---

@app.post("/api/nakama")
def create_nakama(nakama: s.Nakama):
    """Create a Nakama profile"""
    inserted_id = create_document("nakama", nakama)
    return {"ok": True, "id": inserted_id}

@app.get("/api/i18n")
def get_i18n(lang: str = "ES"):
    """Return key->text mapping from Ecos_Globales for selected language"""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    lang = lang.upper()
    field = {"ES": "eco_es", "EN": "eco_en", "JA": "eco_ja"}.get(lang)
    if not field:
        raise HTTPException(status_code=400, detail="Unsupported language")
    rows = db["ecos_globales"].find({}, {"_id": 0, "string_id": 1, field: 1})
    mapping = {r["string_id"]: r.get(field, "") for r in rows}
    return {"lang": lang, "strings": mapping}

@app.post("/api/reward/heartbeat")
def heartbeat(username: str):
    """Update last_active_ts for a Nakama (simple heartbeat)."""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    from datetime import datetime
    res = db["nakama"].update_one({"username": username}, {"$set": {"last_active_ts": datetime.utcnow()}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Nakama not found")
    return {"ok": True}

@app.post("/api/reward/tick")
def reward_tick(minutes: int = 10, belly_per_active: int = 5):
    """Credit $BELLY to active Nakamas in the last X minutes. Intended for cron/scheduler."""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    from datetime import datetime, timedelta
    threshold = datetime.utcnow() - timedelta(minutes=minutes)
    res = db["nakama"].update_many({"last_active_ts": {"$gte": threshold}}, {"$inc": {"belly": belly_per_active}})
    return {"ok": True, "rewarded": res.modified_count, "belly": belly_per_active}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

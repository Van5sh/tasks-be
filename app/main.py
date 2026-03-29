from fastapi import FastAPI
from app.db import get_db

app=FastAPI()

def main():
    print("Starting the application...")
    @app.get("/health")
    async def read_root():
        db=get_db()
        await db.command("ping")
        return {"status": "ok"}

if __name__ == "__main__":
    main()

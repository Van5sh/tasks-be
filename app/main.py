from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.db.database import get_db
from app.api.auth.routes import router as auth_router
from app.api.tasks.routes import router as tasks_router
from app.api.users.routes import router as users_router

app = FastAPI(
    title="Tasks API",
    version="1.0.0",
    description="REST API with JWT auth, role-based access, and task CRUD.",
)


@app.get("/health")
async def read_root():
    db = get_db()
    await db.command("ping")
    return {"status": "ok"}


app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/api/v1", tags=["tasks"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["components"] = schema.get("components", {})
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Apply bearer auth globally to protected routes via Swagger "Authorize"
    schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

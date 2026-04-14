import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from app.db.database import get_db, init_db
from app.api.auth.routes import router as auth_router
from app.api.tasks.routes import router as tasks_router
from app.api.users.routes import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Tasks API",
    version="1.0.0",
    description="REST API with JWT auth, role-based access, and task CRUD.",
    lifespan=lifespan,
)

frontend_origin = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_available_routes():
    routes = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        routes.append(
            {
                "path": route.path,
                "methods": sorted(route.methods - {"HEAD", "OPTIONS"}),
                "name": route.name,
            }
        )
    return sorted(routes, key=lambda route: route["path"])


@app.get("/")
async def available_routes():
    return {"available_routes": _get_available_routes()}


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
    for path, methods in schema.get("paths", {}).items():
        is_public_auth_route = path.startswith("/api/v1/auth/")
        for operation in methods.values():
            if is_public_auth_route:
                operation["security"] = []
            else:
                operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

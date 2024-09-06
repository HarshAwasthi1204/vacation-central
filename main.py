# from fastapi import FastAPI, status
from fastapi import FastAPI, Request
from dbstuff.dbcrud import db_router
from routes.routes import routes_router
from auth.auth import auth_router
from fastapi.staticfiles import StaticFiles
# from fastapi.responses import RedirectResponse
# import random

tags = [
    {
        "name": "Navigation",
        "description": "General navigation endpoints.",
    },
    {
        "name": "Auth",
        "description": "Authentication & Authorization endpoints.",
    },
    {
        "name": "Database",
        "description": "Database operation endpoints.",
    }
]

app = FastAPI(title="Vacation Central",
              description="API for Vacation Central",
            #   summary="Backend API stuff for Vacation Central",
              version="0.1.0",
              openapi_tags=tags)

# randlst = []

# @app.middleware("http")
# async def session_middleware(request, call_next):
#     if request.url.path not in ["/", "/login", "/signup"] and not request.url.path.startswith("/static"):
#         session = request.headers.get("session")
#         if session is None:
#             return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
#     response = await call_next(request)
#     return response

# @app.middleware("http")
# async def add_session_middleware(request, call_next):
#     session = request.headers.get("session")
#     if session is None:
#         session_id = random.randint(1,1000)
#         while True:
#             if session_id not in randlst:
#                 session_header = {"session": session_id}
#                 request.headers.update = session_header
#                 randlst.append(session_id)
#                 break
#             else:
#                 session_id = random.randint(1,1000)
        
#     else:
#         session_data = db.Sessions.find()
#     response = await call_next(request)
#     return response

# @app.middleware("http")
# async def redirect_unauthorized_middleware(request, call_next):
#     response = await call_next(request)
#     if response.status_code == 401:
#         response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
#     return response

@app.middleware("http")
async def headers_middleware(request: Request, call_next):
    headers = request.headers
    if "Authorization" in headers:
        print("Authorization: ", headers["Authorization"])
    else:
        print("No Authorization header.")
    response = await call_next(request)
    return response

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(routes_router, tags=["Navigation"])
app.include_router(auth_router, tags=["Auth"])
app.include_router(db_router, tags=["Database"])
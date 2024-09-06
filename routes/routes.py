from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth import get_token_by_authentication
from models.models import UnsecureUser, ContactNo
from dbstuff.dbcrud import create_user
from datetime import datetime
from auth.auth import decode_token

routes_router = APIRouter()

templates = Jinja2Templates(directory = "templates")

# @routes_router.get('/')
# async def home():
#     return "Hello World"

# def get_session_data():
#     session_data = db.Sessions.find()
#     return session_data

# temp_global_user = None
# unauthorized_user = None
# redirect = None

# @routes_router.get("/logout")
# async def logout():
#     global temp_global_user
#     global unauthorized_user
#     global redirect
#     temp_global_user = None
#     unauthorized_user = None
#     redirect = None
#     return RedirectResponse("/",status_code=status.HTTP_302_FOUND)

# @routes_router.post("/updateuser/{username}")
# async def update_user_stuff(request : Request, username: str, profusername: Annotated[str, Form()], fullname: Annotated[str, Form()], contact: Annotated[str, Form()],address: Annotated[str, Form()], region: Annotated[str, Form()], dob: Annotated[str, Form()], sex:Annotated[str,Form()], password: Annotated[str, Form()], email: Annotated[str, Form()]):
#     global temp_global_user
#     global unauthorized_user
#     global redirect
#     updated_user = UnsecuredUser(username=profusername, full_name=fullname, contact_no=contact, addresses=address, region=region, dob=dob, email=email, password=password, sex=sex)
#     read_user_query = db.Users.find_one({"email": email})
#     if not read_user_query:
#         unauthorized_user = True
#         temp_global_user = None
#         redirect = "User Not Found"
#         return RedirectResponse("/login",status_code=status.HTTP_302_FOUND)
#     else:
#         updated_userlol = await update_user(username, updated_user) #type: ignore
#         if updated_userlol:
#             temp_global_user = updated_user.model_dump()
#             unauthorized_user = None
#             redirect = None
#             print("User Updated")
#             print(temp_global_user)
#             return RedirectResponse(f"/profile/{temp_global_user['username']}/posts",status_code=status.HTTP_302_FOUND) #type: ignore
        
#     unauthorized_user = False
#     # temp_global_user = None
#     # redirect = "Error in Updation"
#     return RedirectResponse("/login",status_code=status.HTTP_302_FOUND)
from auth.auth import oauth2_pwdbearer_flow
from jose import jwt, JWTError, ExpiredSignatureError
@routes_router.get("/test", response_class=JSONResponse, status_code=200)
async def get_test(request : Request, token: str = Depends(oauth2_pwdbearer_flow)) -> JSONResponse:
    if token:
        try:
            jwt_payload = decode_token(jwttoken = token)
            return JSONResponse(content={"message": "hello world", "payload": jwt_payload})
        except ExpiredSignatureError:
            # jwt_payload2 = decode_token(jwttoken = token, verify=False)
            # refreshtoken = jwt_payload2.get("refresh_token", False)
            # if refreshtoken:
            #     try:
            #         decode_token(jwttoken = refreshtoken)
                    return JSONResponse(content={"message": "Refresh Token"}, status_code=401)
            #     except JWTError:
            #         return JSONResponse(content={"message": "Invalid Refresh Token"}, status_code=401)
            # return JSONResponse(content={"message": "Expired Token"}, status_code=401)
        except JWTError:
            return JSONResponse(content={"message": "Invalid Token"}, status_code=401)
    else:
        return JSONResponse(content={"message": "No token"})

@routes_router.get("/", response_class=HTMLResponse)
async def get_landing(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )

@routes_router.get("/login", response_class=HTMLResponse)
async def get_login(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="login.html", context={}
    )

# @routes_router.post("/login", status_code=200, response_class=JSONResponse)
# async def post_login(request : Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], checkinput: Annotated[bool, Form()] = False ) -> JSONResponse:
#     return JSONResponse(content={"username": form_data.username, "password": form_data.password, "rememberme": checkinput})

@routes_router.post("/login", status_code=200, response_class=JSONResponse)
async def post_login(request : Request) -> JSONResponse:
    form = await request.form()
    form_data = OAuth2PasswordRequestForm(username=str(form["username"]), password=str(form["password"]))
    if "rememberme" in form.keys() and form["rememberme"] == "on":
        rememberme = "on"
    else:
        rememberme = None
    token = await get_token_by_authentication(form_data, rememberme)
    return JSONResponse(content={"form": jsonable_encoder(form), "accesstoken": jsonable_encoder(decode_token(jwttoken = str(token.access_token)))})

# @routes_router.get("/login", response_class=HTMLResponse)
# async def get_login(request : Request) -> HTMLResponse:
#     global redirect
#     if redirect:
#         context = {"error": redirect}
#     else:
#         context = {}
#     return templates.TemplateResponse(
#         request=request, name="login.html", context=context
#     )

# @routes_router.post("/login")
# # async def post_login(username: Annotated[str, Form()], password: Annotated[str, Form()], session: Session = Depends(get_session_data)):
# async def post_login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
#     global temp_global_user
#     global unauthorized_user
#     global redirect
#     if username=="kathanjani2803@gmail.com":
#         temp_global_user = dummy_user_dict
#         unauthorized_user = None
#         redirect = None
#         return RedirectResponse("/dashboard",status_code=status.HTTP_302_FOUND)
#     read_user_query = db.Users.find_one({"email": username})
#     # print(read_user_query)
#     if read_user_query:
#         if password+"lol" == read_user_query["hashed_password"]:
#             # sess
#             temp_global_user = read_user_query
#             unauthorized_user = None
#             redirect = None
#             return RedirectResponse("/dashboard",status_code=status.HTTP_302_FOUND)
#         else:
#             unauthorized_user = True
#             temp_global_user = None
#             redirect = "Invalid Credentials"
#             # return JSONResponse({"message": "Invalid Credentials"}, status_code=status.HTTP_401_UNAUTHORIZED)
#             return  RedirectResponse("/login",status_code=status.HTTP_302_FOUND)
#     unauthorized_user = True
#     temp_global_user = None
#     redirect = "User Not Found"
#     # return JSONResponse({"message": "User not found"}, status_code=status.HTTP_401_UNAUTHORIZED)
#     return  RedirectResponse("/login",status_code=status.HTTP_302_FOUND)

@routes_router.get("/signup", response_class=HTMLResponse)
async def get_signup(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="signup.html", context={}
    )

@routes_router.post("/signup", response_class=JSONResponse)
async def post_signup(request : Request) -> JSONResponse:
    form = await request.form()
    form_data = dict(username=form["username"], full_name=form["fullname"], email=form["email"], contact_no=ContactNo(contact_no=str(form["contact"])), addresses=form["address"], region=form["region"], aadhar_card=form["aadharcard"], dob=form["dob"], gender=form["gender"], password=form["password"])
    register_user = await create_user(UnsecureUser(**jsonable_encoder(form_data)))
    return JSONResponse(content={"message": jsonable_encoder(register_user), "register_user_type": str(type(register_user))})

# @routes_router.get("/signup")
# async def get_signup(request : Request):
#     global temp_global_user
#     global unauthorized_user
#     if unauthorized_user is None or temp_global_user is None:
#         return templates.TemplateResponse(
#             request=request, name="signup.html", context={}
#         )
#     return RedirectResponse("/dashboard",status_code=status.HTTP_302_FOUND)


# @routes_router.post("/signup")
# # async def post_signup(request : Request, username: Annotated[str, Form()], password: Annotated[str, Form()], email: Annotated[str, Form()]):
# async def post_signup(request : Request, username: Annotated[str, Form()], fullname: Annotated[str, Form()], contact: Annotated[str, Form()],address: Annotated[str, Form()], region: Annotated[str, Form()], dob: Annotated[str, Form()], sex:Annotated[str,Form()], password: Annotated[str, Form()], email: Annotated[str, Form()]):
#     global temp_global_user
#     global unauthorized_user
#     global redirect

#     # register_user = {
#     #     "username": username,
#     #     "fullname": fullname,
#     #     "contact": contact,
#     #     "address": address,
#     #     "region": region,
#     #     "dob": dob,
#     #     "email": email,
#     #     "hashed_password": password+"lol"
#     # }
#     register_user = UnsecuredUser(username=username, full_name=fullname, contact_no=contact, addresses=address, region=region, dob=dob, email=email, password=password, sex=sex)
#     read_user_query = db.Users.find_one({"email": email})
#     if read_user_query:
#         unauthorized_user = True
#         temp_global_user = None
#         redirect = "User Already Exists"
#         return RedirectResponse("/signup",status_code=status.HTTP_302_FOUND)
#     registered_user = await create_user(register_user)
#     if registered_user:
#         registered_user_lol = await read_user(username)
#         temp_global_user = registered_user_lol
#         unauthorized_user = None
#         redirect = None
#         print("User Registered")
#         print(temp_global_user)
#         return RedirectResponse("/dashboard",status_code=status.HTTP_302_FOUND)
    
#     unauthorized_user = True
#     temp_global_user = None
#     redirect = "Error in Registration"
#     return RedirectResponse("/login",status_code=status.HTTP_302_FOUND)

dummy_comment_objs = [
    {"user": "KathanJani2803", "post":"1", "body": "dummy comment 1","img": "img/dummy_search_img_1.jpg", "posted_at": "It's been 84 years...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": [{"user": "HarshAwasthi1204", "post":"1", "body": "dummy comment 2","img": "img/dummy_search_img_2.jpg", "posted_at": "A millenium ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": []},{"user": "PriyankaJavani2310", "post":"1", "body": "dummy comment 3","img": "img/dummy_search_img_3.jpg", "posted_at": "??? years ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": [{"user": "HarshAwasthi1204", "post":"1", "body": "dummy comment 2","img": "img/dummy_search_img_2.jpg", "posted_at": "A millenium ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": [{"user": "KathanJani2803", "post":"1", "body": "dummy comment 1","img": "img/dummy_search_img_1.jpg", "posted_at": "It's been 84 years...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": []},{"user": "PriyankaJavani2310", "post":"1", "body": "dummy comment 3","img": "img/dummy_search_img_3.jpg", "posted_at": "??? years ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": []}]},]}]},
    {"user": "HarshAwasthi1204", "post":"1", "body": "dummy comment 2","img": "img/dummy_search_img_2.jpg", "posted_at": "A millenium ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": [{"user": "KathanJani2803", "post":"1", "body": "dummy comment 1","img": "img/dummy_search_img_1.jpg", "posted_at": "It's been 84 years...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": []},{"user": "PriyankaJavani2310", "post":"1", "body": "dummy comment 3","img": "img/dummy_search_img_3.jpg", "posted_at": "??? years ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": []}]},
    {"user": "PriyankaJavani2310", "post":"1", "body": "dummy comment 3","img": "img/dummy_search_img_3.jpg", "posted_at": "??? years ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": [{"user": "KathanJani2803", "post":"1", "body": "dummy comment 1","img": "img/dummy_search_img_1.jpg", "posted_at": "It's been 84 years...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": []},{"user": "KathanJani2803", "post":"1", "body": "dummy comment 1","img": "img/dummy_search_img_1.jpg", "posted_at": "It's been 84 years...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": [{"user": "HarshAwasthi1204", "post":"1", "body": "dummy comment 2","img": "img/dummy_search_img_2.jpg", "posted_at": "A millenium ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": []},{"user": "PriyankaJavani2310", "post":"1", "body": "dummy comment 3","img": "img/dummy_search_img_3.jpg", "posted_at": "??? years ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": [{"user": "HarshAwasthi1204", "post":"1", "body": "dummy comment 2","img": "img/dummy_search_img_2.jpg", "posted_at": "A millenium ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": [{"user": "KathanJani2803", "post":"1", "body": "dummy comment 1","img": "img/dummy_search_img_1.jpg", "posted_at": "It's been 84 years...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": []},{"user": "PriyankaJavani2310", "post":"1", "body": "dummy comment 3","img": "img/dummy_search_img_3.jpg", "posted_at": "??? years ago...","tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "replies": []}]},]}]},]},
]

dummy_post_objs = [
    {"user" : "KathanJani2803", "imgs" : ["img/postimglol.jpg","img/post_img_2.png","img/post_img_1.png","img/post_img_3.png"], "community": {"img" : "img/vclogo-white.svg", "header_img" : "img/postimglol.jpg", "name" : "Community2", "descheading" : "dummy desc heading 2", "desc" : "dummy community desc 2", "member_count" : "100", "mod_count" : "10", "created_in" : "2020"}, "title" : "Statue Of Unity", "desc" : "dummy description 2", "posted_at" : "It's been 84 years...", "tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "comments": dummy_comment_objs, "id": "1"},
    {"user" : "HarshAwasthi1204", "imgs" : ["img/post_img_1.png"], "community": {"img" : "img/vclogo.svg", "header_img" : "img/post_img_1.png", "name" : "Community1", "descheading" : "dummy desc heading 1", "desc" : "dummy community desc 1", "member_count" : "1000", "mod_count" : "4", "created_in" : "2024"}, "title" : "Taj Mahal", "desc" : "dummy description 1", "posted_at" : "A millenium ago...", "tags": ["Agra","TajMahalPalaceHotel","MehtabBagh"], "likes": 100, "dislikes": 50, "comments": dummy_comment_objs, "id": "2"},
    {"user" : "PriyankaJavani2310", "imgs" : ["img/post_img_3.png"], "community": {"img" : "img/vclogo.svg", "header_img" : "img/post_img_3.png", "name" : "Community3", "descheading" : "dummy desc heading 3", "desc" : "dummy community desc 3", "member_count" : "30", "mod_count" : "6", "created_in" : "2023"}, "title" : "Qutub Minar", "desc" : "dummy description 3", "posted_at" : "??? years ago...", "tags": ["Delhi","QutubResidencyHotel","QutubMinarPark"], "likes": 50, "dislikes": 10, "comments": dummy_comment_objs, "id": "3"},
    {"user" : "KathanJani2803", "imgs" : ["img/post_img_2.png"], "community": {"img" : "img/vclogo-white.svg", "header_img" : "img/postimglol.jpg", "name" : "Community2", "descheading" : "dummy desc heading 2", "desc" : "dummy community desc 2", "member_count" : "100", "mod_count" : "10", "created_in" : "2020"}, "title" : "Statue Of Unity", "desc" : "dummy description 2", "posted_at" : "It's been 84 years...", "tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "comments": dummy_comment_objs, "id": "4"},
    {"user" : "HarshAwasthi1204", "imgs" : ["img/post_img_1.png"], "community": {"img" : "img/vclogo.svg", "header_img" : "img/post_img_1.png", "name" : "Community1", "descheading" : "dummy desc heading 1", "desc" : "dummy community desc 1", "member_count" : "1000", "mod_count" : "4", "created_in" : "2024"}, "title" : "Taj Mahal", "desc" : "dummy description 1", "posted_at" : "A millenium ago...", "tags": ["Agra","TajMahalPalaceHotel","MehtabBagh"], "likes": 100, "dislikes": 50, "comments": dummy_comment_objs, "id": "5"},
    {"user" : "PriyankaJavani2310", "imgs" : ["img/post_img_3.png"], "community": {"img" : "img/vclogo.svg", "header_img" : "img/post_img_3.png", "name" : "Community3", "descheading" : "dummy desc heading 3", "desc" : "dummy community desc 3", "member_count" : "30", "mod_count" : "6", "created_in" : "2023"}, "title" : "Qutub Minar", "desc" : "dummy description 3", "posted_at" : "??? years ago...", "tags": ["Delhi","QutubResidencyHotel","QutubMinarPark"], "likes": 50, "dislikes": 10, "comments": dummy_comment_objs, "id": "6"},
]

dummy_tipstricks_objs = [
    {"user" : "KathanJani2803", "imgs" : ["img/postimglol.jpg"], "community": {"img" : "img/vclogo-white.svg", "header_img" : "img/postimglol.jpg", "name" : "Community2", "descheading" : "dummy desc heading 2", "desc" : "dummy community desc 2", "member_count" : "100", "mod_count" : "10", "created_in" : "2020"}, "title" : "Statue Of Unity", "desc" : "dummy description 2", "posted_at" : "It's been 84 years...", "tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "comments": dummy_comment_objs, "id": "1", "tipstricks": {"id":"1","content":["Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1", "Tip 2", "Tip 3", "Tip4"]}},
    # {"user" : "KathanJani2803", "imgs" : ["img/post_img_2.png"], "community": {"img" : "img/vclogo-white.svg", "header_img" : "img/postimglol.jpg", "name" : "Community2", "descheading" : "dummy desc heading 2", "desc" : "dummy community desc 2", "member_count" : "100", "mod_count" : "10", "created_in" : "2020"}, "title" : "Statue Of Unity", "desc" : "dummy description 2", "posted_at" : "It's been 84 years...", "tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "comments": dummy_comment_objs, "id": "1", "tipstricks": {"id":"1","content":["Statue of Unity is closed on Mondays.", "Most crowded on Sundays, a little less crowded on Saturdays, and least crowded Tuesdays to Fridays.", "There are so many other places to visit near Statue of Unity, that one day is not enough to fit them all in.", "You'll need 2-3 days to explore all nearby attractions or plan ahead for those places you'd like to see in one day.", "There are so many other places to visit near Statue of Unity, that one day is not enough to fit them all in.", "You'll need 2-3 days to explore all nearby attractions or plan ahead for those places you'd like to see in one day."]}},
    {"user" : "HarshAwasthi1204", "imgs" : ["img/post_img_1.png"], "community": {"img" : "img/vclogo.svg", "header_img" : "img/post_img_1.png", "name" : "Community1", "descheading" : "dummy desc heading 1", "desc" : "dummy community desc 1", "member_count" : "1000", "mod_count" : "4", "created_in" : "2024"}, "title" : "Taj Mahal", "desc" : "dummy description 1", "posted_at" : "A millenium ago...", "tags": ["Agra","TajMahalPalaceHotel","MehtabBagh"], "likes": 100, "dislikes": 50, "comments": dummy_comment_objs, "id": "2", "tipstricks": {"id":"2","content":["Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1", "Tip 2Tip 2Tip 2Tip 2Tip 2Tip 2Tip 2Tip 2Tip 2", "Tip 3"]}},
    {"user" : "PriyankaJavani2310", "imgs" : ["img/post_img_3.png"], "community": {"img" : "img/vclogo.svg", "header_img" : "img/post_img_3.png", "name" : "Community3", "descheading" : "dummy desc heading 3", "desc" : "dummy community desc 3", "member_count" : "30", "mod_count" : "6", "created_in" : "2023"}, "title" : "Qutub Minar", "desc" : "dummy description 3", "posted_at" : "??? years ago...", "tags": ["Delhi","QutubResidencyHotel","QutubMinarPark"], "likes": 50, "dislikes": 10, "comments": dummy_comment_objs, "id": "3", "tipstricks": {"id":"3","content":["Tip 1", "Tip 2", "Tip 3", "Tip4"]}},
    {"user" : "KathanJani2803", "imgs" : ["img/post_img_2.png"], "community": {"img" : "img/vclogo-white.svg", "header_img" : "img/postimglol.jpg", "name" : "Community2", "descheading" : "dummy desc heading 2", "desc" : "dummy community desc 2", "member_count" : "100", "mod_count" : "10", "created_in" : "2020"}, "title" : "Statue Of Unity", "desc" : "dummy description 2", "posted_at" : "It's been 84 years...", "tags": ["Gujarat","HotelBRGBudgetStay","SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "comments": dummy_comment_objs, "id": "4", "tipstricks": {"id":"4","content":["Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1", "Tip 2", "Tip 3", "Tip4"]}},
    {"user" : "HarshAwasthi1204", "imgs" : ["img/post_img_1.png"], "community": {"img" : "img/vclogo.svg", "header_img" : "img/post_img_1.png", "name" : "Community1", "descheading" : "dummy desc heading 1", "desc" : "dummy community desc 1", "member_count" : "1000", "mod_count" : "4", "created_in" : "2024"}, "title" : "Taj Mahal", "desc" : "dummy description 1", "posted_at" : "A millenium ago...", "tags": ["Agra","TajMahalPalaceHotel","MehtabBagh"], "likes": 100, "dislikes": 50, "comments": dummy_comment_objs, "id": "5", "tipstricks": {"id":"5","content":["Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1Tip 1", "Tip 2Tip 2Tip 2Tip 2Tip 2Tip 2Tip 2Tip 2Tip 2", "Tip 3"]}},
    {"user" : "PriyankaJavani2310", "imgs" : ["img/post_img_3.png"], "community": {"img" : "img/vclogo.svg", "header_img" : "img/post_img_3.png", "name" : "Community3","descheading" : "dummy desc heading 3", "desc" : "dummy community desc 3", "member_count" : "30", "mod_count" : "6", "created_in" : "2023"}, "title" : "Qutub Minar", "desc" : "dummy description 3", "posted_at" : "??? years ago...", "tags": ["Delhi","QutubResidencyHotel","QutubMinarPark"], "likes": 50, "dislikes": 10, "comments": dummy_comment_objs, "id": "6", "tipstricks": {"id":"6","content":["Tip 1", "Tip 2", "Tip 3", "Tip4"]}},
]

dummy_recent_search_objs = [
    {"img" : "img/dummy_search_img_1.jpg", "name" : "Thar Desert", "place" : "Rajasthan & Gujarat"},
    {"img" : "img/vclogo.svg", "header_img" : "img/post_img_1.png", "name" : "Community1", "desc" : "dummy community desc 1"},
    {"img" : "img/dummy_search_img_2.jpg", "name" : "Red Fort", "place" : "Delhi"},
    {"img" : "img/vclogo-white.svg", "header_img" : "img/postimglol.jpg", "name" : "Community2", "desc" : "dummy community desc 2"},
    {"img" : "img/dummy_search_img_3.jpg", "name" : "Golden Temple", "place" : "Punjab"},
]

now = datetime.now()
dummy_trending_objs = [
    {"name" : "Thar Desert", "place" : "Rajasthan & Gujarat", "day" : now.day, "month": now.strftime('%b').upper()},
    {"name" : "Red Fort", "place" : "Delhi", "day" : now.day, "month": now.strftime('%b').upper()},
    {"name" : "Golden Temple", "place" : "Punjab", "day" : now.day, "month": now.strftime('%b').upper()},
]

dummy_followed_communities_objs = [
    {"img" : "img/vclogo.svg", "header_img" : "img/post_img_1.png", "name" : "Community1", "descheading" : "dummy desc heading 1", "desc" : "dummy community desc 1", "member_count" : "1000", "mod_count" : "4", "created_in" : "2024", "posts": [post_obj for post_obj in dummy_post_objs if post_obj["community"]["name"] == "Community1"]},
    {"img" : "img/vclogo-white.svg", "header_img" : "img/postimglol.jpg", "name" : "Community2", "descheading" : "dummy desc heading 2", "desc" : "dummy community desc 2", "member_count" : "100", "mod_count" : "10", "created_in" : "2020", "posts": [post_obj for post_obj in dummy_post_objs if post_obj["community"]["name"] == "Community2"]},
    {"img" : "img/vclogo.svg", "header_img" : "img/post_img_3.png", "name" : "Community3", "descheading" : "dummy desc heading 3", "desc" : "dummy community desc 3", "member_count" : "30", "mod_count" : "6", "created_in" : "2023", "posts": [post_obj for post_obj in dummy_post_objs if post_obj["community"]["name"] == "Community3"]},
]

dob=datetime(2004,3,28)
dummy_post_objs1 = list(x for x in dummy_post_objs if x["user"] == "KathanJani2803")
dummy_tipstricks_objs1 = list(x for x in dummy_tipstricks_objs if x["user"] == "KathanJani2803")
dummy_user_dict = {
    "username" : "KathanJani2803", "name": "Kathan Jani", "bio":"I don't know where I'm going, but I'm on my way.", "user_id" : "1234567890", "profile_pic" : "img/generic_pfp.png",
    "emailid": "kj2803@gmail.com", "region":"Asia", "contactno": "1234567890", "dob":dob.strftime("%Y-%m-%d"), "gender":"Male",
    "posts": dummy_post_objs,"posts2": [dummy_post_objs[i:i+3] for i in range(0, len(dummy_post_objs), 3)], "recent_searches": dummy_recent_search_objs,
    "trending": dummy_trending_objs, "followed_communities": dummy_followed_communities_objs, "search_suggestions": ["Thar Desert", "Red Fort", "Golden Temple"], "location":"Gandhinagar",
    "birthdate":str(dob.strftime('%b'))+' '+str(dob.day)+', '+str(dob.year), "post_count": len(list(x for x in dummy_post_objs if x["user"] == "KathanJani2803")), "points": 1000,
    "tipstricks": dummy_tipstricks_objs, "tipstricks2": [dummy_tipstricks_objs1[i:i+3] for i in range(0, len(dummy_tipstricks_objs1), 3)], "tipstrickscontent": [{dummy_tipstricks_objs1[i]['tipstricks']['id'] : dummy_tipstricks_objs1[i]['tipstricks']['content'][j:j+2]} for i in range(0, len(dummy_tipstricks_objs1)) for j in range(0, len(dummy_tipstricks_objs1[i]['tipstricks']['content']), 2)]
}

dummy_user_dict1 = {
    "username" : "KathanJani2803", "name": "Kathan Jani", "bio":"I don't know where I'm going, but I'm on my way.", "user_id" : "1234567890", "profile_pic" : "img/generic_pfp.png",
    "emailid": "kj2803@gmail.com", "region":"Asia", "contactno": "1234567890", "dob":dob.strftime("%Y-%m-%d"), "gender":"Male",
    "posts": [dummy_post_objs[i:i+3] for i in range(0, len(dummy_post_objs), 3)], "recent_searches": dummy_recent_search_objs,
    "trending": dummy_trending_objs, "followed_communities": dummy_followed_communities_objs, "search_suggestions": ["Thar Desert", "Red Fort", "Golden Temple"], "location":"Gandhinagar",
    "birthdate":str(dob.strftime('%b'))+' '+str(dob.day)+', '+str(dob.year), "post_count": len(list(x for x in dummy_post_objs if x["user"] == "KathanJani2803")), "points": 1000,
    "tipstricks": dummy_tipstricks_objs, "tipstricks2": [dummy_tipstricks_objs1[i:i+3] for i in range(0, len(dummy_tipstricks_objs1), 3)], "tipstrickscontent": [{dummy_tipstricks_objs1[i]['tipstricks']['id'] : dummy_tipstricks_objs1[i]['tipstricks']['content'][j:j+2]} for i in range(0, len(dummy_tipstricks_objs1)) for j in range(0, len(dummy_tipstricks_objs1[i]['tipstricks']['content']), 2)]
}
dob2=datetime(2003,4,12)
dummy_post_objs2 = list(x for x in dummy_post_objs if x["user"] == "HarshAwasthi1204")
dummy_tipstricks_objs2 = list(x for x in dummy_tipstricks_objs if x["user"] == "HarshAwasthi1204")
dummy_user_dict2 = {
    "username" : "KathanJani2803", "name": "Harsh Awasthi", "bio":"I don't know where I'm going, but I'm on my way.", "user_id" : "1204", "profile_pic" : "img/generic_pfp.png",
    "emailid": "ha1204@gmail.com", "region":"Asia", "contactno": "1234567890", "dob":dob2.strftime("%Y-%m-%d"), "gender":"Male",
    "posts": dummy_post_objs,"posts2": [dummy_post_objs2[i:i+3] for i in range(0, len(dummy_post_objs2), 3)], "recent_searches": dummy_recent_search_objs,
    "trending": dummy_trending_objs, "followed_communities": dummy_followed_communities_objs, "search_suggestions": ["Thar Desert", "Red Fort", "Golden Temple"], "location":"Ahmedabad",
    "birthdate":str(dob2.strftime('%b'))+' '+str(dob2.day)+', '+str(dob2.year), "post_count": len(list(x for x in dummy_post_objs if x["user"] == "HarshAwasthi1204")), "points": 1000,
    "tipstricks": dummy_tipstricks_objs, "tipstricks2": [dummy_tipstricks_objs2[i:i+3] for i in range(0, len(dummy_tipstricks_objs2), 3)], "tipstrickscontent": [{dummy_tipstricks_objs2[i]['tipstricks']['id'] : dummy_tipstricks_objs2[i]['tipstricks']['content'][j:j+2]} for i in range(0, len(dummy_tipstricks_objs2)) for j in range(0, len(dummy_tipstricks_objs2[i]['tipstricks']['content']), 2)]
}
dob3=datetime(2003,10,23)
dummy_post_objs3 = list(x for x in dummy_post_objs if x["user"] == "PriyankaJavani2310")
dummy_tipstricks_objs3 = list(x for x in dummy_tipstricks_objs if x["user"] == "PriyankaJavani2310")
dummy_user_dict3 = {
    "username" : "KathanJani2803", "name": "Priyanka Javani", "bio":"I don't know where I'm going, but I'm on my way.", "user_id" : "2310", "profile_pic" : "img/generic_pfp.png",
    "emailid": "pj2310@gmail.com", "region":"Asia", "contactno": "1234567890", "dob":dob3.strftime("%Y-%m-%d"), "gender":"Female",
    "posts": dummy_post_objs,"posts2": [dummy_post_objs3[i:i+3] for i in range(0, len(dummy_post_objs3), 3)], "recent_searches": dummy_recent_search_objs,
    "trending": dummy_trending_objs, "followed_communities": dummy_followed_communities_objs, "search_suggestions": ["Thar Desert", "Red Fort", "Golden Temple"], "location":"Ahmedabad",
    "birthdate":str(dob3.strftime('%b'))+' '+str(dob3.day)+', '+str(dob3.year), "post_count": len(list(x for x in dummy_post_objs if x["user"] == "PriyankaJavani2310")), "points": 1000,
    "tipstricks": dummy_tipstricks_objs, "tipstricks2": [dummy_tipstricks_objs3[i:i+3] for i in range(0, len(dummy_tipstricks_objs3), 3)], "tipstrickscontent": [{dummy_tipstricks_objs3[i]['tipstricks']['id'] : dummy_tipstricks_objs3[i]['tipstricks']['content'][j:j+2]} for i in range(0, len(dummy_tipstricks_objs3)) for j in range(0, len(dummy_tipstricks_objs3[i]['tipstricks']['content']), 2)]
}

@routes_router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={
            "status":True, "user":dummy_user_dict
        }
    )
# @routes_router.get("/dashboard")
# async def get_dashboard(request : Request):
#     global temp_global_user
#     global unauthorized_user
#     global redirect
#     if temp_global_user and not unauthorized_user:
#         return templates.TemplateResponse(
#             request=request, name="dashboard.html", context={
#                 "status":True, "user":temp_global_user
#             }
#         )
#     else:
#         redirect = "Unauthorized User"
#         return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@routes_router.get("/help", response_class=HTMLResponse)
async def get_help(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="help.html", context={
            "status":True,"user":dummy_user_dict
        }
    )
# @routes_router.get("/help")
# async def get_help(request : Request):
#     global temp_global_user
#     global unauthorized_user
#     global redirect
#     if temp_global_user and not unauthorized_user:
#         return templates.TemplateResponse(
#             request=request, name="help.html", context={
#                 "status":True,"user":temp_global_user
#             }
#         )
#     else:
#         redirect = "Unauthorized User"
#         return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@routes_router.get("/searchresults", response_class=HTMLResponse)
async def get_searchresults(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="searchresults.html", context={
            "status":True,"user":dummy_user_dict1
        }
    )
# @routes_router.get("/searchresults")
# async def get_searchresults(request : Request):
#     global temp_global_user
#     global unauthorized_user
#     global redirect
#     if temp_global_user and not unauthorized_user:
#         return templates.TemplateResponse(
#             request=request, name="searchresults.html", context={
#                 "status":True,"user":temp_global_user
#             }
#         )
#     else:
#         redirect = "Unauthorized User"
#         return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@routes_router.get("/discussionthread/{id}", response_class=HTMLResponse)
async def get_discussionthread(request : Request, id : int) -> HTMLResponse:
    post = [post_obj for post_obj in dummy_post_objs if post_obj["id"] == str(id)][0]
    return templates.TemplateResponse(
        request=request, name="discussionthread.html", context={
            "status":True,"user":dummy_user_dict, "post":post
        }
    )

@routes_router.get("/community/vc/{name}", response_class=HTMLResponse)
async def get_community(request : Request, name : str) -> HTMLResponse:
    community = [community_obj for community_obj in dummy_followed_communities_objs if community_obj["name"] == name][0]
    post = dummy_post_objs[0]
    return templates.TemplateResponse(
        request=request, name="community.html", context={
            "status":True,"user":dummy_user_dict, "community":community
        }
    )

@routes_router.get("/faqs", response_class=HTMLResponse)
async def get_faqs(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="faqs.html", context={
            "status":True,"user":dummy_user_dict
        }
    )
# @routes_router.get("/faqs")
# async def get_faqs(request : Request):
#     global temp_global_user
#     global unauthorized_user
#     global redirect
#     if temp_global_user and not unauthorized_user:
#         return templates.TemplateResponse(
#             request=request, name="faqs.html", context={
#                 "status":True,"user":temp_global_user
#             }
#         )
#     else:
#         redirect = "Unauthorized User"
#         return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

@routes_router.get("/profile/{username}/{tab}", response_class=HTMLResponse)
async def get_profile(request : Request, tab : str, username : str) -> HTMLResponse:
    if username == "KathanJani2803":
        userdict = dummy_user_dict
    elif username == "HarshAwasthi1204":
        userdict = dummy_user_dict2
    elif username == "PriyankaJavani2310":
        userdict = dummy_user_dict3
    return templates.TemplateResponse(
        request=request, name="profile.html", context={
            "status":True,"user":userdict, "tab":tab, "username":username
        }
    )
# @routes_router.get("/profile/{username}/{tab}")
# async def get_profile(request : Request, tab : str, username : str):
#     global temp_global_user
#     global unauthorized_user
#     global redirect
#     if temp_global_user and not unauthorized_user:
#         user_dob_year = int(temp_global_user["dob"].split("-")[0]) #type: ignore
#         user_dob_month = int(temp_global_user["dob"].split("-")[1]) #type: ignore
#         user_dob_day = int(temp_global_user["dob"].split("-")[2]) #type: ignore
#         # temp_global_user["dob"] = datetime(user_dob_year,user_dob_month,user_dob_day).strftime("%Y-%m-%d") #type: ignore
#         temp_global_user["birthdate"] = datetime(user_dob_year,user_dob_month,user_dob_day).strftime('%b')+' '+str(user_dob_day)+', '+str(user_dob_year) #type: ignore
#         return templates.TemplateResponse(
#             request=request, name="profile.html", context={
#                 "status":True,"user":temp_global_user, "tab":tab, "username":temp_global_user["username"] #type: ignore
#             }
#         )
#     else:
#         redirect = "Unauthorized User"
#         return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
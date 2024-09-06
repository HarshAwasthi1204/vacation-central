from fastapi import APIRouter
from fastapi.responses import JSONResponse
from security.hashers import get_hashed_password
from models.models import UnsecureUser, SecureUser
from models.converters import mongo_compat_conv, json_compat_conv
from .dbconfig import db

db_router = APIRouter()

#User CRUD Endpoints
@db_router.post("/createuser/", status_code=201, response_class=JSONResponse)
async def create_user(register_user: UnsecureUser) -> JSONResponse:
    create_user_check = db.Users.find_one({"username" : register_user.username})
    if create_user_check:
        return JSONResponse({"message" : "User Already Exists"},status_code=409)
    user_dict = register_user.model_dump()
    # if user_dict:
        # print(type(user_dict['dob']))
        # user_dict['dob'] = str(user_dict['dob'])
        # print(type(user_dict['created_at']))
        # user_dict['created_at'] = str(user_dict['created_at'])
        # print(type(user_dict['aadhar_card']))
        # user_dict['aadhar_card'] = str(user_dict['aadhar_card'])
        # user_dict["user_id"] = str(user_dict["user_id"])
    create_hashed_pwd = get_hashed_password(user_dict["password"])
    create_secure_user_dict = SecureUser(**user_dict, hashed_password=create_hashed_pwd).model_dump()
    mongo_compat_create_user_dict = mongo_compat_conv(create_secure_user_dict)
    create_user_query = db.Users.insert_one(mongo_compat_create_user_dict)
    if not create_user_query:
        return JSONResponse({"message" : "Internal Server Error"},status_code=500)
    update_userid_query = db.Users.update_one({"_id": create_user_query.inserted_id}, {"$set": {"user_id": create_user_query.inserted_id}})
    if not update_userid_query:
        return JSONResponse({"message" : "Internal Server Error"},status_code=500)
    return JSONResponse(content={"message" : "User Successfully Created", "user_id" : str(create_user_query.inserted_id)})

@db_router.get("/readuser/{username}", status_code=200, response_model= SecureUser)
async def read_user(username: str) -> SecureUser | JSONResponse:
    read_user_query = db.Users.find_one({"username": username})
    if not read_user_query:
        return JSONResponse(content={"message" : "User Not Found"},status_code=404)
    else:
        read_user_query = json_compat_conv(read_user_query)
    # return JSONResponse(content=read_user_query)
    return SecureUser(**read_user_query)

#Remove later
@db_router.get("/readuserlogin/{username}", status_code=200, response_model= SecureUser)
async def read_user_login(username: str) -> SecureUser | JSONResponse:
    read_user_query = db.Users.find_one({"$or": [{"username": username}, {"email": username}]})
    if not read_user_query:
        return JSONResponse(content={"message" : "User Not Found"},status_code=404)
    else:
        read_user_query = json_compat_conv(read_user_query)
    # return JSONResponse(content=read_user_query)
    return SecureUser(**read_user_query)
#Remove later

@db_router.put("/updateuser/{username}", status_code=200, response_class=JSONResponse)
async def update_user(username: str, update_user_data: UnsecureUser) -> JSONResponse:
    update_user_check = db.Users.find_one({"username" : username})
    if not update_user_check:
        return JSONResponse(content={"message" : "User Not Found"},status_code=404)
    update_user_data_dict = update_user_data.model_dump(exclude_unset=True)
    if get_hashed_password(update_user_data_dict["password"]) != update_user_check["hashed_password"]:
        update_hashed_pwd = get_hashed_password(update_user_data_dict["password"])
        update_secure_user_dict = SecureUser(**update_user_data_dict, hashed_password=update_hashed_pwd).model_dump(exclude_unset=True)
    else:
        update_secure_user_dict = SecureUser(**update_user_data_dict, hashed_password=update_user_check["hashed_password"]).model_dump(exclude_unset=True)
    mongo_compat_update_user_dict = mongo_compat_conv(update_secure_user_dict)
    update_user_query = db.Users.update_one({"username": username}, {"$set": mongo_compat_update_user_dict})
    if not update_user_query:
        return JSONResponse({"message" : "Internal Server Error"},status_code=500)
    return JSONResponse(content={"message" : "User Successfully Updated", "user_id" : str(update_user_check["_id"])})

@db_router.delete("/deleteuser/{username}", status_code=200, response_class=JSONResponse)
async def delete_user(username: str, password: str) -> JSONResponse:
    delete_user_check = db.Users.find_one({"username" : username})
    if not delete_user_check:
        return JSONResponse(content={"message" : "User Not Found"},status_code=404)
    if get_hashed_password(password) != delete_user_check["hashed_password"]:
        return JSONResponse(content={"message" : "Invalid Password"},status_code=401)
    find_following_users_query = db.Users.find({"followers.user_id": delete_user_check["_id"]})
    for following_users in find_following_users_query:
        for user in following_users["followers"]:
            if user["user_id"] == delete_user_check["_id"]:
                following_users["followers"].remove(user)
        update_following_users_query = db.Users.update_one({"_id": following_users["_id"]}, {"$set": {"followers": following_users["followers"]}})
    delete_user_query = db.Users.delete_one({"username": username})
    if not delete_user_query or not update_following_users_query:
        return JSONResponse({"message" : "Internal Server Error"},status_code=500)
    return JSONResponse(content={"message" : "User Successfully Deleted", "deleted_user_id" : str(delete_user_check["_id"])})
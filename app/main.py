from fastapi import Cookie, FastAPI, Form, Request, Response, templating
from fastapi.responses import RedirectResponse
from jose import jwt

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository

app = FastAPI()
templates = templating.Jinja2Templates("templates")


flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()


def encode_jwt(user_id: int):
    body = {"user_id": user_id}
    token = jwt.encode(body, "test", 'HS256')
    return token


def decode_jwt(token: str):
    data = jwt.decode(token, "test", 'HS256')
    return data["user_id"]


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ваше решение сюда
@app.get("/signup")
def get_signup(request: Request):
    return templates.TemplateResponse("/user/signup.html", {"request": request})


@app.post("/signup")
def post_signup(
    request: Request,
    email: str=Form(),
    full_name: str=Form(),
    password: str=Form()
):
    user = User(email=email, full_name=full_name, password=password)
    if users_repository.get_user_by_email(email=email) != None:
        return Response(
            content=b"Email is already exists\n",
            media_type="text/plain",
            status_code=403
        )

    users_repository.save_user(user=user)
    return RedirectResponse("/login", status_code=303)


@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("/user/login.html", {"request": request})


@app.post("/login")
def post_login(
    request: Request,
    email: str=Form(),
    password: str=Form()
):
    user = users_repository.get_user_by_email(email=email)
    if user is None:
        return Response(
            content=b"User not found\n",
            media_type="text/plain",
            status_code=404
        )

    if user.password != password:
        return Response(
            content=b"Incorrect password\n",
            media_type="text/plain",
            status_code=401
        )

    response = RedirectResponse("/profile", status_code=303)
    token = encode_jwt(user_id=user.id)
    response.set_cookie("token", token)
    return response


@app.get("/profile")
def get_profile(request: Request, token: str=Cookie()):
    user_id = decode_jwt(token=token)
    if not users_repository.get_user_by_id(user_id):
        return RedirectResponse("/login", status_code=401)
    
    return templates.TemplateResponse("/user/profile.html",{"request": request, "user": user})


@app.get("/flowers")
def get_flowers(request: Request):
    flowers = flowers_repository.get_all()
    return templates.TemplateResponse("/flower/flowers.html", {"request": request, "flowers": flowers})


@app.get("/flowers/add")
def get_new_flower(request: Request):
    return templates.TemplateResponse("/flower/add_flower.html", {"request": request})


@app.post("/flowers/add")
def post_flowers(
    request: Request,
    name: str=Form(),
    count: int=Form(),
    cost: int=Form()
):
    flower = Flower(name=name, count=count, cost=cost)
    if flowers_repository.get_flower_by_name(name=name) != None:
        return Response(
            content=b"Flower is already exists\n",
            media_type="text/plain",
            status_code=403
        ) 

    flowers_repository.save_flower(flower=flower)
    return RedirectResponse("/flowers", status_code=303)


@app.post("/cart/items")
def post_cart(
    response: Response,
    flower_id: int=Form(),
    cart: str=Cookie(default="[]")
):
    flower = flowers_repository.get_flower_by_id(id=flower_id)
    cart_json = json.loads(cart)
    if flower != None:
        cart_json.append(flower_id)
        new_cart = json.dumps(cart_json)

    response = RedirectResponse("/cart/items", status_code=303)
    response.set_cookie(token, new_cart)
    return response

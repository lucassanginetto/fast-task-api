from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from pydantic.dataclasses import dataclass

app = FastAPI()


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str


@dataclass
class UserRow:
    id: int
    username: str
    email: EmailStr
    password: str


def user_out_from_user_row(row: UserRow) -> UserOut:
    return UserOut(id=row.id, username=row.username, email=row.email)


users_table: list[UserRow] = []


@app.get("/users/")
def get_users() -> list[UserOut]:
    return list(map(user_out_from_user_row, users_table))


@app.get("/users/{id}")
def get_user(id: int) -> UserOut:
    def is_requested_user_row(row: UserRow) -> bool:
        return row.id == id

    try:
        requested_user_row = next(filter(is_requested_user_row, users_table))
    except StopIteration:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    return user_out_from_user_row(requested_user_row)


@app.post("/users/", status_code=status.HTTP_201_CREATED)
def post_user(user_in: UserIn) -> UserOut:
    new_user_row = UserRow(
        **user_in.model_dump(),
        id=(1 if len(users_table) == 0 else users_table[-1].id + 1),
    )

    users_table.append(new_user_row)

    return user_out_from_user_row(new_user_row)


@app.put("/users/{id}")
def put_user(id: int, user_in: UserIn) -> UserOut:
    def is_requested_user_row(row: UserRow) -> bool:
        return row.id == id

    try:
        requested_user_row = next(filter(is_requested_user_row, users_table))
    except StopIteration:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    new_user_row = UserRow(**user_in.model_dump(), id=id)
    users_table[users_table.index(requested_user_row)] = new_user_row

    return user_out_from_user_row(new_user_row)


@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int) -> None:
    def is_requested_user_row(row: UserRow) -> bool:
        return row.id == id

    try:
        requested_user_row = next(filter(is_requested_user_row, users_table))
    except StopIteration:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    del users_table[users_table.index(requested_user_row)]


@app.get("/")
def get_root() -> str:
    return "Server is running"

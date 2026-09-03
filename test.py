import httpx

res = httpx.post("http://127.0.0.1:5000/api/auth/get_login_token",
                json = {"phone_number": "+79256499426"}
)
print(res.json())

code = input()

res2 = httpx.post("http://127.0.0.1:5000/api/auth/verify_phone",
                json = {"phone_number": "+79256499426", "code": code}
)
print(res2.json())
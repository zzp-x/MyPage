from django.http import HttpResponse
from django.shortcuts import render
import json

# Create your views here.

user = "admin"
pwd = "123456"


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        result = {"state": "fail", "msg": ""}

        if not username:
            result["msg"] = "用户名不能为空"
            return HttpResponse(json.dumps(result))
        if not password:
            result["msg"] = "密码不能为空"
            return HttpResponse(json.dumps(result))
        print("username = " + username)
        print("password = " + password)
        if username == user:
            if password == pwd:
                result["state"] = "success"
                return HttpResponse(json.dumps(result))
            else:
                result["msg"] = "密码错误"
                return HttpResponse(json.dumps(result))
        else:
            result["msg"] = "用户名错误"
            return HttpResponse(json.dumps(result))
    else:
        return render(request, "login.html")


def main(request):
    return render(request, "main.html")


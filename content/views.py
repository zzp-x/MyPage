from django.http import HttpResponse
from django.shortcuts import render,redirect
import json

# Create your views here.

user = "admin"
pwd = "123456"


def check_login(func):
    def wrapper(*args, **kwargs):
        login_state = args[0].session.get('user', None)
        if not login_state:
            return redirect("/login/")
        return func(*args, **kwargs)
    return wrapper


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
                request.session["user"] = username
                return HttpResponse(json.dumps(result))
            else:
                result["msg"] = "密码错误"
                return HttpResponse(json.dumps(result))
        else:
            result["msg"] = "用户名错误"
            return HttpResponse(json.dumps(result))
    else:
        return render(request, "login.html")


def logout(request):
    request.session.delete()
    return HttpResponse(json.dumps({"state": "success", "msg": "退出成功"}))


@check_login
def content(request):

    # login_state = request.session.get('user',None)
    login_state = request.session.items
    return render(request, "content.html", context={"login_state":login_state})




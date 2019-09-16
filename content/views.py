from django.http import HttpResponse
from django.shortcuts import render,redirect
from content.models import User
import json
import hashlib


def check_login(func):
    def wrapper(*args, **kwargs):
        login_state = args[0].session.get('username', None)
        if not login_state:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper


def render_content(request, html, context={}):
    username = request.session.get('username', None)
    user = User.objects.filter(username=username).first()
    if user.nickname:
        name = user.nickname
    else:
        name = user.username
    context["name"] = name
    return render(request, html, context)


def get_md5(value):
    md5 = hashlib.md5()
    md5.update(value.encode("utf-8"))
    return md5.hexdigest()


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
        password_md5 = get_md5(password)
        print("password_md5 = " + password_md5)
        user = User.objects.filter(username=username, password=password_md5)
        count = user.count()
        if count == 1:
            result["state"] = "success"
            request.session["username"] = username
            return HttpResponse(json.dumps(result))
        else:
            result["msg"] = "用户名或密码错误！"
            return HttpResponse(json.dumps(result))
    else:
        return render(request, "login.html")


def logout(request):
    request.session.delete()
    return HttpResponse(json.dumps({"state": "success", "msg": "退出成功"}))


@check_login
def main(request):
    return render_content(request, "main.html")


@check_login
def base_msg(request):
    username = request.session.get('username', None)
    user = User.objects.filter(username=username).first()
    nickname = user.nickname if user.nickname else ""
    age = user.age if user.age else ""
    desc = user.desc if user.desc else ""
    context = {
        "username": username,
        "nickname": nickname,
        "age": age,
        "desc": desc,
    }
    return render_content(request, "base_msg.html", context)


def change_pwd(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
    else:
        result = {"state": "fail", "msg": ""}
        return HttpResponse(json.dumps(result))



from django.http import HttpResponse
from django.shortcuts import render,redirect
from content.models import User
import json
import os
from tool import tool


def check_login(func):
    def wrapper(*args, **kwargs):
        login_state = args[0].session.get('username', None)
        if not login_state:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper


def HttpResponse_format(state, msg):
    result = {"state": "", "msg": msg}
    if "success" in state:
        result["state"] = "success"
    else:
        result["state"] = "fail"
    return HttpResponse(json.dumps(result))


def render_format(request, html, context={}):
    username = request.session.get('username', None)
    user = User.objects.filter(username=username).first()
    if user.nickname:
        name = user.nickname
    else:
        name = user.username
    context["name"] = name
    context["path"] = request.path
    return render(request, html, context)


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username:
            return HttpResponse_format("", "用户名不能为空")
        if not password:
            return HttpResponse_format("", "密码不能为空")
        print("username = " + username)
        print("password = " + password)
        password_md5 = tool.get_md5(password)
        print("password_md5 = " + password_md5)
        user = User.objects.filter(username=username, password=password_md5)
        count = user.count()
        if count == 1:
            request.session["username"] = username
            return HttpResponse_format("success", "")
        else:
            return HttpResponse_format("", "用户名或密码错误！")
    else:
        return render(request, "login.html")


def logout(request):
    request.session.delete()
    return HttpResponse_format("success", "退出成功")


@check_login
def main(request):
    return render_format(request, "content/main.html")


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
    return render_format(request, "content/base_msg.html", context)


@check_login
def change_pwd(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        username = request.session.get('username', None)
        user = User.objects.filter(username=username).first()
        old_password_md5 = tool.get_md5(old_password)
        new_password_md5 = tool.get_md5(new_password)
        if user.password == old_password_md5:
            if old_password_md5 == new_password_md5:
                return HttpResponse_format("", "密码修改失败，新旧密码相同！")
            else:
                user.password = new_password_md5
                user.save()
                request.session.delete()
                return HttpResponse_format("success", "密码修改成功，请使用新密码重新登录！")
        else:
            return HttpResponse_format("", "密码修改失败，旧密码不正确！")
    else:
        return HttpResponse_format("", "错误的请求方式！")


@check_login
def change_user(request):
    if request.method == "POST":
        nickname = request.POST.get("nickname")
        age = request.POST.get("age")
        desc = request.POST.get("desc")
        username = request.session.get('username', None)
        user = User.objects.filter(username=username).first()
        user.nickname = nickname
        user.age = age
        user.desc = desc
        user.save()
        return HttpResponse_format("success", "个人信息修改成功！")
    else:
        return HttpResponse_format("", "错误的请求方式！")


@check_login
def local_msg(request):
    ipconfig_list = tool.detail_ipconfig()
    platform_msg = tool.platform_msg()
    python_msg = tool.python_msg()
    system_time = tool.get_system_time()
    return render_format(request, "network/local_msg.html", {
        "ipconfig_list": ipconfig_list,
        "platform_msg": platform_msg,
        "python_msg": python_msg,
        "system_time": system_time,
    })


@check_login
def ping(request):
    if request.method == "POST":
        ip = request.POST.get("ip")
        times = request.POST.get("times")
        state = tool.check_ip(ip)
        if not state:
            return HttpResponse_format("", "IP 地址格式错误！")
        if not times:
            return HttpResponse_format("", "必须为选项 -n 提供值。")
        return HttpResponse_format("success", tool.run_command("ping " + ip + " -n " + times).strip())
    else:
        return render_format(request, "network/ping.html")


@check_login
def tcp_port(request):
    if request.method == "POST":
        ip = request.POST.get("ip")
        port = request.POST.get("port")
        if not tool.check_ip(ip):
            return HttpResponse_format("", "IP 地址格式错误！")
        port_list = []
        if port.isdigit():
            if not tool.check_port(port):
                return HttpResponse_format("", "端口格式错误！")
            port_list.append(port)
        else:
            if "," in port:
                for i in port.split(","):
                    if not tool.check_port(i):
                        return HttpResponse_format("", "端口格式错误！")
                    port_list.append(i)
            elif "-" in port:
                row_port_list = port.split("-")
                if len(row_port_list) != 2:
                    return HttpResponse_format("", "端口格式错误！")
                for i in row_port_list:
                    if not tool.check_port(i):
                        return HttpResponse_format("", "端口格式错误！")
                port_list.append(port)
            else:
                return HttpResponse_format("", "端口格式错误！")
        port_pass = ""
        port_reject = ""
        for i in port_list:
            if "-" in i:
                for num in range(int(i.split("-")[0]), int(i.split("-")[1])):
                    if tool.telnet(ip, num):
                        port_pass += str(num) + "、"
                    else:
                        port_reject += str(num) + "、"
            else:
                if tool.telnet(ip, i):
                    port_pass += i + "、"
                else:
                    port_reject += i + "、"
        message = ""
        if port_pass:
            message += "端口开启： " + port_pass
        if port_reject:
            if message:
                message += "\n"
            message += "端口关闭： " + port_reject
        return HttpResponse_format("success", message)
    else:
        return render_format(request, "network/tcp_port.html")


@check_login
def arp_table(request):
    arp_list = tool.arp_table()
    return render_format(request, "network/arp_table.html", {"arp_list": arp_list})


@check_login
def route_table(request):
    arp_list = tool.arp_table()
    return render_format(request, "route_table.html", {"arp_list": arp_list})


@check_login
def packet_capture(request):
    if request.method == "POST":
        switch = request.POST.get("switch")
        if switch == "":
            return HttpResponse_format("", "未开启抓包！")
        net_ka = request.POST.get("net_ka")
        count = request.POST.get("count")
        message = "抓包成功！"
        try:
            tool.packet_sniffer(net_ka, int(count))
        except Exception as e:
            message = str(e)
        return HttpResponse_format("success", message)
    else:
        ipconfig_list = tool.detail_ipconfig()
        net_kas = []
        for net_ka in ipconfig_list:
            net_kas.append(net_ka["name"])
        if os.path.exists(os.getcwd() + "/tool/cache/sniff.pcap"):
            download = True
        else:
            download = False
        return render_format(request, "network/packet_capture.html", {"net_kas": net_kas, "download": download})


@check_login
def download_packet(request):
    file_path = os.getcwd() + "/tool/cache/sniff.pcap"
    if os.path.isfile(file_path):
        file = open(file_path, "rb")
        response = HttpResponse(file)
        response["Content-type"] = "application/octet-stream"
        response["Content-Disposition"] = "attachment;filename=sniff.pcap"
        return response
    else:
        return HttpResponse_format("", "找不到抓包路径！")


@check_login
def download_packet_del(request):
    file_path = os.getcwd() + "/tool/cache/sniff.pcap"
    if os.path.exists(file_path):
        os.remove(file_path)
        return HttpResponse_format("success", "删除成功！")
    else:
        return HttpResponse_format("", "删除失败，抓包文件不存在！")


@check_login
def demo(request):
    return render_format(request, "demo.html")


@check_login
def local_area_network(request):
    msg_list = tool.get_local_area_network_msg()
    return render_format(request, "arp/local_area_network.html", {"msg_list": msg_list})


arp_cheat_obj = None

@check_login
def arp_cheat(request):
    if arp_cheat_obj is None:
        arp_cheat_obj_flag = False
    else:
        arp_cheat_obj_flag = True
    ipconfig_list = tool.detail_ipconfig()
    print("-" * 88)
    print(json.dumps(ipconfig_list))
    print("-" * 88)
    return render_format(request, "arp/arp_cheat.html", {
        "ipconfig_list": ipconfig_list,
        "ipconfig_list_json": json.dumps(ipconfig_list),
        "arp_cheat_obj_flag": arp_cheat_obj_flag,
    })





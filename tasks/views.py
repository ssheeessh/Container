from datetime import datetime
from django.shortcuts import render, redirect

USERS_DB = {
    "kirill": {"password": "kirill123", "role": "admin"},
    "albert": {"password": "albert456", "role": "operator"},
    "ivan": {"password": "ivan789", "role": "auditor"},
}

PERMISSIONS = {
    "admin": ["Просмотр", "Развертывание", "Изменение", "Удаление"],
    "operator": ["Просмотр", "Развертывание"],
    "auditor": ["Просмотр"],
}

VM_IMAGES = {
    "ubuntu-base.img": {"level": "standard"},
    "secure-db.img": {"level": "protected"},
    "ml-node.img": {"level": "standard"},
    "archive-template.img": {"level": "archive"},
}

EVENT_LOG = []


def evaluate_access(username, password, operation, image_name, is_https=True):
    user = USERS_DB.get(username)

    if not is_https:
        return False, None, "Доступ разрешён только по HTTPS"

    if not user:
        return False, None, "Пользователь не найден"

    if user["password"] != password:
        return False, None, "Неверный пароль"

    role = user["role"]

    if operation not in PERMISSIONS.get(role, []):
        return False, role, f"Операция '{operation}' запрещена для роли '{role}'"

    image_info = VM_IMAGES.get(image_name)
    if not image_info:
        return False, role, "Выбранный образ не найден"

    image_level = image_info["level"]

    if image_level == "protected" and operation in ["Изменение", "Удаление"] and role != "admin":
        return False, role, "Защищённый образ может изменять или удалять только администратор"

    if image_level == "archive" and operation == "Удаление":
        return False, role, "Архивный образ запрещено удалять через веб-интерфейс"

    return True, role, "Доступ разрешён"


def add_log_entry(username, role, image_name, operation, action, reason):
    EVENT_LOG.insert(0, {
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "user": username,
        "role": role if role else "-",
        "image": image_name,
        "operation": operation,
        "action": action,
        "reason": reason,
    })

    if len(EVENT_LOG) > 50:
        EVENT_LOG.pop()


def index(request):
    context = {
        "images": list(VM_IMAGES.keys()),
        "operations": ["Просмотр", "Развертывание", "Изменение", "Удаление"],
        "logs": EVENT_LOG[:10],
    }
    return render(request, "tasks/index.html", context)


def check_access(request):
    if request.method != "POST":
        return redirect("tasks:index")

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "").strip()
    image_name = request.POST.get("image_name", "").strip()
    operation = request.POST.get("operation", "").strip()

    # Учебная имитация HTTPS для локальной среды VS Code
    simulate_https = request.POST.get("simulate_https") == "on"
    is_https = simulate_https or request.is_secure() or request.headers.get("X-Forwarded-Proto") == "https"

    allowed, role, reason = evaluate_access(
        username,
        password,
        operation,
        image_name,
        is_https
    )

    action = "Разрешено" if allowed else "Отклонено"

    add_log_entry(username, role, image_name, operation, action, reason)

    context = {
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "username": username,
        "role": role if role else "-",
        "image_name": image_name,
        "operation": operation,
        "action": action,
        "reason": reason,
        "is_https": is_https,
    }

    return render(request, "tasks/result.html", context)


def logs_view(request):
    return render(request, "tasks/logs.html", {"logs": EVENT_LOG})
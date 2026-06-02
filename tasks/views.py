import json
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


def normalize_denial_reason(reason):
    """
    Приводит разные текстовые причины отказа к фиксированным категориям
    для построения диаграммы причин отказов.
    """
    if not reason:
        return None

    if "Неверный пароль" in reason:
        return "Неверный пароль"

    if "запрещена для роли" in reason:
        return "Операция запрещена для роли"

    if "HTTPS" in reason:
        return "Доступ только по HTTPS"

    if "Архивный образ" in reason:
        return "Архивный образ запрещено удалять"

    if "Пользователь не найден" in reason:
        return "Пользователь не найден"

    return None


def build_visualization_context():
    """
    Формирует статистику и данные для диаграмм на главной странице
    и странице журнала событий.
    """
    total_attempts = len(EVENT_LOG)
    allowed_attempts = sum(1 for item in EVENT_LOG if item.get("action") == "Разрешено")
    denied_attempts = sum(1 for item in EVENT_LOG if item.get("action") == "Отклонено")

    if total_attempts:
        denial_percent = round((denied_attempts / total_attempts) * 100, 1)
    else:
        denial_percent = 0

    role_counts = {
        "admin": 0,
        "operator": 0,
        "auditor": 0,
        "Не определена": 0,
    }

    operation_counts = {
        "Просмотр": 0,
        "Развертывание": 0,
        "Изменение": 0,
        "Удаление": 0,
    }

    image_counts = {
        "ubuntu-base.img": 0,
        "secure-db.img": 0,
        "ml-node.img": 0,
        "archive-template.img": 0,
    }

    denial_reason_counts = {
        "Неверный пароль": 0,
        "Операция запрещена для роли": 0,
        "Доступ только по HTTPS": 0,
        "Архивный образ запрещено удалять": 0,
        "Пользователь не найден": 0,
    }

    for item in EVENT_LOG:
        role = item.get("role", "-")
        operation = item.get("operation", "")
        image = item.get("image", "")
        action = item.get("action", "")
        reason = item.get("reason", "")

        if role in role_counts:
            role_counts[role] += 1
        else:
            role_counts["Не определена"] += 1

        if operation in operation_counts:
            operation_counts[operation] += 1

        if image in image_counts:
            image_counts[image] += 1

        if action == "Отклонено":
            normalized_reason = normalize_denial_reason(reason)
            if normalized_reason in denial_reason_counts:
                denial_reason_counts[normalized_reason] += 1

    return {
        "stats": {
            "total_attempts": total_attempts,
            "allowed_attempts": allowed_attempts,
            "denied_attempts": denied_attempts,
            "denial_percent": denial_percent,
        },

        "role_chart_labels": json.dumps(list(role_counts.keys()), ensure_ascii=False),
        "role_chart_data": json.dumps(list(role_counts.values()), ensure_ascii=False),

        "failure_chart_labels": json.dumps(list(denial_reason_counts.keys()), ensure_ascii=False),
        "failure_chart_data": json.dumps(list(denial_reason_counts.values()), ensure_ascii=False),

        "operation_chart_labels": json.dumps(list(operation_counts.keys()), ensure_ascii=False),
        "operation_chart_data": json.dumps(list(operation_counts.values()), ensure_ascii=False),

        "image_chart_labels": json.dumps(list(image_counts.keys()), ensure_ascii=False),
        "image_chart_data": json.dumps(list(image_counts.values()), ensure_ascii=False),
    }


def index(request):
    context = {
        "images": list(VM_IMAGES.keys()),
        "operations": ["Просмотр", "Развертывание", "Изменение", "Удаление"],
        "logs": EVENT_LOG[:10],
    }

    context.update(build_visualization_context())

    return render(request, "tasks/index.html", context)


def check_access(request):
    if request.method != "POST":
        return redirect("tasks:index")

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "").strip()
    image_name = request.POST.get("image_name", "").strip()
    operation = request.POST.get("operation", "").strip()

    # Учебная имитация HTTPS для локальной среды VS Code / Docker
    simulate_https = request.POST.get("simulate_https") == "on"

    is_https = (
        simulate_https
        or request.is_secure()
        or request.headers.get("X-Forwarded-Proto") == "https"
    )

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
    context = {
        "logs": EVENT_LOG,
    }

    context.update(build_visualization_context())

    return render(request, "tasks/logs.html", context)
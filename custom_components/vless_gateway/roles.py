"""Pure contract mapping: no guessed entity IDs and no invented values."""

SENSOR_ROLES = {
    "gateway_status": "Шлюз",
    "active_route": "Активный маршрут",
    "default_route": "Маршрут по умолчанию",
    "dns_route": "Маршрут DNS",
    "routing_mode": "Режим маршрутизации",
    "bypass_rules": "Правила обхода",
    "last_route_change": "Последняя смена маршрута",
    "latency": "Задержка",
    "uptime": "Время работы",
    "download_rate": "Скорость загрузки",
    "upload_rate": "Скорость отправки",
    "routed_traffic": "Общий трафик",
    "active_connections": "Активные соединения",
    "traffic_today": "Трафик за день",
    "traffic_month": "Трафик за месяц",
}
BINARY_ROLES = {
    "lan_status": "Локальная сеть",
    "tunnel_status": "Туннель",
    "vless_server_status": "VLESS-сервер",
    "internet_status": "Интернет",
}


def _data(values, endpoint):
    envelope = values.get(endpoint, {})
    f = envelope.get("freshness", {})
    if not f.get("available") or f.get("stale", True) or f.get("age_seconds", 999) > 45:
        return {}
    return envelope.get("data", {})


def _metric(value):
    return (
        value.get("value")
        if isinstance(value, dict) and value.get("available") is True
        else None
    )


def role_value(values, role):
    status = _data(values, "status")
    if role == "gateway_status":
        return status.get("state")
    if role in (
        "active_route",
        "dns_route",
        "bypass_rules",
        "lan_status",
        "tunnel_status",
        "internet_status",
    ):
        return _metric(status.get(role))
    if role == "default_route":
        return status.get("desired_route")
    if role == "routing_mode":
        return status.get("mode")
    if role == "last_route_change":
        return (status.get("last_route_change") or {}).get("at")
    if role == "uptime":
        return _metric(_data(values, "system").get("uptime"))
    if role in ("latency", "vless_server_status"):
        route = _metric(status.get("active_route"))
        routes = _data(values, "routes")
        chosen = routes.get({"de": "germany", "nl": "netherlands"}.get(route, ""), {})
        if role == "latency":
            return _metric(chosen.get("latency_ms"))
        return chosen.get("healthy") if chosen.get("available") is True else None
    traffic = _data(values, "traffic")
    if role == "routed_traffic":
        down, up = (
            _metric(traffic.get("download_total")),
            _metric(traffic.get("upload_total")),
        )
        return down + up if down is not None and up is not None else None
    return _metric(traffic.get(role))

#!/usr/bin/env python3

import json
import socket
import threading
import time
from fastmcp import FastMCP

mcp = FastMCP("raspberry-pi-wan-emulator")

END_POINT_IP = "192.168.31.67"
END_POINT_PORT = 10393

CHECK_INTERVAL_SEC = 10
REQUEST_TIMEOUT_SEC = 2

DEFAULT_CONFIG = {
    "bandUp": 8096,
    "bandDw": 8096,
    "delayUp": 0,
    "delayDw": 0,
    "lossUp": 0,
    "lossDw": 0,
    "disconnUp": 0,
    "disconnDw": 0,
}

current_config = DEFAULT_CONFIG.copy()
emulator_status = "init"

state_lock = threading.Lock()


def status_message() -> str:
    if emulator_status == "running":
        return "正常に処理が行える状態です。"
    return "現在処理が受け付けられない状態です。"


def validate_config(req: dict) -> None:
    for key, value in req.items():
        if key == "action":
            continue
        if not isinstance(value, int):
            raise ValueError(f"{key} must be int")
        if value < 0:
            raise ValueError(f"{key} must be >= 0")

    if req["disconnUp"] not in (0, 1):
        raise ValueError("disconnUp must be 0 or 1")

    if req["disconnDw"] not in (0, 1):
        raise ValueError("disconnDw must be 0 or 1")


def update_config_from_response(response: dict) -> dict:
    global current_config

    new_config = {
        "bandUp": response["bandUp"],
        "bandDw": response["bandDw"],
        "delayUp": response["delayUp"],
        "delayDw": response["delayDw"],
        "lossUp": response["lossUp"],
        "lossDw": response["lossDw"],
        "disconnUp": response["disconnUp"],
        "disconnDw": response["disconnDw"],
    }

    with state_lock:
        current_config = new_config.copy()

    return new_config


def send_request(req: dict, timeout: float = REQUEST_TIMEOUT_SEC) -> dict:
    pkt = json.dumps(req).encode("utf-8")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(pkt, (END_POINT_IP, END_POINT_PORT))
        data, _ = sock.recvfrom(4096)

    return json.loads(data.decode("utf-8"))


def refresh_status() -> dict:
    global emulator_status

    try:
        response = send_request({"action": "get"}, timeout=REQUEST_TIMEOUT_SEC)

        config = update_config_from_response(response)

        with state_lock:
            emulator_status = "running"

        return {
            "emulator_status": "running",
            "status_message": "正常に処理が行える状態です。",
            "config": config,
        }

    except socket.timeout:
        with state_lock:
            emulator_status = "stop"

        return {
            "emulator_status": "stop",
            "status_message": "現在処理が受け付けられない状態です。",
            "config": current_config.copy(),
        }

    except Exception as e:
        with state_lock:
            emulator_status = "stop"

        return {
            "emulator_status": "stop",
            "status_message": "現在処理が受け付けられない状態です。",
            "error": str(e),
            "config": current_config.copy(),
        }


def health_check_loop() -> None:
    while True:
        refresh_status()
        time.sleep(CHECK_INTERVAL_SEC)


def require_running() -> None:
    with state_lock:
        status = emulator_status

    if status != "running":
        raise RuntimeError(
            f"WANエミュレーターは現在処理を受け付けられません。"
            f"emulator_status={status}"
        )


def send_wan_config(config: dict) -> dict:
    validate_config(config)

    require_running()

    req = config.copy()
    req["action"] = "set"

    response = send_request(req, timeout=REQUEST_TIMEOUT_SEC)
    updated_config = update_config_from_response(response)

    return {
        "status": "success",
        "emulator_status": emulator_status,
        "status_message": status_message(),
        "config": updated_config,
    }


@mcp.tool
def get_wan_emulator_status() -> dict:
    """
    WANエミュレーターの現在状態を取得する。

    emulator_status:
    - running: 正常に処理が行える状態
    - init / stop: 現在処理が受け付けられない状態

    bandUp / bandDw: 帯域(kbps)
    delayUp / delayDw: 遅延(ms)
    lossUp / lossDw: パケットロス率(%)
    disconnUp / disconnDw: 0=通常, 1=切断エミュレーション状態    
    """
    return refresh_status()


@mcp.tool
def set_wan_emulator(
    band_up: int = 8096,
    band_dw: int = 8096,
    delay_up: int = 0,
    delay_dw: int = 0,
    loss_up: int = 0,
    loss_dw: int = 0,
    disconn_up: int = 0,
    disconn_dw: int = 0,
) -> dict:
    """
    WANエミュレーターの通信条件をまとめて設定する。
    emulator_status が running のときだけ処理可能。

    band_up: 上り帯域(kbps)
    band_dw: 下り帯域(kbps)
    delay_up: 上り遅延(ms)
    delay_dw: 下り遅延(ms)
    loss_up: 上りパケットロス率(%)
    loss_dw: 下りパケットロス率(%)
    disconn_up: 上り切断フラグ。0=何もしない/通常, 1=切断エミュレーション状態
    disconn_dw: 下り切断フラグ。0=何もしない/通常, 1=切断エミュレーション状態    
    """

    config = {
        "bandUp": band_up,
        "bandDw": band_dw,
        "delayUp": delay_up,
        "delayDw": delay_dw,
        "lossUp": loss_up,
        "lossDw": loss_dw,
        "disconnUp": disconn_up,
        "disconnDw": disconn_dw,
    }

    return send_wan_config(config)


@mcp.tool
def reset_wan_emulator() -> dict:
    """
    WANエミュレーターを初期状態に戻す。
    emulator_status が running のときだけ処理可能。

    初期状態:
    - 上り帯域: 8096 kbps
    - 下り帯域: 8096 kbps
    - 上り/下り遅延: 0 ms
    - 上り/下りロス: 0 %
    - 上り/下り切断フラグ: 0    
    """
    return send_wan_config(DEFAULT_CONFIG.copy())


@mcp.tool
def set_bandwidth(up_kbps: int = 8096, down_kbps: int = 8096) -> dict:
    """
    WANエミュレーターの帯域だけを変更する。
    emulator_status が running のときだけ処理可能。

    up_kbps: 上り帯域(kbps)
    down_kbps: 下り帯域(kbps)
    """
    status = refresh_status()
    config = status["config"].copy()

    config["bandUp"] = up_kbps
    config["bandDw"] = down_kbps

    return send_wan_config(config)


@mcp.tool
def set_delay(up_ms: int = 0, down_ms: int = 0) -> dict:
    """
    WANエミュレーターの遅延だけを変更する。
    emulator_status が running のときだけ処理可能。

    up_ms: 上り遅延(ms)
    down_ms: 下り遅延(ms)
    """
    status = refresh_status()
    config = status["config"].copy()

    config["delayUp"] = up_ms
    config["delayDw"] = down_ms

    return send_wan_config(config)


@mcp.tool
def set_packet_loss(up_percent: int = 0, down_percent: int = 0) -> dict:
    """
    WANエミュレーターのパケットロス率だけを変更する。
    emulator_status が running のときだけ処理可能。

    up_percent: 上りパケットロス率(%)
    down_percent: 下りパケットロス率(%)    
    """
    status = refresh_status()
    config = status["config"].copy()

    config["lossUp"] = up_percent
    config["lossDw"] = down_percent

    return send_wan_config(config)


@mcp.tool
def disconnect_wan() -> dict:
    """
    上り/下りを切断エミュレーション状態にする。
    emulator_status が running のときだけ処理可能。
    """
    status = refresh_status()
    config = status["config"].copy()

    config["disconnUp"] = 1
    config["disconnDw"] = 1

    return send_wan_config(config)


@mcp.tool
def reconnect_wan() -> dict:
    """
    上り/下りの切断エミュレーションを解除する。
    emulator_status が running のときだけ処理可能。
    """
    status = refresh_status()
    config = status["config"].copy()

    config["disconnUp"] = 0
    config["disconnDw"] = 0

    return send_wan_config(config)


if __name__ == "__main__":
    thread = threading.Thread(target=health_check_loop, daemon=True)
    thread.start()

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
    )

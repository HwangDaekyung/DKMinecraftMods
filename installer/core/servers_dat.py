"""servers.dat (NBT) 파일에 서버 IP 등록"""
from pathlib import Path

import nbtlib
from nbtlib import Compound, List, String, Byte

import config


def add_server(mc_path: str) -> bool:
    """
    servers.dat에 config의 서버 정보 추가.
    이미 같은 IP가 있으면 스킵.
    Returns: True(추가됨) / False(이미 존재해서 스킵)
    """
    servers_path = Path(mc_path) / "servers.dat"

    if servers_path.exists():
        nbt = nbtlib.load(str(servers_path))
        servers_list = nbt.get("servers", List[Compound]())
    else:
        servers_list = List[Compound]()
        nbt = nbtlib.File({"servers": servers_list})

    # 중복 체크
    for s in servers_list:
        if str(s.get("ip", "")) == config.SERVER_IP:
            return False  # 이미 있음

    servers_list.append(Compound({
        "ip":             String(config.SERVER_IP),
        "name":           String(config.SERVER_NAME),
        "acceptTextures": Byte(1),
    }))

    nbt["servers"] = servers_list
    nbt.save(str(servers_path))
    return True

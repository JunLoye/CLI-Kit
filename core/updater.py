import json
from urllib.request import Request, urlopen

CURRENT_VERSION = "1.0.0"
GITHUB_API_URL = "https://api.github.com/repos/JunLoye/CLI-Kit/releases/latest"
update_info = {"has_update": False, "version": None}

def check_update_worker():
    global update_info
    try:
        req = Request(GITHUB_API_URL)
        req.add_header('User-Agent', 'DevBox-CLI')
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            latest = data.get("tag_name", "").replace("v", "")
            if latest and latest > CURRENT_VERSION:
                update_info["has_update"] = True
                update_info["version"] = latest
    except:
        pass

def get_update_status():
    return update_info
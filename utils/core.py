urls = {
    "great": "https://pvpoke.com/rankings/all/1500/overall/",
    "ultra": "https://pvpoke.com/rankings/all/2500/overall/",
    "master": "https://pvpoke.com/rankings/all/10000/overall/"
    }

url_pattern = r"https://pvpoke\.com/rankings/all/(\d{4,5})/overall/"
iv_pattern = r"^(?:1[0-5]|[0-9]),(?:1[0-5]|[0-9]),(?:1[0-5]|[0-9])$"
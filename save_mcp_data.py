import json, os

digest_dir = "/home/hermes_agent/digest"
os.makedirs(digest_dir, exist_ok=True)

mcp_data = {
    "hsi": {"price": 24961.951, "change": -291.449, "percent": -1.154, "name": "恒生指数"},
    "sh": {"price": 4027.7362, "change": -30.04, "percent": -0.74, "name": "上证指数"},
    "sz": {"price": 15314.7, "change": -346.87, "percent": -2.21, "name": "深证成指"},
    "cyb": {"price": 3957.935, "change": -130.95, "percent": -3.2, "name": "创业板指"},
    "sp500": {"price": 7383.7402, "change": -200.57, "percent": -2.64, "name": "标普500指数"},
    "nasdaq": {"price": 25709.432, "change": -1121.53, "percent": -4.18, "name": "纳斯达克"},
    "dow": {"price": 50866.7812, "change": -695.15, "percent": -1.35, "name": "道琼斯"},
    "sectors_hy": [
        {"name": "航天装备Ⅱ", "percent": 6.78, "rp_net": 1706207104},
        {"name": "电机Ⅱ", "percent": 3.15, "rp_net": 231151424},
        {"name": "化学纤维", "percent": 3.05, "rp_net": 741716288},
        {"name": "金属新材料", "percent": 2.98, "rp_net": 523993728},
        {"name": "数字媒体", "percent": 2.92, "rp_net": 335967136}
    ],
    "sectors_gn": [
        {"name": "空中成像", "percent": 7.42, "rp_net": 731150720},
        {"name": "药用玻璃", "percent": 5.66, "rp_net": 740304256},
        {"name": "航天科技集团", "percent": 5.41, "rp_net": 1550040320},
        {"name": "NFC概念", "percent": 5.41, "rp_net": 789200000},
        {"name": "华为机器人", "percent": 5.38, "rp_net": 48545168}
    ],
    "fund_flow": [
        {"name": "卫星互联网", "rp_net": 9078712320},
        {"name": "无人机", "rp_net": 6581354496},
        {"name": "低空经济", "rp_net": 6468456448}
    ],
    "lianban": [
        {"name": "泰坦股份", "lianBan": "十天五板", "percent": 10.01},
        {"name": "大有能源", "lianBan": "五天五板", "percent": 10.0},
        {"name": "中重科技", "lianBan": "三天三板", "percent": 10.04},
        {"name": "凤凰航运", "lianBan": "二天二板", "percent": 10.05},
        {"name": "祥和实业", "lianBan": "二天二板", "percent": 9.98}
    ],
    "hk_sectors": [
        {"name": "消费者主要零售商", "change_avg_price": 0.971},
        {"name": "纺织及服饰", "change_avg_price": 0.803},
        {"name": "农业产品", "change_avg_price": 0.552},
        {"name": "工用运输", "change_avg_price": 0.506},
        {"name": "软件服务", "change_avg_price": 0.337}
    ],
    "forex": {
        "EURUSD": {"price": 1.1519, "pctChg": -0.78},
        "USDJPY": {"price": 160.29, "pctChg": 0.17},
        "USDCNY": {"price": 6.7878, "pctChg": -0.015},
        "USDHKD": {"price": 7.8332, "pctChg": -0.02}
    }
}

with open(f"{digest_dir}/mcp_data.json", "w") as f:
    json.dump(mcp_data, f, ensure_ascii=False, indent=2)
print("MCP data saved")

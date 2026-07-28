import os
import json
import requests

APP_ID = os.environ.get("FEISHU_APP_ID")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET")
# 请替换为你的飞书 App Token 和 Table ID
APP_TOKEN = "cli_a92400311fe29bc3" 
TABLE_ID = "biRzPE5atUBadMdnrOZAdfBAiXG4vUXN"

# 1. 获取 Tenant Access Token
def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    return res.get("tenant_access_token")

# 2. 从飞书多维表获取最新的那一条记录
def get_latest_feishu_data(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 1} # 默认拿最新的记录
    res = requests.get(url, headers=headers, params=params).json()
    
    items = res.get("data", {}).get("items", [])
    if not items:
        raise Exception("飞书表格中未找到数据")
    
    return items[0].get("fields", {})

# 3. 将飞书格式还原为你的 data.json 结构
def update_local_json():
    token = get_tenant_token()
    fields = get_latest_feishu_data(token)

    # 读取旧的 data.json 保持部分未在表格中修改的复杂结构
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 用飞书中的新值覆写 JSON 字段
    if "实时 OEE" in fields:
        data["kpi"]["oeeValue"] = float(fields["实时 OEE"]) * 100 if fields["实时 OEE"] <= 1 else float(fields["实时 OEE"])
    if "今日事件数" in fields:
        data["kpi"]["eventNum"] = str(fields["今日事件数"])
    if "在线设备" in fields:
        data["kpi"]["runDev"] = str(fields["在线设备"])
    if "待修工单" in fields:
        data["kpi"]["repairDev"] = str(fields["待修工单"])

    # 将更新后的数据重新写入 data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ 已成功将飞书最新数据覆写至本地 data.json！")

if __name__ == "__main__":
    update_local_json()
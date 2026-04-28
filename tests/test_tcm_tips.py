"""测试中医小常识接口：随机性 + 性能"""
import urllib.request
import json
import time

URL = "http://localhost:8000/api/utils/tcm-tips"

# 1. 随机性验证
print("=== 随机性验证 ===")
all_titles = set()
for i in range(5):
    resp = urllib.request.urlopen(URL)
    data = json.loads(resp.read())
    titles = [item["title"] for item in data["data"]]
    all_titles.update(titles)
    print(f"  第{i+1}次: {titles}")

print(f"\n5次请求共获得 {len(all_titles)} 条不同常识（应 > 3）")
print(f"随机性: {'✅ 通过' if len(all_titles) > 3 else '❌ 未通过'}")

# 2. 性能测试
print("\n=== 性能测试 ===")
start = time.perf_counter()
for _ in range(50):
    urllib.request.urlopen(URL)
elapsed = time.perf_counter() - start
avg_ms = (elapsed / 50) * 1000
print(f"  50次请求总耗时: {elapsed*1000:.0f}ms")
print(f"  平均响应时间: {avg_ms:.2f}ms/次")
print(f"性能: {'✅ 通过 (<200ms)' if avg_ms < 200 else '❌ 未通过 (>=200ms)'}")

# 3. 响应格式验证
print("\n=== 响应格式验证 ===")
resp = urllib.request.urlopen(URL)
data = json.loads(resp.read())
has_code = "code" in data and data["code"] == 200
has_message = "message" in data
has_data = "data" in data and isinstance(data["data"], list) and len(data["data"]) == 3
has_title_content = all(
    "title" in item and "content" in item
    for item in data["data"]
)
print(f"  code=200: {'✅' if has_code else '❌'}")
print(f"  message存在: {'✅' if has_message else '❌'}")
print(f"  data是3条列表: {'✅' if has_data else '❌'}")
print(f"  每条含title+content: {'✅' if has_title_content else '❌'}")

print("\n=== 全部测试完成 ===")

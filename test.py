import requests

WORKER_URL = "https://div-rice-5371.martinmoreiraractor.workers.dev"
ADMIN_KEY  = "Mj2026311x"

# 注意这里改成了 /activate
resp = requests.post(
    f"{WORKER_URL}/activate",
    json={
        "machineCode":    "test-machine-001",
        "activationCode": "TEST-ABCD-1234-EFGH"
    },
    headers={"X-Auth-Key": ADMIN_KEY}
)
print(resp.json())

#!/usr/bin/env python3
"""One-time import of FileBeam activation codes into Cloudflare ACTIVATION_KV."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_LICENSE_FILE = Path(r"F:\MyProject\PC_phone\licenses.json")
API_ROOT = "https://api.cloudflare.com/client/v4"


def load_license_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("licenses")
    if not isinstance(rows, list) or not rows:
        raise ValueError("licenses.json 中没有可导入的 licenses 数组")

    imported_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        code = str(row.get("code", "")).strip().upper()
        if not code or code in seen:
            continue
        seen.add(code)
        records.append(
            {
                "type": "license",
                "product": payload.get("product", "FileBeam Pro"),
                "code": code,
                "status": str(row.get("status", "active")),
                "use_count": int(row.get("use_count", 0) or 0),
                "max_uses": int(row.get("max_uses", 10) or 10),
                "activated_at": row.get("activated_at"),
                "imported_at": imported_at,
                "license_scope": "personal-multi-device",
                "hardware_bound": False,
            }
        )
    if not records:
        raise ValueError("没有解析到有效激活码")
    return records


def kv_items(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "key": record["code"],
            "value": json.dumps(record, ensure_ascii=False, separators=(",", ":")),
        }
        for record in records
    ]


def api_request(method: str, url: str, token: str, payload: Any | None = None) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Explorer-License-Importer/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            value = json.loads(response.read(4 * 1024 * 1024).decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read(64 * 1024).decode("utf-8", errors="replace")
        raise RuntimeError(f"Cloudflare API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"无法连接 Cloudflare API: {exc.reason}") from exc
    if not isinstance(value, dict) or not value.get("success"):
        raise RuntimeError(f"Cloudflare API 返回失败: {value}")
    return value


def list_namespaces(account_id: str, token: str) -> list[dict[str, Any]]:
    url = f"{API_ROOT}/accounts/{account_id}/storage/kv/namespaces?per_page=100"
    value = api_request("GET", url, token)
    namespaces = value.get("result", [])
    return namespaces if isinstance(namespaces, list) else []


def find_namespace(account_id: str, token: str, hint: str) -> str:
    namespaces = list_namespaces(account_id, token)
    candidates = [
        item
        for item in namespaces
        if hint.lower() in str(item.get("title", "")).lower()
        or hint.lower() in str(item.get("id", "")).lower()
    ]
    if len(candidates) != 1:
        available = ", ".join(str(item.get("title", item.get("id"))) for item in namespaces)
        raise RuntimeError(
            f"无法唯一识别 KV namespace {hint!r}。请用 --namespace-id 指定。"
            f" 可用项: {available}"
        )
    return str(candidates[0]["id"])


def import_with_api(
    account_id: str,
    namespace_id: str,
    token: str,
    items: list[dict[str, str]],
) -> None:
    url = (
        f"{API_ROOT}/accounts/{account_id}/storage/kv/namespaces/"
        f"{urllib.parse.quote(namespace_id)}/bulk"
    )
    batch_size = 200
    for offset in range(0, len(items), batch_size):
        batch = items[offset : offset + batch_size]
        api_request("PUT", url, token, batch)
        print(f"Imported {min(offset + len(batch), len(items))}/{len(items)} activation records.")


def find_wrangler() -> list[str]:
    executable = shutil.which("wrangler")
    if executable:
        return [executable]
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if npx:
        return [npx, "--yes", "wrangler"]
    raise RuntimeError("未找到 wrangler 或 npx")


def import_with_wrangler(namespace_id: str, items: list[dict[str, str]]) -> None:
    temp_path = ROOT / ".wrangler-kv-import.json"
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or os.environ.get("CF_ACCOUNT_ID")
    try:
        temp_path.write_text(
            json.dumps(items, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        command = [
            *find_wrangler(),
            "kv",
            "bulk",
            "put",
            str(temp_path),
            f"--namespace-id={namespace_id}",
            "--remote",
        ]
        if account_id:
            command.append(f"--account-id={account_id}")
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout).strip()[:2000])
        print(f"Imported {len(items)} activation records with wrangler.")
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="一次性导入 FileBeam 激活码到 Cloudflare ACTIVATION_KV"
    )
    parser.add_argument("--file", type=Path, default=DEFAULT_LICENSE_FILE)
    parser.add_argument("--account-id", default=os.environ.get("CLOUDFLARE_ACCOUNT_ID") or os.environ.get("CF_ACCOUNT_ID"))
    parser.add_argument(
        "--namespace-id",
        default=os.environ.get("CLOUDFLARE_KV_NAMESPACE_ID")
        or os.environ.get("ACTIVATION_KV_NAMESPACE_ID"),
    )
    parser.add_argument(
        "--namespace-name",
        default=os.environ.get("ACTIVATION_KV_NAMESPACE_NAME", "ACTIVATION_KV"),
    )
    parser.add_argument("--wrangler", action="store_true", help="使用 wrangler kv bulk put")
    parser.add_argument("--dry-run", action="store_true", help="只检查数据，不写入 Cloudflare")
    parser.add_argument("--confirm", action="store_true", help="确认执行实际导入")
    args = parser.parse_args()

    if not args.file.is_file():
        raise FileNotFoundError(f"找不到授权文件: {args.file}")

    records = load_license_records(args.file)
    items = kv_items(records)
    print(f"Validated {len(records)} unique activation codes. No code content is printed.")

    if args.dry_run:
        print("Dry run completed; Cloudflare was not modified.")
        return 0
    if not args.confirm:
        raise RuntimeError("实际导入需要显式添加 --confirm；可先使用 --dry-run 检查。")

    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if args.wrangler:
        namespace_id = args.namespace_id
        if not namespace_id:
            raise RuntimeError("wrangler 模式需要 --namespace-id 或环境变量 CLOUDFLARE_KV_NAMESPACE_ID")
        import_with_wrangler(namespace_id, items)
        return 0

    if not token:
        raise RuntimeError("缺少 CLOUDFLARE_API_TOKEN，或使用 --wrangler")
    if not args.account_id:
        raise RuntimeError("缺少 Cloudflare account id")
    namespace_id = args.namespace_id or find_namespace(
        args.account_id,
        token,
        args.namespace_name,
    )
    import_with_api(args.account_id, namespace_id, token, items)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Import failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


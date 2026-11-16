"""读取 YAML 配置并逐步执行，步骤级重试，最后输出报告。"""

import argparse
import json
import sys
import time
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from actions import ACTIONS, OUTPUT_DIR  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def run_step(page, step, site_uri):
    action = step["action"]
    if action not in ACTIONS:
        raise ValueError(f"未知动作: {action}")
    ACTIONS[action](page, step, site_uri)


def main():
    parser = argparse.ArgumentParser(description="配置驱动的浏览器自动化执行器")
    parser.add_argument("--config", required=True, help="流程配置文件路径")
    parser.add_argument("--headed", action="store_true", help="显示浏览器窗口")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    steps = config.get("steps", [])
    retries = int(config.get("retry", 1))
    site_uri = (ROOT / "demo" / "site").as_uri()
    OUTPUT_DIR.mkdir(exist_ok=True)

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        page = browser.new_page()

        for index, step in enumerate(steps, start=1):
            name = step.get("name") or step["action"]
            started = time.time()
            passed = False
            error = None

            for attempt in range(retries + 1):
                try:
                    run_step(page, step, site_uri)
                    passed = True
                    break
                except Exception as exc:  # noqa: BLE001
                    error = str(exc)
                    if attempt < retries:
                        time.sleep(1)

            duration = round(time.time() - started, 2)
            if not passed:
                page.screenshot(path=str(OUTPUT_DIR / f"failure_step{index}.png"))

            results.append(
                {
                    "index": index,
                    "step": name,
                    "status": "passed" if passed else "failed",
                    "duration_s": duration,
                    "error": error,
                }
            )
            print(f"[{'PASS' if passed else 'FAIL'}] {index}. {name} ({duration}s)")

            if not passed:
                break

        browser.close()

    report = OUTPUT_DIR / "report.json"
    report.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    failed = [r for r in results if r["status"] == "failed"]
    print(f"\n完成: {len(results) - len(failed)}/{len(results)} 步通过，报告: {report}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

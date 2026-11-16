"""步骤动作实现。每个动作接收 page 与步骤配置，失败时直接抛异常。"""

from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def _resolve(value, site_uri):
    """替换配置里的 {site} 占位符，指向本地示例站点。"""
    if isinstance(value, str) and site_uri:
        return value.replace("{site}", site_uri)
    return value


def goto(page, step, site_uri):
    page.goto(_resolve(step["url"], site_uri), wait_until="load")


def fill(page, step, site_uri):
    page.fill(step["selector"], _resolve(step.get("value", ""), site_uri))


def click(page, step, site_uri):
    page.click(step["selector"])


def expect_text(page, step, site_uri):
    expected = _resolve(step["value"], site_uri)
    actual = page.inner_text(step["selector"])
    if expected not in actual:
        raise AssertionError(f"期望包含 {expected!r}，实际为 {actual!r}")


def wait(page, step, site_uri):
    page.wait_for_timeout(int(step.get("ms", 1000)))


def screenshot(page, step, site_uri):
    OUTPUT_DIR.mkdir(exist_ok=True)
    page.screenshot(path=str(OUTPUT_DIR / step.get("path", "screenshot.png")))


ACTIONS = {
    "goto": goto,
    "fill": fill,
    "click": click,
    "expect_text": expect_text,
    "wait": wait,
    "screenshot": screenshot,
}

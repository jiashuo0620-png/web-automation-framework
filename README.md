# Web Automation Framework

> 配置驱动的浏览器自动化框架：步骤断言、失败重试、异常截图，适合多步骤表单、后台录入、批量任务等流程。

## 背景

后台流程自动化最常见的三个问题是：步骤写死在代码里、出错不知道哪一步、失败后没法复现。

这个框架把流程抽象成配置文件，每一步都能断言，失败自动重试并截图，最后输出结构化报告。

## 功能

- **配置驱动**：用 YAML 描述流程，新增步骤不用改代码
- **步骤断言**：每一步都可以校验页面状态，失败立即定位
- **失败重试**：步骤级重试，避免网络抖动导致的误判
- **异常截图**：失败时自动保存页面截图，方便复现
- **结构化报告**：输出 JSON，记录每步耗时、状态与错误信息

## 技术栈

Python 3.10+ / Playwright / PyYAML

## 快速开始

```bash
pip install -r requirements.txt
playwright install chromium
python src/runner.py --config config/demo_flow.yaml
```

预期输出：

```
[PASS] 1. 打开示例页面 (0.42s)
[PASS] 2. 填写姓名 (0.03s)
[PASS] 3. 填写邮箱 (0.03s)
[PASS] 4. 点击提交 (0.05s)
[PASS] 5. 断言结果 (0.02s)
[PASS] 6. 保存截图 (0.08s)

完成: 6/6 步通过，报告: outputs/report.json
```

想看到浏览器窗口，加 `--headed`：

```bash
python src/runner.py --config config/demo_flow.yaml --headed
```

## 配置示例

```yaml
name: demo-form-flow
retry: 1
steps:
  - action: goto
    url: "{site}/index.html"
  - action: fill
    selector: "#name"
    value: "测试用户"
  - action: expect_text
    selector: "#result"
    value: "提交成功"
```

支持的动作为：`goto` / `fill` / `click` / `expect_text` / `wait` / `screenshot`。

## 设计要点

1. **配置驱动**：流程与执行逻辑分离，业务变化只需要改 YAML
2. **断言即文档**：每一步的预期状态写在配置里，读配置就能看懂流程
3. **重试粒度在步骤级**：只重跑失败的那一步，不从头再来
4. **失败可复现**：截图 + 报告，定位问题不用靠猜

## 目录结构

```
.
├── config/
│   └── demo_flow.yaml      # 流程配置
├── demo/
│   └── site/index.html     # 本地示例页面（无需联网）
├── src/
│   ├── actions.py          # 动作实现
│   └── runner.py           # 执行器
└── requirements.txt
```

## 说明

Demo 使用本地 HTML 页面，不依赖外部网络，克隆下来就能跑。

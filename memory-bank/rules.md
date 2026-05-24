# 项目规范

## Always（必须遵守）

1. **每次修改后自动运行测试** — `python -m unittest discover tests/ -v`
2. **小步提交** — 每完成一个模块就 git commit
3. **模块化优先** — 扫描引擎不依赖 UI，CLI 和 GUI 各自独立调用引擎
4. **使用 type hints** — 所有函数参数和返回值标注类型
5. **修改代码后更新所有 md 文件** — 包括 CLAUDE.md 和 memory-bank/*.md，保持文档与代码一致
6. **每次修改代码后 git commit** — 用简洁的 commit message 描述改动原因，小步提交，每完成一个功能就存档

## Never（严禁）

1. **不要在扫描引擎中直接 print** — 通过返回值/回调传递结果，由 UI 层决定如何展示
2. **不要在 GUI 线程中执行扫描** — 扫描必须在后台 daemon 线程，通过 root.after() 更新 UI
3. **不要引入外部依赖** — 只用 Python 标准库
4. **不要硬编码配置** — IP、端口、线程数等都通过参数传入
5. **不要忽略异常** — 所有 socket 操作必须有 try/except，记录错误原因

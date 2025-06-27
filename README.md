# Python 转 APK 工具

这是一个将Python脚本转换为Android APK的在线工具，支持Kivy、Tkinter和PySide6框架。

## 功能特性

- 上传Python文件和资源文件
- 选择GUI框架（Kivy、Tkinter或PySide6）
- 添加额外依赖和Android权限
- 自动构建APK文件
- 1分钟后自动删除构建结果

## 使用说明

1. 访问 [python-to-apk.vercel.app](https://python-to-apk.vercel.app)
2. 选择GUI框架
3. 上传Python主文件
4. (可选)上传资源文件
5. (可选)添加额外依赖和权限
6. 点击"开始转换"按钮
7. 等待构建完成
8. 下载APK文件（1分钟后自动删除）

## 技术栈

- 前端: HTML5, CSS3, JavaScript
- 后端: Python + Flask
- 部署: Vercel
- CI/CD: GitHub Actions

## 环境变量

| 变量名 | 描述 |
|--------|------|
| API_BASE_URL | API基础URL |
| API_TOKEN | API认证令牌 |
| PYTHON_VERSION | Python版本 |

## 许可证

MIT

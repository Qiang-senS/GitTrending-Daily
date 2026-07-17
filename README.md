# 📊 GitTrending-Daily

**每日 GitHub Trending 热门仓库中文日报**

自动抓取 GitHub Trending 榜单，生成中文日报，每天自动更新。

## ✨ 特性

- 📥 每日自动抓取 GitHub Trending 热门项目
- 🇨🇳 中文展示，一目了然
- 📄 支持 GitHub Pages 在线查看
- 🔄 每天 UTC 0:00 自动更新
- 📱 适配移动端阅读

## 🌐 在线日报

👉 [查看最新日报](https://Qiang-senS.github.io/GitTrending-Daily/)

## 📸 今日预览

![今日日报](output/latest.json)

最新日报存放在 `output/` 目录，格式为 `YYYY-MM-DD.md`。

## 🛠️ 本地运行

```bash
pip install requests beautifulsoup4 lxml
python scripts/fetch_trending.py
```

## 📄 开源协议

MIT License © 2024 [Qiang-senS](https://github.com/Qiang-senS)

#!/usr/bin/env python3
"""
GitTrending-Daily: 每日 GitHub Trending 中文日报
使用 GitHub Search API 获取热门仓库
"""

import json
import os
import requests
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))

def fetch_hot_repos():
    """从 GitHub API 获取高星仓库（模拟 Trending）"""
    all_repos = []

    # 按不同时间段搜索热门仓库
    queries = [
        # 今日热门：最近7天创建的高增长项目
        'created:>2026-07-10 stars:>50 sort:stars-desc',
    ]

    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }

    for query in queries:
        try:
            url = f'https://api.github.com/search/repositories?q={requests.utils.quote(query)}&per_page=25'
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                items = resp.json().get('items', [])
                for item in items:
                    all_repos.append({
                        'full_name': item['full_name'],
                        'author': item['owner']['login'],
                        'repo_name': item['name'],
                        'description': item.get('description', '') or '',
                        'lang': item.get('language', '') or '',
                        'stars': item['stargazers_count'],
                        'forks': item['forks_count'],
                        'open_issues': item['open_issues_count'],
                        'topics': item.get('topics', []),
                        'html_url': item['html_url'],
                        'created_at': item.get('created_at', ''),
                        'updated_at': item.get('updated_at', ''),
                    })
        except Exception as e:
            print(f'[WARN] 搜索失败: {e}')

    # 去重（按 full_name）
    seen = set()
    unique = []
    for repo in all_repos:
        if repo['full_name'] not in seen:
            seen.add(repo['full_name'])
            unique.append(repo)

    # 按 star 数排序
    unique.sort(key=lambda r: r['stars'], reverse=True)
    return unique[:20]


def fetch_trending_from_web():
    """从网页抓取 Trending（备用方案）"""
    url = 'https://github.com/trending?since=daily'
    headers = {
        'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                       'AppleWebKit/537.36'),
        'Accept': 'text/html',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f'[WARN] 网页抓取失败: {e}')
        return []

    # 简单正则提取仓库名
    import re
    repos = []
    # 找 owner/name 格式
    pattern = r'href="/trending[^"]*">.*?<h2[^>]*>.*?href="/([^/"]+/[^/"]+)"'
    matches = re.findall(r'href="/([^/"]+/[^/"]+)"', resp.text)

    seen = set()
    for m in matches:
        if '/' in m and m.count('/') == 1:
            if m not in seen:
                seen.add(m)
                repos.append({'full_name': m})

    return repos


def enrich_repos(repos):
    """补充仓库详细信息"""
    for repo in repos:
        full_name = repo.get('full_name', '')
        if not full_name:
            continue
        try:
            url = f'https://api.github.com/repos/{full_name}'
            resp = requests.get(url, headers={
                'Accept': 'application/vnd.github.v3+json'
            }, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                repo['stars'] = data.get('stargazers_count', 0)
                repo['forks'] = data.get('forks_count', 0)
                repo['open_issues'] = data.get('open_issues_count', 0)
                repo['description'] = repo.get('description') or (data.get('description') or '')
                repo['lang'] = repo.get('lang') or (data.get('language') or '')
                repo['topics'] = data.get('topics', [])
                repo['html_url'] = data['html_url']
                repo['author'] = data['owner']['login']
                repo['repo_name'] = data['name']
            else:
                print(f'[WARN] 获取 {full_name} 详情失败: {resp.status_code}')
        except Exception as e:
            print(f'[WARN] 获取详情失败 {full_name}: {e}')

    # 过滤掉没有 star 的或者信息不完整的
    repos = [r for r in repos if r.get('stars', 0) > 0]
    repos.sort(key=lambda r: r['stars'], reverse=True)
    return repos[:20]


def generate_markdown(repos):
    """生成中文日报 Markdown"""
    now = datetime.now(BEIJING_TZ)
    date_str = now.strftime('%Y-%m-%d')
    weekday_map = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekday_map[now.weekday()]

    lines = []
    lines.append(f'# 📊 GitHub Trending 日报 — {date_str} ({weekday})\n')
    lines.append(f'> 每日自动更新 · 数据来源: [GitHub](https://github.com/trending)\n')
    lines.append('---\n')

    if not repos:
        lines.append('*今日暂无热门仓库数据*\n')
        return '\n'.join(lines)

    for i, repo in enumerate(repos, 1):
        full_name = repo.get('full_name', '?')
        desc = repo.get('description', '暂无描述')
        lang = repo.get('lang', '')
        stars = repo.get('stars', 0)
        forks = repo.get('forks', 0)
        topics = repo.get('topics', [])
        url = repo.get('html_url', f'https://github.com/{full_name}')

        lines.append(f'### {i}. [{full_name}]({url})\n')
        if desc:
            lines.append(f'> {desc}\n')
        lines.append('')

        info_parts = []
        if lang:
            info_parts.append(f'🔤 **{lang}**')
        info_parts.append(f'⭐ **{stars:,}**')
        info_parts.append(f'🍴 **{forks:,}**')

        lines.append(f'{" · ".join(info_parts)}\n')

        if topics:
            topics_str = ' '.join([f'`{t}`' for t in topics[:6]])
            lines.append(f'🏷️ {topics_str}\n')
        lines.append('')

    lines.append('---\n')

    # 赞助区
    lines.append('## 🤝 支持这个项目\n')
    lines.append('如果这个日报对你有帮助，欢迎赞助支持持续开发！\n')
    lines.append('')
    lines.append(f'![支付宝赞赏码](assets/alipay_qr.jpg)\n')
    lines.append('')

    lines.append(f'*最后更新: {now.strftime("%Y-%m-%d %H:%M:%S")}*\n')

    return '\n'.join(lines)


def main():
    os.makedirs('output', exist_ok=True)
    os.makedirs('docs', exist_ok=True)

    print('[INFO] 开始获取热门仓库...')

    # 先用 API 搜索
    repos = fetch_hot_repos()

    # 如果 API 搜索没结果，尝试网页抓取
    if not repos:
        print('[INFO] API 搜索无结果，尝试网页抓取...')
        web_repos = fetch_trending_from_web()
        if web_repos:
            repos = enrich_repos(web_repos)

    print(f'[INFO] 获取到 {len(repos)} 个仓库')

    if not repos:
        print('[WARN] 没有任何数据，生成空日报')
        repos = []

    # 生成日报
    markdown = generate_markdown(repos)

    # 写入文件
    today = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
    output_path = f'output/{today}.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f'[OK] 日报: {output_path}')

    # 写入 docs/index.md
    with open('docs/index.md', 'w', encoding='utf-8') as f:
        f.write(markdown)
    print('[OK] Pages: docs/index.md')

    # 写入 latest.json
    with open('output/latest.json', 'w', encoding='utf-8') as f:
        json.dump({
            'date': today,
            'count': len(repos),
            'repos': [{
                'name': r.get('full_name', ''),
                'url': r.get('html_url', ''),
                'description': r.get('description', ''),
                'language': r.get('lang', ''),
                'stars': r.get('stars', 0),
            } for r in repos]
        }, f, ensure_ascii=False, indent=2)
    print('[OK] JSON: output/latest.json')

    print('\n=== ✅ 完成 ===')


if __name__ == '__main__':
    main()

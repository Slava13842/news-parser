#!/usr/bin/env python3
import argparse
import sqlite3
import sys
from dataclasses import dataclass
from typing import List
import requests
from bs4 import BeautifulSoup

@dataclass
class Article:
    title: str
    url: str

def fetch_html(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (NewsParser/1.0)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text

def parse_articles(html: str) -> List[Article]:
    soup = BeautifulSoup(html, 'html.parser')
    results: List[Article] = []
    for h in soup.select('h1 a, h2 a, h3 a'):
        title = (h.get_text(strip=True) or '').strip()
        link = h.get('href') or ''
        if title and link:
            results.append(Article(title=title, url=link))
    return results

def init_db(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS articles (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT)')
    con.commit()
    con.close()

def save_articles(db_path: str, articles: List[Article]) -> int:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executemany('INSERT INTO articles(title, url) VALUES (?, ?)', [(a.title, a.url) for a in articles])
    con.commit()
    count = cur.rowcount
    con.close()
    return count

def search_articles(db_path: str, keyword: str) -> List[Article]:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('SELECT title, url FROM articles WHERE title LIKE ?', (f'%{keyword}%',))
    rows = cur.fetchall()
    con.close()
    return [Article(title=r[0], url=r[1]) for r in rows]

def cmd_fetch(args):
    init_db(args.db)
    html = fetch_html(args.url)
    articles = parse_articles(html)
    saved = save_articles(args.db, articles)
    print(f'Saved {saved} articles to {args.db}')

def cmd_search(args):
    results = search_articles(args.db, args.keyword)
    if not results:
        print('No results.')
        return
    for i, a in enumerate(results, 1):
        print(f'{i:02d}. {a.title} -> {a.url}')

def build_parser():
    p = argparse.ArgumentParser(description='News Parser CLI')
    sub = p.add_subparsers(dest='command')

    pf = sub.add_parser('fetch', help='Fetch URL and save parsed articles to DB')
    pf.add_argument('--url', required=True, help='Target URL')
    pf.add_argument('--db', default='data/news.db', help='SQLite DB path')
    pf.set_defaults(func=cmd_fetch)

    ps = sub.add_parser('search', help='Search articles in DB')
    ps.add_argument('--db', default='data/news.db', help='SQLite DB path')
    ps.add_argument('--keyword', required=True, help='Keyword to search in titles')
    ps.set_defaults(func=cmd_search)

    return p

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, 'func'):
        parser.print_help()
        return 0
    return args.func(args)

if __name__ == '__main__':
    main()

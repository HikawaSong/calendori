import os
from datetime import datetime
from typing import List, Dict
import httpx
import re
from bs4 import BeautifulSoup
import asyncio
from fake_useragent import UserAgent
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Event, Artist
import unicodedata


SOURCE_URL = os.getenv("EVENTS_SOURCE_URL", "https://bang-dream.com/events")
ua = UserAgent()


def get_headers() -> dict:
    return {
        "User-Agent": ua.random,
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,webp,*/*;q=0.8",
        "Referer": "https://bang-dream.com/",
        "Connection": "keep-alive",
    }


def get_source_url(page: int = 1) -> str:
    return f"{SOURCE_URL}/page/{page}"


async def fetch_page_source(url: str) -> BeautifulSoup:

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            current_headers = get_headers()
            response = await client.get(url, headers=current_headers, timeout=10.0)
            if response.status_code != 200:
                if response.status_code != 404:
                    print(f"❌ 抓取停止或失败: {url} 状态码: {response.status_code}")
                return None
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(f"❌ 请求发生异常: {e}")
            return None


def parse_events(soup: BeautifulSoup) -> List[Dict]:

    # 1. 找到所有的活动条目
    articles = soup.select("article.p-live-event-list__item")

    page_data = []

    for article in articles:
        # --- 提取字段 ---
        title = article.select_one(".p-live-event-list__item-title").get_text(
            strip=True
        )
        link = article.select_one("a.p-live-event-list__item-link")["href"]
        img_node = article.select_one(".p-live-event-list__item-thumb img")
        thumbnail_url = img_node["src"] if img_node else ""
        category = article.select_one(
            ".p-live-event-list__item-category span"
        ).get_text(strip=True)
        place = get_val_by_label(article, "場所")

        artist_nodes = article.select(".p-live-event-list__item-artist-item")
        artists = [node.get_text(strip=True) for node in artist_nodes]

        raw_date_text = get_val_by_label(article, "開催日")
        event_dates = convert_raw_text_to_iso_dates(raw_date_text)
        # 取第一个日期作为活动开始日期
        event_start_date = event_dates[0] if event_dates else None

        # --- 组装数据 ---
        page_data.append(
            {
                "title": title,
                "event_url": link,
                "thumbnail_url": thumbnail_url,
                "category": category,
                "place": place,
                "artists": artists,  # List类型
                "dates": event_dates,  # List类型，例 ["2026-03-20", "2026-03-21"]
                "event_start_date": event_start_date,
            }
        )

    return page_data


def get_val_by_label(article, label_text: str) -> str:

    node = article.find("h2", string=re.compile(label_text))
    if node:
        target_p = node.find_next("p")
        return target_p.get_text(strip=True) if target_p else ""
    return ""


def convert_raw_text_to_iso_dates(raw_text: str) -> list[str]:
    """
    日期转换：处理 '2026年3月20日(金)・21日(土)' 这种复杂格式
    """
    # 提取年份，默认取 2026 (或者从字符串动态提)

    if not raw_text:
        return []

    # 全角转半角
    raw_text = unicodedata.normalize("NFKC", raw_text)

    year_match = re.search(r"(\d{4})", raw_text)
    year = year_match.group(1) if year_match else str(datetime.now().year)

    # 按 '・' 分割多段日期
    segments = re.split(r"[・/]", raw_text)
    dates = []
    current_month = "01"

    for seg in segments:
        # 看看这一段有没有月份（比如跨月的情况）
        m_match = re.search(r"(\d{1,2})月", seg)
        if m_match:
            current_month = m_match.group(1).zfill(2)

        # 提取日子
        d_match = re.search(r"(\d{1,2})日", seg)
        if d_match:
            day = d_match.group(1).zfill(2)
            dates.append(f"{year}-{current_month}-{day}")

    return sorted(list(set(dates)))


def save_events_to_db(db: Session, scraped_data: list[dict]):

    new_events_count = 0

    # 1.查出 DB 里现有的所有乐队，放在内存
    existing_artists = {a.name: a for a in db.query(Artist).all()}

    # 2. 性能优化：查出所有已存在的 Event 标题（用于快速排重）
    existing_event_titles = {e.title for e in db.query(Event.title).all()}

    for item in scraped_data:
        # --- A. 排重逻辑 ---
        if item["title"] in existing_event_titles:
            continue

        # --- B. 处理关联的复数乐队 ---
        current_event_artists = []
        for b_name in item["artists"]:
            if b_name in existing_artists:
                artist_obj = existing_artists[b_name]
            else:
                artist_obj = Artist(name=b_name)
                db.add(artist_obj)
                db.flush()  # 立即获取 ID，但不提交事务
                existing_artists[b_name] = artist_obj
            current_event_artists.append(artist_obj)

        # --- C. 创建 Event 对象 ---
        new_event = Event(
            title=item["title"],
            dates=item["dates"],  # 传入 Python List，SQLAlchemy JSON 自动处理
            event_start_date=item["event_start_date"],
            place=item["place"],
            category=item["category"],
            event_url=item["event_url"],
            thumbnail_url=item["thumbnail_url"],  #
            artists=current_event_artists,  # 关联复数 Artist 对象，中间表自动填充
        )
        db.add(new_event)
        new_events_count += 1

    # --- D. 统一提交事务 ---
    try:
        db.commit()
        print(f"✅ 成功写入 {new_events_count} 个新活动。")
        return new_events_count
    except Exception as e:
        db.rollback()
        print(f"❌ 数据库提交失败，已回滚: {e}")


async def main():
    page = 1
    all_extracted_items = []
    max_pages = int(os.getenv("EVENTS_CRAWL_MAX_PAGES", "50"))

    print("🚀 开始批量爬取任务...")

    while page <= max_pages:
        url = get_source_url(page)
        print(f"📡 正在处理第 {page} 页: {url}")

        soup = await fetch_page_source(url)

        # 终止条件 1: 请求失败或 404
        if not soup:
            print(f"🏁 翻页结束：在第 {page} 页未发现更多内容。")
            break

        page_items = parse_events(soup)

        # 终止条件 2: 页面没有活动条目
        if not page_items:
            print(f"🏁 翻页结束：第 {page} 页为空。")
            break

        print(f"✅ 成功提取 {len(page_items)} 条数据")
        all_extracted_items.extend(page_items)

        page += 1
        await asyncio.sleep(1)

    print(f"\n📊 爬取阶段结束，共抓取到 {len(all_extracted_items)} 条活动数据。")

    if all_extracted_items:
        print("💾 开始执行数据库批量写入...")
        with SessionLocal() as db:
            save_events_to_db(db, all_extracted_items)
    else:
        print("⚠️ 未发现任何数据，跳过数据库写入。")


if __name__ == "__main__":
    asyncio.run(main())

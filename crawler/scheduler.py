import asyncio
from apscheduler.schedulers.blocking import BlockingScheduler
from crawler.spiders.events_crawler import main as events_crawler


def start_crawl_job():
    try:
        asyncio.run(events_crawler())
    except Exception as e:
        print(f"❌ [Scheduler] 爬虫任务执行失败: {e}")


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(
        start_crawl_job,
        "cron",
        hour=3,
        minute=0,
        id="daily_event_crawl",
        replace_existing=True,
    )

    print("🚀 [Scheduler] 定时任务服务已启动，准备监控任务...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("🛑 [Scheduler] 服务已停止")


if __name__ == "__main__":
    main()

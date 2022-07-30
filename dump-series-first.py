import requests
import sqlite3
import lxml.html
import time

# 適当に配信停止した作品のseriesを使うと少しでもレスポンスが減らせてお得
r = requests.get("https://www.nicovideo.jp/series/337468")
r.raise_for_status()
r = lxml.html.fromstring(r.content)
series_links = r.xpath('//li[@class="SeriesMenuContainer-seriesItem "]/a/@href')
print("len", len(series_links))
for series in series_links:
    series_id = int(list(series.split("/"))[-1])
    print(series_id)
    if series_id < 1:
        raise Exception("series_id invalid")
    with sqlite3.connect("./data.sqlite3") as db:
        if db.execute("SELECT COUNT(*) FROM series WHERE id = ?", (series_id,)).fetchone()[0] > 0:
            continue
        v = requests.get("https://nvapi.nicovideo.jp/v1/series/" + str(series_id), headers={
            "X-Frontend-Id": "6",
        })
        v.raise_for_status()
        v = v.json()
        time.sleep(1)
        if v["data"]["totalCount"] != len(v["data"]["items"]):
            raise Exception("wrong count...")
        db.execute("INSERT INTO series(id, created_at, title) VALUES(?, ?, ?)", (v["data"]["detail"]["id"], v["data"]["detail"]["createdAt"], v["data"]["detail"]["title"]))
        db.executemany("INSERT INTO series_contents(danime_video_id, series_id) VALUES (?, ?)", [(i["video"]["id"], series_id) for i in v["data"]["items"]])
        db.commit()
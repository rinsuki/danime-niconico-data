import requests
import sqlite3
import time

page = 1

with sqlite3.connect("./data.sqlite3") as db:
    while True:
        print("get page", page)
        r = requests.get("https://nvapi.nicovideo.jp/v1/nicoch/ch2632720/series", params={
            "pageSize": 100,
            "page": page,
            "_frontendId": "6",
        })
        page += 1
        r.raise_for_status()
        time.sleep(1)
        r = r.json()
        items = r["data"]["items"]
        if len(items) == 0:
            break
        for item in r["data"]["items"]:
            series_id = item["id"]
            print(f"series/{series_id}")
            current = db.execute("SELECT api_thumbnail_url, api_items_count FROM series WHERE id = ?", (series_id,)).fetchone()
            if current is not None:
                current_thumbnail, current_count = current
                if current_thumbnail == item["thumbnailUrl"] and current_count == item["itemsCount"]:
                    continue
            v = requests.get(f"https://nvapi.nicovideo.jp/v1/series/{series_id}", params={
                "_frontendId": "6",
            })
            v.raise_for_status()
            v = v.json()
            time.sleep(1)
            if v["data"]["totalCount"] != len(v["data"]["items"]):
                raise Exception("wrong count")
            db.executemany("INSERT INTO series_contents(danime_video_id, series_id) VALUES (?, ?) ON CONFLICT(danime_video_id) DO NOTHING", [(i["video"]["id"], series_id) for i in v["data"]["items"]])
            db.execute("INSERT INTO series(id, created_at, title, api_thumbnail_url, api_items_count) VALUES(?, ?, ?, ?, ?) ON CONFLICT DO UPDATE SET title = EXCLUDED.title, api_thumbnail_url = EXCLUDED.api_thumbnail_url, api_items_count = EXCLUDED.api_items_count", (v["data"]["detail"]["id"], v["data"]["detail"]["createdAt"], v["data"]["detail"]["title"], v["data"]["detail"]["thumbnailUrl"], v["data"]["totalCount"]))
            db.commit()

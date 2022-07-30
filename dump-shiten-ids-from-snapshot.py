import requests
import time
import datetime
import sqlite3

offset = 0

updated_at = requests.get("https://api.search.nicovideo.jp/api/v2/snapshot/version").json()["last_modified"]
# TODO: もう数時間で更新されそうだったら断念する

with sqlite3.connect("./data.sqlite3") as db:
    while True:
        print(offset)
        time.sleep(1)
        r = requests.get("https://api.search.nicovideo.jp/api/v2/snapshot/video/contents/search", params={
            "q": "dアニメストア",
            "targets": "tagsExact",
            "fields": "contentId,channelId,title,viewCounter,commentCounter,mylistCounter,likeCounter,startTime,thumbnailUrl,lengthSeconds",
            "_sort": "+startTime",
            "_limit": "100",
            "_offset": offset,
        })
        r.raise_for_status()
        r = r.json()
        if len(r["data"]) == 0:
            break
        rows = []
        for v in r["data"]:
            offset += 1
            if v["channelId"] != 2632720:
                continue
            rows.append((v["contentId"], v["channelId"], v["title"], v["viewCounter"], v["commentCounter"], v["mylistCounter"], v["likeCounter"], v["startTime"], v["thumbnailUrl"], updated_at, v["lengthSeconds"]))
        db.executemany("INSERT OR REPLACE INTO videos (id, channel_id, title, view_counter, comment_counter, mylist_counter, like_counter, start_time, thumbnail_url, updated_at, length_seconds) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
        db.commit()
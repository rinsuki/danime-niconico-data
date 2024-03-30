import sqlite3
import os
import csv
import shutil
import zlib
import json

def clean_dir(path: str):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            raise Exception(f"{path} isn't dir")
    os.makedirs(path)

# 最初のほうはシリーズ機能対応でめちゃくちゃ狭いID範囲に多数のシリーズがあるが、
# 最近は一般ユーザーのぶんが合間に十分に入っているので結構広いID範囲でいっしょにしても大丈夫…たぶん
SERIES_CONTENTS_GID = '(CASE series_id < 100000 WHEN TRUE THEN (series_id/250) + 1000000 ELSE (series_id/10000) + 2000000 END)'
VIDEOS_GID = 'SUBSTR(id, 0, LENGTH(id) - 4)'

with sqlite3.connect("./data.sqlite3") as db:
    cur = db.execute("SELECT id, created_at, title, api_thumbnail_url, api_items_count FROM series ORDER BY id ASC")
    clean_dir("csv/series")
    with open("csv/series/1.csv", "w") as f:
        c = csv.writer(f)
        c.writerows(cur.fetchall())
    gcur = db.execute(f"SELECT {SERIES_CONTENTS_GID} AS gid FROM series_contents GROUP BY gid ORDER BY COUNT(*) DESC")
    clean_dir("csv/series_contents")
    for gid, in gcur.fetchall():
        cur = db.execute(f"SELECT series_id, danime_video_id FROM series_contents WHERE ({SERIES_CONTENTS_GID}) = ? ORDER BY series_id ASC, danime_video_id ASC", (gid,))
        print(gid)
        with open(f"csv/series_contents/{gid}.csv", "w") as f:
            c = csv.writer(f)
            c.writerows(cur.fetchall())
    gcur = db.execute(f"SELECT {VIDEOS_GID} as gid FROM videos GROUP BY gid")
    clean_dir("csv/videos")
    # gzip はタイムスタンプが入って毎回更新されるので、zlibを使う
    with open("csv/videos_updated_date.json.zlib.bin", "wb") as f:
        f.write(zlib.compress(json.dumps(db.execute("SELECT id, updated_at FROM videos").fetchall()).encode("utf-8")))
    for gid, in gcur.fetchall():
        cur = db.execute(f"SELECT id, start_time, channel_id, length_seconds, title, view_counter, comment_counter, mylist_counter, like_counter, 'updated_at_was_moved', thumbnail_url FROM videos WHERE ({VIDEOS_GID}) = ? ORDER BY id ASC", (gid,))
        print(gid)
        with open(f"csv/videos/{gid}.csv", "w") as f:
            c = csv.writer(f)
            c.writerows(cur.fetchall())
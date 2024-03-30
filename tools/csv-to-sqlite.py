import sqlite3
import os
from glob import iglob
import csv
import json
import zlib

if os.path.exists("./data.sqlite3"):
    os.remove("./data.sqlite3")
with sqlite3.connect("./data.sqlite3") as db:
    db.execute("""
        CREATE TABLE thread_ids (
            thread_id INTEGER UNIQUE NOT NULL,
            video_id TEXT NOT NULL
        ) STRICT
    """)
    for csvpath in iglob("./csv/thread_ids/*.csv"):
        print("TODO", csvpath)
    db.execute("""
        CREATE TABLE danime_to_channel (
            danime_video_id TEXT UNIQUE NOT NULL,
            channel_video_id TEXT UNIQUE
        ) STRICT
    """)
    for csvpath in iglob("./csv/danime_to_channel/*.csv"):
        print("TODO", csvpath)
    db.execute("""
        CREATE TABLE series_contents (
            danime_video_id TEXT UNIQUE NOT NULL,
            series_id INTEGER
        ) STRICT
    """)
    for csvpath in iglob("./csv/series_contents/*.csv"):
        with open(csvpath, "r") as f:
            c = csv.reader(f)
            db.executemany("INSERT INTO series_contents (series_id, danime_video_id) VALUES (?, ?)", c)
    db.execute("""
        CREATE TABLE series (
            id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            title TEXT NOT NULL,
            api_thumbnail_url TEXT NOT NULL DEFAULT '',
            api_items_count INTEGER NOT NULL DEFAULT 0
        ) STRICT
    """)
    for csvpath in iglob("./csv/series/*.csv"):
        with open(csvpath, "r") as f:
            c = csv.reader(f)
            db.executemany("INSERT INTO series (id, created_at, title, api_thumbnail_url, api_items_count) VALUES (?, ?, ?, ?, ?)", c)
    db.execute("""
        CREATE TABLE videos (
            id TEXT PRIMARY KEY,
            channel_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            length_seconds INTEGER NOT NULL,
            view_counter INTEGER NOT NULL,
            comment_counter INTEGER NOT NULL,
            mylist_counter INTEGER NOT NULL,
            like_counter INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            thumbnail_url TEXT NOT NULL,
            updated_at TEXT NOT NULL
        ) STRICT
    """)
    for csvpath in iglob("./csv/videos/*.csv"):
        with open(csvpath, "r") as f:
            c = csv.reader(f)
            db.executemany("INSERT INTO videos (id, start_time, channel_id, length_seconds, title, view_counter, comment_counter, mylist_counter, like_counter, updated_at, thumbnail_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", c)
    with open("csv/videos_updated_date.json.zlib.bin", "rb") as f:
        j = json.loads(zlib.decompress(f.read()).decode("utf-8"))
        for k, v in j:
            db.execute("UPDATE videos SET updated_at = ? WHERE id = ?", (v, k))
    # ---
    db.commit()

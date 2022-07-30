import sqlite3
import json
import os
import shutil

comment_per_series_query = """
    SELECT
        series.id, series.title,
        SUM(videos.comment_counter) as all_comment_count,
        COUNT(*) as count,
        MAX(videos.comment_counter) as max_comment_count,
        AVG(videos.comment_counter) as avg_comment_count,
        MEDIAN(videos.comment_counter) as median_comment_count,
        MAX(videos.comment_counter)/MAX(1.0, CAST(MEDIAN(videos.comment_counter) AS REAL)) as max_median_mag_comment_count
    FROM series
    JOIN series_contents ON series_contents.series_id = series.id
    JOIN videos ON videos.id = series_contents.danime_video_id
    GROUP BY series.id
    ORDER BY all_comment_count DESC;
"""

class Median:
    def __init__(self):
        self.data = []

    def step(self, x):
        self.data.append(x)

    def finalize(self):
        data = sorted(self.data)
        ld = len(data)
        if ld == 0:
            return int(0)
        elif ld % 2 == 0:
            return int((data[ld // 2 - 1] + data[ld // 2]) / 2)
        else:
            return int(data[ld // 2])

def clean_dir(path: str):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            raise Exception(f"{path} isn't dir")
    os.makedirs(path)

with sqlite3.connect("./data.sqlite3") as db:
    db.row_factory = sqlite3.Row
    db.create_aggregate("median", 1, Median)
    cur = db.execute(comment_per_series_query)
    clean_dir("public/data")
    with open("public/data/comment-per-series-ranking.json", "w") as f:
        f.write("[")
        is_first = True
        for o in cur:
            o = dict(o)
            if is_first:
                is_first = False
            else:
                f.write("\n,")
            json.dump(o, f, ensure_ascii=False)
        f.write("\n]")
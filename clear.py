# 每天凌晨4:00清水chat.db
import sqlite3
import time

day = time.localtime().tm_yday
while True:
    t = time.localtime()
    if t.tm_hour == 4 and t.tm_yday > day:
        d = sqlite3.connect('hacker.db')
        c = d.cursor()
        c.execute('delete from chat')
        d.commit()
        c.close()
        d.close()
        day = t.tm_yday
    time.sleep(600)  # 10min

import sqlite3

con = sqlite3.connect('data.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS "Movies"
                    ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
                    "movie_name" VARCHAR(100),
                    "frame_timestamp" VARCHAR(100),
                    "frame_norm" INTEGER,
                    "frame_dif" INTEGER,
                    "median" INTEGER);
                    ''')

def insert_into_db(mas):
    query_str = '''INSERT INTO Movies(movie_name, frame_timestamp, frame_norm, frame_dif, median) VALUES'''
    for i in mas:
        query_str +='''('{0}','{1}','{2}','{3}','{4}')'''.format(i[0], i[1], i[2], i[3], i[4])
        query_str+=','
    query_str=query_str[:-1]
    query_str+=';'
    cur.execute(query_str)
    con.commit()
    return

def drop_data(movie):
    query_str = '''DELETE FROM Movies WHERE movie_name="{0}"'''.format(movie)
    cur.execute(query_str)
    con.commit()
    return
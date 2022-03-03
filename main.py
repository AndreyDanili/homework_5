if __name__ == '__main__':
    import sqlalchemy
    from pprint import pprint
    import data

    engine = sqlalchemy.create_engine('postgresql://homework:123456@localhost:5432/homework_db')
    conn = engine.connect()

    conn.execute("""CREATE TABLE IF NOT EXISTS genre (
                id serial PRIMARY KEY,
                name varchar(40) NOT NULL
                );"""
                 )

    conn.execute("""CREATE TABLE IF NOT EXISTS singer (
                id serial PRIMARY KEY,
                name varchar(40) unique NOT NULL
                );"""
                 )

    conn.execute("""CREATE TABLE IF NOT EXISTS singer_genre (
                id serial PRIMARY KEY,
                singer_id integer NOT NULL REFERENCES singer(id),
                genre_id integer NOT NULL REFERENCES genre(id)
                );"""
                 )

    conn.execute("""CREATE TABLE IF NOT EXISTS album (
                id serial PRIMARY KEY,
                name varchar(40) NOT NULL,
                release integer NOT NULL
                );"""
                 )

    conn.execute("""CREATE TABLE IF NOT EXISTS singer_album (
                id serial PRIMARY KEY,
                singer_id integer NOT NULL REFERENCES singer(id),
                album_id integer NOT NULL REFERENCES album(id)
                );"""
                 )

    conn.execute("""CREATE TABLE IF NOT EXISTS track (
                id serial PRIMARY KEY,
                name varchar(120) NOT NULL,
                duration integer NOT NULL,
                album_id integer NOT NULL REFERENCES album(id)
                );"""
                 )

    conn.execute("""CREATE TABLE IF NOT EXISTS collection (
                id serial PRIMARY KEY,
                name varchar(40) not null,
                release integer not null
                );"""
                 )

    conn.execute("""CREATE TABLE IF NOT EXISTS track_collection (
                id serial PRIMARY KEY,
                track_id integer NOT NULL REFERENCES track(id),
                collection_id integer NOT NULL REFERENCES collection(id)
                );"""
                 )
    conn.execute(f"INSERT into singer (name) values {data.singer};")
    conn.execute(f"INSERT into genre (name) values {data.genre};")
    conn.execute(f"INSERT into singer_genre (singer_id, genre_id) values {data.singer_genre};")
    conn.execute(f"INSERT into album (name, release) values {data.album};")
    conn.execute(f"INSERT into singer_album (singer_id, album_id) values {data.singer_album};")
    conn.execute(f"INSERT into track (name, duration, album_id) values {data.track};")
    conn.execute(f"INSERT into collection (name, release) values {data.collection};")
    conn.execute(f"INSERT into track_collection (track_id, collection_id) values {data.track_collection};")

    singer_quantity = conn.execute("""SELECT name, COUNT(singer_id) singer_q FROM genre g
                            JOIN singer_genre sg ON g.id = sg.genre_id
                            GROUP BY name
                            ;""").fetchall()

    track_quantity = conn.execute("""SELECT COUNT(t.name) track_q FROM album a
                            JOIN track t ON a.id = t.album_id
                            WHERE a.release BETWEEN 2019 AND 2020
                            ;""").fetchall()

    avg_dur_track = conn.execute("""SELECT a.name, ROUND(AVG(t.duration), 2) avg_d FROM album a
                            JOIN track t ON a.id = t.album_id
                            GROUP BY a.name
                            ORDER BY AVG(t.duration)
                            ;""").fetchall()

    singer_no_2020 = conn.execute("""SELECT DISTINCT s.name FROM singer s
                            WHERE s.name NOT IN (
                                SELECT DISTINCT s.name FROM singer s
                                LEFT JOIN singer_album sa ON s.id = sa.singer_id
                                LEFT JOIN album a ON sa.album_id = a.id
                                WHERE a.release = 2020)
                            ;""").fetchall()

    collection_singer = conn.execute("""SELECT c.name FROM collection c
                            JOIN track_collection tc ON c.id = tc.collection_id
                            JOIN track t ON tc.track_id = t.id
                            JOIN album a ON t.album_id = a.id
                            JOIN singer_album sa ON a.id = sa.album_id
                            JOIN singer s ON sa.singer_id = s.id
                            WHERE s.name LIKE '%%Calvin Harris%%'
                            ;""").fetchall()

    album_genre = conn.execute("""SELECT a.name, COUNT(sg.genre_id) genre_count FROM album a
                                LEFT JOIN singer_album sa ON a.id = sa.album_id
                                LEFT JOIN singer s ON sa.singer_id = s.id
                                LEFT JOIN singer_genre sg ON s.id = sg.singer_id
                                GROUP BY a.name
                                HAVING COUNT(sg.genre_id) > 1
                            ;""").fetchall()

    no_track_collection = conn.execute("""SELECT t.name FROM track t
                            LEFT JOIN track_collection tc ON t.id = tc.track_id
                            WHERE tc.collection_id IS NULL
                            ;""").fetchall()

    singer_min_duration = conn.execute("""SELECT s.name, MIN(t.duration) FROM singer s
                            JOIN singer_album sa ON s.id = sa.singer_id
                            JOIN album a ON sa.singer_id = a.id
                            JOIN track t ON a.id = t.album_id
                            GROUP BY s.name  
                            HAVING MIN(t.duration) = (
                                SELECT MIN(t.duration) FROM track t)          
                            ;""").fetchall()

    album_min_track = conn.execute("""SELECT a.name, COUNT(t.name) FROM album a
                            JOIN track t ON a.id = t.album_id
                            GROUP BY a.name
                            HAVING COUNT(t.name) = (
                                SELECT COUNT(t.name) FROM album a
                                JOIN track t ON a.id = t.album_id
                                GROUP BY a.name
                                ORDER BY COUNT(t.name)
                                LIMIT 1) 
                            ;""").fetchall()

    pprint(singer_quantity)
    pprint(track_quantity)
    pprint(avg_dur_track)
    pprint(singer_no_2020)
    pprint(collection_singer)
    pprint(album_genre)
    pprint(no_track_collection)
    pprint(singer_min_duration)
    pprint(album_min_track)

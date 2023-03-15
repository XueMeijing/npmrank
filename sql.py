import sqlite3
import datetime
import json

DATABASE = 'database.db'

'''
id                        TEXT PRIMARY KEY     NOT NULL,  包名
name                      TEXT                 NOT NULL,  包名
npm_url                   TEXT                 NOT NULL,  npm地址
github_url                TEXT                 ,          github地址
homepage_url              TEXT                 ,          主页地址
last_publish              TEXT                 ,          上次更新时间
week_downloads            TEXT                 NOT NULL,  最近一年每周的下载量
last_day_downloads        TEXT                 NOT NULL,  昨天总下载量
last_week_downloads       TEXT                 NOT NULL,  上周总下载量
last_month_downloads      TEXT                 NOT NULL,  上月总下载量
last_year_downloads       TEXT                 NOT NULL,  去年总下载量
all_time_downloads        TEXT                 NOT NULL,  全部下载量
github_star               TEXT                 NOT NULL   github star
'''

# 查询结果元组转字典
def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
  return d

def init_db():
  db = sqlite3.connect(DATABASE, check_same_thread=False)
  cursor = db.cursor()
  create_table_query = '''CREATE TABLE IF NOT EXISTS package(
                          id                        TEXT PRIMARY KEY     NOT NULL,
                          name                      TEXT                 NOT NULL,
                          npm_url                   TEXT                 NOT NULL,
                          github_url                TEXT                 ,
                          homepage_url              TEXT                 ,
                          last_publish              TEXT                 ,
                          week_downloads            TEXT                 ,
                          last_day_downloads        INTEGER              ,
                          last_week_downloads       INTEGER              ,
                          last_month_downloads      INTEGER              ,
                          last_year_downloads       INTEGER              ,
                          all_time_downloads        INTEGER              ,
                          github_star               INTEGER              );'''
  cursor.execute(create_table_query)

  # 每年新增新的字段
  columns = cursor.execute('PRAGMA table_info(package)')
  print('PRAGMA table_info', columns)
  start_time = 2015
  end_time = datetime.datetime.now().year
  for year in range(start_time, end_time + 1):
    column_name = f'downloads_{year}'
    column_exist_flag = False
    for colunn in columns:
      if colunn[1] == column_name:
        column_exist_flag = True
        break

    if column_exist_flag == False:
      add_column_query = f'''ALTER TABLE package ADD COLUMN {column_name} INTEGER'''
      cursor.execute(add_column_query)

  cursor.close()
  db.close()
  print('数据库初始化成功')

def get_db():
  db = sqlite3.connect(DATABASE, check_same_thread=False)
  db.row_factory = dict_factory
  return db

def query_db(query, args=(), one=False):
  db = get_db()
  cur = db.cursor()
  cur.execute(query, args)
  rv = cur.fetchall()
  db.commit()
  cur.close()
  db.close()
  return (rv[0] if rv else None) if one else rv

# 复制表，sqlite不能直接修改列
# copy_table_query = 'create table temp as select id, name, href, download from package;'
# query_db(copy_table_query)

# 增加列
# alter_table_query = '''ALTER TABLE package ADD COLUMN last_publish TEXT'''
# query_db(alter_table_query)

# 修改数据
# all_data_query = 'SELECT * FROM package'
# records = query_db(all_data_query)
# for record in records:
#   downloads = json.loads(record['download'])
#   latest_download = downloads[len(downloads) - 1]['downloads']
#   update_data_query = ''' UPDATE package SET latest_download = ? WHERE id = ? '''
#   query_db(update_data_query, (latest_download, record['name']))

__all__ = [
  init_db,
  query_db
]
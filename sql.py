import sqlite3
import json

DATABASE = 'database.db'

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
                                id                 TEXT PRIMARY KEY     NOT NULL,
                                name               TEXT                 NOT NULL,
                                href               TEXT                 NOT NULL,
                                download           TEXT                 NOT NULL,
                                latest_download    TEXT                 NOT NULL);'''
  cursor.execute(create_table_query)
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
# alter_table_query = '''ALTER TABLE package ADD COLUMN "latest_download" INTEGER'''
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
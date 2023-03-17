import sqlite3

# 查询结果元组转字典
def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
  return d

DATABASE = 'database.db'

def init_db():
  db = sqlite3.connect(DATABASE, check_same_thread=False)
  cursor = db.cursor()
  create_table_pkgbase_query  = '''
                                  CREATE TABLE IF NOT EXISTS pkgbase(
                                  id                        TEXT PRIMARY KEY     NOT NULL,
                                  npm_url                   TEXT                 NOT NULL,
                                  github_url                TEXT                         ,
                                  homepage_url              TEXT                         ,
                                  version                   TEXT                         ,
                                  license                   TEXT                         ,
                                  github_star               TEXT                      ,
                                  size                      TEXT                         ,
                                  created                   TEXT                      ,
                                  updated                   TEXT                      );
                                '''
  create_table_pkgdownload_query  = '''
                                    CREATE TABLE IF NOT EXISTS pkgdownload(
                                    id                        TEXT                 NOT NULL,
                                    dltype                    TEXT                 NOT NULL,
                                    downloads                 INTEGER                      ,
                                    timepoint                 TEXT                         );
                                  '''                 
  cursor.execute(create_table_pkgbase_query)
  cursor.execute(create_table_pkgdownload_query)
  cursor.close()
  db.close()
  print('数据库初始化成功')

class SQLDB(object):
	def __init__(self):
		self.db = sqlite3.connect(DATABASE, isolation_level=None)
		self.db.row_factory = dict_factory

	def	get(self,query, args=(), one=False):
		cur = self.db.cursor()
		cur.execute(query, args)
		rv = cur.fetchall()
		cur.close()
		return (rv[0] if rv else None) if one else rv
	
	def	update(self,SQL, args):
		# 判断是否报错，报错回滚，否则提交
		cur = self.db.cursor()
		cur.execute(SQL, args)
		self.db.commit()
		cur.close()

	def __del__(self):
		self.db.commit()
		self.db.close()

__all__ = [
  init_db,
  SQLDB
]

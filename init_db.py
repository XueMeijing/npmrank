'''
从md中拿到库名并存到数据库
'''
import re

from sql import init_db, query_db

SOURCE_FILE = 'data/source.md'

init_db()

with open(SOURCE_FILE, 'r') as f:
  lines = f.readlines()
  for line in lines:
    name = re.findall(r'\[(.*?)\]', line)
    href = re.findall(r'\((.*?)\)', line)
    print('line\n', line)
    if name and href:
      get_data_query = '''SELECT * FROM package WHERE id = ?'''
      record = query_db(get_data_query, (name[0],), one=True)
      if record is None:
        insert_data_query = ''' INSERT INTO package
                                  ('id', 'name', 'href', 'download', 'latest_download')
                                  VALUES(?,?,?,?,?) '''
        query_db(insert_data_query, (name[0], name[0], href[0], 0, 0))
from quart import Quart, request
import re

from db import SQLDB

app = Quart(__name__)

sql_obj = SQLDB()

'''
获取包的数据
'''
@app.route('/api/ranking/packages/<path:rank_type>')
async def get_packages(rank_type):
  top = request.args.get('top')
  if top is None:
    top = 30
  if top > 200:
    top = 200
  rank_types = get_rank_types()
  rank_type =  next((c['value'] for c in rank_types if c['value'] == rank_type), None)

  if rank_type:
    rank_type = re.sub(r'\-', '_', rank_type)
    get_data_query =  '''
                      SELECT
                        a.id,
                        npm_url npmUrl,
                        github_url githubUrl,
                        homepage_url homepageUrl,
                        dltype dltype,
                        downloads downloads,
                        github_star githubStar,
                        version,
                        license,
                        updated,
                        created 
                      FROM
                        ( SELECT id, dltype, downloads FROM pkgdownload WHERE dltype = ? ORDER BY downloads DESC LIMIT 0, ? ) a,
                        pkgbase b
                      WHERE
                        a.id = b.id 
                      '''
    records = sql_obj.get(get_data_query, (rank_type, top))

    for index, record in enumerate(records):
      records[index]['rank'] = index + 1
    
    return {
      'code': 200,
      'data': records,
      'success': True
    }

'''
获取排名类型
'''
@app.route('/api/ranking/types')
async def get_types():
  return {
    'code': 200,
    'data': get_rank_types(),
    'success': True
  }

def get_rank_types():
  get_types_query = 'SELECT DISTINCT dltype FROM pkgdownload'
  records = list(map(convert_type, sql_obj.get(get_types_query)))
  
  return records

def convert_type(record):
    type = re.sub(r'\_', '-', record['dltype'])
    return {
      'label': type,
      'value': type
    }

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
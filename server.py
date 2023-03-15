from quart import Quart, request
from quart_cors import cors
import json
import datetime

from sql import query_db

app = Quart(__name__)
app = cors(app, allow_origin="*")

def get_json(record):
  del record['week_downloads']
  return record

@app.route('/api/rank/<path:rank_type>')
async def get_data(rank_type):
  top = request.args.get('top')
  if top is None:
    top = 20
  if top > 200:
    top = 200
  rank_types = get_rank_types()
  rank_item =  next((c for c in rank_types if c['label'] == rank_type), None)

  if rank_item:
    get_data_query = f'''SELECT * 
                      FROM package
                      ORDER BY {rank_item['value']} DESC
                      LIMIT ?
                      '''
    records = query_db(get_data_query, (top,))
    records = list(map(get_json, records))
    return {
      'code': 200,
      'data': records,
      'success': True
    }
  else:
    return {
      'code': 500,
      'data': [],
      'success': False
    }

def get_rank_types():
  base_rank_types = [
    {
      'label': 'last-day',
      'value': 'last_day_downloads',
    },
    {
      'label': 'last-week',
      'value': 'last_week_downloads',
    },
    {
      'label': 'last-month',
      'value': 'last_month_downloads',
    },
    {
      'label': 'last-year',
      'value': 'last_year_downloads',
    },
    {
      'label': 'all-time',
      'value': 'all_time_downloads',
    },
  ]
  start_time = 2015
  end_time = datetime.datetime.now().year

  for year in range(start_time, end_time + 1):
    rank_type = f'downloads_{year}'
    base_rank_types.append({
      'label': f'{year}',
      'value': rank_type 
    })
  return base_rank_types


@app.route('/api/rank-types')
async def get_types():
  data = {
    'code': 200,
    'data': get_rank_types(),
    'success': True
  }
  return data


if __name__ == '__main__':
    # 指定host和port，0.0.0.0可以运行在服务器上对外访问，记得开服务器的网络防火墙端口
    # GCP在VPC network -> firewalls -> 增加一条 VPC firewall rules 指定端口，target填 http-server或https-server
    app.run(host='127.0.0.1', port=8080)
    # app.run(host='0.0.0.0', port=8080)
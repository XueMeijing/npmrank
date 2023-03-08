from quart import Quart, request
from quart_cors import cors
import json

from sql import query_db

app = Quart(__name__)
app = cors(app, allow_origin="*")

def get_json(record):
  record['download'] = json.loads(record['download'])
  return record

@app.route('/')
async def get_data():
  print(request.args.get('top'))
  get_data_query = '''SELECT *
                      FROM package
                      ORDER BY latest_download DESC
                      LIMIT 10
                      '''
  records = query_db(get_data_query)
  records = list(map(get_json, records))

  return records

if __name__ == '__main__':
    # 指定host和port，0.0.0.0可以运行在服务器上对外访问，记得开服务器的网络防火墙端口
    # GCP在VPC network -> firewalls -> 增加一条 VPC firewall rules 指定端口，target填 http-server或https-server
    app.run(host='127.0.0.1', port=8080)
    # app.run(host='0.0.0.0', port=8080)
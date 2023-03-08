'''
根据库名获取npm下载数据
'''
import requests
import json
import asyncio

from sql import query_db

payload={}
# 控制台network复制npmjs接口，copy as fetch，然后粘贴到console，再复制参数到postman请求接口，在右边代码块找到python请求代码
headers = {
  'accept': '*/*',
  'accept-language': 'zh,en;q=0.9,zh-CN;q=0.8',
  'manifest-hash': '2c383d069ae9a4c734cc',
  'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'x-requested-with': 'XMLHttpRequest',
  'x-spiferack': '1',
  'referrer': 'https://www.npmjs.com/',
  'referrerPolicy': 'strict-origin-when-cross-origin',
  'body': '',
  'method': 'GET',
  'mode': 'cors',
  'credentials': 'include',
}

# PROXY_PATH = 'proxies.txt'
# proxies = []
# # 生成代理池
# with open(PROXY_PATH) as f:
#   lines = f.readlines()
#   for line in lines:
#     proxies.append(line)

# # 获取随机代理地址
# def get_proxy():
#   index = random.randint(0, len(proxies) - 1)
#   return {
#     "http": proxies[index],
#     "https": proxies[index]
#   }

async def main():
  all_data_query = '''SELECT * FROM package'''
  records = query_db(all_data_query)
  for index, record in enumerate(records):
    print('name', record['name'], index)
    try:
      '''
      下载限速后，从这里开始重新下载
      '''
      # fetch_start_index = 999
      # if record['download'] != '0':
      # if index < fetch_start_index:
      #   continue

      '''
      获取下载量并写入数据库
      '''
      # 数据来源的href是npmjs.org，现在是npmjs.com
      href = 'https://www.npmjs.com/package/' + record['name']
      # 用代理会报错
      # proxies = get_proxy()
      # print('proxies', proxies)
      # response = requests.request("GET", href, proxies=proxies, headers=headers, data=payload)
      response = requests.request("GET", href, headers=headers, data=payload)
      data = response.json()
      download = json.dumps(data['downloads'])
      latest_download = data['downloads'][len(data['downloads']) - 1].downloads
      update_data_query = ''' UPDATE package SET download = ?, latest_download = ?, WHERE id = ? '''
      query_db(update_data_query, (download, latest_download, record['name']))
      # 不加会报429，请求太频繁，2秒间隔大概每次请求100条会限速，修改fetch_start_index再重新请求
      await asyncio.sleep(2)
    except Exception as e:
      print('error\n', e)
    print('--------------')

asyncio.run(main())

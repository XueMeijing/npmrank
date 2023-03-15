'''
根据source.md中的库名获取npm下载数据
'''
import requests
import json
import asyncio
import re
import datetime

from sql import init_db, query_db
import config

SOURCE_FILE = 'source.md'

NPM_BASE_URL = 'https://www.npmjs.com/package/'
'''
total: https://api.npmjs.org/downloads/point/2015-02-01:2018-02-08/express
range: https://api.npmjs.org/downloads/range/2015-02-01:2018-02-08/express
More info at https://github.com/npm/registry/blob/master/docs/download-counts.md
'''
NPM_BASE_API_POINT_URL = 'https://api.npmjs.org/downloads/point/'

# npm页面控制台network复制npmjs接口，copy as fetch，然后粘贴到console，再复制参数到postman请求接口，在右边代码块找到python请求代码
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

init_db()

'''
从md中拿到库名并存到数据库
'''
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
                                ('id', 'name', 'npm_url', 'github_url', 'homepage_url', 'last_publish')
                                VALUES(?,?,?,?,?) '''
        query_db(insert_data_query, (name[0], name[0], NPM_BASE_URL + name[0], '', '', ''))


'''
获取某一时期的下载量
'''
def get_point_downloads(date_range, package_name):
  href = f'{NPM_BASE_API_POINT_URL}{date_range}/{package_name}'
  print('href', href)
  response = requests.request("GET", href)
  data = response.json()
  print('data', data)
  return data['downloads']


'''
获取全部下载量，npm每次最多返回18个月的数据，所以分段下载
'''
def get_point_all_downloads(package_name):
  start_time = 2015
  end_time = datetime.datetime.now().year
  all_downloads = 0

  for year in range(start_time, end_time + 1):
    column_name = f'downloads_{year}'
    date_range = f'{year}-01-01:{year + 1}-01-01'
    print('date_range', date_range)

    if config.ONLY_UPDATE_THIS_YEAR and year != end_time:
        get_data_query = f'''SELECT {column_name} FROM package
                            WHERE id = ?
                          '''
        data = query_db(get_data_query, (package_name,), one=True)
        all_downloads += data[f'{column_name}']
        print('old downloads', data[f'{column_name}'])
    else:
      downloads = get_point_downloads(date_range, record['name'])
      all_downloads += downloads
      print('new downloads',downloads)
      update_data_query = f'''UPDATE package
                              SET {column_name} = ?
                              WHERE id = ?;
                          '''
      query_db(update_data_query, (downloads, package_name))
  return all_downloads

'''
获取github数据
'''
def get_github_info(github_url):
  response = requests.request("GET", github_url)
  data = response.json()
  return data

'''
更新下载量
'''
async def main():
  all_data_query = '''SELECT * FROM package'''
  records = query_db(all_data_query)
  for index, record in enumerate(records):
    while True:
      print('name', record['name'], index)
      # 下载中断后，重新下载跳过已下载数据
      start_index = 225
      if index < start_index:
        break
      try:
        '''
        获取下载量并写入数据库
        '''
        href = NPM_BASE_URL + record['name']
        npm_response = requests.request("GET", href, headers=headers)
        npm_data = npm_response.json()
        downloads = npm_data['downloads']

        github_url = npm_data['packageVersion'].get('repository', '')
        homepage_url = npm_data['packageVersion'].get('homepage', '')
        last_publish = npm_data['capsule']['lastPublish'].get('time', '')
        week_downloads = json.dumps(downloads)
        last_day_downloads = get_point_downloads('last-day', record['name'])
        print('last_day_downloads', last_day_downloads)
        last_week_downloads = get_point_downloads('last-week', record['name'])
        print('last_week_downloads', last_week_downloads)
        last_month_downloads = get_point_downloads('last-month', record['name'])
        print('last_month_downloads', last_month_downloads)
        last_year_downloads = get_point_downloads('last-year', record['name'])
        print('last_year_downloads', last_year_downloads)

        all_time_downloads = get_point_all_downloads(record['name'])
        print('all_time_downloads', all_time_downloads)
        github_star = 0
        if npm_data.get('ghapi', None):
          github_data = get_github_info(npm_data['ghapi'])
          if github_data.get('stargazers_count', None):
            github_star = github_data['stargazers_count']

        update_data_query = ''' UPDATE package
                                SET github_url = ?, homepage_url = ?, last_publish = ?, week_downloads = ?, last_day_downloads = ?, last_week_downloads = ?, last_month_downloads = ?, last_year_downloads = ?, all_time_downloads = ?, github_star= ?
                                WHERE id = ? '''
        query_db(update_data_query, (github_url, homepage_url, last_publish, week_downloads, last_day_downloads, last_week_downloads, last_month_downloads, last_year_downloads, all_time_downloads, github_star, record['name']))
        # 暂停两秒，请求太频繁会报429，2秒间隔大概每次请求100条会限速
        await asyncio.sleep(2)
        break
      except Exception as e:
        # 请求报错过60秒重试
        print('error ------------------\n', e)
        await asyncio.sleep(60)
        continue
    print('--------------')

asyncio.run(main())

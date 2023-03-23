'''
根据source.md中的库名获取npm下载数据
'''
import requests
import asyncio
import re
import datetime
from bs4 import BeautifulSoup

from db import init_db, SQLDB

SOURCE_FILE = 'source.md'
NPM_BASE_URL = 'https://www.npmjs.com/package/'
NPM_BASE_API_POINT_URL = 'https://api.npmjs.org/downloads/point/'

# npm页面控制台network复制npmjs接口，copy as fetch，然后粘贴到console，再复制参数到postman请求接口，在右边代码块找到python请求代码
npm_headers = {
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

github_headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'zh,en;q=0.9,zh-CN;q=0.8',
  'cache-control': 'max-age=0',
  'if-none-match': 'W/"396aa0eef163ad59fc27f13d1f34d3d5"',
  'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'referrerPolicy': 'no-referrer-when-downgrade',
  'body': '',
  'method': 'GET',
  'mode': 'cors',
  'credentials': 'include',
}

init_db()

sql_obj = SQLDB()

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
      get_pkgbase_query = '''SELECT * FROM pkgbase WHERE id = ?'''
      record_base = sql_obj.get(get_pkgbase_query, (name[0],), one=True)
      if record_base is None:
        insert_data_query = '''
                            INSERT INTO pkgbase
                            ('id', 'npm_url', 'github_url', 'homepage_url', 'version', 'license', 'github_star', 'size', created, updated)
                            VALUES(?,?,?,?,?,?,?,?,?,?)
                            '''
        sql_obj.update(insert_data_query, (name[0], NPM_BASE_URL + name[0], '', '', '', '', 0, '', 0, 0))

'''
获取某一时期的下载量
'''
def get_point_downloads(date_range, package_name):
  href = f'{NPM_BASE_API_POINT_URL}{date_range}/{package_name}'
  response = requests.request("GET", href)
  data = response.json()
  return data['downloads']

'''
获取全部下载量，npm每次最多返回18个月的数据，所以分段下载后再累加
'''
def get_point_all_downloads(package_name):
  start_time = 2015
  end_time = datetime.datetime.now().year
  all_downloads = 0

  for year in range(start_time, end_time + 1):
    dltype = f'{year}'
    date_range = f'{year}-01-01:{year + 1}-01-01'
    print('date_range', date_range)

    get_data_query = '''
                        SELECT * FROM pkgdownload
                        WHERE id = ? AND dltype = ?
                        '''
    exist_record = sql_obj.get(get_data_query, (package_name, dltype), one=True)

    if exist_record is None:
      downloads = get_point_downloads(date_range, package_name)
      all_downloads += downloads
      print('new downloads',downloads)
      add_data_query = '''
                      INSERT INTO pkgdownload
                      ('id', 'dltype', 'downloads', 'timepoint')
                      VALUES(?,?,?,?)
                      '''
      sql_obj.update(add_data_query, (package_name, dltype, downloads, datetime.datetime.now()))
    else:
      if year == end_time:
        downloads = get_point_downloads(date_range, package_name)
        all_downloads += downloads
        print('new downloads',downloads)
        update_data_query = '''
                            UPDATE pkgdownload
                            SET downloads = ?, timepoint = ?
                            WHERE id = ? AND dltype = ?
                            '''
        sql_obj.update(update_data_query, (downloads, datetime.datetime.now(), package_name, dltype))
      else:
        get_downloads_query = '''
                              SELECT * FROM pkgdownload
                              WHERE id = ? AND dltype = ?
                              '''
        record = sql_obj.get(get_downloads_query, (package_name, dltype), one=True)
        all_downloads += record['downloads']
        print('old downloads', record['downloads'])
  return all_downloads

'''
获取github数据
使用npm返回的ghapi获取star每小时限速60,所以用爬虫
'''
def set_github_info(github_url, package_name):
  response = requests.get(github_url, headers=github_headers)
  soup = BeautifulSoup(response.content, "html.parser")
  star = soup.find("span", class_='text-bold').get_text() if soup.find("span", class_='text-bold') else 0
  update_pkgbase_query =  '''
                            UPDATE pkgbase
                            SET github_star = ?
                            WHERE id = ?
                            '''
  print('package_name star', package_name, star)
  sql_obj.update(update_pkgbase_query, (star, package_name))

'''
更新下载量
'''
async def main():
  all_data_query = '''SELECT * FROM pkgbase'''
  records = sql_obj.get(all_data_query)
  for index, record in enumerate(records):
    while True:
      print('id', record['id'], index)
      # 下载中断后，重新下载跳过已下载数据
      # start_index = 225
      # if index < start_index:
      #   break
      try:
        '''
        获取下载量并写入数据库
        '''
        href = NPM_BASE_URL + record['id']
        npm_response = requests.request("GET", href, headers=npm_headers)
        npm_data = npm_response.json()

        # pkgbase
        github_url = npm_data['packageVersion'].get('repository', '')
        homepage_url = npm_data['packageVersion'].get('homepage', '')
        version = npm_data['packument'].get('version', '')
        license = npm_data['packument'].get('license', '')
        # 有仓库两个license
        license = license if type(license) == str else '-'
        versions = npm_data['packument'].get('versions') if npm_data['packument'].get('versions') else []
        updated = datetime.datetime.fromtimestamp(versions[0]['date']['ts'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        created = datetime.datetime.fromtimestamp(versions[len(versions) - 1]['date']['ts'] / 1000).strftime("%Y-%m-%d %H:%M:%S")

        update_pkgbase_query =  '''
                                UPDATE pkgbase
                                SET github_url = ?, homepage_url = ?, version = ?, license = ?, updated = ?, created = ?
                                WHERE id = ?
                                '''
        sql_obj.update(update_pkgbase_query, (github_url, homepage_url, version, license, updated, created, record['id']))

        # pkgdownload
        base_dltype = ['last-day', 'last-week', 'last-month', 'last-year', 'all-time']
        for dltype in base_dltype:
          if dltype == 'all-time':
            downloads = get_point_all_downloads(record['id'])
          else:
            downloads = get_point_downloads(dltype, record['id'])
          print('dltype', dltype)
          print('downloads', downloads)
          replaced_dltype = re.sub(r'\-', '_', dltype)
          get_data_query =  '''
                            SELECT * FROM pkgdownload
                            WHERE id = ? AND dltype = ?
                            '''
          exist_record = sql_obj.get(get_data_query, (record['id'], replaced_dltype), one=True)

          if exist_record is None:
            add_pkgdownload_query =  '''
                                    INSERT INTO pkgdownload
                                    ('id', 'dltype', 'downloads', 'timepoint')
                                    VALUES(?,?,?,?)
                                    '''
            sql_obj.update(add_pkgdownload_query, (record['id'], replaced_dltype, downloads, datetime.datetime.now()))
          else:
            update_pkgdownload_query =  '''
                                      UPDATE pkgdownload
                                      SET downloads = ?, timepoint = ?
                                       WHERE id = ? AND dltype = ?
                                      '''
            sql_obj.update(update_pkgdownload_query, (downloads, datetime.datetime.now(), record['id'], replaced_dltype))
        
        # github数据 有仓库是git:协议，不支持
        if github_url and github_url.startswith('https://'):
          set_github_info(github_url, record['id'])

        # 暂停两秒，请求太频繁会报429，2秒间隔大概每次请求100条会限速
        await asyncio.sleep(2)
        break
      except Exception as e:
        # 请求报错过60秒重试
        print('error ------------------\n', e)
        await asyncio.sleep(60)
        continue
    print('--------------')
  print(f'{datetime.datetime.now()} 数据库更新成功')
asyncio.run(main())

# Npm Rank
根据2019年的npm下载量前1000的包名，获取npm最近的下载量排行
# 数据来源
数据使用的包名来自 [anvaka](https://gist.github.com/anvaka/8e8fa57c7ee1350e3491) 2019年爬取的top1000数据，距今三四年的时间，但是老的包一般被依赖的多下载量大，所以对前面的排名影响应该不是很大，如果有看到下载量比较多但是不在```source.md```的，欢迎提issue
# 目录
```
├── README.md
├── database.db
├── get_package_download.py    获取下载量
├── init_db.py                 初始化数据库
├── proxies.txt                请求代理地址，避免npm限速，但暂时无效
├── server.py                  返回下载量json数据
├── source.md                  2019的npm top 1000的包
└── sql.py
```
# 注意
 - 更新数据```get_package_download```时电脑不能开代理，否则请求报SSL443错误
 - 同一接口如 https://www.npmjs.com/package/glob 会根据不同的header来返回json或者html，但是暂未确认是哪个header
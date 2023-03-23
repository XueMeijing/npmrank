# Npm Rank

根据 2019 年 8 月 16 的 npm top1000 的包名，获取这些包现在的下载量排行，默认展示前30。地址 https://www.npmrank.net/
 ，前端仓库地址为 [npmrank-v](https://github.com/XueMeijing/npmrank-v) 
 
![image](https://user-images.githubusercontent.com/35559153/226794702-32a27544-1ed9-4155-9bcf-9b441f0c2d23.png)

# 数据来源

- 数据使用的包名来自 [anvaka](https://gist.github.com/anvaka/8e8fa57c7ee1350e3491) 2019 年爬取的 top1000 数据，距今三四年的时间，但是老的包一般被依赖的多下载量大，所以对前面的排名影响应该不是很大
- 获取数据使用的 api 来自 [npm](https://github.com/npm/registry/blob/master/docs/download-counts.md)
- npm 每天在 UTC 凌晨不久后更新数据，所以这里选择在 UTC 3 点 使用 crontab 定时任务更新新的数据，持续大约1～2小时，因为这是协调世界时，这会产生一些有点不直观的结果
- 总数据为 2015 年至今的数据
- github star 来自爬到的 github 页面数据

如果有看到下载量比较多但是不在`source.md`的包，欢迎提 issue

# 快速开始

1. 安装依赖
   ```
   pip3 install -r requirements.txt
   ```
2. 生成或更新下载数据, 网络正常的情况下持续大约1~2小时
   ```
   nohup python3 -u generate_download_data.py > nohup.out 2>&1 &
   ```
3. 查看日志
   ```
   tail -30f nohup.out
   ```

# 目录

```
.
├── LICENSE
├── README.md
├── database.db                   # sqlite3的包下载数据
├── db.py                         # 数据库方法
├── generate_download_data.py     # 生成、更新新数据
├── requirements.txt
├── server.py                     # 给前端展示提供数据
└── source.md                     # 2019年包排名
```

# 待办

- 使用代理，同时发出多个请求
- 目前是前 30 条，希望能展示更多的数据，但是图表不方便展示更多的数据

# 注意

- 更新数据 `generate_download_data` 时电脑不能开代理，否则请求报 SSL443 错误
- 同一接口如 https://www.npmjs.com/package/glob 会根据不同的 header 来返回 json 或者 html，但是暂未确认是哪个 header
- 单次查询最多限于 18 个月的数据，返回数据的最早日期是 2015 年 1 月 10 日
- 获取某个包某个区间的下载量，可能为 0，不确定是什么原因，例如
  ```
  https://api.npmjs.org/downloads/point/2020-01-01:2021-01-01/express
  ```
  返回
  ```
  {
      "downloads": 0,
      "start": "2020-01-01",
      "end": "2021-01-01",
      "package": "express"
  }
  ```

# 致谢

感谢大哥的数据库指导 [sunkxs](https://github.com/sunkxs) 
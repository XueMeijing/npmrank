# Npm Rank
根据2019年8月16的npm下载量前1000的包名，获取这些包现在的下载量排行
# 数据来源
- 数据使用的包名来自 [anvaka](https://gist.github.com/anvaka/8e8fa57c7ee1350e3491) 2019年爬取的top1000数据，距今三四年的时间，但是老的包一般被依赖的多下载量大，所以对前面的排名影响应该不是很大
- 获取数据使用的api来自 [npm](https://github.com/npm/registry/blob/master/docs/download-counts.md)
- npm每天在UTC凌晨不久后更新数据，所以这里选择在UTC3点更新新的数据，因为这是协调世界时，这会产生一些有点不直观的结果
- 总数据为2015年至今的数据


如果有看到下载量比较多但是不在```source.md```的，欢迎提issue
# 快速开始
1. 安装依赖
    ```
    pip3 install -r requirements.txt
    ```
2. 生成或更新下载数据, 网络正常的情况下持续大约四五十分钟（两秒请求一条数据，报错暂停一分钟）
    ```
    python3 generate_download_data.py
    ```

# 目录
# 待办
- 使用代理，同时发出多个请求
# 注意
- 更新数据 ```generate_download_data``` 时电脑不能开代理，否则请求报SSL443错误
- 同一接口如 https://www.npmjs.com/package/glob 会根据不同的header来返回json或者html，但是暂未确认是哪个header
- 查询最多限于18个月的数据，返回数据的最早日期是2015年1月10日
- 获取某个包某个区间的下载量，可能为0，不确定是什么原因，例如
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
- github api每小时每个ip限速60次请求，[详见文档](https://docs.github.com/en/rest/overview/resources-in-the-rest-api?apiVersion=2022-11-28#rate-limiting)
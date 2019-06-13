# SOSearch

基于Django和Bootstrap3的StackOverflow内容搜索网站

## Run

在根目录/SOSearch/下运行
```
python mangage.py runserver
```
在浏览器中访问[localhost:8000](127.0.0.1:8000)

## Project Overview

* Project: SOSearch, 目录SOSearch/
* App: websearch, haystack, 目录websearch/
* manage.py 管理文件
* test.db 测试用sqlite3数据库(**当前使用**)
* db.sqlite3 项目生成sqlite3数据库(当前未利用)

### Project - SOSearch

* 项目根目录SOSearch/
* 目录whoosh_index/存放search engine索引
* settings.py 定义参数
* urls.py 定义(项目层级)url路径与视图匹配规则

### App - websearch

* 应用根目录websearch/
* 目录migrations/存放(数据库)(待)迁移命令
* 目录static/存放静态文件(css,js,img...)
* 目录templates/存放前端模板(html)
* 目录templatetags/存放自定义前端模板(标签)样式
* admin.py admin页面管理内容(模型)
* apps.py 应用名
* models.py 定义模型
* search_indexes.py 定义索引域
* urls.py 定义(应用层级)url路径与视图匹配规则
* views.py 定义三类页面(all questions, question detail, search result)控制
* test.py 定义测试(未利用)

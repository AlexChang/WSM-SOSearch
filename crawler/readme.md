# Crawler

## question_list_spider.py

```
python question_list_spider.py --l 100500
```

将网站所有问题按时间排序，从第start_page_number(--s)页起(1 base)，爬取到第page_limit(--l)页的问题链接和创建时间，存储为json格式，
输出文件名为output_file_name(--o)加上时间戳后缀("%y%m%d_%H%M%S")，输出路径为data_path(--p)

## question_answer_spider.py

```
python question_answer_spider.py --l 5000797
```

根据question_list.json文件中的问题链接，爬取第start_item_number(--s)项起(0 base)至第item_limit(--l)项的问题页面，解析问题、回答、评论等内容，存储为json格式，
输出文件名为output_file_name(--o)加上时间戳后缀("%y%m%d_%H%M%S")，数据/输出路径为data_path(--p), 代理数量为proxy_number(--pn)

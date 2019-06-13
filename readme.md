# WSM-SOSearch

Web Search and Mining - StackOverflow Search

## Setup

1. Install the following dependency libraries with **Python 3(>= 3.5)**

    * For **Linux** (**python3-dev** is also needed)
    ```
    sudo apt install python3-dev
    pip install -r requirements.txt
    ```
    
    * For **Windows**
    
    ```
    pip install -r requirements_win.txt
    ```

2. (Optional) Install NLTK data. If you don't want to build the index by yourself, you can skip this step.

    ```
    python -m nltk.downloader stopwords punkt
    ```

3. Download the database (and config file) from this [link](https://pan.baidu.com/s/1lCxzOB9GWIRqG1L4Zf8eYg) (extraction code: qgao) and place it under directory ```SOSearch/```. We provide two types of databases, one containing only raw data and the other containing both data and indexes (and also Django fields). Each type of the database has three specifications, which are small (5k), medium (100k) and large (300k).

4. Change the settings in the following files according to the database you choose.

    * ```SOSearch/SOSearch/settings.py```
    * ```SOSearch/test_backend.py```
    * ```SOSearch/test_indexer.py```

5. (Optional) Add additional fields to the database and build index by running the following commands (at ```SOSearch/```). If you chose to use the database with index (and also Django fields), you can skip this step.
    
    ```
    python manage.py makemigrations
    python manage.py migrate
    python manage.py rebuild_index
    ```
    
6. (Optional) Modify file ```SOSearch/config.txt``` according to the data in ```SOSearch/question_index```  and ```SOSearch/answer_index```. If you chose to use the database with index (and also Django fields), you can skip this step.
 
7. (Optional) Add static file service by running the following command (at ```SOSearch/```). If you are in debug mode(set ```DEBUG = True``` in ```SOSearch/SOSearch/settings.py```), you can skip this step.

    ```
    python manage.py collectstatic
    ```
8. Finally, run the following command to start server locally.
 
    ```
    python manage.py runserver
    ```
    
    Or make it public by 
    
    ```
    python manage.py runserver 0.0.0.0:8000
    ```

## Crawler

* question_list_spider.py

    ```
    python question_list_spider.py --l 100500
    ```

* question_answer_spider.py

    ```
    python question_answer_spider.py --l 5000797
    ```

## Database

create sqlite3 database

## Web

See ```SOSearch/readme.md``` for more details.
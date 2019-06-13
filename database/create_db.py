import sqlite3
import json
import time


def main():

    # sample_file_path = './data/sample_question_answer.json'
    sample_file_path = './data/question_answer_part1.json'
    json_file = json.load(open(sample_file_path, 'r'))
    sample_record = json_file[0]

    print('sample record: {}'.format(sample_record))
    for k, v in sample_record.items():
        print(k)
        if isinstance(v, list) and len(v):
            vi = v[0]
            for vii in vi:
                print('\t' + vii)
        if isinstance(v, dict):
            for kk, _ in v.items():
                print('\t' + kk)

    # db_name = './test.db'
    db_name = './db.sqlite3'
    table_name_list = ['question', 'answer', 'user', 'comment', 'linked_question', 'related_question']

    # open connection with db
    conn = sqlite3.connect(db_name)
    print('Open database "{}" successfully!"'.format(db_name))
    c = conn.cursor()

    for table_name in table_name_list:
        if table_name == 'question':
            print('Creating table "{}"'.format(table_name))
            c.execute("""create table if not exists question(
                    id          INT         NOT NULL,
                    title       TEXT        NOT NULL,
                    link        TEXT        NOT NULL,
                    asked       TEXT        NOT NULL,
                    viewed      INT         NOT NULL,
                    active      TEXT,
                    vote        INT         NOT NULL        DEFAULT 0,
                    star        INT         DEFAULT 0,
                    content     TEXT        NOT NULL,
                    status      TEXT,
                    tags        TEXT,
            --      users       TEXT
            --      comments    TEXT
                    primary key(id)
                    );""")
            print("Table created successfully\n")
        elif table_name == 'answer':
            print('Creating table "{}"'.format(table_name))
            c.execute("""create table if not exists answer(
                    id          INT         NOT NULL,
                    rid         INT         NOT NULL,
                    vote        INT         NOT NULL,
                    accepted    INT         NOT NULL,
                    content     TEXT        NOT NULL,
            --      users       TEXT
            --      comments    TEXT
                    primary key(id),
                    foreign key(rid) references question(id)
                    );""")
            print("Table created successfully\n")
        elif table_name == 'user':
            print('Creating table "{}"'.format(table_name))
            c.execute("""create table if not exists user(
                    id          INT         NOT NULL,
                    rid         INT         NOT NULL,
                    name        TEXT,
                    action      TEXT,
                    time        TEXT,
                    link        TEXT,
                    is_owner    INT         NOT NULL,
                    revision    TEXT,
                    reputation  INT,
                    gold        INT,
                    silver      INT,
                    bronze      INT,
                    --primary key(rid, name, time)
                    primary key(id)
                    );""")
            print("Table created successfully\n")
        elif table_name == 'comment':
            print('Creating table "{}"'.format(table_name))
            c.execute("""create table if not exists comment(
                    id          INT         NOT NULL,
                    rid         INT         NOT NULL,
                    score       INT         NOT NULL,
                    content     TEXT        NOT NULL,
                    user        TEXT        NOT NULL,
                    user_href   TEXT        NOT NULL,
                    time        TEXT        NOT NULL,
                    --primary key(rid, user, time)
                    primary key(id)
                    );""")
            print("Table created successfully\n")
        elif table_name == 'linked_question':
            print('Creating table "{}"'.format(table_name))
            c.execute("""create table if not exists linked_question(
                    id          INT         NOT NULL,
                    rid         INT         NOT NULL,
                    qid         INT         NOT NULL,
                    title       TEXT        NOT NULL,
                    link        TEXT        NOT NULL,
                    vote        INT         NOT NULL,
                    accepted    INT         NOT NULL,
                    --primary key(rid, qid)
                    primary key(id)
                    );""")
            print("Table created successfully\n")
        elif table_name == 'related_question':
            print('Creating table "{}"'.format(table_name))
            c.execute("""create table if not exists related_question(
                    id          INT         NOT NULL,
                    rid         INT         NOT NULL,
                    qid         INT         NOT NULL,
                    title       TEXT        NOT NULL,
                    link        TEXT        NOT NULL,
                    vote        INT         NOT NULL,
                    accepted    INT         NOT NULL,
                    --primary key(rid, qid)
                    primary key(id)
                    );""")
            print("Table created successfully\n")
        else:
            print('Unrecognized table name {}! Ignore and continue...'.format(table_name))

    # commit create tables
    conn.commit()

    for table_name in table_name_list:
        c.execute("""PRAGMA table_info({})""".format(table_name))
        table_schema = c.fetchall()
        print('\nSchema of table {} '.format(table_name))
        for line in table_schema:
            print(line)

    # close connection with db
    conn.close()

    conn = sqlite3.connect(db_name)
    print('Open database "{}" successfully!"'.format(db_name))
    c = conn.cursor()
    for table_name in table_name_list:
        c.execute("""PRAGMA table_info({})""".format(table_name))
        table_schema = c.fetchall()
        print('\nSchema of table {} '.format(table_name))
        for line in table_schema:
            print(line)
    conn.close()


if __name__ == '__main__':
    main()
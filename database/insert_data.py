import sqlite3
import json
import time
from bs4 import BeautifulSoup
import os

user_detail = False
bs_parser = 'lxml'

user_id = 0
comment_id = 0
linked_question_id = 0
related_question_id = 0


def change_to_int_or_default_zero(target, default_value=0):
    if not target:
        target = default_value
    else:
        target = target.replace(',', '')
        target = int(target)
    return target


def change_to_str_or_default_empty(target, default_value=''):
    if not target:
        target = default_value
    else:
        target = str(target)
    return target


def unify_time_format(time_string, convert_format="%b %d '%y at %H:%M", standard_format="%Y-%m-%d %H:%M:%Sz"):
    converted_time = time_string
    try:
        parsed_time = time.strptime(time_string, standard_format)
    except ValueError as ve:
        try:
            parsed_time = time.strptime(time_string, convert_format)
            converted_time = time.strftime(standard_format, parsed_time)
        except ValueError as ve:
            try:
                parsed_time = time.strptime(time_string, "%b %d at %H:%M")
                this_year = time.strptime('2019', '%Y')
                new_parsed_time = time.struct_time(this_year[:1] + parsed_time[1:])
                converted_time = time.strftime(standard_format, new_parsed_time)
            except ValueError as ve:
                raise ve
    finally:
        return converted_time


def insert_users(cursor, users_data, reference_id, show_data=False):
    for user in users_data:
        if show_data:
            print('user: {}'.format(user))
        global user_id
        user_id += 1
        u_id = user_id
        u_rid = reference_id
        u_name = user['name']
        u_action = user['action']
        u_time = user['time']
        if u_time and (u_time.endswith('z') or u_time.endswith('Z')):
            u_time = u_time[:-1]
        u_link = user['link']
        u_is_owner = user['is_owner']
        u_revision = change_to_str_or_default_empty(user['revision'])
        if user_detail:
            u_reputation = change_to_int_or_default_zero(user['reputation'])
            u_gold = change_to_int_or_default_zero(user['gold'])
            u_silver = change_to_int_or_default_zero(user['silver'])
            u_bronze = change_to_int_or_default_zero(user['bronze'])
            u_insertion = """insert or ignore into user (id, rid, name, action, time, link, is_owner, revision, 
            reputation, gold, silver, bronze) values (?,?,?,?,?,?,?,?,?,?,?,?)"""
            cursor.execute(u_insertion, (u_id, u_rid, u_name, u_action, u_time, u_link, u_is_owner, u_revision,
                                         u_reputation, u_gold, u_silver, u_bronze))
        else:
            u_insertion = """insert or ignore into user (id, rid, name, action, time, link, is_owner, revision) 
            values (?,?,?,?,?,?,?,?)"""
            cursor.execute(u_insertion, (u_id, u_rid, u_name, u_action, u_time, u_link, u_is_owner, u_revision))


def insert_comments(cursor, comments_data, reference_id, show_data=False):
    for comment in comments_data:
        if show_data:
            print('comment: {}'.format(comment))
        global comment_id
        comment_id += 1
        c_id = comment_id
        c_rid = reference_id
        c_score = change_to_int_or_default_zero(comment['score'])
        c_content = BeautifulSoup(comment['content'], bs_parser).text
        c_user = comment['user']
        c_user_href = comment['user_href']
        c_time = unify_time_format(comment['date'])
        if c_time and (c_time.endswith('z') or c_time.endswith('Z')):
            c_time = c_time[:-1]
        c_insertion = """insert or ignore into comment (id, rid, score, content, user, user_href, time) 
                        values (?,?,?,?,?,?,?)"""
        cursor.execute(c_insertion, (c_id, c_rid, c_score, c_content, c_user, c_user_href, c_time))


def insert_linked_or_related_questions(table_name, cursor, questions_data, reference_id, show_data=False):
    for question in questions_data:
        if show_data:
            print('{}: {}'.format(table_name, question))
        if table_name == 'linked_question':
            global linked_question_id
            linked_question_id += 1
            q_id = linked_question_id
        elif table_name == 'related_question':
            global related_question_id
            related_question_id += 1
            q_id = related_question_id
        q_rid = reference_id
        q_qid = change_to_int_or_default_zero(question['id'])
        q_title = question['title']
        q_link = question['link']
        q_vote = change_to_int_or_default_zero(question['vote'])
        q_accepted = question['accepted']
        q_insertion = """insert or ignore into {table_name} (id, rid, qid, title, link, vote, accepted) 
                                values (?,?,?,?,?,?,?)""".format(table_name=table_name)
        cursor.execute(q_insertion, (q_id, q_rid, q_title, q_title, q_link, q_vote, q_accepted))


def main():

    # sample_file_path = './data/sample_question_answer.json'
    # sample_file_path = './data/sample_mid_question_answer.json'
    # json_file = json.load(open(sample_file_path, 'r'))
    sample_file_dir = './data'

    # db_name = './test.db'
    db_name = './db.sqlite3'
    table_name_list = ['question', 'answer', 'user', 'comment', 'linked_question', 'related_question']

    # open connection with db
    conn = sqlite3.connect(db_name)
    print('Open database "{}" successfully!"'.format(db_name))
    c = conn.cursor()

    for filename in os.listdir(sample_file_dir):
        if filename == '.gitkeep':
            continue
        json_file = json.load(open(os.path.join(sample_file_dir, filename), 'r'))
        for idx, line in enumerate(json_file):
            # question
            question = line['question']
            # print('question: {}'.format(question))
            if idx % 100 == 99:
                print('Processing item: {}'.format(idx + 1))
            if question['id'] == None:
                continue
            q_id = change_to_int_or_default_zero(question['id'])
            q_title = question['title']
            q_link = question['link']
            q_asked = question['asked']
            q_viewed = change_to_int_or_default_zero(question['viewed'])
            try:
                q_active = question['active']
            except KeyError as ke:
                q_active = ''
                # print('KeyError: {} in question: {}'.format(ke, q_id))
            q_vote = change_to_int_or_default_zero(question['vote'])
            q_star = change_to_int_or_default_zero(question['star'])
            q_content = BeautifulSoup(question['content'], bs_parser).text
            q_status = BeautifulSoup(change_to_str_or_default_empty(question['status']), bs_parser).text
            q_tags = ','.join(question['tags'])

            q_insertion = """insert or ignore into question (id, title, link, asked, viewed, active, vote, star, content, 
            status, tags) values (?,?,?,?,?,?,?,?,?,?,?)"""
            c.execute(q_insertion, (q_id, q_title, q_link, q_asked, q_viewed, q_active, q_vote, q_star, q_content,
                                  q_status, q_tags))
            # question users
            insert_users(c, question['users'], q_id, False)
            # question comments
            insert_comments(c, question['comments'], q_id, False)
            # linked question
            insert_linked_or_related_questions('linked_question', c, line['linked_questions'], q_id, False)
            # related question
            insert_linked_or_related_questions('related_question', c, line['related_questions'], q_id, False)

            # answers
            for answer in line['answers']:
                # print('answer: {}'.format(answer))
                a_id = change_to_int_or_default_zero(answer['id'])
                a_rid = q_id
                a_vote = change_to_int_or_default_zero(answer['vote'])
                a_accepted = answer['accepted']
                a_content = BeautifulSoup(answer['content'], bs_parser).text
                a_insertion = """insert or ignore into answer (id, rid, vote, accepted, content) values (?,?,?,?,?)"""
                c.execute(a_insertion, (a_id, a_rid, a_vote, a_accepted, a_content))
                # answer users
                insert_users(c, answer['users'], a_id, False)
                # answer comments
                insert_comments(c, answer['comments'], a_id, False)

    # commit insert data
    conn.commit()

    for table_name in table_name_list:
        c.execute("""select * from {}""".format(table_name))
        table_record = c.fetchall()
        print('\nRecords of table {} '.format(table_name))
        print(len(table_record))
        # for line in table_record:
        #     print(line)

    # close connection with db
    conn.close()


if __name__ == '__main__':
    main()
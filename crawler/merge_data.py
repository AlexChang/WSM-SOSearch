import json
import os
import argparse

mode_to_filename = {
    'ql': 'question_list',
    'qa': 'question_answer'
}

def get_previous_filename_and_no(args):
    if args.m == 'qa':
        if os.path.exists(args.op):
            filenames = os.listdir(args.op)
            valid_filenames = []
            for filename in filenames:
                if filename.startswith('question_answer') and not filename.startswith('question_answer_spider'):
                    valid_filenames.append(filename)
            valid_filenames = sorted(valid_filenames)
            if valid_filenames:
                if len(valid_filenames) > 1:
                    max_no = -1
                    for filename in valid_filenames:
                        if 'part' in filename:
                            max_no = max(max_no, int(filename.split('part')[-1].split('.json')[0]))
                    return 'question_answer_part{}.json'.format(str(max_no)), max_no
                else:
                    return valid_filenames[0], 1
            else:
                return '', 1
        else:
            return '', 1
    elif args.m == 'ql':
        previous_filename = mode_to_filename[args.m] + '.json'
        if os.path.exists(os.path.join(args.op, previous_filename)):
            return previous_filename, 1
        else:
            return '', 1
    else:
        raise ValueError()

def merge_result(args, previous_result, file_no=1):
    result = previous_result.copy()
    for dirpath, dirnames, filenames in os.walk(args.p):
        for filename in filenames:
            if filename.startswith(mode_to_filename[args.m]) and filename.endswith('.json') and 'spider' in filename:
                file_full_name = os.path.join(dirpath, filename)
                print('File {} is going to be merged... Reading from file...'.format(file_full_name))
                json_data = json.load(open(file_full_name, 'r'))
                print('Current file contains {} items!'.format(len(json_data)))
                result.extend(json_data)
                if args.m == 'ql':
                    result = list({x['link']: x for x in result}.values())
                else:
                    result = list({x['question']['id']: x for x in result}.values())
                if args.s:
                    while len(result) > args.si:
                        save_result(args, result[:args.si], file_no)
                        file_no += 1
                        result = result[args.si:]
    if result:
        save_result(args, result, file_no)

def save_result(args, result_data, file_no=-1):
    if not os.path.exists(args.op):
        os.mkdir(args.op)
    if file_no != -1:
        filename = os.path.join(args.op, '{}_part{}.json'.format(mode_to_filename[args.m], file_no))
    else:
        filename = os.path.join(args.op, '{}.json'.format(mode_to_filename[args.m]))
    print('Saving result to "{}"...'.format(filename))
    json.dump(result_data, open(filename, 'w'))
    print('Save process done!')

def initArgParser():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--m', type=str, default='qa', help='mode')     # ql, qa
    parser.add_argument('--p', type=str, default='./data/backup/', help='input(backup) data path')
    parser.add_argument('--op', type=str, default='./data/merged/', help='output(merged) data path')
    parser.add_argument('--s', action='store_true', default=True, help='segmentation')
    parser.add_argument('--si', type=int, default=10000, help='segmentation interval')
    args = parser.parse_args()
    return args

def main():
    args = initArgParser()
    if args.m not in mode_to_filename.keys():
        raise ValueError('Unsupported mode {}! Please try {}.'.format(args.m, list(mode_to_filename.keys())))

    previous_filename, file_no = get_previous_filename_and_no(args)
    previous_result = []
    if previous_filename:
        print('Reading previous result from "{}"...'.format(previous_filename))
        previous_result = json.load(open(os.path.join(args.op, previous_filename), 'r'))
        print('Read process done!')

    if args.s:
        merge_result(args, previous_result, file_no)
    else:
        merge_result(args, previous_result, -1)
    print('All done!')
    return

if __name__ == '__main__':
    main()
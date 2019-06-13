import json


def main():
    input_data_path = './data/question_answer.json'
    # output_data_path = './data/sample_question_answer.json'
    output_data_path = './data/sample_mid_question_answer.json'

    print('Loading from "{}"'.format(input_data_path))
    json_data = json.load(open(input_data_path, 'r'))
    print('original len: {}'.format(len(json_data)))

    # chopped_json_data = json_data[:50]
    chopped_json_data = json_data[:5000]
    print('modified len: {}'.format(len(chopped_json_data)))
    print('Saving data to "{}"'.format(output_data_path))
    json.dump(chopped_json_data, open(output_data_path, 'w'))
    print('All done!')


if __name__ == '__main__':
    main()
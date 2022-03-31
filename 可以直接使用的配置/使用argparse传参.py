import argparse


def handler_args():
    # 创建一个解析器
    parser = argparse.ArgumentParser(description='Process some integers.')
    # 添加参数
    parser.add_argument(
        '-d',
        '--delat_day',
        dest='max_day',
        type=int,
        default=90,
        help='max delat day to update'
    )
    parser.add_argument(
        '-n',
        '--commit_num',
        dest='commit_num',
        type=int,
        default=1000,
        help='number of data for each sql commit'
    )

    # 解析参数
    args = parser.parse_args()
    print(args.max_day)
    print(args.commit_num)


def main():
    handler_args()


if __name__ == '__main__':
    main()

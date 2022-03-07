from datetime import date, timedelta


def get_data(year, weeks, weekday):
    """计算year年第weeks周的星期weekday是哪一天"""
    start = date(year, 1, 1)
    for i in range(7):
        if start.isoweekday() == weekday:
            break
        start += timedelta(days=1)

    return start + timedelta(weeks=weeks - 1)


# print(get_data(2022, 7, 2))  # 返回2022年第7周的星期二
print(get_data(2022, 9, 1))

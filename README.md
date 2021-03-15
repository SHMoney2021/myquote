行情数据 myquote 支持sina/tencent实时行情、Tushare历史行情

        
    Usage:
        from myquote import myquote

        # 实时行情 默认sina，返回dataframe
        print(myquote.stock_now('000958'))
        print(myquote.stock_now(['601012', '000958']))

        # 实时行情 tencent/qq, 返回dataframe
        print(myquote.stock_now('000958', 'qq'))
        print(myquote.stock_now(['601012', '000958'], 'qq'))

        # 历史行情 tushare, 返回dataframe
        print(myquote.stock_days('000958'))
        TODAY = datetime.now().strftime('%Y%mm%dd')
        print(myquote.stock_days('601012', start_date='20210101', end_date=TODAY))
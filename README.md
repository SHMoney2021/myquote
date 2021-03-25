# myquote

#### 介绍
股票实时行情（sina, tencent）、历史行情（tushare）、掘金Goldminer行情

#### 使用说明

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

        # Goldminer掘金量化行情
        #查询当前行情快照 返回tick dataframe数据
        print(myquote.stock_current('000958'))
        # 查询历史行情, 返回dataframe数据 默认前复权 默认日线数据
        print(myquote.stock_history('000958', start_date='20210101', end_date='20210324'))

        # 使用tushare行情需要在class TushareQuote()配置自己的token，参考tushare文档
        # TS_TOKEN = 'YOUR-TUSHARE-TOKEN'

        # 使用掘金量化行情需要在 class GmQuote()设置token set_token('YOUR-GM-TOKEN')
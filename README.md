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

        # 支持策略回测 将行情bar数据序列化输出给策略函数 策略函数执行策略
        quote = myquote.stock_history('000958', start_date='20210101', end_date=TODAY)
        backtest_account = myquote.backtest_account()
        # 执行回测
        myquote.stock_backtest_serial(quote, 11, strategy_demo, backtest_account)
        def strategy_demo(data, account):
            # 实现你的策略

        # 查询策略收益
        backtest_account.status()
        # 输出：
        --- backtest strategy: strategy_demo ---
        总买入额: 826.00
        总卖出额: 404.00
        持仓市值: 505.00
        买卖盈亏: 10.05%
        [['20210201', 'buy', 4.1, 100], ['20210202', 'sell', 4.04, 100], ['20210219', 'buy', 4.16, 100]]

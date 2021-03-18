# -*- coding: utf-8 -*-
"""
    myquote - 股票行情 实时行情(sina, tencent) 历史行情(tushare)
    2021/3/12
    usage:
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

        # 使用tushare行情需要在class TushareQuote()配置自己的token，参考tushare文档
        # TS_TOKEN = 'YOUR-TUSHARE-TOKEN'
"""
import re
import requests
import abc
import tushare as ts
import pandas as pd
from datetime import datetime


# 控制台全部打印
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)


# 实时行情抽象基类
class BaseQuote(metaclass=abc.ABCMeta):
    quote_session = requests.session()

    @abc.abstractmethod
    def stock_api(self, stock_list):
        # 子类实现
        pass

    @abc.abstractmethod
    def format_response_data(self, res_data):
        # 子类实现
        pass

    @staticmethod
    def quote_headers(referer=None, cookie=None):
        # a reasonable UA
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        headers = {'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.5', 'User-Agent': ua}
        if referer is not None:
            headers.update({'Referer': referer})
        if cookie is not None:
            headers.update({'Cookie': cookie})
        return headers

    @staticmethod
    def get_stock_type(stock_code):
        assert type(stock_code) is str, "stock code need str type"
        sh_head = ("50", "51", "60", "90", "110", "113",
                   "132", "204", "5", "6", "9", "7")
        if stock_code.startswith(("sh", "sz", "zz")):
            return stock_code[:2]
        else:
            return "sh" if stock_code.startswith(sh_head) else "sz"

    def gen_stock_list(self, stock_codes):
        stocks_with_type = [self.get_stock_type(code) + code[-6:] for code in stock_codes]
        stock_list = ','.join(stocks_with_type)
        return stock_list

    def get_stock_data(self, stock_list):
        stock_url = self.stock_api(stock_list)
        stock_data = self.quote_session.get(stock_url, headers=self.quote_headers())
        return self.format_response_data([stock_data.text])

    def stocks(self, stock_codes):
        if not isinstance(stock_codes, list):
            stock_codes = [stock_codes]

        stock_list = self.gen_stock_list(stock_codes)
        return self.get_stock_data(stock_list)


# 实时行情 sina API实现
class SinaQuote(BaseQuote):
    sina_data_format = ['code', 'name', 'open', 'pre_close', 'now', 'high', 'low', 'buy', 'sell', 'vol', 'amount',
                        'bid1_volume', 'bid1', 'bid2_volume', 'bid2', 'bid3_volume', 'bid3', 'bid4_volume', 'bid4',
                        'bid5_volume', 'bid5', 'ask1_volume', 'ask1', 'ask2_volume', 'ask2', 'ask3_volume', 'ask3',
                        'ask4_volume', 'ask4', 'ask5_volume', 'ask5', 'date', 'time']
    sina_data_select = ['code', 'name', 'now', 'pre_close', 'open', 'high', 'low', 'vol', 'amount', 'date', 'time']

    # 股票代码(\d)、股票名(\w)、数字、小数(\.)、日期(-)、时间(:)
    sina_data_patten = re.compile(r'(\d+)="(\w+),%s' % (r'([-:\.\d]+),' * (len(sina_data_format) - 2)))

    def stock_api(self, stock_list):
        return 'http://hq.sinajs.cn/list=%s' % stock_list

    def format_response_data(self, res_data):
        data = ''.join(res_data)
        data = self.sina_data_patten.finditer(data)

        result_list = []
        for item in data:
            assert len(self.sina_data_format) == len(item.groups())
            result_list.append(dict(zip(self.sina_data_format, item.groups())))

        # to dataframe
        df = pd.DataFrame(columns=self.sina_data_select)
        for d in result_list:
            _data = dict(zip(self.sina_data_select, [d.get(x) for x in self.sina_data_select]))
            df = df.append(_data, ignore_index=True)

        df.index = df.code
        df.drop("code", inplace=True, axis=1)
        for i in range(1, 8):
            df.iloc[:, i] = df.iloc[:, i].astype(float)
            
        return df


# 实时行情 tencent API实现
class TencentQuote(BaseQuote):
    tencent_data_format = ['name', 'code', 'now', 'pre_close', 'open', 'volume', 'bid_volume', 'ask_volume', 'bid1',
                           'bid1_volume', 'bid2', 'bid2_volume', 'bid3', 'bid3_volume', 'bid4', 'bid4_volume', 'bid5',
                           'bid5_volume', 'ask1', 'ask1_volume', 'ask2', 'ask2_volume', 'ask3', 'ask3_volume', 'ask4',
                           'ask4_volume', 'ask5', 'ask5_volume', 'unknown1', 'datetime', '涨跌', '涨跌(%)', 'high', 'low',
                           '价格/成交量(手)/成交额', 'vol', 'amount', 'turnover', 'PE', 'unknown2', 'high_2', 'low_2', '振幅',
                           '流通市值', '总市值', 'PB', '涨停价', '跌停价', '量比', '委差', '均价', '市盈(动)', '市盈(静)']
    tencent_data_select = ['code', 'name', 'now', 'pre_close', 'open', 'high', 'low', 'vol', 'amount', 'datetime']

    # ~开头的股票名(\w)、数字(\w)、小数(\.)、负数(-)、日期时间(/)、及两个unknown空位('')
    tencent_data_patten = re.compile(r'~([-/\.\w]*)' * len(tencent_data_format))

    def stock_api(self, stock_list):
        return 'http://qt.gtimg.cn/q=%s' % stock_list

    def format_response_data(self, res_data):
        data = ''.join(res_data)
        data = self.tencent_data_patten.finditer(data)

        result_list = []
        for item in data:
            assert len(self.tencent_data_format) == len(item.groups())
            result_list.append(dict(zip(self.tencent_data_format, item.groups())))

        # to dataframe
        df = pd.DataFrame(columns=self.tencent_data_select)
        for d in result_list:
            _data = dict(zip(self.tencent_data_select, [d.get(x) for x in self.tencent_data_select]))
            df = df.append(_data, ignore_index=True)

        df.index = df.code
        df.drop("code", inplace=True, axis=1)
        for i in range(1, 8):
            df.iloc[:, i] = df.iloc[:, i].astype(float)
            
        return df


# 历史行情 tushare API实现
class TushareQuote():
    # 第一次使用需要配置token
    # TS_TOKEN = 'YOUR-TUSHARE-TOKEN'
    # pro = ts.pro_api(TS_TOKEN)

    pro = ts.pro_api()

    # return tushare dataframe data
    # trade_date ts_code trade_date    open  ...  pct_chg         vol        amount
    def stock(self, stock_code, start_date, end_date) -> pd.DataFrame:
        stock_code = self.check_stock_code(stock_code)
        df = self.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        df.index = df.trade_date
        df.drop("trade_date", inplace=True, axis=1)
        return df

    @staticmethod
    def check_stock_code(stock_code):
        assert type(stock_code) is str, "stock code need str type"
        sh_head = ("50", "51", "60", "90", "110", "113",
                   "132", "204", "5", "6", "9", "7")
        ends = '.SH' if stock_code[-6:].startswith(sh_head) else '.SZ'
        return stock_code[-6:] + ends


# fake quote for test
class FakerQuote():
    def stock_now(self, stock_codes):
        pass

    def stock_days(self, stock_code):
        pass


# 行情查询API
# stock_now(股票代码， 行情源默认sina): 单只或多只股票实时行情
# stock_days(股票代码， 开始日期， 结束日期): 单只股票历史行情
class myQuote():
    sina_quote = SinaQuote()
    tencent_quote = TencentQuote()
    tushare_quote = TushareQuote()

    # 单只或多只股票实时行情
    def stock_now(self, stock_codes, source='sina'):
        if source in ['tencent', 'qq']:
            data = self.tencent_quote.stocks(stock_codes)
        else:
            data = self.sina_quote.stocks(stock_codes)

        return data

    # 单只股票历史行情
    def stock_days(self, stock_code, start_date='20210101',
                   end_date=datetime.now().strftime('%Y%mm%dd')):
        data = self.tushare_quote.stock(stock_code, start_date, end_date)

        return data


# 行情查询API
# from myquote import myquote
myquote = myQuote()

# test usage
if __name__ == '__main__':
    print(myquote.stock_now('000958'))
    print(myquote.stock_now(['601012', '000958']))

    print(myquote.stock_now('000958', 'qq'))
    print(myquote.stock_now(['601012', '000958'], 'qq'))

    print(myquote.stock_days('000958'))
    TODAY = datetime.now().strftime('%Y%mm%dd')
    print(myquote.stock_days('601012', start_date='20210101', end_date=TODAY))



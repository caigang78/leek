#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/01/20 11:21
# @Author  : shenglin.li
# @File    : runner.py
# @Software: PyCharm
import decimal
import inspect
import signal
from importlib import import_module

from leek.common import EventBus, logger
from leek.common.utils import get_all_base_classes, get_constructor_args
from leek.data.data import DataSource, WSDataSource
from leek.strategy import BaseStrategy
from leek.strategy.strategy_common import PRE_STRATEGY_LIST, RISK_STRATEGY_LIST
from leek.trade.trade import Trader


def _invoke_init(instance, cls, cfg):
    args = get_constructor_args(cls)
    parameter_map = {k: v for k, v in cfg.items() if k in args}
    init_method = getattr(cls, "__init__")
    init_method(instance, **parameter_map)


def _init_model(ins_cfg, excludes=[]):
    module = import_module(ins_cfg["package"])
    cls = getattr(module, ins_cfg["class"])
    sig = inspect.signature(cls)
    params = sig.parameters
    parameter_map = {k: v for k, v in ins_cfg["config"].items() if k in list(params.keys())}
    instance = cls(**parameter_map)
    classes = get_all_base_classes(cls)
    for c in classes:
        ignore = [c == exclude for exclude in excludes]
        if ignore.count(True):
            continue
        _invoke_init(instance, c, ins_cfg["config"])
    return instance


def _has_override(subclass, baseclass, method_name):
    # 获取父类的方法
    base_method = getattr(baseclass, method_name, None)

    # 获取子类的方法
    sub_method = getattr(subclass, method_name, None)

    # 如果子类有该方法且源代码不同于父类的源代码，则认为覆写了
    return sub_method is not None and inspect.getsource(sub_method) != inspect.getsource(base_method)


class BaseWorkflow(object):
    """
    流定义基类
    """

    def __init__(self, job_id):
        self.data_source: DataSource = None
        self.trader: Trader = None
        self.strategy: BaseStrategy = None

        self.job_id = job_id
        self.bus: EventBus = EventBus()
        self.run_state = True

    def start(self):
        try:
            signal.signal(signal.SIGTERM, lambda signal, frame: self.shutdown())
        except Exception:
            pass
        self.data_source.start()

    def _clean_config(self, cls, cfg):
        arr = cls.split("|")
        pkg = arr[0].strip(" ")
        cls = arr[1].strip(" ")
        pre = cls.lower() + "_"
        rd = {
            "package": pkg,
            "class": cls
        }
        rcfg = {}
        for k, v in cfg.items():
            if pre in k:
                rcfg[k.replace(pre, "")] = v
            else:
                rcfg[k] = v
        rd["config"] = rcfg
        return rd

    def _init_trader(self, cfg_trader):
        instance = _init_model(cfg_trader, excludes=[Trader])
        if isinstance(instance, Trader):
            Trader.__init__(instance, self.bus)
        self.trader = instance

    def _init_strategy(self, cfg_strategy):
        instance = _init_model(cfg_strategy, excludes=[BaseStrategy])
        if isinstance(instance, BaseStrategy):
            BaseStrategy.__init__(instance, self.job_id, self.bus,
                                  decimal.Decimal(cfg_strategy["config"]["total_amount"]))
        self.strategy = instance

    def _init_data_source(self, cfg_data_source):
        instance = _init_model(cfg_data_source, excludes=[DataSource])
        if isinstance(instance, DataSource):
            DataSource.__init__(instance, self.bus)
        # if isinstance(instance, WSDataSource):
        #     if "url" not in cfg_data_source["config"]:
        #         raise RuntimeError("WSDataSource 需配置「url」属性")
        #     WSDataSource.__init__(instance, cfg_data_source["config"]["url"])
        self.data_source = instance

    def strategy_to_trader(self, data):
        if data:
            order = self.trader.order(data)
            self.trader_to_strategy(order)

    def data_source_to_strategy(self, data):
        order = self._strategy_run(data)
        self.strategy_to_trader(order)

    def _strategy_run(self, data):
        for fil in PRE_STRATEGY_LIST:
            if isinstance(self.strategy, fil) and not fil.pre(self.strategy, data):
                return

        for risk_manager in RISK_STRATEGY_LIST:
            if not isinstance(self.strategy, risk_manager):
                continue
            if order := risk_manager.handle(self.strategy, data):
                return order
        BaseStrategy.handle(self.strategy, data)
        return self.strategy.handle(data)

    def trader_to_strategy(self, data):
        if data:
            self.strategy.handle_position(data)

    def shutdown(self):
        logger.info(f"{self.strategy.job_id} 收到停止信号！")
        self.run_state = False
        self.data_source.shutdown()
        self.strategy.shutdown()
        self.trader.shutdown()
        logger.info(f"{self.strategy.job_id} 停止成功！")


if __name__ == '__main__':
    pass
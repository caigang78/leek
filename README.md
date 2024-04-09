量韭
===============
韭菜量化平台, 基于Python的事件驱动quant平台, 提供从数据获取到交易的整套流程, 以及交易的回测, 策略评估

策略
--------------------

| 名称       | 是否支持     | 支持版本   |
|:---------|:---------|:-------|
| 单标的单向网格  | &#10004; | v0.0.1 |
| 均值回归     | &#10004; | v0.0.2 |
| 布林带策略    | &#10004; | v0.0.2 |
| ATR+HA策略 | &#10004; | v0.0.3 |
| 双均线      | &#10004; | v0.0.4 |
| MACD均线   | &#10004; | v0.0.4 |
| 双均线      | &#10008; | v0.0.5 |
| ...      | &#10008; | ...    |




升级日志
----------------------

| 日期     | 版本         | 更新内容                                                                                                                                                        |
|:-------|:-----------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|
| v0.0.1 | 2024-01-21 | 1.打通数据源 -> 策略 -> 交易 -> 策略 事件流<br/>2.单标的单向网格策略<br/>3.基础django构建web配置页面                                                                                       |
| v0.0.2 | 2024-02-04 | 1.回测使用sqlite3替换H5数据源<br/>2.支持布林带交易策略<br/> 3.下沉部分风控/过滤策略<br/>4.修复部分BUG和体验问题<br/>                                                                             |
| v0.0.3 | 2024-02-29 | 1.升级策略架构，指令改为事件<br/> 2.独立仓位管理，简化策略职责, 优化开空仓位计算<br/> 3.ATR+Heikin-Ashi+stochastics混合策略<br/> 4. 回测交易执行器收集更多策略评估信息<br/> 5. 策略可视化调试<br/> 6. 修复部分BUG<br/>... ... |
| v0.0.4 | 2024-04-13 | 1.增加快捷升级脚本<br/> 2.优化币安行情下载脚本<br/> 3.单均线策略<br/> 4. MACD策略<br/> 5. update BUG修复<br/> 6. 增加仓位投入公共函数，优化多标的操作仓位控制<br/> 7. 修复部分BUG<br/>... ...                    |
| v0.0.5 | 2024-06-xx |                                                                                                                                                             |
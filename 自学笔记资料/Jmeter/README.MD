计算关系：

QPS = 并发量 / 平均响应时间

并发量 = QPS * 平均响应时间

原理：每天80%的访问集中在20%的时间里，这20%时间叫做峰值时间。

公式：( 总PV数 * 80% ) / ( 每天秒数 * 20% ) = 峰值时间每秒请求数(QPS) 。

机器：峰值时间每秒QPS / 单台机器的QPS = 需要的机器 。

案例分析：

每天300w PV 的在单台机器上，这台机器需要多少QPS？

( 3000000 * 0.8 ) / (86400 * 0.2 ) = 139 (QPS)。

一般需要达到139QPS，因为是峰值。

如果一台机器的QPS是58，需要几台机器来支持？

139 / 58 = 3
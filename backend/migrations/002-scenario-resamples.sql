-- 输入不确定性分析：窗口方案增加整条重抽组数（0=关闭，2—100启用）。
-- 新部署由 SQLAlchemy 建表自带本列；既有部署执行本文件后再升级镜像。
ALTER TABLE capacity_scenarios ADD COLUMN resamples INT NOT NULL DEFAULT 0;

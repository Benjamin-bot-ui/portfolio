USE earthquake;
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/observatory-utf-8.csv'
INTO TABLE 觀測站
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' -- 依據檔案的分隔符號
LINES TERMINATED BY '\n' -- 依據檔案每列的分隔方式
IGNORE 1 ROWS; -- 略過第一行

USE earthquake;
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\data-utf-8.csv'
INTO TABLE 地震事件
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, @當年地震編號,地震類型,發生時間,震央經度,震央緯度,芮氏規模,深度,最大震度,位置)  -- 根據你的欄位數目調整
SET 當年地震編號 = NULLIF(@當年地震編號, 'NULL');

USE earthquake;
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\city-utf-8.csv'
INTO TABLE 縣市
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' -- 依據檔案的分隔符號
LINES TERMINATED BY '\n' -- 依據檔案每列的分隔方式
IGNORE 1 ROWS; -- 略過第一行

USE earthquake;
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/observation-utf-8.csv'
INTO TABLE 觀測
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' -- 依據檔案的分隔符號
LINES TERMINATED BY '\n' -- 依據檔案每列的分隔方式
IGNORE 1 ROWS; -- 略過第一行 

USE earthquake;
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Influence-utf-8.csv'
INTO TABLE 影響
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' -- 依據檔案的分隔符號
LINES TERMINATED BY '\n' -- 依據檔案每列的分隔方式
IGNORE 1 ROWS; -- 略過第一行
 
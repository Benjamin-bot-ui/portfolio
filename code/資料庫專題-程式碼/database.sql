CREATE database earthquake;

USE earthquake;
CREATE TABLE 觀測站(
	`測站代碼` VARCHAR(20) ,
    `觀測網` VARCHAR(20),
	`測站名稱` VARCHAR(50),
    `縣市` VARCHAR(20),
    `鄉鎮` VARCHAR(20),
    `經度` DECIMAL(5,2),
    `緯度` DECIMAL(4,2),
    PRIMARY KEY (測站代碼, 觀測網)
);

USE earthquake;
CREATE TABLE 地震事件(
	id INT PRIMARY KEY,
    `當年地震編號` INT,
    `地震類型` varchar(20),
    `發生時間` TIMESTAMP,
    `震央經度` DECIMAL(5,2),
    `震央緯度` DECIMAL(5,2),
    `芮氏規模` DECIMAL(2,1),
    `深度` DECIMAL(4,1),
	`最大震度` VARCHAR(5),
    `位置` varchar(20)
);

USE earthquake;
CREATE TABLE 縣市(
	`縣市編號` INT PRIMARY KEY,
	`縣市名稱` VARCHAR(50)
);

USE earthquake;
CREATE TABLE 觀測(
	id INT,
	`測站代碼` VARCHAR(50),
    `觀測網` VARCHAR(20),
    `震度` INT,
    PRIMARY KEY (id, `測站代碼`, `觀測網`),
    FOREIGN KEY (id) REFERENCES 地震事件(id),
    FOREIGN KEY (`測站代碼`,`觀測網`) REFERENCES 觀測站(`測站代碼`,`觀測網`)
);

USE earthquake;
CREATE TABLE 影響(
	id INT,
	`縣市編號` INT,
    `當地震度` INT,
    PRIMARY KEY (id, `縣市編號`),
    FOREIGN KEY (id) REFERENCES 地震事件(id),
    FOREIGN KEY (`縣市編號`) REFERENCES 縣市(`縣市編號`)
);


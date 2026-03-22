USE earthquake;
SELECT 
	e.發生時間,
	c.縣市名稱,
    i.當地震度,
	CASE 
			WHEN c.縣市名稱 = e.位置 THEN '震央'
			ELSE ''
    END AS 備註
FROM 影響 i
JOIN 縣市 c ON i.縣市編號 = c.縣市編號
JOIN 地震事件 e ON i.id = e.id
ORDER BY 發生時間 DESC;

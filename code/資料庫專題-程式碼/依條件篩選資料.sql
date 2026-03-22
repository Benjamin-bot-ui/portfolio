USE earthquake;
SELECT * FROM 地震事件
WHERE 1 = 1
  AND (發生時間 >= '2024-01-01' OR '2024-01-01' IS NULL)
  AND (發生時間 <= '2024-12-31' OR '2024-12-31' IS NULL)
  AND (位置 LIKE '%南投%' OR '%南投%' IS NULL)
  AND (芮氏規模 >= 4.0 OR 4.0 IS NULL)
  AND (芮氏規模 <= 6.0 OR 6.0 IS NULL)
ORDER BY 發生時間 DESC;



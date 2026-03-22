// 📦 引入必要模組（使用 mysql2/promise）
const mysql = require('mysql2/promise');
const express = require('express');
const app = express();
const port = 3000;

let connection;

// 建立資料庫連線
(async () => {
  try {
    connection = await mysql.createConnection({
      host: 'localhost',
      user: 'root',
      password: '0000',
      database: 'earthquake'
    });
    console.log('✅ 成功連線到資料庫');
  } catch (err) {
    console.error('❌ 資料庫連線失敗：', err);
  }
})();

app.use(express.json());
app.use(express.static('public'));

// 🔍 篩選地震資料（依時間、地點關鍵字、規模）
app.get('/filter', async (req, res) => {
  const { start, end, location, minMag, maxMag } = req.query;

  let sql = `SELECT * FROM 地震事件 WHERE 1=1`;
  const params = [];

  if (start) {
    sql += ` AND 發生時間 >= ?`;
    params.push(start);
  }

  if (end) {
    sql += ` AND 發生時間 <= ?`;
    params.push(end);
  }

  if (location) {
    sql += ` AND 位置 LIKE ?`;
    params.push(`%${location}%`);
  }

  if (minMag) {
    sql += ` AND 芮氏規模 >= ?`;
    params.push(minMag);
  }

  if (maxMag) {
    sql += ` AND 芮氏規模 <= ?`;
    params.push(maxMag);
  }

  sql += ` ORDER BY 發生時間 DESC`;

  try {
    const [rows] = await connection.execute(sql, params);
    res.json(rows);
  } catch (err) {
    console.error('❌ 篩選查詢失敗：', err);
    res.status(500).json({ success: false, message: '查詢錯誤' });
  }
});

// 取得全部地震資料
app.get('/data', async (req, res) => {
  try {
    const [results] = await connection.execute('SELECT * FROM `地震事件`');
    res.json(results);
  } catch (error) {
    console.error('查詢失敗：', error);
    res.status(500).send('資料查詢失敗');
  }
});

// 最新資料（最大 ID）
app.get('/latest', async (req, res) => {
  try {
    const [results] = await connection.execute('SELECT * FROM 地震事件 ORDER BY id DESC LIMIT 1');
    res.json(results[0]);
  } catch (error) {
    console.error('查詢最新資料失敗：', error);
    res.status(500).json({ error: '查詢錯誤' });
  }
});

// 統計震央位置次數
app.get('/stats', async (req, res) => {
  const { start, end } = req.query;
  const sql = `
    SELECT 位置 AS 震央位置, COUNT(*) AS 總次數
    FROM 地震事件
    WHERE 發生時間 BETWEEN ? AND ?
    GROUP BY 位置
    ORDER BY 總次數 DESC
  `;
  try {
    const [rows] = await connection.execute(sql, [start, end]);
    res.json(rows);
  } catch (err) {
    console.error('查詢統計失敗：', err);
    res.status(500).json({ success: false });
  }
});

// 查詢縣市地震震度
app.get('/city-intensity', async (req, res) => {
  const { start, end } = req.query;
  const sql = `
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
    WHERE e.發生時間 BETWEEN ? AND ?
    ORDER BY e.發生時間 DESC;
  `;
  try {
    const [rows] = await connection.execute(sql, [start, end]);
    res.json(rows);
  } catch (err) {
    console.error('查詢縣市震度失敗：', err);
    res.status(500).json({ success: false });
  }
});

// 🔐 管理者登入
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  try {
    const [results] = await connection.execute(
      'SELECT * FROM admin WHERE username = ? AND password = ?',
      [username, password]
    );
    res.json({ success: results.length > 0 });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false });
  }
});

// ➕ 新增地震事件
app.post('/add', async (req, res) => {
  try {
    const {
      id,
      event_number = null,
      type,
      datetime,
      longitude,
      latitude,
      magnitude,
      depth,
      intensity,
      location
    } = req.body;
    const formattedDatetime = datetime.replace(/:/, '-').replace(/:/, '-');
    const sql = `
      S`;
    const values = [
      id,
      event_number,
      type,
      formattedDatetime,
      longitude,
      latitude,
      magnitude,
      depth,
      intensity,
      location
    ];
    await connection.execute(sql, values);
    res.json({ success: true });
  } catch (err) {
    console.error('新增失敗：', err);
    res.status(500).json({ success: false });
  }
});

// ❌ 刪除地震事件
app.post('/delete', async (req, res) => {
  const { id } = req.body;
  if (!id) return res.status(400).json({ success: false, message: '缺少 id' });

  try {
    const [result] = await connection.execute('DELETE FROM 地震事件 WHERE id = ?', [id]);
    if (result.affectedRows > 0) {
      res.json({ success: true });
    } else {
      res.json({ success: false, message: '找不到資料' });
    }
  } catch (err) {
    console.error('❌ 刪除失敗：', err);
    res.status(500).json({ success: false });
  }
});

// 🚀 啟動伺服器
app.listen(port, () => {
  console.log(`伺服器啟動於 http://localhost:${port}`);
});



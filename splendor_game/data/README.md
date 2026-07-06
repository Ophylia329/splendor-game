# 数据文件目录

此目录用于存放游戏数据文件。

## 文件说明

### cards.csv
卡牌数据文件，包含90张发展卡的信息。

**格式：**
```csv
card_id,level,color,cost_white,cost_blue,cost_green,cost_red,cost_black,points
1,1,white,0,3,0,0,0,0
2,1,blue,2,0,0,1,0,0
...
```

**字段说明：**
- `card_id`: 卡牌唯一ID
- `level`: 卡牌等级 (1/2/3)
- `color`: 红利颜色 (white/blue/green/red/black)
- `cost_white`: 白色宝石花费
- `cost_blue`: 蓝色宝石花费
- `cost_green`: 绿色宝石花费
- `cost_red`: 红色宝石花费
- `cost_black`: 黑色宝石花费
- `points`: 声望分数

### nobles.csv
贵族数据文件，包含10张贵族卡的信息。

**格式：**
```csv
noble_id,name,req_white,req_blue,req_green,req_red,req_black
1,贵族1,3,3,3,0,0
2,贵族2,4,4,0,0,0
...
```

**字段说明：**
- `noble_id`: 贵族唯一ID
- `name`: 贵族名称
- `req_white`: 需要的白色红利数量
- `req_blue`: 需要的蓝色红利数量
- `req_green`: 需要的绿色红利数量
- `req_red`: 需要的红色红利数量
- `req_black`: 需要的黑色红利数量

## Excel格式

也可以使用Excel文件（.xlsx）格式，表头与CSV相同。

贵族数据可以在同一个Excel文件的"Nobles"工作表中。

## 注意

如果数据文件不存在，程序会自动使用内置的测试数据。

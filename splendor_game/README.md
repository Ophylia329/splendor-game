# 璀璨宝石 Splendor

一个基于Python和Pygame的璀璨宝石桌游电子化版本。

## 游戏说明

《璀璨宝石》是一款经典的策略桌游。玩家扮演文艺复兴时期的富商，通过收集宝石、购买发展卡、吸引贵族来获得声望分数。首先达到15分的玩家触发游戏结束，最终得分最高者获胜。

## 环境要求

- Python 3.8+
- pygame 2.5.0+
- openpyxl 3.1.0+（可选，用于读取Excel数据）

## 安装依赖

```bash
# 激活conda环境（如果使用conda）
conda activate splendor

# 安装依赖
pip install -r requirements.txt
```

## 运行游戏

### 使用conda环境运行

```bash
cd splendor_game
python main.py
```

### 或指定完整路径

```bash
"C:\Users\lin\.conda\envs\splendor\python.exe" main.py
```

## 游戏操作

### 开始游戏
1. 运行程序后会显示菜单
2. 选择玩家数量（2人/3人/4人）
3. 点击对应按钮开始游戏

### 游戏玩法

#### 主要动作（每回合选一个）
1. **拿取宝石**
   - 点击"拿取宝石"按钮
   - 点击宝石选择：
     - 3个不同颜色的宝石
     - 2个相同颜色的宝石（该颜色至少有4个）
   - 点击"确认动作"

2. **保留卡牌**
   - 点击"保留卡牌"按钮
   - 点击要保留的卡牌
   - 点击"确认动作"
   - 自动获得1个黄金（如果有）

3. **购买卡牌**
   - 点击"购买卡牌"按钮
   - 点击要购买的卡牌（桌面卡牌或保留卡）
   - 点击"确认动作"

#### 其他操作
- **结束回合**：点击"结束回合"按钮
- **取消动作**：点击"取消"按钮取消当前选择
- **返回菜单**：按ESC键

### 游戏规则要点

- 手上宝石最多10个，超过需弃置
- 最多保留3张卡牌
- 购买卡牌时，已拥有的红利可抵扣花费
- 黄金可当作任意颜色宝石使用
- 满足贵族需求时自动获得贵族（3分）
- 达到15分触发游戏结束，进行最后一轮

## 项目结构

```
splendor_game/
├── main.py              # 主程序入口
├── config.py            # 游戏配置
├── requirements.txt     # 依赖列表
├── models/              # 数据模型
│   ├── card.py
│   ├── noble.py
│   ├── player.py
│   └── game_state.py
├── core/                # 核心逻辑
│   ├── validator.py
│   ├── actions.py
│   └── game_engine.py
├── ui/                  # 界面
│   ├── components.py
│   ├── renderer.py
│   └── event_handler.py
├── utils/               # 工具函数
│   ├── data_loader.py
│   └── helpers.py
├── data/                # 数据文件
│   ├── cards.csv        # 卡牌数据（待添加）
│   └── nobles.csv       # 贵族数据（待添加）
└── assets/              # 素材文件
    └── images/          # 图片素材（待添加）
```

## 数据文件

### 卡牌数据（cards.csv）
格式：
```csv
card_id,level,color,cost_white,cost_blue,cost_green,cost_red,cost_black,points
1,1,white,0,3,0,0,0,0
```

### 贵族数据（nobles.csv）
格式：
```csv
noble_id,name,req_white,req_blue,req_green,req_red,req_black
1,贵族1,3,3,3,0,0
```

如果数据文件不存在，程序会自动使用内置测试数据（24张卡牌+10个贵族）。

## 打包成exe

```bash
# 安装pyinstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --windowed --add-data "data;data" --add-data "assets;assets" main.py

# 生成的exe文件在 dist/main.exe
```

## 开发者

课程设计项目

## 许可

仅用于学习和课程作业

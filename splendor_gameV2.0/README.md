# 璀璨宝石 Splendor

一个基于 Python 和 Pygame 开发的桌游《璀璨宝石》（Splendor）电子版实现。

## 📖 项目简介

《璀璨宝石》是一款经典的策略桌游，玩家扮演文艺复兴时期的宝石商人，通过收集宝石、购买发展卡、吸引贵族，最终获得15分声望即可获胜。本项目完整实现了游戏的核心规则和玩法，提供了友好的图形化界面。

## ✨ 特色功能

### 核心游戏功能
- **完整游戏规则**：严格按照官方规则实现 2-4 人游戏模式
- **三种核心动作**：
  - 拿取宝石（3个不同颜色或2个相同颜色）
  - 保留卡牌（从桌面或牌堆顶，获得1个黄金）
  - 购买卡牌（使用宝石和红利）
- **贵族系统**：当玩家红利满足条件时自动拜访，提供3分声望
- **胜利条件**：率先达到15分触发最后一轮，所有玩家行动后分数最高者获胜

### 技术特色
- **自适应UI缩放**：基于基准分辨率（1920x1080）的缩放系统，支持任意窗口大小
- **全屏/窗口切换**：按 F11 可在全屏和窗口模式间切换
- **完善的验证机制**：所有游戏动作都经过严格的合法性验证
- **数据驱动设计**：从 CSV 文件加载卡牌和贵族数据，便于扩展
- **中文支持**：完整的中文界面和提示系统
- **智能提示**：底部提示框实时显示操作指引和游戏状态

### UI 特性
- **直观的可视化界面**：
  - 左上区域：贵族竖列展示
  - 中上区域：三个等级的卡牌（每级4张）
  - 中间区域：公共宝石供应区（横排展示）
  - 右侧区域：所有玩家信息（竖列展示）
  - 底部区域：操作提示框
- **交互高亮**：悬停时高亮显示可点击元素
- **可购买标记**：购买模式下以绿色边框标记可购买的卡牌
- **实时状态显示**：当前玩家、分数、宝石、卡牌等信息

## 🏗️ 项目结构

```
splendor_gameV1.0/
├── main.py                 # 游戏主入口
├── config.py              # 游戏配置和常量
├── requirements.txt       # 项目依赖
│
├── models/                # 数据模型层
│   ├── card.py           # 卡牌类（Card）
│   ├── noble.py          # 贵族类（Noble）
│   ├── player.py         # 玩家类（Player）
│   └── game_state.py     # 游戏状态类（GameState）
│
├── core/                  # 核心游戏逻辑层
│   ├── game_engine.py    # 游戏引擎（GameEngine）
│   ├── actions.py        # 动作执行器（ActionExecutor）
│   └── validator.py      # 动作验证器（Validator）
│
├── ui/                    # 用户界面层
│   ├── renderer.py       # 渲染器（Renderer）
│   ├── event_handler.py  # 事件处理器（EventHandler）
│   └── components.py     # UI组件（CardDisplay, GemDisplay等）
│
├── utils/                 # 工具模块
│   ├── scaler.py         # UI缩放器（UIScaler）
│   ├── data_loader.py    # 数据加载器（CSV/Excel）
│   └── helpers.py        # 辅助函数
│
├── data/                  # 游戏数据
│   ├── cards.csv         # 卡牌数据（90张）
│   └── nobles.csv        # 贵族数据（10个）
│
└── assets/                # 游戏资源
    └── images/           # 图片资源
        ├── cards/        # 卡牌图片（70+张）
        ├── gems/         # 宝石图片（6种）
        ├── nobles/       # 贵族图片（10张）
        ├── decks/        # 牌堆图片（3张）
        └── bonus/        # 红利图标（5种）
```

## 📦 核心类说明

### 数据模型类（models/）

#### 1. Card（卡牌类）
**定义**: `models/card.py`

**属性**:
- `card_id`: int - 卡牌唯一标识
- `level`: int - 卡牌等级（1/2/3）
- `color`: str - 红利颜色（white/blue/green/red/black）
- `cost`: Dict[str, int] - 购买花费（各颜色宝石数量）
- `points`: int - 声望分数

**方法**:
- `get_total_cost()` - 计算卡牌总花费

#### 2. Noble（贵族类）
**定义**: `models/noble.py`

**属性**:
- `noble_id`: int - 贵族唯一标识
- `name`: str - 贵族名称
- `requirements`: Dict[str, int] - 所需红利数量
- `points`: int - 固定为3分

**方法**:
- `check_requirements(bonuses)` - 检查玩家红利是否满足条件

#### 3. Player（玩家类）
**定义**: `models/player.py`

**属性**:
- `player_id`: int - 玩家编号（0-3）
- `name`: str - 玩家名称
- `gems`: Dict[str, int] - 拥有的宝石
- `cards`: List[Card] - 已购买的发展卡
- `reserved_cards`: List[Card] - 保留的卡牌（最多3张）
- `nobles`: List[Noble] - 获得的贵族

**方法**:
- `get_total_gems()` - 获取宝石总数
- `get_bonuses()` - 获取红利（来自已购买卡牌）
- `get_points()` - 计算总声望分数
- `can_reserve_card()` - 检查能否保留卡牌
- `add_gems(gems)` - 添加宝石
- `remove_gems(gems)` - 移除宝石
- `add_card(card)` - 添加卡牌
- `reserve_card(card)` - 保留卡牌
- `add_noble(noble)` - 获得贵族

#### 4. GameState（游戏状态类）
**定义**: `models/game_state.py`

**属性**:
- `num_players`: int - 玩家数量（2/3/4）
- `players`: List[Player] - 玩家列表
- `current_player_idx`: int - 当前玩家索引
- `gem_bank`: Dict[str, int] - 公共宝石供应区
- `card_decks`: Dict[int, List[Card]] - 三个等级的牌堆
- `table_cards`: Dict[int, List[Card]] - 桌面展示的卡牌
- `nobles`: List[Noble] - 可用的贵族
- `game_over`: bool - 游戏是否结束
- `final_round`: bool - 是否进入最后一轮
- `trigger_player_idx`: int - 触发结束的玩家索引

**方法**:
- `get_current_player()` - 获取当前玩家
- `next_player()` - 切换到下一个玩家
- `check_win_condition()` - 检查胜利条件
- `get_winner()` - 获取获胜者
- `refill_table_cards()` - 补充桌面卡牌

### 核心逻辑类（core/）

#### 5. GameEngine（游戏引擎）
**定义**: `core/game_engine.py`

**职责**: 控制游戏流程和状态管理

**主要方法**:

- `take_gems_action(gems)` - 执行拿宝石动作
- `reserve_card_action(card, from_deck)` - 执行保留卡牌动作
- `reserve_card_from_deck(level)` - 从牌堆顶保留卡牌
- `purchase_card_action(card, from_reserved)` - 执行购买卡牌动作
- `end_turn()` - 结束回合（第一阶段：检查贵族）
- `complete_turn(selected_noble)` - 完成回合切换（第二阶段：授予贵族并切换玩家）
- `is_game_over()` - 检查游戏是否结束
- `get_winner()` - 获取获胜者
- `get_current_player()` - 获取当前玩家
- `get_game_state()` - 获取游戏状态

#### 6. ActionExecutor（动作执行器）
**定义**: `core/actions.py`

**职责**: 执行并验证玩家的游戏动作

**主要方法**:
- `take_gems(game_state, gems)` - 执行拿宝石动作
- `reserve_card(game_state, card, from_deck)` - 执行保留卡牌动作
- `purchase_card(game_state, card, from_reserved)` - 执行购买卡牌动作
- `discard_gems(player, gems, game_state)` - 执行弃置宝石动作
- `award_noble(player, noble, game_state)` - 授予玩家贵族
- `check_and_award_nobles(game_state)` - 检查可拜访的贵族

#### 7. Validator（验证器）
**定义**: `core/validator.py`

**职责**: 验证所有游戏动作的合法性

**主要方法**:
- `validate_take_gems(game_state, gems)` - 验证拿宝石动作
  - 规则1：拿3个不同颜色或2个相同颜色（该颜色至少有4个）
  - 规则2：不能拿黄金
  - 规则3：宝石种类不足时可拿1-2个
- `validate_reserve_card(game_state, card, from_deck)` - 验证保留卡牌动作
  - 规则：最多保留3张卡牌
- `validate_purchase_card(game_state, card)` - 验证购买卡牌动作
  - 规则：必须有足够的宝石（考虑红利和黄金）
- `validate_discard_gems(player, gems)` - 验证弃置宝石动作
  - 规则：回合结束时必须弃置到正好10个宝石
- `check_noble_visit(player, nobles)` - 检查贵族拜访条件

### 用户界面类（ui/）

#### 8. Renderer（渲染器）
**定义**: `ui/renderer.py`

**职责**: 负责绘制游戏画面，支持自适应缩放

**主要方法**:
- `render(game_state, ...)` - 渲染整个游戏画面
- `resize(width, height)` - 窗口大小改变时调整布局
- `draw_message(message, duration)` - 显示临时消息
- `set_hint_message(message)` - 设置底部提示框消息
- `clear_hint_message()` - 清空提示消息

**UI组件**:
- `CardDisplay` - 卡牌显示组件
- `GemDisplay` - 宝石显示组件
- `NobleDisplay` - 贵族显示组件
- `MessageBox` - 消息框组件

#### 9. EventHandler（事件处理器）
**定义**: `ui/event_handler.py`

**职责**: 处理所有用户交互（鼠标、键盘等）

**主要状态**:
- `current_action` - 当前动作模式（拿宝石/保留卡牌/购买卡牌）
- `selected_gems` - 选中的宝石
- `selected_card` - 选中的卡牌
- `selected_deck_level` - 选中的牌堆等级
- `purchasable_cards` - 可购买的卡牌列表

**主要方法**:
- `handle_events(events)` - 处理事件列表
- `draw_ui(screen)` - 绘制UI元素（按钮等）

#### 10. SplendorGame（主游戏类）
**定义**: `main.py`

**职责**: 游戏主循环和整体控制

**主要方法**:
- `run()` - 主游戏循环
- `show_menu()` - 显示开始菜单
- `start_game(num_players)` - 开始游戏
- `toggle_fullscreen()` - 切换全屏/窗口模式
- `handle_menu_events(buttons)` - 处理菜单事件
- `handle_game_events()` - 处理游戏事件
- `update()` - 更新游戏状态
- `render()` - 渲染游戏画面

### 工具类（utils/）

#### 11. UIScaler（UI缩放器）
**定义**: `utils/scaler.py`

**职责**: 根据实际窗口大小缩放所有UI元素

**主要方法**:
- `scale_value(value)` - 缩放数值
- `scale_font_size(size)` - 缩放字体大小
- `get_layout_value(area, key)` - 获取布局区域的缩放值

#### 12. DataLoader（数据加载器）
**定义**: `utils/data_loader.py`

**职责**: 从CSV/Excel加载游戏数据

**主要方法**:
- `load_cards_from_csv(file_path)` - 从CSV加载卡牌
- `load_nobles_from_csv(file_path)` - 从CSV加载贵族
- `shuffle_cards(cards)` - 洗牌
- `shuffle_nobles(nobles)` - 洗贵族

## 🎮 游戏动作说明

### 1. 拿取宝石（Take Gems）
**操作流程**:
1. 点击"拿取宝石"按钮进入拿宝石模式
2. 点击宝石选择（可选1-3个）
3. 再次点击已选宝石可取消选择
4. 点击同一按钮确认拿取

**规则**:
- 拿3个不同颜色的宝石（每种1个）
- 或拿2个相同颜色的宝石（该颜色至少有4个）
- 宝石不足时可拿1-2个
- 不能拿黄金（黄金只能通过保留卡牌获得）

### 2. 保留卡牌（Reserve Card）
**操作流程**:
1. 点击"保留卡牌"按钮进入保留模式
2. 点击桌面上的卡牌进行保留
3. 或点击牌堆图片从牌堆顶保留（盲抽）

**规则**:
- 最多保留3张卡牌
- 保留时获得1个黄金（如果有）
- 可以从桌面或牌堆顶保留
- 保留的卡牌可以在之后的回合购买

### 3. 购买卡牌（Purchase Card）
**操作流程**:
1. 点击"购买卡牌"按钮进入购买模式
2. 系统会以绿色边框标记可购买的卡牌
3. 点击可购买的卡牌完成购买

**规则**:
- 需要支付对应颜色的宝石
- 红利可以抵扣同色宝石花费
- 黄金可以替代任意颜色的宝石
- 可以购买桌面或保留区的卡牌
- 购买后获得卡牌提供的红利和分数

### 4. 弃置宝石（Discard Gems）
**触发条件**: 回合结束时宝石超过10个

**操作流程**:
1. 系统自动弹出弃置窗口
2. 点击要弃置的宝石
3. 必须弃置到正好10个

### 5. 贵族拜访（Noble Visit）
**触发条件**: 回合结束时红利满足贵族要求

**流程**:
- 自动检测满足条件的贵族
- 如果有多个，玩家可选择其中一个
- 每回合最多获得1个贵族
- 贵族提供3分声望

## 🎯 胜利条件

1. **触发最后一轮**: 任一玩家在回合结束时达到15分
2. **最后一轮规则**: 所有玩家再进行一轮（包括触发玩家）
3. **判定获胜者**:
   - 分数最高者获胜
   - 平局时发展卡最少者获胜

## 🚀 运行说明

### 环境要求
- Python 3.8+
- Windows 系统（中文字体路径依赖）

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行游戏
```bash
python main.py
```

### 操作说明
- **选择玩家数量**: 开始菜单点击 2人/3人/4人 游戏
- **F11**: 切换全屏/窗口模式
- **ESC**: 返回主菜单
- **鼠标点击**: 所有游戏操作

## 📊 游戏数据

### 卡牌数据（data/cards.csv）
- 等级I：40张卡牌
- 等级II：30张卡牌
- 等级III：20张卡牌
- 总计：90张发展卡

### 贵族数据（data/nobles.csv）
- 总计：10个贵族
- 根据玩家数量选择：
  - 2人游戏：3个贵族
  - 3人游戏：4个贵族
  - 4人游戏：5个贵族

### 宝石配置
根据玩家数量配置宝石数量：
- 2人游戏：每色4个（黄金5个）
- 3人游戏：每色5个（黄金5个）
- 4人游戏：每色7个（黄金5个）

## 📝 配置说明

主要配置项位于 `config.py`：

- `FULLSCREEN`: 初始全屏状态（默认False）
- `BASE_WIDTH/BASE_HEIGHT`: 基准分辨率（1920x1080）
- `CARD_WIDTH/CARD_HEIGHT`: 卡牌尺寸（可调整，其他区域自动适应）
- `MAX_HAND_GEMS`: 最大宝石持有量（10个）
- `MAX_RESERVED_CARDS`: 最大保留卡数量（3张）
- `WIN_POINTS`: 胜利所需分数（15分）

## 🔧 技术亮点

1. **分层架构**: 严格的模型-逻辑-界面三层分离
2. **自适应缩放**: 基于基准分辨率的缩放系统，支持任意分辨率
3. **数据驱动**: 从CSV加载游戏数据，易于维护和扩展
4. **完善验证**: 所有动作都经过严格的合法性验证
5. **状态管理**: 清晰的游戏状态流转和回合管理
6. **事件驱动**: 基于事件的交互系统，响应灵敏

## 📄 许可证

本项目仅供学习交流使用。

---

**开发者**: Python课程设计项目
**版本**: V1.0
**最后更新**: 2025

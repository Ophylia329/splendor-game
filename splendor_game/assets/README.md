# 素材文件目录

此目录用于存放游戏的图片和字体等素材。

## 目录结构

```
assets/
├── images/
│   ├── cards/          # 卡牌图片
│   │   ├── level1/     # 1级卡图片
│   │   ├── level2/     # 2级卡图片
│   │   └── level3/     # 3级卡图片
│   ├── gems/           # 宝石图标
│   ├── nobles/         # 贵族卡图片
│   ├── background.png  # 背景图
│   └── card_back.png   # 卡牌背面
└── fonts/              # 字体文件（可选）
```

## 文件命名规范

### 卡牌图片
- 文件名格式: `card_{card_id}.png`
- 例如: `card_1.png`, `card_2.png`
- 尺寸建议: 240x360 像素

### 宝石图标
- 文件名格式: `gem_{color}.png`
- 例如: `gem_white.png`, `gem_blue.png`, `gem_gold.png`
- 尺寸建议: 100x100 像素

### 贵族图片
- 文件名格式: `noble_{noble_id}.png`
- 例如: `noble_1.png`, `noble_2.png`
- 尺寸建议: 200x200 像素

## 注意

如果图片文件不存在，游戏会使用纯色矩形和文字作为替代显示。

可以在游戏基本功能完成后再添加图片素材。

"""
测试可缩放界面和全屏功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("璀璨宝石 - 可缩放界面测试")
print("=" * 60)
print()
print("测试内容:")
print("1. 基准分辨率：1920x1080")
print("2. 默认窗口：1600x900（可调整大小）")
print("3. F11 切换全屏")
print("4. 拖拽窗口边缘调整大小")
print("5. 所有UI元素自动缩放")
print("6. 玩家区域增加至340px高度，可容纳保留卡")
print()
print("操作说明:")
print("- F11: 切换全屏/窗口模式")
print("- ESC: 返回菜单")
print("- 拖拽窗口边缘: 调整窗口大小")
print()
print("=" * 60)
print()

try:
    # 导入并运行游戏
    from main import main
    main()
except ImportError as e:
    print(f"错误: 无法导入游戏模块 - {e}")
    print("请确保在 splendor_game 目录下运行此脚本")
except Exception as e:
    print(f"游戏运行出错: {e}")
    import traceback
    traceback.print_exc()

"""
按钮闪烁测试脚本
用于验证按钮是否还会闪烁
"""
import pygame
import sys
sys.path.insert(0, '.')

from ui.components import Button
from ui.renderer import get_chinese_font
import config

def test_button_flicker():
    """测试按钮闪烁"""
    pygame.init()

    # 创建窗口
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("按钮闪烁测试")

    # 创建字体
    font = get_chinese_font(config.FONT_SIZE_MEDIUM)

    # 创建测试按钮（持久化对象）
    buttons = [
        Button(100, 100, 160, 50, "按钮1"),
        Button(100, 170, 160, 50, "按钮2"),
        Button(100, 240, 160, 50, "按钮3"),
        Button(100, 310, 160, 50, "按钮4（禁用）"),
    ]

    # 禁用第4个按钮
    buttons[3].set_enabled(False)

    clock = pygame.time.Clock()
    running = True

    frame_count = 0

    print("=" * 60)
    print("按钮闪烁测试")
    print("=" * 60)
    print("移动鼠标悬停在按钮上，观察是否闪烁")
    print("按 ESC 退出测试")
    print()

    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 清空屏幕
        screen.fill(config.COLOR_BACKGROUND)

        # 第一步：更新按钮启用状态（本测试中固定）
        # buttons[3].set_enabled(False)  # 已经设置过了

        # 第二步：更新按钮悬停状态
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.is_hovered = btn.rect.collidepoint(mouse_pos) and btn.is_enabled

        # 第三步：绘制按钮
        for i, btn in enumerate(buttons):
            btn.draw(screen, font)

            # 显示按钮状态信息
            status = f"hovered={btn.is_hovered}, enabled={btn.is_enabled}"
            status_text = font.render(status, True, config.COLOR_WHITE)
            screen.blit(status_text, (280, 105 + i * 70))

        # 显示帧数
        frame_count += 1
        fps_text = font.render(f"FPS: {int(clock.get_fps())} | Frame: {frame_count}",
                              True, config.COLOR_WHITE)
        screen.blit(fps_text, (100, 450))

        # 显示提示
        hint_text = font.render("移动鼠标到按钮上测试悬停效果", True, config.COLOR_LIGHT_GRAY)
        screen.blit(hint_text, (100, 500))

        # 统一刷新（只调用一次 flip）
        pygame.display.flip()

        # 控制帧率
        clock.tick(config.FPS)

    pygame.quit()
    print("\n测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_button_flicker()

"""
主程序 - 游戏入口
"""
import sys
import pygame
from core import GameEngine
from ui import Renderer, EventHandler, Button
import config


class SplendorGame:
    """璀璨宝石游戏主类"""

    def __init__(self):
        """初始化游戏"""
        # 初始化pygame
        pygame.init()

        # 全屏状态
        self.is_fullscreen = config.FULLSCREEN

        # 创建窗口
        self.create_window()

        # 创建时钟
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.running = True
        self.game_engine = None
        self.renderer = Renderer(self.screen)
        self.event_handler = None

        # 游戏模式
        self.in_menu = True

        # 菜单按钮（预先创建，避免每帧重新创建导致闪烁）
        self.menu_buttons = None

    def create_window(self):
        """创建或重建窗口"""
        if self.is_fullscreen:
            # 全屏模式 - 自动获取屏幕尺寸
            info = pygame.display.Info()
            config.WINDOW_WIDTH = info.current_w
            config.WINDOW_HEIGHT = info.current_h
            self.screen = pygame.display.set_mode(
                (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
                pygame.FULLSCREEN
            )
        else:
            # 窗口模式（可调整大小）
            self.screen = pygame.display.set_mode(
                (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
                pygame.RESIZABLE
            )

        pygame.display.set_caption(config.WINDOW_TITLE)

    def toggle_fullscreen(self):
        """切换全屏/窗口模式（F11）"""
        self.is_fullscreen = not self.is_fullscreen
        self.create_window()

        # 更新渲染器的屏幕引用和缩放
        self.renderer.screen = self.screen
        self.renderer.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # 重置菜单按钮（需要根据新尺寸重新创建）
        self.menu_buttons = None

        print(f"切换到 {'全屏' if self.is_fullscreen else '窗口'} 模式 ({config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT})")

    def show_menu(self):
        """显示开始菜单"""
        self.screen.fill(config.COLOR_BACKGROUND)

        # 导入字体函数
        from ui.renderer import get_chinese_font

        # 使用渲染器的缩放器
        s = self.renderer.scaler.scale_value

        # 标题
        title = self.renderer.font_title.render("璀璨宝石 Splendor", True, config.COLOR_WHITE)
        title_rect = title.get_rect(center=(config.WINDOW_WIDTH // 2, s(150)))
        self.screen.blit(title, title_rect)

        # 选择玩家数量提示
        prompt = self.renderer.font_medium.render("选择玩家数量:", True, config.COLOR_WHITE)
        prompt_rect = prompt.get_rect(center=(config.WINDOW_WIDTH // 2, s(300)))
        self.screen.blit(prompt, prompt_rect)

        # 操作提示
        hint = self.renderer.font_medium.render("按 ESC 返回菜单 | 按 F11 全屏切换", True, config.COLOR_LIGHT_GRAY)
        hint_rect = hint.get_rect(center=(config.WINDOW_WIDTH // 2, s(500)))
        self.screen.blit(hint, hint_rect)

        # 创建或复用按钮（避免每帧重新创建）
        if self.menu_buttons is None:
            buttons = []
            for i, num in enumerate([2, 3, 4]):
                x = config.WINDOW_WIDTH // 2 - s(180) + i * s(140)
                y = s(380)
                btn = Button(x, y, s(120), s(60), f"{num}人游戏")
                buttons.append((btn, num))
            self.menu_buttons = buttons

        # 更新按钮悬停状态并绘制
        mouse_pos = pygame.mouse.get_pos()
        for btn, num in self.menu_buttons:
            btn.is_hovered = btn.rect.collidepoint(mouse_pos)
            btn.draw(self.screen, self.renderer.font_medium)

        pygame.display.flip()

    def start_game(self, num_players):
        """
        开始游戏

        参数:
            num_players: 玩家数量
        """
        print(f"\n开始{num_players}人游戏...")

        # 创建游戏引擎
        player_names = [f"玩家{i+1}" for i in range(num_players)]
        self.game_engine = GameEngine(num_players, player_names)

        # 创建事件处理器
        self.event_handler = EventHandler(self.game_engine, self.renderer)

        self.in_menu = False

        # 显示开始提示
        first_player = self.game_engine.get_current_player()
        self.renderer.draw_message(f"游戏开始！\n{first_player.name} 先手", duration=2000)

    def handle_menu_events(self, buttons):
        """
        处理菜单事件

        参数:
            buttons: 按钮列表
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # 按ESC退出游戏
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                # F11切换全屏
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    return

            # 窗口大小改变
            if event.type == pygame.VIDEORESIZE:
                config.WINDOW_WIDTH = event.w
                config.WINDOW_HEIGHT = event.h
                self.renderer.resize(event.w, event.h)
                self.menu_buttons = None  # 重置菜单按钮
                return

            # 检查按钮点击
            for btn, num_players in buttons:
                if btn.handle_event(event):
                    self.start_game(num_players)
                    return

    def handle_game_events(self):
        """处理游戏中的事件"""
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return

            # 按ESC返回菜单
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.in_menu = True
                    self.game_engine = None
                    self.event_handler = None
                    self.menu_buttons = None  # 重置菜单按钮
                    return
                # F11切换全屏
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    return

            # 窗口大小改变
            if event.type == pygame.VIDEORESIZE:
                config.WINDOW_WIDTH = event.w
                config.WINDOW_HEIGHT = event.h
                self.renderer.resize(event.w, event.h)
                # 重新创建 event_handler 的按钮
                if self.event_handler:
                    self.event_handler.recreate_buttons()
                return

        # 交给事件处理器处理
        if self.event_handler:
            self.event_handler.handle_events(events)

    def update(self):
        """更新游戏状态"""
        if not self.in_menu and self.game_engine:
            # 检查游戏是否结束
            if self.game_engine.is_game_over():
                self._show_game_over_screen()

    def _show_game_over_screen(self):
        """显示游戏结束画面"""
        winner = self.game_engine.get_winner()

        # 渲染最终画面
        self.renderer.render(self.game_engine.get_game_state())

        # 导入字体函数
        from ui.renderer import get_chinese_font

        # 显示获胜信息
        font_title = get_chinese_font(config.FONT_SIZE_TITLE)
        font_medium = get_chinese_font(config.FONT_SIZE_MEDIUM)

        # 半透明背景
        s = pygame.Surface((800, 400))
        s.set_alpha(230)
        s.fill(config.COLOR_DARK_GRAY)
        x = (config.WINDOW_WIDTH - 800) // 2
        y = (config.WINDOW_HEIGHT - 400) // 2
        self.screen.blit(s, (x, y))

        # 边框
        pygame.draw.rect(self.screen, config.COLOR_WHITE, (x, y, 800, 400), 5)

        # 标题
        title = font_title.render("游戏结束！", True, config.COLOR_WHITE)
        title_rect = title.get_rect(center=(config.WINDOW_WIDTH // 2, y + 60))
        self.screen.blit(title, title_rect)

        # 获胜者
        winner_text = font_title.render(f"{winner.name} 获胜！", True, config.GEM_COLORS['gold'])
        winner_rect = winner_text.get_rect(center=(config.WINDOW_WIDTH // 2, y + 130))
        self.screen.blit(winner_text, winner_rect)

        # 分数
        score_text = font_medium.render(f"最终得分: {winner.get_points()}分", True, config.COLOR_WHITE)
        score_rect = score_text.get_rect(center=(config.WINDOW_WIDTH // 2, y + 190))
        self.screen.blit(score_text, score_rect)

        # 所有玩家排名
        sorted_players = sorted(
            self.game_engine.game_state.players,
            key=lambda p: (p.get_points(), -len(p.cards)),
            reverse=True
        )

        rank_y = y + 240
        rank_text = font_medium.render("最终排名:", True, config.COLOR_WHITE)
        self.screen.blit(rank_text, (x + 50, rank_y))

        for i, player in enumerate(sorted_players):
            rank_y += 35
            text = f"{i+1}. {player.name}: {player.get_points()}分 ({len(player.cards)}张卡)"
            player_text = font_medium.render(text, True, config.COLOR_WHITE)
            self.screen.blit(player_text, (x + 80, rank_y))

        # 提示
        hint = font_medium.render("按 ESC 返回菜单", True, config.COLOR_LIGHT_GRAY)
        hint_rect = hint.get_rect(center=(config.WINDOW_WIDTH // 2, y + 370))
        self.screen.blit(hint, hint_rect)

        pygame.display.flip()

        # 等待用户按键
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.in_menu = True
                        self.game_engine = None
                        self.event_handler = None
                        self.menu_buttons = None  # 重置菜单按钮
                        waiting = False

            self.clock.tick(config.FPS)

    def render(self):
        """渲染游戏画面"""
        if self.in_menu:
            # 显示菜单（在主循环中处理）
            pass
        else:
            # 渲染游戏画面
            if self.game_engine:
                # 获取选中状态
                selected_card = self.event_handler.selected_card if self.event_handler else None
                selected_gems = self.event_handler.selected_gems if self.event_handler else {}
                selected_deck_level = self.event_handler.selected_deck_level if self.event_handler else None
                purchasable_cards = self.event_handler.purchasable_cards if self.event_handler else []

                self.renderer.render(
                    self.game_engine.get_game_state(),
                    selected_card=selected_card,
                    selected_gems=selected_gems,
                    selected_deck_level=selected_deck_level,
                    purchasable_cards=purchasable_cards
                )

                # 渲染UI元素（按钮、提示等）
                if self.event_handler:
                    self.event_handler.draw_ui(self.screen)

                pygame.display.flip()

    def run(self):
        """主游戏循环"""
        print("游戏启动...")
        print("=" * 60)

        while self.running:
            if self.in_menu:
                # 菜单模式
                self.show_menu()
                self.handle_menu_events(self.menu_buttons)
            else:
                # 游戏模式
                self.handle_game_events()
                self.update()
                self.render()

            # 控制帧率
            self.clock.tick(config.FPS)

        # 退出游戏
        pygame.quit()
        print("\n游戏结束！")
        print("=" * 60)


def main():
    """主函数"""
    try:
        game = SplendorGame()
        game.run()
    except Exception as e:
        print(f"游戏运行出错: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()


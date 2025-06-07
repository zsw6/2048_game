import random
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from functools import partial
from kivy.animation import Animation
import copy

# 定义方块颜色映射
TILE_COLORS = {
    0: (205/255, 193/255, 180/255, 1),  # 空白方块
    2: (238/255, 228/255, 218/255, 1),
    4: (237/255, 224/255, 200/255, 1),
    8: (242/255, 177/255, 121/255, 1),
    16: (245/255, 149/255, 99/255, 1),
    32: (246/255, 124/255, 95/255, 1),
    64: (246/255, 94/255, 59/255, 1),
    128: (237/255, 207/255, 114/255, 1),
    256: (237/255, 204/255, 97/255, 1),
    512: (237/255, 200/255, 80/255, 1),
    1024: (237/255, 197/255, 63/255, 1),
    2048: (237/255, 194/255, 46/255, 1),
    4096: (60/255, 58/255, 50/255, 1),
    8192: (60/255, 58/255, 50/255, 1)
}

# 定义方块文字颜色
TEXT_COLORS = {
    0: (0, 0, 0, 0),  # 透明
    2: (119/255, 110/255, 101/255, 1),
    4: (119/255, 110/255, 101/255, 1),
    8: (249/255, 246/255, 242/255, 1),
    16: (249/255, 246/255, 242/255, 1),
    32: (249/255, 246/255, 242/255, 1),
    64: (249/255, 246/255, 242/255, 1),
    128: (249/255, 246/255, 242/255, 1),
    256: (249/255, 246/255, 242/255, 1),
    512: (249/255, 246/255, 242/255, 1),
    1024: (249/255, 246/255, 242/255, 1),
    2048: (249/255, 246/255, 242/255, 1),
    4096: (249/255, 246/255, 242/255, 1),
    8192: (249/255, 246/255, 242/255, 1)
}

# 游戏板类，处理游戏逻辑
class GameBoard:
    def __init__(self, size=4):
        self.size = size
        self.score = 0
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.add_random_tile()
        self.add_random_tile()
        self.game_over = False
        self.won = False
    
    def reset(self):
        """重置游戏板"""
        self.score = 0
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.add_random_tile()
        self.add_random_tile()
        self.game_over = False
        self.won = False
    
    def add_random_tile(self):
        """在随机空位置添加一个新方块（90%概率为2，10%概率为4）"""
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4
            return i, j
        return None
    
    def move(self, direction):
        """移动方块
        direction: 0=上, 1=右, 2=下, 3=左
        返回: (移动是否有效, 新方块位置)
        """
        # 保存移动前的状态用于比较
        old_board = copy.deepcopy(self.board)
        old_score = self.score
        
        # 根据方向执行移动
        if direction == 0:  # 上
            self._move_up()
        elif direction == 1:  # 右
            self._move_right()
        elif direction == 2:  # 下
            self._move_down()
        elif direction == 3:  # 左
            self._move_left()
        
        # 检查移动是否有效（板子是否改变）
        moved = old_board != self.board
        
        # 如果移动有效，添加新方块
        new_tile_pos = None
        if moved:
            new_tile_pos = self.add_random_tile()
            
            # 检查是否达到2048
            if not self.won and any(2048 in row for row in self.board):
                self.won = True
            
            # 检查游戏是否结束
            self.game_over = self._is_game_over()
        
        return moved, new_tile_pos
    
    def _move_left(self):
        """向左移动并合并方块"""
        for i in range(self.size):
            # 移除零并合并相同的数字
            row = [tile for tile in self.board[i] if tile != 0]
            for j in range(len(row) - 1):
                if row[j] == row[j + 1]:
                    row[j] *= 2
                    self.score += row[j]
                    row[j + 1] = 0
            
            # 再次移除零
            row = [tile for tile in row if tile != 0]
            
            # 填充零
            row += [0] * (self.size - len(row))
            self.board[i] = row
    
    def _move_right(self):
        """向右移动并合并方块"""
        for i in range(self.size):
            # 移除零并合并相同的数字
            row = [tile for tile in self.board[i] if tile != 0]
            for j in range(len(row) - 1, 0, -1):
                if row[j] == row[j - 1]:
                    row[j] *= 2
                    self.score += row[j]
                    row[j - 1] = 0
            
            # 再次移除零
            row = [tile for tile in row if tile != 0]
            
            # 填充零
            row = [0] * (self.size - len(row)) + row
            self.board[i] = row
    
    def _move_up(self):
        """向上移动并合并方块"""
        for j in range(self.size):
            # 获取列
            col = [self.board[i][j] for i in range(self.size)]
            
            # 移除零并合并相同的数字
            col = [tile for tile in col if tile != 0]
            for i in range(len(col) - 1):
                if col[i] == col[i + 1]:
                    col[i] *= 2
                    self.score += col[i]
                    col[i + 1] = 0
            
            # 再次移除零
            col = [tile for tile in col if tile != 0]
            
            # 填充零
            col += [0] * (self.size - len(col))
            
            # 更新列
            for i in range(self.size):
                self.board[i][j] = col[i]
    
    def _move_down(self):
        """向下移动并合并方块"""
        for j in range(self.size):
            # 获取列
            col = [self.board[i][j] for i in range(self.size)]
            
            # 移除零并合并相同的数字
            col = [tile for tile in col if tile != 0]
            for i in range(len(col) - 1, 0, -1):
                if col[i] == col[i - 1]:
                    col[i] *= 2
                    self.score += col[i]
                    col[i - 1] = 0
            
            # 再次移除零
            col = [tile for tile in col if tile != 0]
            
            # 填充零
            col = [0] * (self.size - len(col)) + col
            
            # 更新列
            for i in range(self.size):
                self.board[i][j] = col[i]
    
    def _is_game_over(self):
        """检查游戏是否结束"""
        # 如果有空格，游戏未结束
        if any(0 in row for row in self.board):
            return False
        
        # 检查水平相邻的方块
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.board[i][j] == self.board[i][j + 1]:
                    return False
        
        # 检查垂直相邻的方块
        for i in range(self.size - 1):
            for j in range(self.size):
                if self.board[i][j] == self.board[i + 1][j]:
                    return False
        
        # 没有可能的移动，游戏结束
        return True

# 方块UI组件
from kivy.animation import Animation
from kivy.graphics import RoundedRectangle

class Tile(ButtonBehavior, Label):
    value = NumericProperty(0)
    background_color = ListProperty([1, 1, 1, 1])
    
    def __init__(self, **kwargs):
        super(Tile, self).__init__(**kwargs)
        self.font_size = dp(24)
        self.bold = True
        self.font_name = 'Roboto'  # 添加字体设置
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # 初始化圆角矩形背景
        with self.canvas.before:
            Color(*TILE_COLORS.get(self.value, (205/255, 193/255, 180/255, 1)))
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(5)]  # 设置圆角半径
            )
        
        # 设置初始外观
        self.update_tile(animate=False)
    
    def _update_rect(self, instance, value):
        """更新背景矩形的大小和位置"""
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size
    
    def update_tile(self, animate=True):
        """更新方块外观"""
        new_text = str(self.value) if self.value > 0 else ""
        new_background = TILE_COLORS.get(self.value, (205/255, 193/255, 180/255, 1))
        new_color = TEXT_COLORS.get(self.value, (119/255, 110/255, 101/255, 1))
        
        # 根据数字大小调整字体
        if self.value >= 1000:
            new_font_size = dp(18)
        elif self.value >= 100:
            new_font_size = dp(22)
        else:
            new_font_size = dp(24)
        
        # 更新文本和颜色
        self.text = new_text
        self.color = new_color
        self.font_size = new_font_size
        
        # 更新背景颜色
        if hasattr(self, 'rect'):
            self.canvas.before.clear()
            with self.canvas.before:
                Color(*new_background)
                self.rect = RoundedRectangle(
                    pos=self.pos,
                    size=self.size,
                    radius=[dp(5)]
                )
        
        # 如果是新值，添加简单的透明度动画
        if animate and self.text != "":
            self.opacity = 0
            anim = Animation(opacity=1, duration=0.2)
            anim.start(self)
        
        # 更新背景颜色
        if hasattr(self, 'rect'):
            self.canvas.before.clear()
            with self.canvas.before:
                Color(*new_background)
                self.rect = RoundedRectangle(
                    pos=self.pos,
                    size=self.size,
                    radius=[dp(5)]
                )

    def on_value(self, instance, value):
        """当值改变时更新外观"""
        self.update_tile()
    
    def on_size(self, *args):
        """当大小改变时更新外观"""
        self.update_tile()
    
    def on_pos(self, *args):
        """当位置改变时更新外观"""
        self.update_tile()

# 游戏界面
class Game2048(BoxLayout):
    score_label = ObjectProperty(None)
    grid_layout = ObjectProperty(None)
    game_board = None
    tiles = None
    
    # 触摸控制相关常量
    MIN_SWIPE_DISTANCE = dp(30)    # 最小滑动距离
    SWIPE_THRESHOLD = 0.3          # 滑动方向判定阈值
    
    def __init__(self, **kwargs):
        # 设置窗口背景色
        Window.clearcolor = (250/255, 248/255, 239/255, 1)
        
        super(Game2048, self).__init__(**kwargs)
        
        # 初始化触摸事件变量
        self.touch_start_x = 0
        self.touch_start_y = 0
        
        # 设置键盘事件
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        # 基本布局设置
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)
        
        # 创建顶部控制栏
        top_bar = BoxLayout(size_hint=(1, 0.15), spacing=dp(10))
        
        # 创建标题和分数容器
        title_score_box = BoxLayout(orientation='vertical', size_hint=(0.7, 1))
        
        # 游戏标题
        title_label = Label(
            text="2048",
            size_hint=(1, 0.6),
            font_size=dp(36),
            bold=True,
            color=(119/255, 110/255, 101/255, 1),
            font_name='Roboto'  # 添加字体设置
        )
        
        # 分数显示
        score_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.4),
            padding=(dp(5), 0),
            spacing=dp(2)
        )
        
        score_title = Label(
            text="分数",
            size_hint=(1, 0.4),
            font_size=dp(14),
            color=(119/255, 110/255, 101/255, 1),
            font_name='Roboto'  # 添加字体设置
        )
        
        self.score_label = Label(
            text="0",
            size_hint=(1, 0.6),
            font_size=dp(20),
            bold=True,
            color=(119/255, 110/255, 101/255, 1),
            font_name='Roboto'  # 添加字体设置
        )
        
        score_box.add_widget(score_title)
        score_box.add_widget(self.score_label)
        
        title_score_box.add_widget(title_label)
        title_score_box.add_widget(score_box)
        
        # 控制按钮
        buttons_box = BoxLayout(size_hint=(0.3, 1), spacing=dp(10))
        new_game_button = Button(
            text="新游戏",
            size_hint=(1, 0.5),
            pos_hint={'center_y': 0.5},
            background_color=(143/255, 122/255, 102/255, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16),
            bold=True,
            font_name='Roboto'  # 添加字体设置
        )
        new_game_button.bind(on_press=self.new_game)
        buttons_box.add_widget(new_game_button)
        
        top_bar.add_widget(title_score_box)
        top_bar.add_widget(buttons_box)
        self.add_widget(top_bar)
        
        # 创建游戏网格容器（带背景色）
        grid_container = BoxLayout(size_hint=(1, 0.85))
        with grid_container.canvas.before:
            Color(187/255, 173/255, 160/255, 1)  # 游戏板背景色
            self.grid_bg = Rectangle(pos=grid_container.pos, size=grid_container.size)
        grid_container.bind(pos=self._update_grid_bg, size=self._update_grid_bg)
        
        # 创建游戏网格
        self.grid_layout = GridLayout(
            cols=4,
            spacing=dp(5),
            padding=dp(5),
            size_hint=(0.95, 0.95),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        grid_container.add_widget(self.grid_layout)
        self.add_widget(grid_container)
        
        # 初始化游戏
        self.game_board = GameBoard()
        self.tiles = []
        self.setup_board()
        
    def _update_grid_bg(self, instance, value):
        """更新网格背景的位置和大小"""
        if hasattr(self, 'grid_bg'):
            self.grid_bg.pos = instance.pos
            self.grid_bg.size = instance.size
    
    def setup_board(self):
        """初始化游戏板UI"""
        self.grid_layout.clear_widgets()
        self.tiles = []
        
        # 创建16个方块
        for i in range(4):
            row = []
            for j in range(4):
                tile = Tile(value=self.game_board.board[i][j])
                self.grid_layout.add_widget(tile)
                row.append(tile)
            self.tiles.append(row)
        
        # 更新分数
        self.score_label.text = str(self.game_board.score)
    
    def update_board(self, new_tile_pos=None):
        """更新游戏板UI"""
        for i in range(4):
            for j in range(4):
                # 使用动画更新方块值
                if new_tile_pos and (i, j) == new_tile_pos:
                    # 新方块出现动画
                    self.tiles[i][j].opacity = 0
                    self.tiles[i][j].value = self.game_board.board[i][j]
                    anim = Animation(opacity=1, duration=0.2)
                    anim.start(self.tiles[i][j])
                else:
                    self.tiles[i][j].value = self.game_board.board[i][j]
        
        # 更新分数
        self.score_label.text = str(self.game_board.score)
        
        # 检查游戏状态
        if self.game_board.won:
            self.show_game_message("恭喜！", "你达到了2048！\n继续游戏或开始新游戏？", 
                                  [("继续", self.dismiss_popup), ("新游戏", self.new_game)])
            self.game_board.won = False  # 防止重复显示
        
        elif self.game_board.game_over:
            self.show_game_message("游戏结束", "没有更多可能的移动了！\n你的分数: " + str(self.game_board.score), 
                                  [("新游戏", self.new_game)])
    
    def move(self, direction):
        """执行移动"""
        moved, new_tile_pos = self.game_board.move(direction)
        if moved:
            self.update_board(new_tile_pos)
    
    def new_game(self, *args):
        """开始新游戏"""
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()
        self.game_board.reset()
        self.update_board()
    
    def show_game_message(self, title, message, buttons):
        """显示游戏消息弹窗"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, font_size=dp(18), font_name='Roboto'))
        
        # 添加按钮
        btn_layout = BoxLayout(size_hint=(1, 0.4), spacing=dp(10))
        for btn_text, btn_callback in buttons:
            btn = Button(text=btn_text, font_name='Roboto')
            btn.bind(on_press=btn_callback)
            btn_layout.add_widget(btn)
        
        content.add_widget(btn_layout)
        
        self.popup = Popup(
            title=title, 
            content=content, 
            size_hint=(0.8, 0.5), 
            auto_dismiss=False,
            title_font='Roboto'  # 设置标题字体
        )
        self.popup.open()
    
    def dismiss_popup(self, *args):
        """关闭弹窗"""
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()
    
    def _keyboard_closed(self):
        """键盘关闭时的处理，清理键盘绑定"""
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """处理键盘按键事件"""
        # 定义按键映射
        key_mapping = {
            'up': 0,     # 上
            'w': 0,      # 上
            'right': 1,  # 右
            'd': 1,      # 右
            'down': 2,   # 下
            's': 2,      # 下
            'left': 3,   # 左
            'a': 3       # 左
        }
        
        # 检查按键是否在映射中
        if keycode[1] in key_mapping:
            direction = key_mapping[keycode[1]]
            self.move(direction)
            return True
            
        # 特殊按键处理
        elif keycode[1] == 'r':  # 按R键重新开始游戏
            self.new_game()
            return True
        elif keycode[1] == 'escape':  # ESC键关闭键盘
            keyboard.release()
            return True
            
        return False
    
    def on_touch_down(self, touch):
        """处理触摸开始事件"""
        self.touch_start_x = touch.x
        self.touch_start_y = touch.y
        return super(Game2048, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        """处理触摸结束事件，判断滑动方向"""
        # 计算滑动距离和角度
        dx = touch.x - self.touch_start_x
        dy = touch.y - self.touch_start_y
        
        # 计算总滑动距离
        total_distance = (dx * dx + dy * dy) ** 0.5
        
        # 如果滑动距离太小，忽略这次滑动
        if total_distance < self.MIN_SWIPE_DISTANCE:
            return super(Game2048, self).on_touch_up(touch)
        
        # 计算水平和垂直方向的移动比例
        try:
            dx_ratio = abs(dx / total_distance)
            dy_ratio = abs(dy / total_distance)
        except ZeroDivisionError:
            return super(Game2048, self).on_touch_up(touch)
        
        # 根据滑动方向的主导性来决定移动方向
        if dx_ratio > self.SWIPE_THRESHOLD and dx_ratio > dy_ratio:
            # 水平滑动
            if dx > 0:
                self.move(1)  # 右
            else:
                self.move(3)  # 左
        elif dy_ratio > self.SWIPE_THRESHOLD and dy_ratio > dx_ratio:
            # 垂直滑动
            if dy > 0:
                self.move(0)  # 上
            else:
                self.move(2)  # 下
        
        return super(Game2048, self).on_touch_up(touch)

from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
import os

# 主应用类
class Game2048App(App):
    def build(self):
        """构建应用"""
        # 设置窗口大小
        if platform != 'android' and platform != 'ios':
            Window.size = (400, 600)
        
        # 添加字体路径
        resource_add_path(os.path.abspath(os.path.dirname(__file__)))
        
        # 注册字体
        try:
            # 尝试使用系统自带的微软雅黑字体
            LabelBase.register('Roboto', 
                'C:/Windows/Fonts/msyh.ttc')  # 微软雅黑
        except:
            try:
                # 备选：尝试使用系统自带的宋体
                LabelBase.register('Roboto',
                    'C:/Windows/Fonts/simsun.ttc')  # 宋体
            except:
                print("警告：未能加载中文字体，中文可能无法正确显示")
        
        return Game2048()

# 运行应用
if __name__ == '__main__':
    Game2048App().run()
import pygame
import sys
import random

# 初始化Pygame
pygame.init()

# 设置窗口大小和网格大小
screen_width = 300
screen_height = 600
block_size = 30
grid_width = screen_width // block_size
grid_height = screen_height // block_size

# 创建游戏窗口
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('俄罗斯方块')

# 创建游戏网格
grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]

# 定义方块形状
shapes = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

# 定义颜色
colors = [
    (0, 255, 255),  # I
    (128, 0, 128),  # T
    (255, 0, 0),    # Z
    (0, 255, 0),    # S
    (255, 255, 0),  # O
    (255, 165, 0),  # L
    (0, 0, 255)     # J
]

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = colors[shapes.index(shape)]
        self.rotation = 0

    def get_shape(self):
        shape = self.shape
        if not isinstance(shape[0], list):
            return [shape]
        return shape

    def rotate(self):
        # 获取当前形状
        current_shape = self.get_shape()
        # 获取形状的行数和列数
        rows = len(current_shape)
        cols = len(current_shape[0])
        
        # 创建新的旋转后的形状
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        # 执行旋转（顺时针90度）
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows-1-r] = current_shape[r][c]
        
        # 保存旋转前的形状
        old_shape = self.shape
        # 尝试更新形状
        self.shape = rotated
        
        return old_shape

    def move_down(self):
        self.y += 1

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

def create_new_piece():
    return Piece(grid_width // 2 - 1, 0, random.choice(shapes))

def check_collision(piece, grid):
    shape = piece.get_shape()
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                new_y = piece.y + i
                new_x = piece.x + j
                if (new_y >= grid_height or  # 检查底部
                    new_x < 0 or  # 检查左边界
                    new_x >= grid_width or  # 检查右边界
                    (new_y >= 0 and grid[new_y][new_x])):  # 检查与其他方块的碰撞
                    return True
    return False

def lock_piece(piece, grid):
    shape = piece.get_shape()
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                if piece.y + i >= 0:  # 只在有位置锁定方块
                    grid[piece.y + i][piece.x + j] = piece.color

def draw_grid(screen, grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j]:
                pygame.draw.rect(screen, grid[i][j],
                               (j * block_size, i * block_size, block_size - 1, block_size - 1))

def clear_rows(grid):
    # 记录要删除的行
    rows_to_clear = []
    
    # 从底部向上检查每一行
    for i in range(len(grid)-1, -1, -1):
        if all(cell != 0 for cell in grid[i]):  # 如果一行都被填满
            rows_to_clear.append(i)
    
    # 删除完整的行并在顶部添加新的空行
    for row in rows_to_clear:
        del grid[row]
        grid.insert(0, [0 for _ in range(len(grid[0]))])

    return len(rows_to_clear)  # 返回消除的行数

# 创建游戏时钟
clock = pygame.time.Clock()
fall_time = 0
fall_speed = 0.05  # 每0.5秒下落一次
current_piece = create_new_piece()

# 主循环
running = True
while running:
    fall_time += clock.get_rawtime()
    clock.tick(60)

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 处理键盘事件
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                current_piece.move_left()
                if check_collision(current_piece, grid):
                    current_piece.move_right()
            
            elif event.key == pygame.K_RIGHT:
                current_piece.move_right()
                if check_collision(current_piece, grid):
                    current_piece.move_left()
            
            elif event.key == pygame.K_DOWN:
                current_piece.move_down()
                if check_collision(current_piece, grid):
                    current_piece.y -= 1
            
            elif event.key == pygame.K_UP:  # 添加旋转控制
                old_shape = current_piece.rotate()
                if check_collision(current_piece, grid):
                    current_piece.shape = old_shape  # 如果旋转后发生碰撞，恢复原来的形状

    # 自动下落
    if fall_time/1000 >= fall_speed:
        current_piece.move_down()
        fall_time = 0
        
        # 检查碰撞
        if check_collision(current_piece, grid):
            current_piece.y -= 1  # 回退一步
            lock_piece(current_piece, grid)  # 锁定方块
            clear_rows(grid)  # 清除完整的行
            current_piece = create_new_piece()  # 创建新方块
            
            # 如果新方块一出现就发生碰撞，说明游戏结束
            if check_collision(current_piece, grid):
                running = False

    # 填充背景颜色
    screen.fill((0, 0, 0))

    # 绘制已锁定的方块
    draw_grid(screen, grid)

    # 绘制当前方块
    shape = current_piece.get_shape()
    for i, row in enumerate(shape):
        for j, value in enumerate(row):
            if value:
                pygame.draw.rect(screen, current_piece.color, 
                               (current_piece.x * block_size + j * block_size, 
                                current_piece.y * block_size + i * block_size, 
                                block_size - 1, block_size - 1))

    # 更新显示
    pygame.display.flip()

# 退出Pygame
pygame.quit()
sys.exit()
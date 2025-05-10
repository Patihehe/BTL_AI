import random

def create_random_matrix(n):
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    
    # 4 hướng: (dy, dx)
    directions = {
        1: (-1, 0),  # UP
        2: (0, 1),   # RIGHT
        3: (1, 0),   # DOWN
        4: (0, -1),  # LEFT
    }
    
    def is_valid(x, y):
        return 0 <= x < n and 0 <= y < n and matrix[y][x] == 0
    
    x, y = 0, 0  # bắt đầu từ góc trên bên trái
    matrix[y][x] = 1  # bước đầu tiên
    count = 1
    t = 20 * n
    a = 1  # hướng ban đầu

    while count < t:
        # thực hiện bước đi hiện tại nếu có thể
        dy, dx = directions[a]
        new_x, new_y = x + dx, y + dy

        if is_valid(new_x, new_y):
            x, y = new_x, new_y
            count += 1
            matrix[y][x] = count
        else:
            # Nếu không đi được, phải chọn hướng khác (vẫn tránh hướng ngược lại)
            while True:
                b = random.randint(1, 4)
                if abs(b - a) != 2:
                    a = b
                    break
    return matrix

# In thử ma trận
def print_matrix(matrix):
    for row in matrix:
        print(' '.join(f"{cell:2d}" for cell in row))

# Ví dụ sử dụng
n = 4
random_matrix = create_random_matrix(n)
print_matrix(random_matrix)

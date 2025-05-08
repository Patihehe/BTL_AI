from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QSpinBox, QComboBox,
                            QFrame, QGroupBox, QProgressBar, QScrollArea, QSizePolicy, QBoxLayout, QGridLayout, QFormLayout)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QPixmap, QLinearGradient, QBrush, QFontDatabase, QPalette
import sys
import os
from .board_utils import create_random_start_board, create_goal_state
from .pattern_database import load_or_create_pdb
from .solver import ida_star
from .utils import print_solution
from .puzzle_state import PuzzleState

# Color palette and font settings
COLORS = {
    'primary': '#FF6F61',  # Coral Red for buttons
    'primary_dark': '#E63946',  # Darker Coral for hover
    'secondary': '#54D1A3',  # Mint Green for action buttons
    'secondary_dark': '#40C090',  # Darker Mint for hover
    'background_start': '#FCE4EC',  # Light Pink (gradient start)
    'background_end': '#E1BEE7',    # Light Purple (gradient end)
    'surface': '#FFFFFF',  # White for panels
    'text': '#4A4A4A',  # Dark Gray for text
    'text_secondary': '#78909C',  # Muted Gray for secondary text
    'border': '#D1C4E9',  # Light Purple for borders
    'empty_tile': '#ECEFF1',  # Light Gray for empty tiles
    'goal_tile': '#C8E6C9',  # Light Green for goal tiles
    'progress': '#81C784',  # Green for progress bar
    'tile_normal': '#B3E5FC',  # Light Blue for normal tiles
    'tile_accent': '#FFCCBC',  # Peach for tile accents
    'tile_shadow': '#B0BEC5',  # Gray for shadows
    'tile_text': '#1976D2',  # Deep Blue for tile numbers
    'highlight': '#FFF9C4',  # Light Yellow for highlights
}

FONT_FAMILY = 'Arial, Helvetica, sans-serif'
FONT_SIZE = {
    'small': 12,
    'medium': 16,
    'large': 18,
    'title': 24
}

class PuzzleTile(QWidget):
    def __init__(self, value, size, parent=None, is_goal=False):
        super().__init__(parent)
        self.value = value
        self.size = size
        self.is_goal = is_goal
        self.setFixedSize(size, size)
        self.original_pos = self.pos()
        self.animation = None
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, self.height())
        if self.value == 0:
            gradient.setColorAt(0, QColor(COLORS['empty_tile']))
            gradient.setColorAt(1, QColor(COLORS['empty_tile']).darker(120))
        else:
            if self.is_goal:
                gradient.setColorAt(0, QColor(COLORS['goal_tile']))
                gradient.setColorAt(1, QColor(COLORS['goal_tile']).darker(110))
            else:
                gradient.setColorAt(0, QColor(COLORS['tile_normal']))
                gradient.setColorAt(1, QColor(COLORS['tile_accent']))
        
        painter.setBrush(QBrush(QColor(COLORS['tile_shadow']).lighter(120)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(4, 4, self.width()-4, self.height()-4, 15, 15)

        painter.setBrush(QBrush(gradient))
        painter.setPen(QColor(COLORS['border']))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)

        if self.value != 0:
            painter.setPen(QColor(COLORS['tile_text']))
            font_size = max(16, min(32, self.size // 3))
            font = QFont(FONT_FAMILY, font_size, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.value))

    def animate_move(self, new_pos):
        if self.animation:
            self.animation.stop()
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(new_pos)
        self.animation.start()

class PuzzleBoard(QWidget):
    def __init__(self, N=4, is_goal=False):
        super().__init__()
        self.N = N
        self.is_goal = is_goal
        self.tiles = {}
        self.board = None
        self.solution = None
        self.current_step = 0
        self.setMinimumSize(320, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 3px solid {COLORS['border']};
                border-radius: 20px;
                padding: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
        """)

    def calculate_cell_size(self, available_size):
        min_cell_size = 30
        cell_size = min(self.width() // self.N, self.height() // self.N)
        cell_size = max(min_cell_size, cell_size)
        return cell_size

    def set_board(self, board, N=None):
        if N is not None and N != self.N:
            self.N = N
        self.board = board
        self.current_step = 0
        for tile in self.tiles.values():
            tile.setParent(None)
            tile.deleteLater()
        self.tiles.clear()
        self.update_tiles()

    def update_tiles(self):
        for tile in self.tiles.values():
            tile.setParent(None)
            tile.deleteLater()
        self.tiles.clear()
        if self.board is None:
            return
       
        cell_size = self.calculate_cell_size(self.size())
        total_size = cell_size * self.N
        x_offset = (self.width() - total_size) // 2
        y_offset = (self.height() - total_size) // 2
        for i in range(self.N):
            for j in range(self.N):
                value = self.board[i][j]
                tile = PuzzleTile(value, cell_size - 8, self, self.is_goal)
                tile.move(x_offset + j * cell_size + 4, y_offset + i * cell_size + 4)
                tile.setFixedSize(cell_size - 8, cell_size - 8)
                self.tiles[(i, j)] = tile
                tile.show()

    def showEvent(self, event):
        super().showEvent(event)
        if self.board is not None:
            self.update_tiles()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.board is not None:
            self.update_tiles()

    def animate_move(self, from_pos, to_pos):
        if from_pos in self.tiles and to_pos in self.tiles:
            from_tile = self.tiles[from_pos]
            to_tile = self.tiles[to_pos]
            
            self.tiles[from_pos], self.tiles[to_pos] = self.tiles[to_pos], self.tiles[from_pos]
            
            cell_size = self.calculate_cell_size(self.size())
            x_offset = (self.width() - cell_size * self.N) // 2
            y_offset = (self.height() - cell_size * self.N) // 2
            
            from_tile.animate_move(QPoint(x_offset + to_pos[1] * cell_size + 4, 
                                        y_offset + to_pos[0] * cell_size + 4))
            to_tile.animate_move(QPoint(x_offset + from_pos[1] * cell_size + 4, 
                                      y_offset + from_pos[0] * cell_size + 4))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("N-Puzzle Solver")
        self.setMinimumSize(900, 650)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8ffae,
                    stop:0.5 #a6c1ee,
                    stop:1 #43c6ac
                );
            }}
            QLabel, QGroupBox::title {{
                font-family: {FONT_FAMILY};
                color: #222;
                font-size: 18px;
                font-weight: 600;
            }}
            QPushButton {{
                font-family: {FONT_FAMILY};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a6c1ee, stop:1 #43c6ac);
                color: #191654;  /* Changed to a darker color for better contrast */
                border: none;
                border-radius: 16px;
                font-size: 20px;
                font-weight: 700;
                padding: 14px 0;
                margin: 10px 0;
                min-width: 120px;
                min-height: 44px;
                transition: all 0.2s;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #43c6ac, stop:1 #a6c1ee);
                color: #191654;  /* Ensure text remains visible on hover */
            }}
            QPushButton:pressed {{
                background: #a6c1ee;
                color: #191654;  /* Ensure text remains visible when pressed */
            }}
            QPushButton:disabled {{
                background: #d3d3d3;
                color: #808080;  /* Gray text for disabled state */
            }}
            QSpinBox, QComboBox {{
                font-family: {FONT_FAMILY};
                border: 2px solid #d1c4e9;
                border-radius: 12px;
                background: #fff;
                font-size: 18px;
                padding: 8px 16px;
                min-width: 90px;
            }}
            QSpinBox:focus, QComboBox:focus {{
                border: 2px solid #a6c1ee;
            }}
            QProgressBar {{
                border: none;
                border-radius: 12px;
                background: #e0eafc;
                height: 28px;
                font-size: 16px;
                color: #333;
                margin-top: 10px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #43c6ac, stop:1 #191654);
                border-radius: 12px;
                transition: width 0.3s;
            }}
            QLabel#title {{
                font-size: 36px;
                font-weight: 900;
                color: #191654;
                letter-spacing: 2px;
                text-shadow: 2px 2px 8px #fff, 0 2px 8px #43c6ac44;
                margin-bottom: 22px;
            }}
        """)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        
        main_widget = QWidget()
        main_widget.setMinimumWidth(900)
        main_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(scroll_area)
        scroll_area.setWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("🧩 N-Puzzle Solver")
        header.setObjectName("title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        self.content_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        main_layout.addLayout(self.content_layout)

        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_panel.setMinimumWidth(180)
        left_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        left_panel.setStyleSheet("""
            background: #fff;
            border-radius: 24px;
            border: 2px solid #d1c4e9;
            box-shadow: 0 4px 18px 0 rgba(100, 100, 180, 0.10);
            padding: 14px 8px 14px 8px;
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(14)

        # Khởi tạo trước khi add vào form_layout
        self.size_spin = QSpinBox()
        self.size_spin.setRange(3, 8)
        self.size_spin.setValue(4)
        self.size_spin.valueChanged.connect(self.on_size_changed)
        self.size_spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.heuristic_combo = QComboBox()
        self.heuristic_combo.addItems(['manhattan', 'misplaced', 'linear_conflict', 'pdb'])
        self.heuristic_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        control_group = QGroupBox("🎮 Controls")
        control_group_layout = QVBoxLayout(control_group)
        control_group_layout.setSpacing(14)
        control_group_layout.setContentsMargins(12, 18, 12, 12)

        # Sử dụng QFormLayout cho phần chọn input
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow(QLabel("Board Size:"), self.size_spin)
        form_layout.addRow(QLabel("Heuristic:"), self.heuristic_combo)
        control_group_layout.addLayout(form_layout)

        # Chỉ thêm các nút thực sự cần thiết
        self.new_board_btn = QPushButton("🎲 New Board")
        self.new_board_btn.setObjectName("actionButton")
        self.new_board_btn.clicked.connect(self.create_new_board)
        self.new_board_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.new_board_btn.setMinimumWidth(130)

        self.solve_btn = QPushButton("🧠 Solve")
        self.solve_btn.setObjectName("actionButton")
        self.solve_btn.clicked.connect(self.solve_puzzle)
        self.solve_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.solve_btn.setMinimumWidth(130)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addWidget(self.new_board_btn)
        btn_layout.addWidget(self.solve_btn)
        control_group_layout.addLayout(btn_layout)

        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        self.prev_step_btn = QPushButton("⬅ Previous")
        self.prev_step_btn.clicked.connect(self.prev_step)
        self.prev_step_btn.setEnabled(False)
        self.prev_step_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.prev_step_btn.setMinimumWidth(110)
        nav_layout.addWidget(self.prev_step_btn)

        self.next_step_btn = QPushButton("Next ➡")
        self.next_step_btn.clicked.connect(self.next_step)
        self.next_step_btn.setEnabled(False)
        self.next_step_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.next_step_btn.setMinimumWidth(110)
        nav_layout.addWidget(self.next_step_btn)
        control_group_layout.addLayout(nav_layout)

        left_layout.addWidget(control_group)

        info_group = QGroupBox("📊 Information")
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(10)
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)

        # Khởi tạo label trước khi add vào form_info
        self.steps_label = QLabel("0")
        self.nodes_label = QLabel("0")

        form_info = QFormLayout()
        form_info.setSpacing(8)
        form_info.addRow(QLabel("Steps:"), self.steps_label)
        form_info.addRow(QLabel("Nodes visited:"), self.nodes_label)
        info_layout.addLayout(form_info)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        info_layout.addWidget(self.progress_bar)

        left_layout.addWidget(info_group)
        left_layout.addStretch()

        right_panel = QWidget()
        right_panel.setMinimumSize(500, 700)
        right_panel.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(28)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        current_label = QLabel("🎯 Current State")
        current_label.setObjectName("title")
        current_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        current_label.setStyleSheet(f"font-size: 26px; font-family: {FONT_FAMILY}; font-weight: 800; color: #191654;")
        right_layout.addWidget(current_label)
        
        self.puzzle_board = PuzzleBoard()
        right_layout.addWidget(self.puzzle_board, alignment=Qt.AlignmentFlag.AlignHCenter)

        goal_label = QLabel("🏁 Goal State")
        goal_label.setObjectName("title")
        goal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        goal_label.setStyleSheet(f"font-size: 26px; font-family: {FONT_FAMILY}; font-weight: 800; color: #191654;")
        right_layout.addWidget(goal_label)
        
        self.goal_board = PuzzleBoard(is_goal=True)
        right_layout.addWidget(self.goal_board, alignment=Qt.AlignmentFlag.AlignHCenter)
        right_layout.addStretch()

        self.content_layout.addWidget(left_panel)
        self.content_layout.addWidget(right_panel, stretch=2)

        self.current_board = None
        self.solution_path = None
        self.pdb = None

        self.create_new_board()

    def resizeEvent(self, event):
        if self.puzzle_board and self.goal_board:
            self.puzzle_board.update_tiles()
            self.goal_board.update_tiles()
        if self.width() < 900:
            self.content_layout.setDirection(QBoxLayout.Direction.TopToBottom)
            self.set_groupbox_padding(8)
        else:
            self.content_layout.setDirection(QBoxLayout.Direction.LeftToRight)
            self.set_groupbox_padding(20)
        super().resizeEvent(event)

    def set_groupbox_padding(self, padding):
        style = f"""
            QGroupBox {{
                background: #fafaff;
                border: 2px solid #d1c4e9;
                border-radius: 22px;
                margin-top: 22px;
                padding: {padding}px;
                box-shadow: 0 4px 18px 0 rgba(100, 100, 180, 0.10);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 18px;
                padding: 10px 22px;
                background: #fffbe7;
                color: #222;
                border-radius: 10px;
                font-size: 20px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
        """
        for gb in self.findChildren(QGroupBox):
            gb.setStyleSheet(style)

    def on_size_changed(self, value):
        self.create_new_board()

    def create_new_board(self):
        N = self.size_spin.value()
        self.current_board = create_random_start_board(N)
        self.puzzle_board.set_board(self.current_board, N)
        
        goal_board = create_goal_state(N)
        self.goal_board.set_board(goal_board, N)
        
        self.info_label.setText("New board created! Let's solve it!")
        self.solution_path = None
        self.next_step_btn.setEnabled(False)
        self.prev_step_btn.setEnabled(False)
        self.steps_label.setText("0")
        self.nodes_label.setText("0")
        self.progress_bar.setValue(0)
        
        QTimer.singleShot(0, self.puzzle_board.update_tiles)
        QTimer.singleShot(0, self.goal_board.update_tiles)

    def is_solvable(self, board, N):
        """Check if the puzzle is solvable by counting inversions."""
        flat_board = [num for row in board for num in row if num != 0]
        inversions = 0
        for i in range(len(flat_board)):
            for j in range(i + 1, len(flat_board)):
                if flat_board[i] > flat_board[j]:
                    inversions += 1
        
        blank_row_from_bottom = None
        for i in range(N):
            for j in range(N):
                if board[i][j] == 0:
                    blank_row_from_bottom = N - i
                    break
            if blank_row_from_bottom is not None:
                break

        if N % 2 == 1:
            return inversions % 2 == 0
        else:
            return (inversions + blank_row_from_bottom - 1) % 2 == 0

    def solve_puzzle(self):
        if self.current_board is None:
            self.info_label.setText("No board to solve!")
            return

        # Reset the state before solving
        self.solution_path = None
        self.puzzle_board.current_step = 0
        self.next_step_btn.setEnabled(False)
        self.prev_step_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.steps_label.setText("0")
        self.nodes_label.setText("0")
        self.info_label.setText("Solving puzzle...")
        QApplication.processEvents()

        N = self.size_spin.value()
        heuristic = self.heuristic_combo.currentText()

        # Check if the puzzle is solvable
        if not self.is_solvable(self.current_board, N):
            self.info_label.setText("This puzzle is not solvable! Try a new board. 😅")
            self.next_step_btn.setEnabled(False)
            self.prev_step_btn.setEnabled(False)
            self.progress_bar.setValue(0)
            return

        if heuristic == 'pdb':
            tiles = [1, 2, 3, 4]
            self.pdb = load_or_create_pdb(N, tiles, f"pdb_{N}_{'_'.join(map(str, tiles))}.pkl")
        else:
            self.pdb = None

        self.progress_bar.setValue(50)
        QApplication.processEvents()
        
        PuzzleState.nodes_visited = 0
        solution, steps = ida_star(self.current_board, N, heuristic, self.pdb)
        
        if solution:
            self.solution_path = []
            current = solution
            while current:
                self.solution_path.append(current)
                current = current.parent
            self.solution_path.reverse()
            
            print(f"Solution path length: {len(self.solution_path)}")
            for i, state in enumerate(self.solution_path):
                print(f"Step {i}: {state.board}")

            self.puzzle_board.current_step = 0
            self.puzzle_board.board = [row[:] for row in self.solution_path[0].board]
            self.puzzle_board.update_tiles()

            total_steps = len(self.solution_path) - 1
            self.info_label.setText(f"Solution found! Navigate using Next/Previous. 🎉")
            self.steps_label.setText(str(total_steps))
            self.nodes_label.setText(f"{PuzzleState.nodes_visited}")
            self.next_step_btn.setEnabled(True)
            self.prev_step_btn.setEnabled(False)
            self.progress_bar.setValue(0)  # Start at 0%, update as user steps through
        else:
            self.info_label.setText("No solution found. Try again! 😅")
            self.next_step_btn.setEnabled(False)
            self.prev_step_btn.setEnabled(False)
            self.progress_bar.setValue(0)

    def prev_step(self):
        if not self.solution_path or self.puzzle_board.current_step <= 0:
            self.info_label.setText("No previous step available")
            self.prev_step_btn.setEnabled(False)
            return

        current_state = self.solution_path[self.puzzle_board.current_step]
        next_state = self.solution_path[self.puzzle_board.current_step - 1]
        
        blank_before = None
        blank_after = None
        for i in range(self.size_spin.value()):
            for j in range(self.size_spin.value()):
                if current_state.board[i][j] == 0:
                    blank_before = (i, j)
                if next_state.board[i][j] == 0:
                    blank_after = (i, j)

        self.puzzle_board.animate_move(blank_before, blank_after)
        
        self.puzzle_board.current_step -= 1
        self.puzzle_board.board = [row[:] for row in next_state.board]
        self.puzzle_board.update_tiles()
        
        total_steps = len(self.solution_path) - 1
        self.info_label.setText(f"Step {self.puzzle_board.current_step} of {total_steps}")
        self.progress_bar.setValue(int((self.puzzle_board.current_step / total_steps) * 100))
        
        self.next_step_btn.setEnabled(True)
        if self.puzzle_board.current_step == 0:
            self.prev_step_btn.setEnabled(False)

    def next_step(self):
        if not self.solution_path:
            self.info_label.setText("No solution available")
            self.next_step_btn.setEnabled(False)
            return

        if self.puzzle_board.current_step >= len(self.solution_path) - 1:
            self.info_label.setText("Solution completed! 🎊")
            self.next_step_btn.setEnabled(False)
            return

        current_state = self.solution_path[self.puzzle_board.current_step]
        next_state = self.solution_path[self.puzzle_board.current_step + 1]
        
        blank_before = None
        blank_after = None
        for i in range(self.size_spin.value()):
            for j in range(self.size_spin.value()):
                if current_state.board[i][j] == 0:
                    blank_before = (i, j)
                if next_state.board[i][j] == 0:
                    blank_after = (i, j)

        self.puzzle_board.animate_move(blank_before, blank_after)
        
        self.puzzle_board.current_step += 1
        self.puzzle_board.board = [row[:] for row in next_state.board]
        self.puzzle_board.update_tiles()
        
        total_steps = len(self.solution_path) - 1
        self.info_label.setText(f"Step {self.puzzle_board.current_step} of {total_steps}")
        self.progress_bar.setValue(int((self.puzzle_board.current_step / total_steps) * 100))
        
        self.prev_step_btn.setEnabled(True)
        if self.puzzle_board.current_step >= len(self.solution_path) - 1:
            self.next_step_btn.setEnabled(False)

def run_gui():
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 12))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
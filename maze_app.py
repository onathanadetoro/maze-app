import streamlit as st
import numpy as np
import random

# Configure the Streamlit page layout
st.set_page_config(page_title="Interactive Maze Solver", layout="centered")

# ==========================================
# STEP 1: BASE FUNDAMENTALS (Maze Generator)
# ==========================================
def generate_maze(size):
    """
    Generates a solvable maze using the Recursive Backtracking algorithm.
    '0' represents a path, and '1' represents a wall.
    """
    maze = np.ones((size, size), dtype=int)  # Start with a grid of walls
    visited = set()

    def carve(x, y):
        # Mark the current cell as visited and carve a path
        maze[x, y] = 0
        visited.add((x, y))

        # Shuffle directions to add randomness
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size and (nx, ny) not in visited:
                # Carve through the wall
                maze[x + dx // 2, y + dy // 2] = 0
                carve(nx, ny)

    # Start carving from the top-left corner
    carve(0, 0)

    # Ensure start and end points are open
    maze[0, 0] = 0
    maze[size - 1, size - 1] = 0
    return maze

# ==========================================
# STEP 2: BASE FUNDAMENTALS (BFS Solver)
# ==========================================
def solve_maze(maze):
    """
    Solves the maze using BFS to find the shortest path from start to end.
    Returns the path as a list of coordinates.
    """
    size = len(maze)
    queue = [(0, 0)]  # Use a plain list as a queue for BFS
    visited = set([(0, 0)])  # Set of visited nodes
    parent = {}  # To reconstruct the path

    # Directions for moving in the maze
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        x, y = queue.pop(0)  # Pop the first element (FIFO behavior)

        # If we've reached the end, reconstruct the path
        if (x, y) == (size - 1, size - 1):
            path = []
            while (x, y) in parent:
                path.append((x, y))
                x, y = parent[(x, y)]
            path.append((0, 0))
            return path[::-1]

        # Explore neighbors
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size and maze[nx, ny] == 0 and (nx, ny) not in visited:
                queue.append((nx, ny))
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)

    return []  # Return an empty path if no solution

# ==========================================
# STEP 3: STREAMLIT LOGIC & UI
# ==========================================

def initialize_game(size):
    """Resets the game state with a new maze."""
    st.session_state.maze = generate_maze(size)
    st.session_state.path = [(0, 0)]
    st.session_state.game_over = False
    st.session_state.auto_solved = False

def handle_click(x, y):
    """Callback triggered when the user clicks a square."""
    if st.session_state.game_over or st.session_state.auto_solved:
        return

    current_path = st.session_state.path
    last_x, last_y = current_path[-1]

    # Check if clicking on the last visited cell (allows backtracking/undo)
    if len(current_path) > 1 and (x, y) == current_path[-2]:
        current_path.pop()
    # Check if moving to an adjacent, open cell
    elif abs(x - last_x) + abs(y - last_y) == 1:
        if st.session_state.maze[x, y] == 0:
            current_path.append((x, y))
    
    # Check win condition
    size = len(st.session_state.maze)
    if current_path[-1] == (size - 1, size - 1):
        st.session_state.game_over = True

def main():
    st.title("Interactive Maze 🧩")
    st.markdown("Navigate from the top-left to the bottom-right! **Click adjacent squares to move.**")

    # --- Sidebar Controls ---
    with st.sidebar:
        st.header("Settings")
        # Keep maximum reasonable so rendering Streamlit columns isn't too slow
        size = st.number_input("Maze Size", min_value=5, max_value=21, value=11, step=2)
        
        if st.button("Generate New Maze", type="primary"):
            initialize_game(size)
            
        st.divider()
        if st.button("I give up. Solve it for me!"):
            if 'maze' in st.session_state:
                st.session_state.path = solve_maze(st.session_state.maze)
                st.session_state.auto_solved = True
                st.session_state.game_over = True

    # --- Initialize Session State ---
    if 'maze' not in st.session_state:
        initialize_game(11)

    maze = st.session_state.maze
    path = st.session_state.path
    size = len(maze)

    # --- Win Condition Messages ---
    if st.session_state.game_over:
        if st.session_state.auto_solved:
            st.info("The computer has solved the maze for you!")
        else:
            st.success("🎉 You solved the maze! Congratulations!")

    # --- Custom CSS for uniform Grid ---
    st.markdown(
        """
        <style>
        /* Force buttons to be square and strip extra padding */
        .stButton > button {
            height: 40px;
            width: 100%;
            padding: 0px;
            font-size: 20px;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # --- Render the Interactive Maze Grid ---
    for i in range(size):
        cols = st.columns(size)
        for j in range(size):
            with cols[j]:
                if maze[i, j] == 1:
                    # It's a Wall
                    st.button("⬛", key=f"wall_{i}_{j}", disabled=True)
                else:
                    # It's a Path
                    if (i, j) == (size - 1, size - 1) and (i, j) not in path:
                        # Goal
                        st.button("🏆", key=f"btn_{i}_{j}", on_click=handle_click, args=(i, j))
                    elif (i, j) in path:
                        if (i, j) == path[-1] and not st.session_state.auto_solved:
                            # Current Player Location
                            st.button("📍", key=f"btn_{i}_{j}", on_click=handle_click, args=(i, j))
                        else:
                            # Traversed Path
                            st.button("🟦", key=f"btn_{i}_{j}", on_click=handle_click, args=(i, j))
                    else:
                        # Unexplored Path
                        st.button("⬜", key=f"btn_{i}_{j}", on_click=handle_click, args=(i, j))

if __name__ == "__main__":
    main()
import streamlit as st
import random
import matplotlib.pyplot as plt
import numpy as np

# Step 1: Define the maze generator using Recursive Backtracking
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

# Step 2: Define the maze solver using Breadth-First Search (BFS)
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

# Step 3: Visualize the maze with enhanced features
def plot_maze(maze, path=[]):
    """
    Plots the maze and optionally displays the solution path.
    Adapted for Streamlit by rendering to a Figure.
    """
    size = len(maze)
    color_maze = np.ones_like(maze, dtype=float)  # Walls are white
    color_maze[maze == 0] = 0.7  # Paths are light gray

    # Mark the solution path
    for (x, y) in path:
        color_maze[x, y] = 0.5  # Path color (darker gray)

    # Start and end points
    color_maze[0, 0] = 0.25  # Start point
    color_maze[size - 1, size - 1] = 0.75  # End point

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(color_maze, cmap='gray', origin='upper')
    ax.set_title("Start (Dark Gray) ➡️ End (Light Gray)\nYour Path (Medium Gray)")
    ax.axis("off")
    st.pyplot(fig)

# Step 4: Streamlit Interactive UI
def main_code():
    st.set_page_config(page_title="Interactive Maze", layout="centered")
    st.title("Interactive Maze Solver")
    
    # Sidebar for Game Controls
    with st.sidebar:
        st.header("Settings")
        size = st.number_input("Enter maze size (minimum 4):", min_value=4, value=8, step=1)
        
        if st.button("Generate New Maze"):
            st.session_state.maze = generate_maze(size)
            st.session_state.path = [(0, 0)]
            st.session_state.game_over = False

    # Initialize session state if it doesn't exist
    if 'maze' not in st.session_state:
        st.session_state.maze = generate_maze(size)
        st.session_state.path = [(0, 0)]
        st.session_state.game_over = False

    maze = st.session_state.maze
    path = st.session_state.path
    current_size = len(maze)
    current_x, current_y = path[-1]

    # Draw the maze with the player's current path
    plot_maze(maze, path)

    # Check for win condition
    if current_x == current_size - 1 and current_y == current_size - 1:
        if not st.session_state.get('game_over', False):
            st.success("🎉 Congratulations! You solved the maze!")
            st.balloons()
            st.session_state.game_over = True
    else:
        st.write("### Where to next?")
        st.write(f"**Current Position:** Row {current_x}, Col {current_y}")
        
        # Determine valid moves
        directions = {"Down ⬇️": (1, 0), "Up ⬆️": (-1, 0), "Right ➡️": (0, 1), "Left ⬅️": (0, -1)}
        cols = st.columns(4)
        col_idx = 0
        
        for name, (dx, dy) in directions.items():
            nx, ny = current_x + dx, current_y + dy
            
            # If the neighbor is within bounds and is a path (0)
            if 0 <= nx < current_size and 0 <= ny < current_size and maze[nx, ny] == 0:
                # Check if it's a step backward (allow undoing a step)
                if len(path) > 1 and (nx, ny) == path[-2]:
                    with cols[col_idx]:
                        if st.button(f"Go Back ({name})"):
                            st.session_state.path.pop()
                            st.rerun()
                # Otherwise, it's a new valid step forward
                elif (nx, ny) not in path:
                    with cols[col_idx]:
                        if st.button(f"Move {name}"):
                            st.session_state.path.append((nx, ny))
                            st.rerun()
                
                col_idx = (col_idx + 1) % 4

        st.markdown("---")
        if st.button("I give up! Show me the solution."):
            st.session_state.path = solve_maze(maze)
            st.session_state.game_over = True
            st.rerun()

# Run the program
if __name__ == "__main__":
    main_code()
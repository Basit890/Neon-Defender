# Neon-Defender
A 3D first-person shooter game built with Python and PyOpenGL. Players navigate an arena, defending against red/blue drones and tanks while collecting shields and medboxes to survive. Features include dynamic spawning, collision detection, and a HUD displaying health, score, and time survived.

 ## Features
 - First-person and third-person views (toggle with 'v')
 - WASD movement, mouse aiming, spacebar shooting
 - Enemies: Red drones (low health), blue drones (aimed shots), tanks (high damage)
 - Power-ups: Shields (5s protection), medboxes (health boost)
 - Scoring: +10 for red drones, +100 for blue drones, +50 for tanks
 - Pause ('p'), exit ('q' or 'esc')

 ## Prerequisites
 - Python 3.6+
 - PyOpenGL, PyOpenGL_accelerate, numpy
 - FreeGLUT (OpenGL Utility Toolkit)

 ## Installation
 1. Clone the repository:
    ```bash
    git clone https://github.com/Basit890/NeonDefender.git
    cd NeonDefender
    ```
 2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
 3. Install FreeGLUT:
    - Windows: Download `freeglut.dll` and place in the project folder or `C:\Windows\System32`
    - Linux: `sudo apt-get install freeglut3-dev`
    - Mac: `brew install freeglut`
 4. Run the game:
    ```bash
    python neon_defender.py
    ```

 ## Controls
 - **WASD**: Move
 - **Mouse**: Aim
 - **Space**: Shoot
 - **V**: Toggle first/third-person view
 - **P**: Pause
 - **Q/Esc**: Quit

 ## Game Mechanics
 - Arena size: 100x100
 - Player health: 100 max, reduced by enemy bullets
 - Gun level: Increases every 100 points, boosting bullet damage
 - Spawning: Tanks/red drones every 5s, blue drones/medboxes/shields every 10s
 - Max entities: 10

 ## License
 MIT License

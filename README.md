# Feature-Based Image Metamorphosis

Implementation of the Beier & Neely (1992) SIGGRAPH paper "Feature-Based Image Metamorphosis".

## Project Structure

```
hw2/
├── main.py              # Main GUI application
├── morph_algorithm.py   # Core morphing algorithms
├── ui_helpers.py        # UI utility functions
├── animations.py        # Animation functions
└── README.md           # This file
```

## Modules

### `morph_algorithm.py`
Core morphing implementation:
- `compute_uv()` - Calculate u,v coordinates relative to lines
- `compute_X_prime()` - Map coordinates between images
- `warp_image_with_lines()` - Main warping algorithm
- `interpolate_lines()` - Interpolate between line sets
- `blend_images()` - Alpha blend two images

### `ui_helpers.py`
UI helper functions:
- `display_image_on_canvas()` - Display images on tkinter canvas
- `draw_arrow_on_canvas()` - Draw numbered arrows for feature lines
- `redraw_canvas_with_lines()` - Redraw canvas with all lines
- `scale_lines_to_image()` - Convert canvas coordinates to image coordinates

### `animations.py`
Animation functions:
- `create_warp_animation()` - 2-image ping-pong animation
- `create_sequential_animation()` - 3-image sequential animation

### `main.py`
Main application with GUI:
- Interactive line drawing
- 2-image and 3-image modes
- Real-time morphing
- Animation playback

## Features

### 2-Image Mode
- Load two images
- Draw corresponding line pairs (alternating between images)
- Set alpha value for morphing
- View warped images and blended result
- Play ping-pong animation (0→1→0)

### 3-Image Mode
- Load three images
- Draw line triplets in sequence (1→2→3)
- Play sequential animation (1→2→3 and reverse)
- Smooth transitions between all three images

### Controls
- **Mode Toggle**: Switch between 2-image and 3-image modes
- **Open Image 1/2/3**: Load images
- **Clear Lines**: Reset all drawn lines
- **Set Alpha and Run**: Single-frame morph (2-image mode only)
- **Warp Animation**: Ping-pong animation (2-image mode)
- **Sequential Animation**: Sequential morphing (3-image mode)
- **ESC**: Stop current animation

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Select mode (2-image or 3-image)

3. Load images using the "Open Image" buttons

4. Draw feature lines by clicking and dragging on images
   - 2-image mode: Alternates between Image 1 and Image 2
   - 3-image mode: Sequence goes Image 1 → Image 2 → Image 3

5. Run morphing or animation:
   - Set alpha value and click "Set Alpha and Run" for single frame
   - Click "Warp Animation" for 2-image ping-pong
   - Click "Sequential Animation" for 3-image sequence

## Algorithm Details

Based on Beier & Neely's field morphing approach:
- Uses feature lines instead of mesh
- Weighted displacement calculation
- Reverse mapping with bilinear interpolation
- Default parameters: a=0.01, b=2.0, p=0.0

## Requirements

- Python 3.x
- tkinter (usually included with Python)
- PIL/Pillow
- NumPy




"""
UI Helper Functions for Image Morphing Application
"""

import tkinter as tk
from PIL import Image, ImageTk


def display_image_on_canvas(image, canvas, canvas_width=400, canvas_height=300):
    """
    Display an image on a canvas with proper scaling.
    
    Args:
        image: PIL Image to display
        canvas: tkinter Canvas widget
        canvas_width: Width of canvas
        canvas_height: Height of canvas
    """
    # Resize image to fit canvas
    img_resized = image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img_resized)
    
    canvas.delete("all")
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.image = photo  # Keep reference


def draw_arrow_on_canvas(canvas, p, q, line_number):
    """
    Draw an arrow from P to Q with line number on canvas.
    
    Args:
        canvas: tkinter Canvas widget
        p: Start point (x, y)
        q: End point (x, y)
        line_number: Number to display on the line
    """
    px, py = p
    qx, qy = q
    
    # Draw line with arrow
    canvas.create_line(px, py, qx, qy, fill="red", width=2, arrow=tk.LAST, arrowshape=(10, 12, 5))
    
    # Draw line number at midpoint
    mid_x = (px + qx) / 2
    mid_y = (py + qy) / 2
    canvas.create_text(mid_x, mid_y - 10, text=str(line_number), fill="yellow", 
                      font=("Arial", 12, "bold"), tags="line_number")
    
    # Draw circles at endpoints
    canvas.create_oval(px-3, py-3, px+3, py+3, fill="green", outline="white")
    canvas.create_oval(qx-3, qy-3, qx+3, qy+3, fill="blue", outline="white")


def redraw_canvas_with_lines(canvas, image, lines, canvas_width=400, canvas_height=300, is_active=False):
    """
    Redraw canvas with image and all lines.
    
    Args:
        canvas: tkinter Canvas widget
        image: PIL Image to display
        lines: List of line tuples [((p_x, p_y), (q_x, q_y)), ...]
        canvas_width: Width of canvas
        canvas_height: Height of canvas
        is_active: Whether to highlight this canvas as active
    """
    if image is None:
        return
    
    # Display image
    display_image_on_canvas(image, canvas, canvas_width, canvas_height)
    
    # Draw all lines
    for i, (p, q) in enumerate(lines):
        draw_arrow_on_canvas(canvas, p, q, i + 1)
    
    # Highlight active canvas
    if is_active:
        canvas.config(highlightbackground="green", highlightthickness=3)
    else:
        canvas.config(highlightbackground="black", highlightthickness=1)


def scale_lines_to_image(lines_canvas, canvas_width, canvas_height, image_width, image_height):
    """
    Scale lines from canvas coordinates to image coordinates.
    
    Args:
        lines_canvas: Lines in canvas coordinates
        canvas_width: Width of canvas
        canvas_height: Height of canvas
        image_width: Width of actual image
        image_height: Height of actual image
    
    Returns:
        Lines scaled to image coordinates
    """
    scale_x = image_width / canvas_width
    scale_y = image_height / canvas_height
    
    lines_scaled = []
    for (p, q) in lines_canvas:
        p_scaled = (p[0] * scale_x, p[1] * scale_y)
        q_scaled = (q[0] * scale_x, q[1] * scale_y)
        lines_scaled.append((p_scaled, q_scaled))
    
    return lines_scaled




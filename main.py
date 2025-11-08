"""
Feature-Based Image Metamorphosis Application
Main GUI Application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Canvas
from PIL import Image
import math

# Import our modular components
from morph_algorithm import (warp_image_with_lines, interpolate_lines, blend_images, 
                             generate_grid, warp_grid_points, merge_multiple_images)
from ui_helpers import display_image_on_canvas, redraw_canvas_with_lines, scale_lines_to_image, display_image_with_grid_overlay


def main():
    # Create the main window
    root = tk.Tk()
    root.title("Feature-Based Image Metamorphosis")
    root.geometry("1800x1100")
    
    # Create main frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title label
    title_label = ttk.Label(main_frame, text="Feature-Based Image Metamorphosis", font=("Arial", 16, "bold"))
    title_label.pack(pady=(0, 10))
    
    # ==================== STATE VARIABLES ====================
    
    # Image variables
    image1_path = None
    image2_path = None
    image3_path = None
    image1_original = None
    image2_original = None
    image3_original = None
    
    # Mode control: 2-image or 3-image mode
    is_three_image_mode = False
    
    # Line storage
    lines_image1 = []
    lines_image2 = []
    lines_image3 = []
    
    # Drawing state
    current_line_start = None
    expecting_image_num = 1  # Which image we're expecting a line on (1, 2, or 3)
    
    # Canvas dimensions
    CANVAS_WIDTH = 400
    CANVAS_HEIGHT = 300
    
    # ==================== UI COMPONENTS ====================
    
    # Status section at top
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill=tk.X, pady=(0, 10))
    
    status_label = ttk.Label(status_frame, text="Ready - Select mode and load images", font=("Arial", 10))
    status_label.pack(side=tk.LEFT)
    
    instruction_label = ttk.Label(status_frame, text="", font=("Arial", 10, "bold"), foreground="blue")
    instruction_label.pack(side=tk.LEFT, padx=(20, 0))
    
    # Image selection section
    image_frame = ttk.LabelFrame(main_frame, text="Image Selection", padding="10")
    image_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Mode toggle button
    def toggle_mode():
        nonlocal is_three_image_mode
        if not is_three_image_mode:
            is_three_image_mode = True
            mode_button.config(text="Mode: 3 Images")
            status_label.config(text="3-image mode: Load all 3 images and draw lines in sequence (1→2→3)")
        else:
            is_three_image_mode = False
            mode_button.config(text="Mode: 2 Images")
            status_label.config(text="2-image mode: Load 2 images and draw line pairs (1↔2)")
        clear_lines()
    
    mode_button = ttk.Button(image_frame, text="Mode: 2 Images", command=toggle_mode)
    mode_button.pack(side=tk.LEFT, padx=(0, 20))
    
    btn_image1 = ttk.Button(image_frame, text="Open Image 1")
    btn_image1.pack(side=tk.LEFT, padx=(0, 10))
    
    btn_image2 = ttk.Button(image_frame, text="Open Image 2")
    btn_image2.pack(side=tk.LEFT, padx=(0, 10))
    
    btn_image3 = ttk.Button(image_frame, text="Open Image 3")
    btn_image3.pack(side=tk.LEFT, padx=(0, 10))
    
    btn_clear_lines = ttk.Button(image_frame, text="Clear Lines")
    btn_clear_lines.pack(side=tk.LEFT, padx=(20, 0))
    
    # Canvas section for interactive drawing
    canvas_frame = ttk.LabelFrame(main_frame, text="Draw Feature Lines (Click and Drag)", padding="10")
    canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    canvas_container = ttk.Frame(canvas_frame)
    canvas_container.pack(fill=tk.BOTH, expand=True)
    
    # Image 1 canvas
    canvas1_frame = ttk.Frame(canvas_container)
    canvas1_frame.pack(side=tk.LEFT, padx=(0, 10))
    
    canvas1_title = ttk.Label(canvas1_frame, text="Image 1", font=("Arial", 12, "bold"))
    canvas1_title.pack()
    
    canvas1 = Canvas(canvas1_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="gray")
    canvas1.pack()
    
    # Image 2 canvas
    canvas2_frame = ttk.Frame(canvas_container)
    canvas2_frame.pack(side=tk.LEFT, padx=(0, 10))
    
    canvas2_title = ttk.Label(canvas2_frame, text="Image 2", font=("Arial", 12, "bold"))
    canvas2_title.pack()
    
    canvas2 = Canvas(canvas2_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="gray")
    canvas2.pack()
    
    # Image 3 canvas
    canvas3_frame = ttk.Frame(canvas_container)
    canvas3_frame.pack(side=tk.LEFT)
    
    canvas3_title = ttk.Label(canvas3_frame, text="Image 3", font=("Arial", 12, "bold"))
    canvas3_title.pack()
    
    canvas3 = Canvas(canvas3_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="gray")
    canvas3.pack()
    
    # Alpha and action controls
    control_frame = ttk.LabelFrame(main_frame, text="Morphing Controls", padding="10")
    control_frame.pack(fill=tk.X, pady=(0, 10))
    
    ttk.Label(control_frame, text="Alpha (0.0 - 1.0):").pack(side=tk.LEFT, padx=(0, 10))
    alpha_var = tk.StringVar(value="0.5")
    alpha_entry = ttk.Entry(control_frame, textvariable=alpha_var, width=10)
    alpha_entry.pack(side=tk.LEFT, padx=(0, 10))
    
    btn_set_alpha = ttk.Button(control_frame, text="Set Alpha and Run")
    btn_set_alpha.pack(side=tk.LEFT, padx=(20, 10))
    
    btn_warp_anim = ttk.Button(control_frame, text="Warp Animation")
    btn_warp_anim.pack(side=tk.LEFT, padx=(0, 10))
    
    btn_seq_anim = ttk.Button(control_frame, text="Sequential Animation")
    btn_seq_anim.pack(side=tk.LEFT)
    
    # Grid visualization toggle
    show_grid_var = tk.BooleanVar(value=False)
    grid_checkbox = ttk.Checkbutton(control_frame, text="Show Grid Visualization", 
                                    variable=show_grid_var)
    grid_checkbox.pack(side=tk.LEFT, padx=(20, 0))
    
    # Barycentric merge controls
    merge_frame = ttk.LabelFrame(main_frame, text="Multiple Image Merge (Barycentric Blending)", padding="10")
    merge_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Weight sliders
    weights_container = ttk.Frame(merge_frame)
    weights_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    ttk.Label(weights_container, text="Barycentric Weights (t₁, t₂, t₃):").pack(side=tk.LEFT, padx=(0, 10))
    
    # Weight 1 (t1)
    ttk.Label(weights_container, text="t₁:").pack(side=tk.LEFT)
    weight1_var = tk.DoubleVar(value=0.333)
    weight1_scale = tk.Scale(weights_container, from_=0.0, to=1.0, resolution=0.01, 
                            orient=tk.HORIZONTAL, variable=weight1_var, length=120)
    weight1_scale.pack(side=tk.LEFT, padx=(5, 10))
    
    # Weight 2 (t2)
    ttk.Label(weights_container, text="t₂:").pack(side=tk.LEFT)
    weight2_var = tk.DoubleVar(value=0.333)
    weight2_scale = tk.Scale(weights_container, from_=0.0, to=1.0, resolution=0.01, 
                            orient=tk.HORIZONTAL, variable=weight2_var, length=120)
    weight2_scale.pack(side=tk.LEFT, padx=(5, 10))
    
    # Weight 3 (t3)
    ttk.Label(weights_container, text="t₃:").pack(side=tk.LEFT)
    weight3_var = tk.DoubleVar(value=0.334)
    weight3_scale = tk.Scale(weights_container, from_=0.0, to=1.0, resolution=0.01, 
                            orient=tk.HORIZONTAL, variable=weight3_var, length=120)
    weight3_scale.pack(side=tk.LEFT, padx=(5, 10))
    
    # Equal weights button
    def set_equal_weights():
        weight1_var.set(0.333)
        weight2_var.set(0.333)
        weight3_var.set(0.334)
    
    btn_equal_weights = ttk.Button(weights_container, text="Equal Weights (⅓, ⅓, ⅓)", command=set_equal_weights)
    btn_equal_weights.pack(side=tk.LEFT, padx=(10, 10))
    
    # Normalized weights display
    normalized_weights_label = ttk.Label(weights_container, text="Normalized: [0.333, 0.333, 0.334]", 
                                         foreground="blue", font=("Arial", 9))
    normalized_weights_label.pack(side=tk.LEFT, padx=(10, 0))
    
    # Update normalized weights display when sliders change
    def update_normalized_display(*args):
        t1, t2, t3 = weight1_var.get(), weight2_var.get(), weight3_var.get()
        weight_sum = t1 + t2 + t3
        if weight_sum > 0:
            t1_norm = t1 / weight_sum
            t2_norm = t2 / weight_sum
            t3_norm = t3 / weight_sum
            normalized_weights_label.config(text=f"Normalized: [{t1_norm:.3f}, {t2_norm:.3f}, {t3_norm:.3f}]")
        else:
            normalized_weights_label.config(text="Normalized: [0.333, 0.333, 0.334]")
    
    weight1_var.trace_add('write', update_normalized_display)
    weight2_var.trace_add('write', update_normalized_display)
    weight3_var.trace_add('write', update_normalized_display)
    
    # Merge button
    btn_merge_three = ttk.Button(merge_frame, text="Merge Three Images")
    btn_merge_three.pack(side=tk.LEFT, padx=(20, 0))
    
    # Output section
    output_frame = ttk.LabelFrame(main_frame, text="Morphing Results", padding="10")
    output_frame.pack(fill=tk.BOTH, expand=True)
    
    output_container = ttk.Frame(output_frame)
    output_container.pack(fill=tk.BOTH, expand=True)
    
    # Output canvas 1: Image 1 warped
    output1_frame = ttk.Frame(output_container)
    output1_frame.pack(side=tk.LEFT, padx=(0, 5))
    
    output1_title = ttk.Label(output1_frame, text="Image 1 Warped", font=("Arial", 10, "bold"))
    output1_title.pack()
    
    output1_canvas = Canvas(output1_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="gray")
    output1_canvas.pack()
    
    # Output canvas 2: Image 2 warped
    output2_frame = ttk.Frame(output_container)
    output2_frame.pack(side=tk.LEFT, padx=(0, 5))
    
    output2_title = ttk.Label(output2_frame, text="Image 2 Warped", font=("Arial", 10, "bold"))
    output2_title.pack()
    
    output2_canvas = Canvas(output2_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="gray")
    output2_canvas.pack()
    
    # Output canvas 3: Image 3 warped
    output3_frame = ttk.Frame(output_container)
    output3_frame.pack(side=tk.LEFT, padx=(0, 5))
    
    output3_title = ttk.Label(output3_frame, text="Image 3 Warped", font=("Arial", 10, "bold"))
    output3_title.pack()
    
    output3_canvas = Canvas(output3_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="gray")
    output3_canvas.pack()
    
    # Output canvas 4: Final blend
    output4_frame = ttk.Frame(output_container)
    output4_frame.pack(side=tk.LEFT)
    
    output4_title = ttk.Label(output4_frame, text="Final Blend", font=("Arial", 10, "bold"))
    output4_title.pack()
    
    output4_canvas = Canvas(output4_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="gray")
    output4_canvas.pack()
    
    # ==================== HELPER FUNCTIONS ====================
    
    def update_instruction_label():
        """Update instruction based on current state"""
        nonlocal expecting_image_num, is_three_image_mode
        if is_three_image_mode:
            if expecting_image_num == 1:
                instruction_label.config(text="→ Draw line on IMAGE 1")
            elif expecting_image_num == 2:
                instruction_label.config(text="→ Draw corresponding line on IMAGE 2")
            else:
                instruction_label.config(text="→ Draw corresponding line on IMAGE 3")
        else:
            if expecting_image_num == 1:
                instruction_label.config(text="→ Draw line on IMAGE 1")
            else:
                instruction_label.config(text="→ Draw corresponding line on IMAGE 2")
    
    def open_image(image_num):
        """Open file dialog to select an image"""
        nonlocal image1_path, image2_path, image3_path
        nonlocal image1_original, image2_original, image3_original
        
        file_path = filedialog.askopenfilename(
            title=f"Select Image {image_num}",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        
        if file_path:
            try:
                image = Image.open(file_path)
                
                if image_num == 1:
                    image1_path = file_path
                    image1_original = image
                    display_image_on_canvas(image, canvas1, CANVAS_WIDTH, CANVAS_HEIGHT)
                    status_label.config(text=f"Image 1 loaded: {file_path.split('/')[-1]}")
                elif image_num == 2:
                    image2_path = file_path
                    image2_original = image
                    display_image_on_canvas(image, canvas2, CANVAS_WIDTH, CANVAS_HEIGHT)
                    status_label.config(text=f"Image 2 loaded: {file_path.split('/')[-1]}")
                elif image_num == 3:
                    image3_path = file_path
                    image3_original = image
                    display_image_on_canvas(image, canvas3, CANVAS_WIDTH, CANVAS_HEIGHT)
                    status_label.config(text=f"Image 3 loaded: {file_path.split('/')[-1]}")
                
                update_instruction_label()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def clear_lines():
        """Clear all drawn lines"""
        nonlocal lines_image1, lines_image2, lines_image3, expecting_image_num, current_line_start
        lines_image1 = []
        lines_image2 = []
        lines_image3 = []
        expecting_image_num = 1
        current_line_start = None
        
        # Redraw canvases
        if image1_original:
            display_image_on_canvas(image1_original, canvas1, CANVAS_WIDTH, CANVAS_HEIGHT)
        if image2_original:
            display_image_on_canvas(image2_original, canvas2, CANVAS_WIDTH, CANVAS_HEIGHT)
        if image3_original:
            display_image_on_canvas(image3_original, canvas3, CANVAS_WIDTH, CANVAS_HEIGHT)
        
        # Clear output canvases
        output1_canvas.delete("all")
        output2_canvas.delete("all")
        output3_canvas.delete("all")
        output4_canvas.delete("all")
        
        update_instruction_label()
        mode_desc = "3-image" if is_three_image_mode else "2-image"
        status_label.config(text=f"Lines cleared - Ready to draw new lines in {mode_desc} mode")
    
    # ==================== DRAWING EVENT HANDLERS ====================
    
    def on_canvas_press(event, canvas, image_num):
        """Handle mouse press on canvas"""
        nonlocal current_line_start, expecting_image_num
        
        # Check if this is the correct canvas to draw on
        if image_num != expecting_image_num:
            return
        
        current_line_start = (event.x, event.y)
    
    def on_canvas_release(event, canvas, image_num):
        """Handle mouse release on canvas"""
        nonlocal current_line_start, expecting_image_num, lines_image1, lines_image2, lines_image3
        
        if current_line_start is None:
            return
        
        # Check if this is the correct canvas
        if image_num != expecting_image_num:
            return
        
        line_end = (event.x, event.y)
        
        # Only add line if it has some length
        dist = math.sqrt((line_end[0] - current_line_start[0])**2 + (line_end[1] - current_line_start[1])**2)
        if dist < 5:
            current_line_start = None
            return
        
        # Add line to appropriate list based on mode
        if is_three_image_mode:
            # 3-image mode: sequence 1 -> 2 -> 3
            if image_num == 1:
                lines_image1.append((current_line_start, line_end))
                redraw_canvas_with_lines(canvas1, image1_original, lines_image1, CANVAS_WIDTH, CANVAS_HEIGHT, False)
                redraw_canvas_with_lines(canvas2, image2_original, lines_image2, CANVAS_WIDTH, CANVAS_HEIGHT, True)
                expecting_image_num = 2
                status_label.config(text=f"Line {len(lines_image1)} added to Image 1 - Now draw on Image 2")
            elif image_num == 2:
                lines_image2.append((current_line_start, line_end))
                redraw_canvas_with_lines(canvas2, image2_original, lines_image2, CANVAS_WIDTH, CANVAS_HEIGHT, False)
                redraw_canvas_with_lines(canvas3, image3_original, lines_image3, CANVAS_WIDTH, CANVAS_HEIGHT, True)
                expecting_image_num = 3
                status_label.config(text=f"Line {len(lines_image2)} added to Image 2 - Now draw on Image 3")
            else:  # image_num == 3
                lines_image3.append((current_line_start, line_end))
                redraw_canvas_with_lines(canvas3, image3_original, lines_image3, CANVAS_WIDTH, CANVAS_HEIGHT, False)
                redraw_canvas_with_lines(canvas1, image1_original, lines_image1, CANVAS_WIDTH, CANVAS_HEIGHT, True)
                expecting_image_num = 1
                status_label.config(text=f"Line triplet {len(lines_image3)} complete - Draw next line on Image 1")
        else:
            # 2-image mode: alternating 1 <-> 2
            if image_num == 1:
                lines_image1.append((current_line_start, line_end))
                redraw_canvas_with_lines(canvas1, image1_original, lines_image1, CANVAS_WIDTH, CANVAS_HEIGHT, False)
                redraw_canvas_with_lines(canvas2, image2_original, lines_image2, CANVAS_WIDTH, CANVAS_HEIGHT, True)
                expecting_image_num = 2
                status_label.config(text=f"Line {len(lines_image1)} added to Image 1 - Now draw on Image 2")
            else:  # image_num == 2
                lines_image2.append((current_line_start, line_end))
                redraw_canvas_with_lines(canvas2, image2_original, lines_image2, CANVAS_WIDTH, CANVAS_HEIGHT, False)
                redraw_canvas_with_lines(canvas1, image1_original, lines_image1, CANVAS_WIDTH, CANVAS_HEIGHT, True)
                expecting_image_num = 1
                status_label.config(text=f"Line pair {len(lines_image2)} complete - Draw next line on Image 1")
        
        update_instruction_label()
        current_line_start = None
    
    def on_canvas_motion(event, canvas, image_num):
        """Handle mouse motion for drawing preview"""
        nonlocal current_line_start, expecting_image_num
        
        if current_line_start is None:
            return
        
        # Check if this is the correct canvas
        if image_num != expecting_image_num:
            return
        
        # Redraw with preview line
        if image_num == 1:
            redraw_canvas_with_lines(canvas1, image1_original, lines_image1, CANVAS_WIDTH, CANVAS_HEIGHT, True)
        elif image_num == 2:
            redraw_canvas_with_lines(canvas2, image2_original, lines_image2, CANVAS_WIDTH, CANVAS_HEIGHT, True)
        else:
            redraw_canvas_with_lines(canvas3, image3_original, lines_image3, CANVAS_WIDTH, CANVAS_HEIGHT, True)
        
        # Draw preview line
        canvas.create_line(current_line_start[0], current_line_start[1], 
                          event.x, event.y, fill="yellow", width=2, dash=(5, 5))
    
    # Bind mouse events to all canvases
    canvas1.bind("<Button-1>", lambda e: on_canvas_press(e, canvas1, 1))
    canvas1.bind("<ButtonRelease-1>", lambda e: on_canvas_release(e, canvas1, 1))
    canvas1.bind("<B1-Motion>", lambda e: on_canvas_motion(e, canvas1, 1))
    
    canvas2.bind("<Button-1>", lambda e: on_canvas_press(e, canvas2, 2))
    canvas2.bind("<ButtonRelease-1>", lambda e: on_canvas_release(e, canvas2, 2))
    canvas2.bind("<B1-Motion>", lambda e: on_canvas_motion(e, canvas2, 2))
    
    canvas3.bind("<Button-1>", lambda e: on_canvas_press(e, canvas3, 3))
    canvas3.bind("<ButtonRelease-1>", lambda e: on_canvas_release(e, canvas3, 3))
    canvas3.bind("<B1-Motion>", lambda e: on_canvas_motion(e, canvas3, 3))
    
    # Connect button commands
    btn_image1.config(command=lambda: open_image(1))
    btn_image2.config(command=lambda: open_image(2))
    btn_image3.config(command=lambda: open_image(3))
    btn_clear_lines.config(command=clear_lines)
    
    # Initialize instruction
    update_instruction_label()
    
    # ==================== MORPHING FUNCTIONS ====================
    
    def set_alpha_and_run():
        """Execute morphing with current alpha value (2-image mode only)"""
        try:
            alpha = float(alpha_var.get())
            if not (0.0 <= alpha <= 1.0):
                messagebox.showerror("Error", "Alpha must be between 0.0 and 1.0")
                return
            
            if is_three_image_mode:
                messagebox.showinfo("Info", "Use 'Sequential Animation' for 3-image mode")
                return
            
            if not image1_original or not image2_original:
                messagebox.showerror("Error", "Please load both Image 1 and Image 2")
                return
            
            if len(lines_image1) == 0 or len(lines_image2) == 0:
                messagebox.showerror("Error", "Please draw at least one line pair")
                return
            
            if len(lines_image1) != len(lines_image2):
                messagebox.showerror("Error", "Number of lines must match on both images")
                return
            
            status_label.config(text=f"Computing morph with alpha={alpha}...")
            root.update()
            
            # Scale lines to original image coordinates
            lines1_scaled = scale_lines_to_image(lines_image1, CANVAS_WIDTH, CANVAS_HEIGHT,
                                                 image1_original.size[0], image1_original.size[1])
            lines2_scaled = scale_lines_to_image(lines_image2, CANVAS_WIDTH, CANVAS_HEIGHT,
                                                 image2_original.size[0], image2_original.size[1])
            
            # Ensure images are same size
            target_size = image1_original.size
            img2_resized = image2_original.resize(target_size, Image.Resampling.LANCZOS)
            
            # Adjust lines2_scaled if needed
            if image2_original.size != target_size:
                scale_x_adj = target_size[0] / image2_original.size[0]
                scale_y_adj = target_size[1] / image2_original.size[1]
                lines2_scaled = [((p[0]*scale_x_adj, p[1]*scale_y_adj), (q[0]*scale_x_adj, q[1]*scale_y_adj)) 
                                for p, q in lines2_scaled]
            
            # Interpolate lines
            lines_interp = interpolate_lines(lines1_scaled, lines2_scaled, alpha)
            
            # Warp both images
            status_label.config(text="Warping Image 1...")
            root.update()
            warped1 = warp_image_with_lines(image1_original, lines1_scaled, lines_interp, a=0.01, b=2.0, p=0.0)
            
            status_label.config(text="Warping Image 2...")
            root.update()
            warped2 = warp_image_with_lines(img2_resized, lines2_scaled, lines_interp, a=0.01, b=2.0, p=0.0)
            
            # Blend
            status_label.config(text="Blending images...")
            root.update()
            blended = blend_images(warped1, warped2, alpha)
            
            # Display results with optional grid visualization
            if show_grid_var.get():
                status_label.config(text="Computing grid visualization...")
                root.update()
                
                # Generate grid for the image
                grid_lines = generate_grid(target_size[0], target_size[1], grid_spacing=30)
                
                # Warp grid from image1 to interpolated position
                warped_grid1 = warp_grid_points(grid_lines, lines1_scaled, lines_interp, 
                                                a=0.01, b=2.0, p=0.0, samples_per_line=20)
                
                # Warp grid from image2 to interpolated position
                warped_grid2 = warp_grid_points(grid_lines, lines2_scaled, lines_interp, 
                                                a=0.01, b=2.0, p=0.0, samples_per_line=20)
                
                # Display images with grid overlays
                display_image_with_grid_overlay(warped1, output1_canvas, warped_grid1, 
                                               CANVAS_WIDTH, CANVAS_HEIGHT, grid_color="cyan")
                display_image_with_grid_overlay(warped2, output2_canvas, warped_grid2, 
                                               CANVAS_WIDTH, CANVAS_HEIGHT, grid_color="yellow")
                output3_canvas.delete("all")  # Clear image 3 canvas (not used in 2-image mode)
                display_image_with_grid_overlay(blended, output4_canvas, warped_grid1, 
                                               CANVAS_WIDTH, CANVAS_HEIGHT, grid_color="lime")
            else:
                # Display without grid overlay
                display_image_on_canvas(warped1, output1_canvas, CANVAS_WIDTH, CANVAS_HEIGHT)
                display_image_on_canvas(warped2, output2_canvas, CANVAS_WIDTH, CANVAS_HEIGHT)
                output3_canvas.delete("all")  # Clear image 3 canvas (not used in 2-image mode)
                display_image_on_canvas(blended, output4_canvas, CANVAS_WIDTH, CANVAS_HEIGHT)
            
            status_label.config(text=f"Morphing complete! Alpha={alpha}, {len(lines_image1)} line pairs used")
            
        except Exception as e:
            messagebox.showerror("Error", f"Morphing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            status_label.config(text="Morphing failed - see error message")
    
    btn_set_alpha.config(command=set_alpha_and_run)
    
    # ==================== MERGE THREE IMAGES FUNCTION ====================
    
    def merge_three_images():
        """Execute multiple image merging with barycentric weights"""
        try:
            if not is_three_image_mode:
                messagebox.showinfo("Info", "Switch to 3-image mode to use 'Merge Three'")
                return
            
            if not image1_original or not image2_original or not image3_original:
                messagebox.showerror("Error", "Please load all 3 images")
                return
            
            if len(lines_image1) == 0 or len(lines_image2) == 0 or len(lines_image3) == 0:
                messagebox.showerror("Error", "Please draw at least one line triplet")
                return
            
            if not (len(lines_image1) == len(lines_image2) == len(lines_image3)):
                messagebox.showerror("Error", "Number of lines must match on all three images")
                return
            
            # Get barycentric weights
            t1 = weight1_var.get()
            t2 = weight2_var.get()
            t3 = weight3_var.get()
            weights = [t1, t2, t3]
            
            status_label.config(text=f"Merging 3 images with weights [{t1:.3f}, {t2:.3f}, {t3:.3f}]...")
            root.update()
            
            # Scale lines to original image coordinates
            lines1_scaled = scale_lines_to_image(lines_image1, CANVAS_WIDTH, CANVAS_HEIGHT,
                                                 image1_original.size[0], image1_original.size[1])
            lines2_scaled = scale_lines_to_image(lines_image2, CANVAS_WIDTH, CANVAS_HEIGHT,
                                                 image2_original.size[0], image2_original.size[1])
            lines3_scaled = scale_lines_to_image(lines_image3, CANVAS_WIDTH, CANVAS_HEIGHT,
                                                 image3_original.size[0], image3_original.size[1])
            
            # Perform multiple image merge
            status_label.config(text="Computing shared geometry and warping images...")
            root.update()
            
            merged_image, warped_images, shared_lines = merge_multiple_images(
                [image1_original, image2_original, image3_original],
                [lines1_scaled, lines2_scaled, lines3_scaled],
                weights,
                a=0.01, b=2.0, p=0.0
            )
            
            # Display results with optional grid visualization
            # Show all 3 warped images AND the final blend in the 4 output canvases
            if show_grid_var.get():
                status_label.config(text="Computing grid visualization...")
                root.update()
                
                # Generate grid for the image
                target_size = image1_original.size
                grid_lines = generate_grid(target_size[0], target_size[1], grid_spacing=30)
                
                # Warp grid from each image to shared geometry
                warped_grid1 = warp_grid_points(grid_lines, lines1_scaled, shared_lines, 
                                                a=0.01, b=2.0, p=0.0, samples_per_line=20)
                warped_grid2 = warp_grid_points(grid_lines, lines2_scaled, shared_lines, 
                                                a=0.01, b=2.0, p=0.0, samples_per_line=20)
                warped_grid3 = warp_grid_points(grid_lines, lines3_scaled, shared_lines, 
                                                a=0.01, b=2.0, p=0.0, samples_per_line=20)
                
                # Display all 3 warped images with grid overlays
                display_image_with_grid_overlay(warped_images[0], output1_canvas, warped_grid1, 
                                               CANVAS_WIDTH, CANVAS_HEIGHT, grid_color="cyan")
                display_image_with_grid_overlay(warped_images[1], output2_canvas, warped_grid2, 
                                               CANVAS_WIDTH, CANVAS_HEIGHT, grid_color="yellow")
                display_image_with_grid_overlay(warped_images[2], output3_canvas, warped_grid3, 
                                               CANVAS_WIDTH, CANVAS_HEIGHT, grid_color="magenta")
                # Display final blend with grid overlay
                display_image_with_grid_overlay(merged_image, output4_canvas, warped_grid1, 
                                               CANVAS_WIDTH, CANVAS_HEIGHT, grid_color="lime")
            else:
                # Display without grid overlay - show all 3 warped images and final blend
                display_image_on_canvas(warped_images[0], output1_canvas, CANVAS_WIDTH, CANVAS_HEIGHT)
                display_image_on_canvas(warped_images[1], output2_canvas, CANVAS_WIDTH, CANVAS_HEIGHT)
                display_image_on_canvas(warped_images[2], output3_canvas, CANVAS_WIDTH, CANVAS_HEIGHT)
                display_image_on_canvas(merged_image, output4_canvas, CANVAS_WIDTH, CANVAS_HEIGHT)
            
            # Normalize weights for display
            weight_sum = t1 + t2 + t3
            if weight_sum > 0:
                t1_norm = t1 / weight_sum
                t2_norm = t2 / weight_sum
                t3_norm = t3 / weight_sum
            else:
                t1_norm = t2_norm = t3_norm = 1/3
            
            status_label.config(text=f"Merge complete! Weights: [{t1_norm:.3f}, {t2_norm:.3f}, {t3_norm:.3f}], {len(lines_image1)} line triplets used")
            
        except Exception as e:
            messagebox.showerror("Error", f"Merge failed: {str(e)}")
            import traceback
            traceback.print_exc()
            status_label.config(text="Merge failed - see error message")
    
    btn_merge_three.config(command=merge_three_images)
    
    # Import animation functions (will be defined next)
    from animations import create_warp_animation, create_sequential_animation
    
    btn_warp_anim.config(command=lambda: create_warp_animation(
        root, status_label, output1_canvas, output2_canvas, output3_canvas, output4_canvas,
        image1_original, image2_original, lines_image1, lines_image2,
        is_three_image_mode, CANVAS_WIDTH, CANVAS_HEIGHT, show_grid_var.get()
    ))
    
    btn_seq_anim.config(command=lambda: create_sequential_animation(
        root, status_label, output1_canvas, output2_canvas, output3_canvas, output4_canvas,
        image1_original, image2_original, image3_original,
        lines_image1, lines_image2, lines_image3,
        is_three_image_mode, CANVAS_WIDTH, CANVAS_HEIGHT, show_grid_var.get()
    ))
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()

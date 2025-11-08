"""
Animation Functions for Image Morphing
"""

from tkinter import messagebox
from morph_algorithm import warp_image_with_lines, interpolate_lines, blend_images, generate_grid, warp_grid_points
from ui_helpers import display_image_on_canvas, scale_lines_to_image, display_image_with_grid_overlay
from PIL import Image


def create_warp_animation(root, status_label, output1_canvas, output2_canvas, output3_canvas, output4_canvas,
                          image1_original, image2_original, lines_image1, lines_image2,
                          is_three_image_mode, canvas_width, canvas_height, show_grid=False):
    """
    Generate and display ping-pong animation for 2-image morphing.
    """
    try:
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
        
        status_label.config(text="Preparing animation...")
        root.update()
        
        # Scale lines to original image coordinates
        lines1_scaled = scale_lines_to_image(lines_image1, canvas_width, canvas_height,
                                             image1_original.size[0], image1_original.size[1])
        lines2_scaled = scale_lines_to_image(lines_image2, canvas_width, canvas_height,
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
        
        # Animation parameters
        alpha_steps = [i * 0.1 for i in range(11)]  # 0, 0.1, 0.2, ..., 1.0
        frame_delay = 200  # milliseconds between frames
        
        # Pre-compute all frames
        status_label.config(text="Computing animation frames...")
        root.update()
        
        # Generate grid if needed
        grid_lines = None
        if show_grid:
            grid_lines = generate_grid(target_size[0], target_size[1], grid_spacing=30)
        
        frames = []
        for alpha in alpha_steps:
            # Interpolate lines
            lines_interp = interpolate_lines(lines1_scaled, lines2_scaled, alpha)
            
            # Warp both images
            warped1 = warp_image_with_lines(image1_original, lines1_scaled, lines_interp, a=0.01, b=2.0, p=0.0)
            warped2 = warp_image_with_lines(img2_resized, lines2_scaled, lines_interp, a=0.01, b=2.0, p=0.0)
            
            # Blend
            blended = blend_images(warped1, warped2, alpha)
            
            # Warp grids if grid visualization is enabled
            warped_grid1 = None
            warped_grid2 = None
            if show_grid and grid_lines:
                warped_grid1 = warp_grid_points(grid_lines, lines1_scaled, lines_interp, 
                                               a=0.01, b=2.0, p=0.0, samples_per_line=20)
                warped_grid2 = warp_grid_points(grid_lines, lines2_scaled, lines_interp, 
                                               a=0.01, b=2.0, p=0.0, samples_per_line=20)
            
            frames.append((alpha, warped1, warped2, blended, warped_grid1, warped_grid2))
            status_label.config(text=f"Computing frame {len(frames)}/{len(alpha_steps)}...")
            root.update()
        
        # Play animation in ping-pong loop
        status_label.config(text="Playing animation (press ESC to stop)...")
        root.update()
        
        # Animation control variables
        animation_running = True
        current_frame = 0
        direction = 1  # 1 for forward, -1 for backward
        
        def stop_animation(event=None):
            nonlocal animation_running
            animation_running = False
        
        def animate_frame():
            nonlocal current_frame, animation_running, direction
            
            if not animation_running:
                status_label.config(text="Animation stopped")
                return
            
            # Get current frame
            alpha, warped1, warped2, blended, warped_grid1, warped_grid2 = frames[current_frame]
            
            # Display all three results with optional grid overlay
            if show_grid and warped_grid1 and warped_grid2:
                display_image_with_grid_overlay(warped1, output1_canvas, warped_grid1, 
                                               canvas_width, canvas_height, grid_color="cyan")
                display_image_with_grid_overlay(warped2, output2_canvas, warped_grid2, 
                                               canvas_width, canvas_height, grid_color="yellow")
                output3_canvas.delete("all")  # Clear image 3 canvas (not used in 2-image mode)
                display_image_with_grid_overlay(blended, output4_canvas, warped_grid1, 
                                               canvas_width, canvas_height, grid_color="lime")
            else:
                display_image_on_canvas(warped1, output1_canvas, canvas_width, canvas_height)
                display_image_on_canvas(warped2, output2_canvas, canvas_width, canvas_height)
                output3_canvas.delete("all")  # Clear image 3 canvas (not used in 2-image mode)
                display_image_on_canvas(blended, output4_canvas, canvas_width, canvas_height)
            
            # Update status with direction indicator
            direction_str = "→" if direction == 1 else "←"
            status_label.config(text=f"Animation playing {direction_str} Alpha: {alpha:.1f} (Frame {current_frame + 1}/{len(frames)})")
            
            # Move to next frame
            current_frame += direction
            
            # Check boundaries and reverse direction
            if current_frame >= len(frames):
                current_frame = len(frames) - 2
                direction = -1
            elif current_frame < 0:
                current_frame = 1
                direction = 1
            
            # Schedule next frame
            if animation_running:
                root.after(frame_delay, animate_frame)
        
        # Bind ESC key to stop animation
        root.bind('<Escape>', stop_animation)
        
        # Start animation
        animate_frame()
        
    except Exception as e:
        messagebox.showerror("Error", f"Animation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        status_label.config(text="Animation failed - see error message")


def create_sequential_animation(root, status_label, output1_canvas, output2_canvas, output3_canvas, output4_canvas,
                                image1_original, image2_original, image3_original,
                                lines_image1, lines_image2, lines_image3,
                                is_three_image_mode, canvas_width, canvas_height, show_grid=False):
    """
    Generate and display sequential animation for 3-image morphing (1→2→3 ping-pong).
    """
    try:
        if not is_three_image_mode:
            messagebox.showinfo("Info", "Switch to 3-image mode to use Sequential Animation")
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
        
        status_label.config(text="Preparing sequential animation...")
        root.update()
        
        # Scale lines to original image coordinates
        lines1_scaled = scale_lines_to_image(lines_image1, canvas_width, canvas_height,
                                             image1_original.size[0], image1_original.size[1])
        lines2_scaled = scale_lines_to_image(lines_image2, canvas_width, canvas_height,
                                             image2_original.size[0], image2_original.size[1])
        lines3_scaled = scale_lines_to_image(lines_image3, canvas_width, canvas_height,
                                             image3_original.size[0], image3_original.size[1])
        
        # Ensure all images are same size
        target_size = image1_original.size
        img2_resized = image2_original.resize(target_size, Image.Resampling.LANCZOS)
        img3_resized = image3_original.resize(target_size, Image.Resampling.LANCZOS)
        
        # Adjust lines if images were resized
        if image2_original.size != target_size:
            scale_x = target_size[0] / image2_original.size[0]
            scale_y = target_size[1] / image2_original.size[1]
            lines2_scaled = [((p[0]*scale_x, p[1]*scale_y), (q[0]*scale_x, q[1]*scale_y)) 
                            for p, q in lines2_scaled]
        
        if image3_original.size != target_size:
            scale_x = target_size[0] / image3_original.size[0]
            scale_y = target_size[1] / image3_original.size[1]
            lines3_scaled = [((p[0]*scale_x, p[1]*scale_y), (q[0]*scale_x, q[1]*scale_y)) 
                            for p, q in lines3_scaled]
        
        # Animation parameters
        alpha_steps = [i * 0.1 for i in range(11)]  # 0, 0.1, 0.2, ..., 1.0
        frame_delay = 200  # milliseconds
        
        # Generate grid if needed
        grid_lines = None
        if show_grid:
            grid_lines = generate_grid(target_size[0], target_size[1], grid_spacing=30)
        
        # Pre-compute all frames for both transitions
        status_label.config(text="Computing transition 1→2...")
        root.update()
        
        frames_1_to_2 = []
        for alpha in alpha_steps:
            # Transition from image 1 to image 2
            lines_interp = interpolate_lines(lines1_scaled, lines2_scaled, alpha)
            
            warped1 = warp_image_with_lines(image1_original, lines1_scaled, lines_interp, a=0.01, b=2.0, p=0.0)
            warped2 = warp_image_with_lines(img2_resized, lines2_scaled, lines_interp, a=0.01, b=2.0, p=0.0)
            
            blended = blend_images(warped1, warped2, alpha)
            
            # Warp grids if visualization is enabled
            warped_grid1 = None
            warped_grid2 = None
            if show_grid and grid_lines:
                warped_grid1 = warp_grid_points(grid_lines, lines1_scaled, lines_interp, 
                                              a=0.01, b=2.0, p=0.0, samples_per_line=20)
                warped_grid2 = warp_grid_points(grid_lines, lines2_scaled, lines_interp, 
                                              a=0.01, b=2.0, p=0.0, samples_per_line=20)
            
            # Store: alpha, warped1, warped2, None (no warped3), blended, desc, grids
            frames_1_to_2.append((alpha, warped1, warped2, None, blended, f"1→2: α={alpha:.1f}", 
                                 warped_grid1, warped_grid2, None))
            
            status_label.config(text=f"Computing 1→2 frame {len(frames_1_to_2)}/{len(alpha_steps)}...")
            root.update()
        
        status_label.config(text="Computing transition 2→3...")
        root.update()
        
        frames_2_to_3 = []
        for alpha in alpha_steps:
            # Transition from image 2 to image 3
            lines_interp = interpolate_lines(lines2_scaled, lines3_scaled, alpha)
            
            warped2 = warp_image_with_lines(img2_resized, lines2_scaled, lines_interp, a=0.01, b=2.0, p=0.0)
            warped3 = warp_image_with_lines(img3_resized, lines3_scaled, lines_interp, a=0.01, b=2.0, p=0.0)
            
            blended = blend_images(warped2, warped3, alpha)
            
            # Warp grids if visualization is enabled
            warped_grid2 = None
            warped_grid3 = None
            if show_grid and grid_lines:
                warped_grid2 = warp_grid_points(grid_lines, lines2_scaled, lines_interp, 
                                              a=0.01, b=2.0, p=0.0, samples_per_line=20)
                warped_grid3 = warp_grid_points(grid_lines, lines3_scaled, lines_interp, 
                                              a=0.01, b=2.0, p=0.0, samples_per_line=20)
            
            # Store: alpha, None (no warped1), warped2, warped3, blended, desc, grids
            frames_2_to_3.append((alpha, None, warped2, warped3, blended, f"2→3: α={alpha:.1f}", 
                                 None, warped_grid2, warped_grid3))
            
            status_label.config(text=f"Computing 2→3 frame {len(frames_2_to_3)}/{len(alpha_steps)}...")
            root.update()
        
        # Combine frames: 1→2 then 2→3
        all_frames = frames_1_to_2 + frames_2_to_3[1:]  # Skip duplicate at boundary
        
        # Play animation in ping-pong loop
        status_label.config(text="Playing sequential animation (press ESC to stop)...")
        root.update()
        
        # Animation control variables
        animation_running = True
        current_frame = 0
        direction = 1  # 1 for forward, -1 for backward
        
        def stop_animation(event=None):
            nonlocal animation_running
            animation_running = False
        
        def animate_frame():
            nonlocal current_frame, animation_running, direction
            
            if not animation_running:
                status_label.config(text="Animation stopped")
                return
            
            # Get current frame
            alpha, warped1, warped2, warped3, blended, desc, grid1, grid2, grid3 = all_frames[current_frame]
            
            # Display all warped images and blend
            if show_grid:
                # Display with grid overlays
                if warped1 and grid1:
                    display_image_with_grid_overlay(warped1, output1_canvas, grid1, 
                                                   canvas_width, canvas_height, grid_color="cyan")
                else:
                    output1_canvas.delete("all")
                
                if warped2 and grid2:
                    display_image_with_grid_overlay(warped2, output2_canvas, grid2, 
                                                   canvas_width, canvas_height, grid_color="yellow")
                else:
                    output2_canvas.delete("all")
                
                if warped3 and grid3:
                    display_image_with_grid_overlay(warped3, output3_canvas, grid3, 
                                                   canvas_width, canvas_height, grid_color="magenta")
                else:
                    output3_canvas.delete("all")
                
                # Display blend with grid overlay (use grid1 or grid2 depending on which exists)
                blend_grid = grid1 if grid1 else grid2
                if blend_grid:
                    display_image_with_grid_overlay(blended, output4_canvas, blend_grid, 
                                                   canvas_width, canvas_height, grid_color="lime")
                else:
                    display_image_on_canvas(blended, output4_canvas, canvas_width, canvas_height)
            else:
                # Display without grid overlays
                if warped1:
                    display_image_on_canvas(warped1, output1_canvas, canvas_width, canvas_height)
                else:
                    output1_canvas.delete("all")
                
                if warped2:
                    display_image_on_canvas(warped2, output2_canvas, canvas_width, canvas_height)
                else:
                    output2_canvas.delete("all")
                
                if warped3:
                    display_image_on_canvas(warped3, output3_canvas, canvas_width, canvas_height)
                else:
                    output3_canvas.delete("all")
                
                display_image_on_canvas(blended, output4_canvas, canvas_width, canvas_height)
            
            # Update status with direction indicator
            direction_str = "→" if direction == 1 else "←"
            status_label.config(text=f"Sequential animation {direction_str} {desc} (Frame {current_frame + 1}/{len(all_frames)})")
            
            # Move to next frame
            current_frame += direction
            
            # Check boundaries and reverse direction
            if current_frame >= len(all_frames):
                current_frame = len(all_frames) - 2
                direction = -1
            elif current_frame < 0:
                current_frame = 1
                direction = 1
            
            # Schedule next frame
            if animation_running:
                root.after(frame_delay, animate_frame)
        
        # Bind ESC key to stop animation
        root.bind('<Escape>', stop_animation)
        
        # Start animation
        animate_frame()
        
    except Exception as e:
        messagebox.showerror("Error", f"Sequential animation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        status_label.config(text="Sequential animation failed - see error message")




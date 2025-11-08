"""
Feature-Based Image Morphing Algorithm
Implementation based on Beier & Neely (1992) SIGGRAPH paper
"""

import numpy as np
from PIL import Image


def compute_uv(X, P, Q):
    """
    Compute u and v coordinates for point X relative to line PQ.
    From paper equations (1) and (2).
    
    Args:
        X: Point coordinates [x, y]
        P: Start point of line [x, y]
        Q: End point of line [x, y]
    
    Returns:
        u: Position along the line (0 to 1 from P to Q)
        v: Perpendicular distance from the line
    """
    X = np.array(X, dtype=float)
    P = np.array(P, dtype=float)
    Q = np.array(Q, dtype=float)
    
    PQ = Q - P
    length_PQ = np.linalg.norm(PQ)
    
    if length_PQ < 1e-6:
        return 0.0, 0.0
    
    # u = (X-P) · (Q-P) / ||Q-P||^2
    u = np.dot(X - P, PQ) / (length_PQ ** 2)
    
    # Perpendicular vector (rotate PQ by 90 degrees)
    PQ_perp = np.array([-PQ[1], PQ[0]])
    
    # v = (X-P) · Perpendicular(Q-P) / ||Q-P||
    v = np.dot(X - P, PQ_perp) / length_PQ
    
    return u, v


def compute_X_prime(u, v, P_prime, Q_prime):
    """
    Compute X' from u, v coordinates and line P'Q'.
    From paper equation (3).
    
    Args:
        u: Position along the line
        v: Perpendicular distance from the line
        P_prime: Start point of source line [x, y]
        Q_prime: End point of source line [x, y]
    
    Returns:
        X_prime: Corresponding point in source image [x, y]
    """
    P_prime = np.array(P_prime, dtype=float)
    Q_prime = np.array(Q_prime, dtype=float)
    
    PQ_prime = Q_prime - P_prime
    length_PQ_prime = np.linalg.norm(PQ_prime)
    
    if length_PQ_prime < 1e-6:
        return P_prime
    
    # Perpendicular vector
    PQ_prime_perp = np.array([-PQ_prime[1], PQ_prime[0]])
    PQ_prime_perp_normalized = PQ_prime_perp / length_PQ_prime
    
    # X' = P' + u(Q'-P') + v * Perpendicular(Q'-P') / ||Q'-P'||
    X_prime = P_prime + u * PQ_prime + v * PQ_prime_perp_normalized
    
    return X_prime


def warp_image_with_lines(src_image, source_lines, dest_lines, a=0.01, b=2.0, p=0.0):
    """
    Warp source image using field morphing algorithm.
    
    From paper: "For each pixel X in the destination image, find the corresponding U,V
    based on destination lines PQ, then find X' in source image using source lines P'Q'."
    
    Args:
        src_image: PIL Image to warp
        source_lines: Lines defined relative to source image (P'Q' in paper)
                     List of tuples: [((p_x, p_y), (q_x, q_y)), ...]
        dest_lines: Lines defined relative to destination image (PQ in paper)
                   List of tuples: [((p_x, p_y), (q_x, q_y)), ...]
        a: Weight parameter (smaller = more precise control, default 0.01)
        b: Distance falloff parameter (default 2.0)
        p: Length influence parameter (default 0.0)
    
    Returns:
        Warped PIL Image
    """
    # Convert PIL image to numpy array
    src_array = np.array(src_image)
    height, width = src_array.shape[:2]
    
    # Create output image
    output_array = np.zeros_like(src_array)
    
    # For each pixel X in destination image
    for y in range(height):
        for x in range(width):
            X = np.array([x, y], dtype=float)
            
            # If no lines, just copy pixel
            if len(dest_lines) == 0:
                output_array[y, x] = src_array[y, x]
                continue
            
            # Multiple line algorithm from paper
            DSUM = np.array([0.0, 0.0])
            weightsum = 0.0
            
            for i in range(len(dest_lines)):
                # PQ = destination line, P'Q' = source line
                P, Q = dest_lines[i]
                P_prime, Q_prime = source_lines[i]
                
                # Calculate u, v based on destination line PQ
                u, v = compute_uv(X, P, Q)
                
                # Calculate X'i based on u,v and source line P'Q'
                X_prime_i = compute_X_prime(u, v, P_prime, Q_prime)
                
                # Displacement Di = X'i - X
                D_i = X_prime_i - X
                
                # Calculate distance from X to destination line PQ
                P_arr = np.array(P, dtype=float)
                Q_arr = np.array(Q, dtype=float)
                PQ = Q_arr - P_arr
                length_PQ = np.linalg.norm(PQ)
                
                if length_PQ < 1e-6:
                    dist = np.linalg.norm(X - P_arr)
                else:
                    # Distance depends on u value (from paper note)
                    if u < 0:
                        dist = np.linalg.norm(X - P_arr)
                    elif u > 1:
                        dist = np.linalg.norm(X - Q_arr)
                    else:
                        dist = abs(v)
                
                # Weight calculation (equation 4 from paper)
                # weight = (length^p) / (a + dist)^b
                weight = (length_PQ ** p) / ((a + dist) ** b)
                
                DSUM += D_i * weight
                weightsum += weight
            
            # Calculate final source position: X' = X + DSUM / weightsum
            if weightsum > 0:
                X_source = X + DSUM / weightsum
            else:
                X_source = X
            
            # Sample from source image using bilinear interpolation
            src_x, src_y = X_source[0], X_source[1]
            
            # Clamp to image bounds
            src_x = max(0, min(width - 1, src_x))
            src_y = max(0, min(height - 1, src_y))
            
            # Check if we can do bilinear interpolation
            if 0 <= src_x < width - 1 and 0 <= src_y < height - 1:
                # Bilinear interpolation
                x0, y0 = int(src_x), int(src_y)
                x1, y1 = x0 + 1, y0 + 1
                
                dx = src_x - x0
                dy = src_y - y0
                
                # Interpolate
                pixel = (1 - dx) * (1 - dy) * src_array[y0, x0] + \
                        dx * (1 - dy) * src_array[y0, x1] + \
                        (1 - dx) * dy * src_array[y1, x0] + \
                        dx * dy * src_array[y1, x1]
                
                output_array[y, x] = pixel.astype(np.uint8)
            else:
                # Edge case: just copy nearest pixel
                output_array[y, x] = src_array[int(src_y), int(src_x)]
    
    return Image.fromarray(output_array)


def interpolate_lines(lines1, lines2, alpha):
    """
    Interpolate between two sets of lines.
    
    Args:
        lines1: First set of lines [((p_x, p_y), (q_x, q_y)), ...]
        lines2: Second set of lines [((p_x, p_y), (q_x, q_y)), ...]
        alpha: Interpolation parameter (0 = lines1, 1 = lines2)
    
    Returns:
        Interpolated lines
    """
    lines_interp = []
    for i in range(len(lines1)):
        P1, Q1 = lines1[i]
        P2, Q2 = lines2[i]
        
        P_interp = ((1-alpha)*P1[0] + alpha*P2[0], (1-alpha)*P1[1] + alpha*P2[1])
        Q_interp = ((1-alpha)*Q1[0] + alpha*Q2[0], (1-alpha)*Q1[1] + alpha*Q2[1])
        
        lines_interp.append((P_interp, Q_interp))
    
    return lines_interp


def blend_images(img1, img2, alpha):
    """
    Blend two images using alpha.
    
    Args:
        img1: First PIL Image
        img2: Second PIL Image
        alpha: Blending parameter (0 = img1, 1 = img2)
    
    Returns:
        Blended PIL Image
    """
    arr1 = np.array(img1, dtype=float)
    arr2 = np.array(img2, dtype=float)
    
    blended_arr = (1 - alpha) * arr1 + alpha * arr2
    
    return Image.fromarray(blended_arr.astype(np.uint8))


def blend_multiple_images(images, weights):
    """
    Blend multiple images using barycentric (or general) weights.
    
    This implements the equation: I = sum(t_i * I_hat_i) where sum(t_i) = 1
    
    Args:
        images: List of PIL Images (all must be same size)
        weights: List of weights (should sum to 1.0), one per image
    
    Returns:
        Blended PIL Image
    """
    if len(images) == 0:
        raise ValueError("Need at least one image to blend")
    
    if len(images) != len(weights):
        raise ValueError("Number of images must match number of weights")
    
    # Normalize weights to sum to 1.0
    weights = np.array(weights, dtype=float)
    weight_sum = np.sum(weights)
    if weight_sum > 0:
        weights = weights / weight_sum
    else:
        # If all weights are 0, use equal weights
        weights = np.ones(len(weights)) / len(weights)
    
    # Convert images to arrays and blend
    arrays = [np.array(img, dtype=float) for img in images]
    
    # Weighted sum
    blended_arr = np.zeros_like(arrays[0], dtype=float)
    for i, (arr, weight) in enumerate(zip(arrays, weights)):
        blended_arr += weight * arr
    
    return Image.fromarray(blended_arr.astype(np.uint8))


def interpolate_multiple_lines(line_sets, weights):
    """
    Interpolate between multiple sets of feature lines using barycentric weights.
    
    Computes shared geometry: L_shared = sum(t_i * L_i) where sum(t_i) = 1
    
    Args:
        line_sets: List of line sets, where each set is [((p_x, p_y), (q_x, q_y)), ...]
        weights: List of weights (should sum to 1.0), one per line set
    
    Returns:
        Interpolated lines representing the shared geometry
    """
    if len(line_sets) == 0:
        raise ValueError("Need at least one line set")
    
    if len(line_sets) != len(weights):
        raise ValueError("Number of line sets must match number of weights")
    
    # Normalize weights to sum to 1.0
    weights = np.array(weights, dtype=float)
    weight_sum = np.sum(weights)
    if weight_sum > 0:
        weights = weights / weight_sum
    else:
        weights = np.ones(len(weights)) / len(weights)
    
    # All line sets should have the same number of lines
    num_lines = len(line_sets[0])
    for line_set in line_sets:
        if len(line_set) != num_lines:
            raise ValueError("All line sets must have the same number of lines")
    
    # Interpolate each line
    shared_lines = []
    for line_idx in range(num_lines):
        # Weighted average of P points
        P_avg = np.zeros(2, dtype=float)
        Q_avg = np.zeros(2, dtype=float)
        
        for line_set, weight in zip(line_sets, weights):
            P, Q = line_set[line_idx]
            P_avg += weight * np.array(P)
            Q_avg += weight * np.array(Q)
        
        shared_lines.append((tuple(P_avg), tuple(Q_avg)))
    
    return shared_lines


def merge_multiple_images(images, line_sets, weights, a=0.01, b=2.0, p=0.0):
    """
    Merge multiple images using barycentric coordinate blending.
    
    This implements the full multiple image morphing algorithm:
    1. Compute shared geometry (weighted average of feature lines)
    2. Warp each image to the shared geometry: I_hat_i = W_i[shared_geom](I_i)
    3. Blend warped images: I = sum(t_i * I_hat_i)
    
    Args:
        images: List of PIL Images (will be resized to match first image)
        line_sets: List of feature line sets, one per image
        weights: List of barycentric weights (t_i), should sum to 1.0
        a, b, p: Warping parameters
    
    Returns:
        Tuple: (merged_image, warped_images, shared_lines)
            - merged_image: Final blended result
            - warped_images: List of individually warped images
            - shared_lines: The computed shared geometry
    """
    if len(images) == 0:
        raise ValueError("Need at least one image")
    
    if not (len(images) == len(line_sets) == len(weights)):
        raise ValueError("Number of images, line sets, and weights must match")
    
    # Normalize weights
    weights = np.array(weights, dtype=float)
    weight_sum = np.sum(weights)
    if weight_sum > 0:
        weights = weights / weight_sum
    else:
        weights = np.ones(len(weights)) / len(weights)
    
    # Resize all images to match the first image's size
    target_size = images[0].size
    resized_images = [images[0]]
    adjusted_line_sets = [line_sets[0]]
    
    for i in range(1, len(images)):
        if images[i].size != target_size:
            resized_img = images[i].resize(target_size, Image.Resampling.LANCZOS)
            resized_images.append(resized_img)
            
            # Scale the feature lines accordingly
            scale_x = target_size[0] / images[i].size[0]
            scale_y = target_size[1] / images[i].size[1]
            scaled_lines = [((p[0]*scale_x, p[1]*scale_y), (q[0]*scale_x, q[1]*scale_y)) 
                           for p, q in line_sets[i]]
            adjusted_line_sets.append(scaled_lines)
        else:
            resized_images.append(images[i])
            adjusted_line_sets.append(line_sets[i])
    
    # Step 1: Compute shared geometry (barycentric interpolation of feature lines)
    shared_lines = interpolate_multiple_lines(adjusted_line_sets, weights)
    
    # Step 2: Warp each image to the shared geometry
    warped_images = []
    for i, (img, lines) in enumerate(zip(resized_images, adjusted_line_sets)):
        warped_img = warp_image_with_lines(img, lines, shared_lines, a=a, b=b, p=p)
        warped_images.append(warped_img)
    
    # Step 3: Blend the warped images using barycentric weights
    merged_image = blend_multiple_images(warped_images, weights)
    
    return merged_image, warped_images, shared_lines


def generate_grid(width, height, grid_spacing=20):
    """
    Generate a grid of horizontal and vertical lines.
    
    Args:
        width: Image width
        height: Image height
        grid_spacing: Spacing between grid lines in pixels
    
    Returns:
        List of grid lines as [((x1, y1), (x2, y2)), ...]
    """
    grid_lines = []
    
    # Horizontal lines
    y = 0
    while y <= height:
        grid_lines.append(((0, y), (width, y)))
        y += grid_spacing
    
    # Vertical lines
    x = 0
    while x <= width:
        grid_lines.append(((x, 0), (x, height)))
        x += grid_spacing
    
    return grid_lines


def warp_grid_points(grid_lines, source_lines, dest_lines, a=0.01, b=2.0, p=0.0, samples_per_line=20):
    """
    Warp grid line points using the same feature-based warping algorithm.
    This visualizes how the grid deforms according to feature lines.
    
    Args:
        grid_lines: List of grid lines [((x1, y1), (x2, y2)), ...]
        source_lines: Source feature lines
        dest_lines: Destination feature lines
        a, b, p: Warping parameters (same as warp_image_with_lines)
        samples_per_line: Number of sample points per grid line for smooth curves
    
    Returns:
        List of warped grid lines [[(x1, y1), (x2, y2), ...], ...]
        Each line is a list of points showing the warped path
    """
    warped_grid_lines = []
    
    for grid_line in grid_lines:
        P_grid, Q_grid = grid_line
        warped_points = []
        
        # Sample points along the grid line
        for i in range(samples_per_line + 1):
            t = i / samples_per_line
            # Interpolate along the grid line
            x = P_grid[0] * (1 - t) + Q_grid[0] * t
            y = P_grid[1] * (1 - t) + Q_grid[1] * t
            
            X = np.array([x, y], dtype=float)
            
            # Apply the same warping algorithm as for pixels
            if len(dest_lines) == 0:
                warped_points.append((x, y))
                continue
            
            # Multiple line algorithm
            DSUM = np.array([0.0, 0.0])
            weightsum = 0.0
            
            for i in range(len(dest_lines)):
                P, Q = dest_lines[i]
                P_prime, Q_prime = source_lines[i]
                
                # Calculate u, v based on destination line
                u, v = compute_uv(X, P, Q)
                
                # Calculate X'i based on u,v and source line
                X_prime_i = compute_X_prime(u, v, P_prime, Q_prime)
                
                # Displacement Di = X'i - X
                D_i = X_prime_i - X
                
                # Calculate distance from X to destination line
                P_arr = np.array(P, dtype=float)
                Q_arr = np.array(Q, dtype=float)
                PQ = Q_arr - P_arr
                length_PQ = np.linalg.norm(PQ)
                
                if length_PQ < 1e-6:
                    dist = np.linalg.norm(X - P_arr)
                else:
                    if u < 0:
                        dist = np.linalg.norm(X - P_arr)
                    elif u > 1:
                        dist = np.linalg.norm(X - Q_arr)
                    else:
                        dist = abs(v)
                
                # Weight calculation
                weight = (length_PQ ** p) / ((a + dist) ** b)
                
                DSUM += D_i * weight
                weightsum += weight
            
            # Calculate final warped position
            if weightsum > 0:
                X_warped = X + DSUM / weightsum
            else:
                X_warped = X
            
            warped_points.append((X_warped[0], X_warped[1]))
        
        warped_grid_lines.append(warped_points)
    
    return warped_grid_lines




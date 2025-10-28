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




# Feature-Based Image Metamorphosis

基於 Beier & Neely (1992) SIGGRAPH 論文 "Feature-Based Image Metamorphosis" 的影像變形實作。

## 專案結構

```
hw2/
├── main.py              # 主應用程式（GUI）
├── morph_algorithm.py   # 核心變形演算法
├── ui_helpers.py        # UI 輔助函數
├── animations.py        # 動畫功能
└── README.md           # 本文件
```

## 模組說明

### `morph_algorithm.py`
核心變形演算法實作：
- `compute_uv()` - 計算相對於特徵線的 u, v 座標
- `compute_X_prime()` - 在影像間映射座標
- `warp_image_with_lines()` - 主要的影像扭曲演算法
- `interpolate_lines()` - 在特徵線組間進行插值
- `blend_images()` - 使用 alpha 混合兩張影像
- `blend_multiple_images()` - 使用 barycentric weights 混合多張影像
- `interpolate_multiple_lines()` - 計算共享幾何 (shared geometry)
- `merge_multiple_images()` - 多影像合併（含扭曲與混合）
- `generate_grid()` - 生成網格線用於視覺化
- `warp_grid_points()` - 扭曲網格點以展示變形場

### `ui_helpers.py`
UI 輔助函數：
- `display_image_on_canvas()` - 在 tkinter canvas 上顯示影像
- `draw_arrow_on_canvas()` - 繪製帶編號的箭頭表示特徵線
- `redraw_canvas_with_lines()` - 重繪包含所有線條的 canvas
- `scale_lines_to_image()` - 將 canvas 座標轉換為影像座標
- `draw_warped_grid_overlay()` - 繪製扭曲的網格覆蓋層
- `display_image_with_grid_overlay()` - 顯示帶有網格覆蓋的影像

### `animations.py`
動畫功能：
- `create_warp_animation()` - 雙影像 ping-pong 動畫
- `create_sequential_animation()` - 三影像序列動畫

### `main.py`
主應用程式（含 GUI）：
- 互動式特徵線繪製
- 雙影像與三影像模式
- 即時影像變形
- 動畫播放
- 網格視覺化控制
- Barycentric weights 調整

## 功能特色

### 雙影像模式 (2-Image Mode)
- 載入兩張影像
- 繪製對應的特徵線配對（在兩張影像間交替繪製）
- 設定 alpha 值進行變形
- 查看扭曲後的影像與混合結果
- 播放 ping-pong 動畫 (0→1→0)
- 支援網格視覺化以展示變形過程

### 三影像模式 (3-Image Mode)
- 載入三張影像
- 依序繪製特徵線三元組 (1→2→3)
- 播放序列動畫 (1→2→3 並可反向)
- 三張影像間的平滑轉換
- 查看所有三張扭曲後的影像

### 多影像合併 (Multiple Image Merge)
- 使用 barycentric coordinate blending 合併三張影像
- 即時調整 barycentric weights (t₁, t₂, t₃)
- 自動正規化權重（總和為 1.0）
- 計算共享幾何 (shared geometry)：L_shared = t₁·L₁ + t₂·L₂ + t₃·L₃
- 將每張影像扭曲至共享幾何
- 使用權重混合所有扭曲後的影像
- 支援網格視覺化展示從各影像到共享幾何的變形

### 網格視覺化 (Grid Visualization)
- 可選的網格覆蓋層展示影像變形
- 視覺化展示 Beier & Neely 演算法的 displacement field
- 不同顏色的網格代表不同的影像：
  - Cyan (青色) - Image 1 的網格
  - Yellow (黃色) - Image 2 的網格
  - Magenta (洋紅) - Image 3 的網格
  - Lime (亮綠) - 最終混合結果的網格
- 展示特徵線如何影響空間的拉伸與壓縮
- 證明對 feature-based warping 機制的深入理解

### 輸出顯示區
四個輸出 canvas 分別顯示：
1. **Image 1 Warped** - 第一張影像扭曲後的結果
2. **Image 2 Warped** - 第二張影像扭曲後的結果
3. **Image 3 Warped** - 第三張影像扭曲後的結果（僅於三影像模式）
4. **Final Blend** - 最終混合結果

### 控制項
- **Mode Toggle** - 在雙影像與三影像模式間切換
- **Open Image 1/2/3** - 載入影像
- **Clear Lines** - 清除所有繪製的線條
- **Set Alpha and Run** - 單幀變形（僅雙影像模式）
- **Warp Animation** - Ping-pong 動畫（雙影像模式）
- **Sequential Animation** - 序列動畫（三影像模式）
- **Show Grid Visualization** - 啟用/停用網格視覺化
- **Barycentric Weights (t₁, t₂, t₃)** - 調整合併權重的滑桿
- **Equal Weights** - 將權重設為均等 (⅓, ⅓, ⅓)
- **Merge Three Images** - 執行三影像合併
- **ESC** - 停止當前動畫

## 使用方法

### 基本操作流程

1. 執行應用程式：
   ```bash
   python main.py
   ```

2. 選擇模式（雙影像或三影像）

3. 使用 "Open Image" 按鈕載入影像

4. 透過在影像上點擊並拖曳來繪製特徵線：
   - **雙影像模式**：在 Image 1 和 Image 2 間交替繪製
   - **三影像模式**：依序在 Image 1 → Image 2 → Image 3 繪製

5. 執行變形或動畫：
   - 設定 alpha 值並點擊 "Set Alpha and Run" 產生單幀
   - 點擊 "Warp Animation" 播放雙影像 ping-pong 動畫
   - 點擊 "Sequential Animation" 播放三影像序列動畫

### 多影像合併操作

1. 切換到三影像模式
2. 載入三張影像
3. 繪製對應的特徵線三元組
4. 調整 barycentric weights (t₁, t₂, t₃)：
   - 拖曳滑桿調整各影像的權重
   - 權重會自動正規化使總和為 1.0
   - 可點擊 "Equal Weights" 快速設為均等權重
5. （可選）勾選 "Show Grid Visualization" 查看變形網格
6. 點擊 "Merge Three Images" 執行合併
7. 查看結果：
   - 前三個 canvas 顯示各影像扭曲至共享幾何的結果
   - 第四個 canvas 顯示最終的 barycentric blend

### 網格視覺化使用

1. 勾選 "Show Grid Visualization" checkbox
2. 執行任何變形操作（Set Alpha、Merge Three、動畫等）
3. 觀察彩色網格如何隨著特徵線變形
4. 網格展示了：
   - 影像空間如何被拉伸或壓縮
   - 演算法計算的 displacement field
   - 特徵線對周圍區域的影響範圍

## 演算法細節

### Beier & Neely Field Morphing

基於 Beier & Neely 的 field morphing 方法：
- 使用特徵線 (feature lines) 而非 mesh
- 加權 displacement 計算
- Reverse mapping 搭配 bilinear interpolation
- 預設參數：a=0.01, b=2.0, p=0.0

**演算法步驟**：
1. 對目標影像的每個像素 X：
2. 計算相對於目標特徵線 PQ 的 (u, v) 座標
3. 使用 (u, v) 在來源特徵線 P'Q' 上找到對應點 X'
4. 計算 displacement: D = X' - X
5. 使用距離權重累加所有特徵線的 displacement
6. 最終位置：X_source = X + ΣD_i·w_i / Σw_i
7. 使用 bilinear interpolation 在來源影像取樣

**權重計算**：
```
weight = (length^p) / (a + distance)^b
```

### Multiple Image Morphing with Barycentric Coordinates

多影像變形使用 barycentric coordinate blending：

**數學原理**：
1. **計算共享幾何**（特徵線的加權平均）：
   ```
   L_shared = t₁·L₁ + t₂·L₂ + t₃·L₃
   其中 t₁ + t₂ + t₃ = 1
   ```

2. **扭曲各影像至共享幾何**：
   ```
   Î₁ = W₁[L_shared](I₁)
   Î₂ = W₂[L_shared](I₂)
   Î₃ = W₃[L_shared](I₃)
   ```

3. **使用 barycentric weights 混合**：
   ```
   I_final = t₁·Î₁ + t₂·Î₂ + t₃·Î₃
   ```

**Barycentric Coordinates 的意義**：
- 在三角形內的任意點 P 可表示為三個頂點的加權組合
- 權重 t_i 等於對面子三角形面積除以總面積
- 提供數學上一致的插值權重
- 自動保證權重總和為 1.0（經正規化後）

### Grid Visualization 的技術實現

網格視覺化不使用任何匯入的 warping 函數，完全基於 Beier & Neely 演算法：

1. **生成規則網格**：在影像空間建立水平與垂直線
2. **沿網格線採樣**：每條線取 20 個樣本點
3. **對每個樣本點**：
   - 應用與像素相同的 warping 演算法
   - 計算所有特徵線的 displacement
   - 使用距離權重累加
4. **連接扭曲後的點**：形成彎曲的網格線
5. **視覺化展示**：使用不同顏色覆蓋在影像上

這展示了對 feature-based warping 機制的真正理解，而非僅將其當作黑盒使用。

## 系統需求

- Python 3.x
- tkinter（通常隨 Python 安裝）
- PIL/Pillow
- NumPy

## 技術特點

### 完全手工實作
- **無使用預製的 warping 函數**（如 `cv::warpPerspective`）
- 所有 warping 計算皆基於 Beier & Neely 論文手工實現
- Grid visualization 也使用相同的手工實現演算法

### 模組化設計
- 清晰分離：演算法 / UI / 動畫
- 易於測試與擴展
- 良好的程式碼組織

### 效能最佳化
- Bilinear interpolation 用於平滑取樣
- 網格點採樣而非逐像素計算（用於視覺化）
- 動畫幀預先計算以確保流暢播放

### 使用者體驗
- 即時視覺回饋
- 互動式特徵線繪製
- 多種視覺化選項
- 直覺的控制介面
- 即時權重正規化顯示

## 專案亮點

1. **深入理解變形機制**：透過網格視覺化展示 displacement field
2. **數學正確性**：實作 barycentric coordinate blending
3. **完整的多影像支援**：不僅雙影像，還支援三影像合併
4. **無黑盒依賴**：所有 warping 邏輯皆為手工實現
5. **視覺化教學價值**：網格動畫幫助理解演算法運作原理




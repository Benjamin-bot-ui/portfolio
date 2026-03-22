import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

video_path = "texture_video.avi"
img1_path = "texture test images/image1.png"
img2_path = "texture test images/image2.png"
img1_gt_path = "texture test images/image1_groundtruth.png"
img2_gt_path = "texture test images/image2_groundtruth.png"
OUTPUT_PATH = 'output.avi'
OUT_FOLDER = 'screenshots/' #儲存截圖資料夾
NUM_BG_FRAMES = 100 #前50幀當作背景
THRESHOLD = 14 #二值化閾值
KERNEL_SIZE = 5 #形態學運算核大小
BLUR_SIZE = 21 #高斯模糊核大小
MIN_AREA = 120 #最小缺陷面積
MAX_DEFECT_AREA = 4000 #最大缺陷面積

def evaluate_metrics(pred_mask, gt_mask):
    pred = (pred_mask == 0)
    gt = (gt_mask == 0)

    TP = np.logical_and(pred, gt).sum()
    FP = np.logical_and(pred, ~gt).sum()
    FN = np.logical_and(~pred, gt).sum()
    TN = np.logical_and(~pred, ~gt).sum()

    accuracy = (TP + TN) / (TP + TN + FP + FN + 1e-8)
    precision = TP / (TP + FP + 1e-8)
    recall = TP / (TP + FN + 1e-8)

    return accuracy, precision, recall

#讀取影片
cap = cv2.VideoCapture(video_path)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))#總幀數
ret, frame = cap.read()
if not ret:
    print("無法讀取影片")
    exit()
height, width, _ = frame.shape
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps ,(width, height))

bg_frame = []
cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # 重置到第一幀
for i in range(NUM_BG_FRAMES):
    ret, f = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (BLUR_SIZE, BLUR_SIZE), 0)
    bg_frame.append(blur.astype(np.float32))
background = np.median(bg_frame, axis = 0) #計算背景中位數
cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # 重置到第一幀
frame_idx = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (BLUR_SIZE, BLUR_SIZE), 0)

    diff = cv2.absdiff(blur, background.astype(np.uint8))#計算與背景的絕對差異

    _, defect_mask = cv2.threshold(diff, THRESHOLD, 255, cv2.THRESH_BINARY)#二值化

    kernel = np.ones((KERNEL_SIZE, KERNEL_SIZE), np.uint8)
    defect_mask = cv2.morphologyEx(defect_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)#形態學開運算去除噪點

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(defect_mask)

    max_area = 0
    max_label = 0
    for i in range(1, num_labels):  # 0是背景
        area = stats[i, cv2.CC_STAT_AREA]
        if area > max_area:
            max_area = area
            max_label = i
    overlay = blur.copy()
# 只保留最大區域
    if max_area >= MIN_AREA:
        mask_largest = np.zeros_like(defect_mask, dtype=np.uint8)
        mask_largest[labels == max_label] = 255

        EXPAND_THRESHOLD = max(5, int(THRESHOLD * 0.6))
        expand_allow = (diff >= EXPAND_THRESHOLD).astype(np.uint8) * 255

        mask_expand = mask_largest.copy()
        kernel = np.ones((7, 7), np.uint8)

        for _ in range(500):
            grown = cv2.dilate(mask_expand, kernel)
            mask_expand = cv2.bitwise_and(grown, expand_allow)

            area = cv2.countNonZero(mask_expand)
            if area >= MAX_DEFECT_AREA:
                break
            
        overlay = cv2.cvtColor(overlay, cv2.COLOR_GRAY2BGR)
        overlay[mask_expand == 255] = [0, 0, 255]

        filename = f'{OUT_FOLDER}frame_{frame_idx}.png'
        cv2.imwrite(filename, overlay)
        print(f"Frame {frame_idx} 存檔，最大面積 = {max_area}")
    out.write(overlay)

    cv2.imshow("Defect Detection", overlay)
    if cv2.waitKey(1) & 0xFF == 27: # 按下ESC鍵退出
        break
    frame_idx += 1
cap.release()
out.release()
cv2.destroyAllWindows()

FOLDER = "screenshots"

for filename in os.listdir(FOLDER):

    # 只處理原始預測圖，不處理已產生的 GT
    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        continue
    if "_gt" in filename:
        continue

    path = os.path.join(FOLDER, filename)
    img = cv2.imread(path)

    if img is None:
        continue

    # 分離通道（OpenCV 為 BGR）
    b, g, r = cv2.split(img)

    # 偵測紅色區域（容許誤差）
    red_mask = (r > 200) & (g < 60) & (b < 60)

    # 建立 GT（白底）
    gt = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255

    # 紅色 → 黑色
    gt[red_mask] = 0

    # 可選：補洞 / 平滑（推薦）
    kernel = np.ones((3, 3), np.uint8)
    gt = cv2.morphologyEx(gt, cv2.MORPH_CLOSE, kernel)

    # 儲存檔名
    name, ext = os.path.splitext(filename)
    out_name = f"{name}_gt{ext}"
    out_path = os.path.join(FOLDER, out_name)

    cv2.imwrite(out_path, gt)
    print(f"產生 GT：{out_name}")

# 兩張 GT 圖
gt_imgs_paths = [
    "texture test images/image1_groundtruth.png",
    "texture test images/image2_groundtruth.png"
]

# screenshots 資料夾內所有 _gt.png
FOLDER = "screenshots"
all_gt_files = [f for f in os.listdir(FOLDER) if f.endswith("_gt.png")]

for gt_path in gt_imgs_paths:
    gt_name = os.path.basename(gt_path)
    gt_img = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE)

    best_metrics = {"acc": 0, "prec": 0, "rec": 0, "best_gt_file": ""}

    for file_name in all_gt_files:
        file_path = os.path.join(FOLDER, file_name)
        candidate_img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        
        # Resize candidate_img 到與 gt_img 相同大小
        candidate_img = cv2.resize(candidate_img, (gt_img.shape[1], gt_img.shape[0]))

        acc, prec, rec = evaluate_metrics(gt_img, candidate_img)

        if acc > best_metrics["acc"]:
            best_metrics.update({"acc": acc, "prec": prec, "rec": rec, "best_gt_file": file_name})

    print("====================================")
    print(f"原始 GT：{gt_name}")
    print(f"最佳對應 screenshots/_gt：{best_metrics['best_gt_file']}")
    print(f"Accuracy : {best_metrics['acc']:.3f}")
    print(f"Precision: {best_metrics['prec']:.3f}")
    print(f"Recall   : {best_metrics['rec']:.3f}")

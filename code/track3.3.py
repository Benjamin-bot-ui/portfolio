# video02.mp4
import cv2
import numpy as np
import argparse
from ultralytics import YOLO
from collections import defaultdict, deque
import supervision as sv

# =========================
# 偵測區域設定
# =========================
SOURCE = np.array([
    [650,150],
    [1250,150],
    [1550,520],
    [300,520]
])

TARGET_WIDTH = 25
TARGET_HEIGHT = 60

TARGET = np.array([
    [0, 0],
    [TARGET_WIDTH - 1, 0],
    [TARGET_WIDTH - 1, TARGET_HEIGHT - 1],
    [0, TARGET_HEIGHT - 1]
])

# =========================
# 透視轉換
# =========================
class ViewTransfomer:
    def __init__(self, source:np.ndarray, target: np.ndarray):
        source = source.astype(np.float32)
        target = target.astype(np.float32)
        self.m = cv2.getPerspectiveTransform(source, target)

    def transform_points(self, points:np.ndarray) -> np.ndarray:
        reshaped_point = points.reshape(-1, 1, 2).astype(np.float32)
        transformed_point = cv2.perspectiveTransform(reshaped_point, self.m)
        return transformed_point.reshape(-1, 2)

# =========================
# 主程式
# =========================
if __name__ == "__main__":

    video_path = "Video Project.mp4"

    # 讀影片資訊
    video_info = sv.VideoInfo.from_video_path(video_path)

    # =========================
    # ⭐ 輸出影片設定
    # =========================
    output_path = "C:\\Users\\user\\Desktop\\portfolio\\video\\output.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    out = cv2.VideoWriter(
        output_path,
        fourcc,
        video_info.fps,
        video_info.resolution_wh
    )

    # =========================
    # 模型 & 追蹤器
    # =========================
    model = YOLO("yolo11m.pt")
    byte_track = sv.ByteTrack(frame_rate=video_info.fps)

    # =========================
    # 視覺化設定
    # =========================
    thickness = sv.calculate_optimal_line_thickness(
        resolution_wh=video_info.resolution_wh
    )
    text_scale = sv.calculate_optimal_text_scale(
        resolution_wh=video_info.resolution_wh
    )

    round_box_annotator = sv.RoundBoxAnnotator(thickness=thickness)

    label_annotator = sv.LabelAnnotator(
        text_scale=text_scale,
        text_thickness=thickness,
        text_position=sv.Position.TOP_CENTER,
    )

    trace_annotator = sv.TraceAnnotator(
        thickness=thickness,
        trace_length=video_info.fps * 2,
        position=sv.Position.BOTTOM_CENTER,
        color=sv.Color.BLUE
    )

    # =========================
    # 資料初始化
    # =========================
    frame_generator = sv.get_video_frames_generator(video_path)
    polygon_zone = sv.PolygonZone(polygon=SOURCE)
    view_transfomer = ViewTransfomer(source=SOURCE, target=TARGET)

    coordinates = defaultdict(lambda: deque(maxlen=video_info.fps))

    # =========================
    # 逐幀處理
    # =========================
    for frame in frame_generator:

        # YOLO 偵測
        result = model(frame, conf=0.25, iou=0.7)[0]
        detections = sv.Detections.from_ultralytics(result)
        zone_mask = polygon_zone.trigger(detections) 
        detections = detections[zone_mask]

        # ByteTrack 追蹤
        detections = byte_track.update_with_detections(detections=detections)

        # 取得底部中心點
        points = detections.get_anchors_coordinates(
            anchor=sv.Position.BOTTOM_CENTER
        )

        # 轉換到俯視平面
        points = view_transfomer.transform_points(points).astype(int)

        labels = []

        # =========================
        # 速度計算
        # =========================
        for tracker_id, [_, y] in zip(detections.tracker_id, points):

            coordinates[tracker_id].append(y)

            if len(coordinates[tracker_id]) < video_info.fps / 2:
                labels.append(f"#{tracker_id}")
            else:
                coordinate_start = coordinates[tracker_id][-1]
                coordinate_end = coordinates[tracker_id][0]

                distance = abs(coordinate_start - coordinate_end)
                time = len(coordinates[tracker_id]) / video_info.fps

                speed = distance / time * 3.6
                labels.append(f"#{tracker_id}/{int(speed)} km/h")

        # =========================
        # 畫圖
        # =========================
        frame = trace_annotator.annotate(scene=frame, detections=detections)

        frame = sv.draw_polygon(
            frame,
            polygon=SOURCE,
            color=sv.Color.RED
        )

        frame = round_box_annotator.annotate(
            scene=frame,
            detections=detections
        )

        frame = label_annotator.annotate(
            scene=frame,
            detections=detections,
            labels=labels
        )

        # =========================
        # ⭐ 顯示 + 存檔
        # =========================
        cv2.imshow("Frame", frame)
        out.write(frame)

        key = cv2.waitKey(30)
        if key == 27:
            break

    # =========================
    # 結束
    # =========================
    out.release()
    cv2.destroyAllWindows()
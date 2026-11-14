"""Real inference adapter; only server-provisioned, digest-verified weights are loaded."""

from io import BytesIO
import math

from PIL import Image, ImageDraw, ImageFont


def detect(models, source, settings, cancelled):
    with Image.open(source) as opened:
        image = opened.convert("RGB")
    source.unlink(missing_ok=True)
    width, height = image.size
    detections = []
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    font = ImageFont.load_default(size=max(14, round(max(width, height) / 70)))
    colors = {"vehicle": "#0059b3", "logo": "#00696c", "plate": "#a92316"}
    for kind in settings["types"]:
        if cancelled.exists():
            return b"", []
        model = models[kind]
        result = model.predict(source=image, conf=settings["confidence"] / 100, imgsz=640,
                               device="cuda", classes=[2, 5, 7] if kind == "vehicle" else None,
                               max_det=300, save=False, verbose=False)[0]
        if result.orig_shape != (height, width):
            raise ValueError("Detector dimensions do not match the normalized input")
        for box, score, identity in zip(result.boxes.xyxy.cpu().tolist(), result.boxes.conf.cpu().tolist(),
                                        result.boxes.cls.cpu().tolist()):
            x1, y1, x2, y2 = box
            if (not all(math.isfinite(value) for value in [*box, score, identity])
                    or not 0 <= x1 < x2 <= width or not 0 <= y1 < y2 <= height
                    or not settings["confidence"] / 100 - 1e-6 <= score <= 1):
                raise ValueError("Detector produced invalid coordinates or confidence")
            class_id = int(identity)
            if kind == "vehicle" and class_id not in [2, 5, 7]:
                raise ValueError("Unexpected vehicle class")
            raw_name = model.names[class_id]
            label = "Plate" if kind == "plate" else raw_name
            detections.append({"object_type": kind, "class_id": class_id, "class_name": raw_name,
                               "label": label, "confidence": score, "bbox": box,
                               "width": width, "height": height})
            color = colors[kind]
            draw.rectangle(box, outline=color, width=max(2, round(max(width, height) / 500)))
            text = f"{label} {score:.0%}"
            text_box = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = text_box[2], text_box[3] + 4
            left, top = max(0, min(x1, width - text_width - 8)), max(0, y1 - text_height)
            draw.rectangle((left, top, min(width, left + text_width + 8), top + text_height), fill=color)
            draw.text((left + 4, top), text, fill="white", font=font)
    output = BytesIO()
    annotated.save(output, format="PNG")
    return output.getvalue(), detections

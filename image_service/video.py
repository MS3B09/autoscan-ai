"""Bounded full decoding and silent H.264 encoding, retaining presentation timing."""

from fractions import Fraction
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import av
from PIL import Image


av.logging.set_level(-8)  # Native codec diagnostics must not echo untrusted media metadata.

VIDEO_FORMATS = {".mp4": "mov", ".mov": "mov", ".m4v": "mov", ".avi": "avi",
                 ".asf": "asf", ".mpeg": "mpeg"}
MAX_VIDEO_BYTES = 20_000_000


class VideoError(ValueError):
    def __init__(self, message, status=422):
        super().__init__(message)
        self.status = status


def decoded(container):
    if len(container.streams.video) != 1:
        raise VideoError("Choose a clip with exactly one video stream.")
    stream = container.streams.video[0]
    # Decoder surfaces may include codec alignment padding; displayed pixels are checked separately.
    stream.codec_context.options = {"err_detect": "explode", "max_pixels": "1048576"}
    stream.thread_count = 1
    if not (0 < min(stream.width, stream.height) <= 720 and max(stream.width, stream.height) <= 1280):
        raise VideoError("Video exceeds 720p (1280 × 720, or portrait equivalent).", 413)
    for packet in container.demux(stream):
        if packet.is_corrupt:
            raise VideoError("Video contains corrupt packets. Re-export the complete clip and try again.")
        for frame in packet.decode():
            if frame.is_corrupt:
                raise VideoError("Video contains corrupt frames. Re-export the complete clip and try again.")
            yield frame


def open_source(source):
    # The format/protocol allowlist prevents playlists and external file/network references.
    return av.open(source, options={"format_whitelist": "mov,avi,asf,mpeg",
                                    "protocol_whitelist": "file,pipe"})


def inspect_video(content, suffix):
    try:
        with open_source(BytesIO(content)) as container:
            if VIDEO_FORMATS[suffix] not in container.format.name.split(","):
                raise VideoError("The decoded video container does not match its filename.", 415)
            if container.format.name == "avi":
                # AVI frame headers can count empty time slots; RIFF bounds independently catch truncation.
                containers = [(0, len(content))]
                while containers:
                    offset, boundary = containers.pop()
                    while offset < boundary:
                        if offset + 8 > boundary:
                            raise VideoError("AVI container is truncated. Re-export the complete clip.")
                        length = int.from_bytes(content[offset + 4:offset + 8], "little")
                        end = offset + 8 + length
                        if end > boundary:
                            raise VideoError("AVI container is truncated. Re-export the complete clip.")
                        if content[offset:offset + 4] in [b"RIFF", b"LIST"]:
                            if length < 4:
                                raise VideoError("AVI container has invalid chunk lengths. Re-export the clip.")
                            containers.append((offset + 12, end))
                        offset = end + length % 2
            stream = container.streams.video[0] if container.streams.video else None
            timestamps: list[Fraction] = []
            durations = []
            geometry = None
            first = None
            for frame in decoded(container):
                if len(timestamps) >= 600:
                    raise VideoError("Video exceeds 600 decoded frames.", 413)
                current = (frame.width, frame.height, frame.rotation)
                if geometry is not None and geometry != current:
                    raise VideoError("Video dimensions or orientation change within the clip. Re-export it first.")
                geometry = current
                if (not 0 < min(frame.width, frame.height) <= 720 or max(frame.width, frame.height) > 1280):
                    raise VideoError("Decoded video exceeds 720p.", 413)
                if frame.rotation not in [0, 90, 180, 270, -90, -180, -270]:
                    raise VideoError("Video has unsupported orientation metadata. Re-export it with upright pixels.")
                if frame.pts is None or frame.time_base is None or frame.time_base <= 0:
                    raise VideoError("Video has invalid frame timing. Re-export it with presentation timestamps.")
                timestamp = frame.pts * frame.time_base
                first = timestamp if first is None else first
                relative = timestamp - first
                if relative < 0 or (timestamps and relative <= timestamps[-1]):
                    raise VideoError("Video timestamps are not strictly increasing. Re-export the clip.")
                if relative >= 10:
                    raise VideoError("Video exceeds ten seconds.", 413)
                timestamps.append(relative)
                durations.append(frame.duration * frame.time_base)
            if not timestamps or not stream or first is None:
                raise VideoError("Video contains no decodable frames.")
            # AVI's header can count time slots, including empty slots, rather than decoded pictures.
            if container.format.name != "avi" and stream.frames and stream.frames != len(timestamps):
                raise VideoError("Video did not decode completely. Re-export the original clip.")
            last_duration = durations[-1]
            if last_duration <= 0 and stream.duration is not None and stream.start_time is not None:
                last_duration = (stream.start_time + stream.duration) * stream.time_base - (first + timestamps[-1])
            if last_duration <= 0:
                raise VideoError("Video has no valid final-frame duration. Re-export with valid timing.")
            duration = timestamps[-1] + last_duration
            if duration > 10 + Fraction(1, 1000000):
                raise VideoError("Video exceeds ten seconds.", 413)
            assert geometry is not None
            width, height, rotation = geometry
            if rotation % 180:
                width, height = height, width
            sar = stream.sample_aspect_ratio or Fraction(1)
            if sar <= 0:
                raise VideoError("Video has an invalid display aspect ratio. Re-export the clip.")
            if rotation % 180:
                sar = 1 / sar
            return {"frame_count": len(timestamps), "timestamps": [str(value) for value in timestamps],
                    "duration_seconds": float(duration), "last_duration": str(last_duration),
                    "width": width, "height": height, "rotation": rotation, "sample_aspect_ratio": str(sar)}
    except VideoError:
        raise
    except (av.FFmpegError, ValueError, OverflowError, OSError):
        raise VideoError("Video is corrupt, unsupported, or cannot be decoded safely. Re-export the complete clip.") from None


def render_video(source, output, info, cancelled, annotate=None, progress=None):
    """One frame at a time; cancelled/failed files are removed by the owning job/upload."""
    timestamps = [Fraction(value) for value in info["timestamps"]]
    # A microsecond clock represents common source time bases without an FPS assumption.
    clock = Fraction(1, 1_000_000)
    pts = [round(value / clock) for value in timestamps]
    if any(right <= left for left, right in zip(pts, pts[1:])):
        raise VideoError("Video timing is too fine to encode safely. Re-export the clip.")
    ends = pts[1:] + [round((timestamps[-1] + Fraction(info["last_duration"])) / clock)]
    lengths = dict(zip(pts, [end - start for start, end in zip(pts, ends)]))
    detections: list[dict] = []
    with open_source(source) as input_container, av.open(str(output), "w", format="mp4",
                                                        options={"movflags": "+faststart"}) as target:
        stream = target.add_stream("libx264", rate=Fraction(1) / Fraction(info["last_duration"]))
        stream.width = info["width"] + info["width"] % 2
        stream.height = info["height"] + info["height"] % 2
        stream.pix_fmt = "yuv420p"
        stream.thread_count = 2
        stream.codec_context.sample_aspect_ratio = (Fraction(info["width"], info["height"])
                                                    * Fraction(info["sample_aspect_ratio"])
                                                    / Fraction(stream.width, stream.height))
        stream.time_base = stream.codec_context.time_base = clock
        stream.codec_context.max_b_frames = 0
        stream.options = {"preset": "veryfast", "crf": "23", "tune": "zerolatency"}

        def mux(packets):
            for packet in packets:
                packet.duration = lengths[packet.pts]
                target.mux(packet)

        count = 0
        first = None
        for index, frame in enumerate(decoded(input_container)):
            if cancelled.exists():
                raise InterruptedError("Cancelled")
            if index >= len(pts):
                raise VideoError("Source video changed after validation.")
            if frame.pts is None:
                raise VideoError("Source timing changed after validation.")
            current = frame.pts * frame.time_base
            first = current if first is None else first
            if current - first != timestamps[index] or frame.rotation != info["rotation"]:
                raise VideoError("Source timing or orientation changed after validation.")
            image = frame.to_image().convert("RGB")
            if info["rotation"]:
                image = image.rotate(info["rotation"], expand=True)
            if image.size != (info["width"], info["height"]):
                raise VideoError("Source dimensions changed after validation.")
            if annotate:
                image, observations = annotate(image)
                detections.extend({**item, "frame_index": index, "timestamp_seconds": float(timestamps[index])}
                                  for item in observations)
            if cancelled.exists():
                raise InterruptedError("Cancelled")
            if image.size != (stream.width, stream.height):
                padded = Image.new("RGB", (stream.width, stream.height))
                padded.paste(image)
                image = padded
            encoded = av.VideoFrame.from_image(image)
            encoded.pts, encoded.time_base = pts[index], clock
            mux(stream.encode(encoded))
            count += 1
            if progress:
                progress(count)
            if output.stat().st_size > 40_000_000:
                raise VideoError("Encoded video exceeds temporary storage capacity. Try a simpler or shorter clip.")
        if count != len(pts):
            raise VideoError("Source video did not decode completely during processing.")
        mux(stream.encode())
    if cancelled.exists():
        raise InterruptedError("Cancelled")
    # Validate the complete muxed output, never publish an unfinalized/partial MP4.
    with av.open(str(output)) as verified:
        verified.streams.video[0].thread_count = 1
        count = 0
        for frame in verified.decode(video=0):
            if count >= len(pts) or abs(float(frame.pts * frame.time_base - timestamps[count])) > 0.00001:
                raise VideoError("Encoded MP4 failed timing verification. Try another clip.")
            count += 1
        if count != len(pts) or verified.streams.audio:
            raise VideoError("Encoded MP4 failed frame/timing verification. Try another clip.")
    return detections


def detect_video(models, source, settings, cancelled):
    from image_service.detector import annotate_image

    info = json.loads((source.parent / "video.json").read_text())
    output = source.parent / "result.mp4"

    def progress(count):
        temporary = source.parent / "progress.tmp"
        temporary.write_text(json.dumps({"processed_frames": count}))
        temporary.replace(source.parent / "progress.json")

    observations = render_video(source, output, info, cancelled,
                                lambda image: annotate_image(models, image, settings, cancelled), progress)
    return output.read_bytes(), observations


def prepare_video(content, suffix, root, preview):
    # Native decoders can crash or hang: never run untrusted upload codecs in the HTTP process.
    try:
        with tempfile.TemporaryDirectory(prefix="preview-", dir=root) as directory:
            path = Path(directory)
            (path / "input").write_bytes(content)
            subprocess.run([sys.executable, "-m", "image_service.video", str(path), suffix,
                            "preview" if preview else "validate"],
                           cwd=Path(__file__).resolve().parents[1], check=True, timeout=50,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            info = json.loads((path / "metadata.json").read_text())
            if "error" in info:
                raise VideoError(info["error"], info["status"])
            return (path / "preview.mp4").read_bytes() if preview else bytes(content), info
    except subprocess.TimeoutExpired:
        raise VideoError("Video validation/preview timed out. Try a shorter clip or re-export as H.264 MP4.", 503) from None
    except (subprocess.CalledProcessError, OSError, json.JSONDecodeError):
        raise VideoError("Video validation/encoding or temporary storage is unavailable. Re-export the clip or try again later.", 503) from None


if __name__ == "__main__":
    directory = Path(sys.argv[1])
    try:
        metadata = inspect_video((directory / "input").read_bytes(), sys.argv[2])
        if sys.argv[3] == "preview":
            render_video(directory / "input", directory / "preview.mp4", metadata, directory / "cancel")
    except VideoError as error:
        metadata = {"error": str(error), "status": error.status}
    except Exception:
        metadata = {"error": "Video preview encoding failed. Re-export the complete clip as H.264 MP4.", "status": 422}
    (directory / "metadata.json").write_text(json.dumps(metadata))

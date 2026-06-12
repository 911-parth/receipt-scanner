"""Image cleanup before OCR. This step matters more than the OCR engine itself.

A raw phone photo of a receipt gives garbage results. Grayscale + denoise +
adaptive threshold fixes most of it.
"""

import cv2
import numpy as np


def preprocess(image_path, debug=False):
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Can't read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # upscale small images, tesseract likes ~300dpi-ish text
    h, w = gray.shape
    if w < 1000:
        scale = 1000 / w
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.fastNlMeansDenoising(gray, h=10)

    # adaptive threshold handles uneven lighting (shadows on the receipt)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 15,
    )

    binary = deskew(binary)

    if debug:
        cv2.imwrite("output/debug_preprocessed.png", binary)
    return binary


def deskew(binary):
    """Straighten a slightly rotated receipt using the minAreaRect trick."""
    coords = np.column_stack(np.where(binary < 128))
    if len(coords) < 100:
        return binary
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    # don't touch it if it's basically straight
    if abs(angle) < 0.5 or abs(angle) > 10:
        return binary
    h, w = binary.shape
    m = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(binary, m, (w, h), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)

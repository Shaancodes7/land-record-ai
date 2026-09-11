import cv2


def preprocess_image(input_path, output_path):
    image = cv2.imread(input_path)

    if image is None:
        raise FileNotFoundError(f"Could not read: {input_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Reduce small noise
    denoised = cv2.GaussianBlur(gray, (3, 3), 0)

    # Adaptive threshold
    processed = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    cv2.imwrite(output_path, processed)

    return output_path


if __name__ == "__main__":
    input_file = "documents/samplee.png"
    output_file = "documents/processed.png"

    preprocess_image(input_file, output_file)

    print("✅ Preprocessing complete!")
    print(f"Saved to: {output_file}")
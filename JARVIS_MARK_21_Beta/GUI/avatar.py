
from PIL import Image, ImageTk, ImageSequence
import os

def show_avatar(label, avatar_path):
    # Check if file exists
    if not os.path.exists(avatar_path):
        return False  # File doesn't exist, skip silently
    
    ext = os.path.splitext(avatar_path)[-1].lower()

    # ---- If it's a GIF (animated) ----
    if ext == ".gif":
        try:
            gif = Image.open(avatar_path)
            frames = [ImageTk.PhotoImage(frame.resize((150, 150))) for frame in ImageSequence.Iterator(gif)]

            def update(index):
                frame_image = frames[index]
                label.configure(image=frame_image)
                label.image = frame_image
                label.after(100, update, (index + 1) % len(frames))

            update(0)
            return True
        except Exception as e:
            print(f"⚠️ Error loading GIF avatar {avatar_path}: {e}")
            return False

    # ---- Else if it's a PNG or JPG (static image) ----
    elif ext in [".png", ".jpg", ".jpeg"]:
        try:
            img = Image.open(avatar_path).resize((200, 200))
            tk_img = ImageTk.PhotoImage(img)
            label.configure(image=tk_img)
            label.image = tk_img
            return True
        except Exception as e:
            print(f"⚠️ Error loading image avatar {avatar_path}: {e}")
            return False

    else:
        return False  # Unsupported format

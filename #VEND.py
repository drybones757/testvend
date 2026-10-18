
# VEND
# Window Setup
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from PIL import Image, ImageTk

window = tk.Tk()
window.title("Vending Machine")
window.geometry("900x750")

# Storage
slots = {}
products = {}
inventory = []
busy = False

# Setup Slots
for column, letter in enumerate("ABC"):
    for row in range(5):
        code = f"{letter}{row+1}"

        slot = tk.Label(window, text=code, width=15,
                        height=5, bg="lightblue")

        slot.grid(row=row, column=column, padx=5, pady=5)
        slots[code] = slot


# Convert an image into a Tkinter image
def prepare_image(image):
    resized = image.copy()
    resized.thumbnail((100, 75), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(resized)


# Put an image into a slot
def add_product(code, image):
    products[code] = image

    photo = prepare_image(image)

    slots[code].config(image=photo, text=code,
                       compound="top", width=120, height=110)

    slots[code].image = photo


# Choose Image Function
def button_clicked():
    if busy:
        return

    code = coordinate_input.get().strip().upper()

    if code not in slots:
        status_label.config(text="Invalid slot!")
        return

    filename = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
    )

    if not filename:
        return

    try:
        with Image.open(filename) as source:
            new_image = source.convert("RGBA")
    except OSError:
        status_label.config(text="Unable to open image!")
        return

    add_product(code, new_image)
    status_label.config(text=f"Product added to {code}")


# Dispense Function
def dispense_clicked():
    global busy

    if busy:
        return

    code = coordinate_input.get().strip().upper()

    if code not in slots:
        status_label.config(text="Invalid slot!")
        return

    if code not in products:
        status_label.config(text="No item configured!")
        return

    busy = True
    status_label.config(text=f"Dispensing {code}...")

    animate_spin(code, 0)


# Spinning Animation
def animate_spin(code, frame):
    if frame >= 24:
        finish_dispense(code)
        return

    image = products[code].copy()
    image.thumbnail((70, 60), Image.Resampling.LANCZOS)

    angle = frame * 30

    rotated = image.rotate(
        angle,
        resample=Image.Resampling.BICUBIC,
        expand=True
    )

    canvas = Image.new("RGBA", (120, 100), (0, 0, 0, 0))

    x = (120 - rotated.width) // 2
    y = (100 - rotated.height) // 2

    canvas.alpha_composite(rotated, (x, y))

    photo = ImageTk.PhotoImage(canvas)

    slots[code].config(image=photo, width=120, height=110)
    slots[code].image = photo

    window.after(60, lambda: animate_spin(code, frame + 1))


# Finish Dispensing
def finish_dispense(code):
    global busy

    image = products.pop(code)

    # Remove product from vending machine
    slots[code].config(image="", text=code, width=15, height=5)
    slots[code].image = None

    # Display product in output tray
    photo = prepare_image(image)
    output_tray.config(image=photo, text="", width=120, height=110)
    output_tray.image = photo

    # Add item to customer inventory
    inventory.append((code, image))
    inventory_list.insert(tk.END, f"{len(inventory)}. {code}")

    status_label.config(text=f"{code} dispensed!")
    busy = False


# Setup Input
coordinate_input = tk.Entry(window)
coordinate_input.grid(row=1, column=3, padx=20, pady=5)


# Choose Image Button
button = tk.Button(window, text="Choose Image",
                   command=button_clicked)
button.grid(row=0, column=3, padx=20)


# Dispense Button
dispense_button = tk.Button(window, text="Dispense",
                            command=dispense_clicked)
dispense_button.grid(row=2, column=3, padx=20)


# Output Tray
output_tray = tk.Label(window, text="OUTPUT TRAY\nEmpty",
                       width=20, height=6, bg="lightgray")
output_tray.grid(row=3, column=3, padx=20, pady=10)


# Customer Inventory
inventory_list = tk.Listbox(window, width=22, height=6)
inventory_list.grid(row=4, column=3, padx=20, pady=10)


# Status Display
status_label = tk.Label(window, text="Ready")
status_label.grid(row=5, column=3)


# Load initial Coca-Cola image if available
cola_path = Path(__file__).with_name("cola.png")

if cola_path.exists():
    with Image.open(cola_path) as source:
        add_product("A1", source.convert("RGBA"))


# Run Window
window.mainloop()

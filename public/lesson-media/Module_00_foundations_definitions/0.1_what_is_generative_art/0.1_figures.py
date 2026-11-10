"""
Draws the figures for lesson 0.1: three runs of the fifty-point rule, the
making-versus-system diagram, the order-to-disorder chart, the rows-of-squares study
and the timeline.

Run it in the lesson's folder. It needs NumPy, Pillow and Matplotlib.

Author: Pixels2GenAI Project
"""
import numpy as np
from PIL import Image, ImageDraw
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

INK = "#1C1B19"
TEAL = "#00838A"
SOFT = "#D6ECEC"
PAPER = "#FFFFFF"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK})


def fifty_points(seed, width=1000, height=500):
    """The rule from Exercise 1, with a seed so the figure stays the same."""
    random_numbers = np.random.default_rng(seed)
    points = []
    for column in range(10):
        for row in range(5):
            points.append(((column + random_numbers.random()) * width / 10,
                           (row + random_numbers.random()) * height / 5))
    wall = Image.new("L", (width, height), 245)
    pencil = ImageDraw.Draw(wall)
    for first in range(len(points)):
        for second in range(first + 1, len(points)):
            pencil.line([points[first], points[second]], fill=70, width=1)
    return wall


def nested_squares(disorder, seed=1974, canvas=600, grid=8, nested=5):
    """The rule from Exercise 2."""
    cell = canvas / grid
    random_numbers = np.random.default_rng(seed)
    image = Image.new("L", (canvas, canvas), 255)
    draw = ImageDraw.Draw(image)
    for row in range(grid):
        for column in range(grid):
            centre_x, centre_y = (column + 0.5) * cell, (row + 0.5) * cell
            for square in range(1, nested + 1):
                half = 0.45 * cell * square / nested
                corners = []
                for x_sign, y_sign in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                    stray_x, stray_y = random_numbers.uniform(-1, 1, 2) * disorder * cell
                    corners.append((centre_x + x_sign * half + stray_x,
                                    centre_y + y_sign * half + stray_y))
                draw.polygon(corners, outline=20)
    return image


def three_runs():
    # Stacked as plain pixels at full size, because resampling these fine lines
    # blurs them and makes the file larger.
    gap = 24
    sheet = Image.new("L", (1000, 3 * 500 + 2 * gap), 255)
    for position, seed in enumerate((3, 11, 118)):
        sheet.paste(fifty_points(seed), (0, position * (500 + gap)))
    # Sixteen greys are plenty for pencil lines and keep the file under 500 KB.
    sheet.quantize(16).save("three_runs.png", optimize=True)


def box(axis, x, y, width, height, text, fill=PAPER, edge=INK, size=13, weight="normal"):
    axis.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02,rounding_size=0.08",
                                  facecolor=fill, edgecolor=edge, linewidth=1.6))
    axis.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=size, weight=weight)


def arrow(axis, start, end):
    axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=18, color=INK, linewidth=1.6))


def making_versus_system():
    figure, axis = plt.subplots(figsize=(9, 4.2), dpi=100)
    axis.set_xlim(-0.1, 10.5)
    axis.set_ylim(0, 4.9)
    axis.axis("off")
    axis.text(0, 4.5, "Making each work", fontsize=14, weight="bold")
    box(axis, 0, 3.15, 2, 0.9, "Artist")
    arrow(axis, (2.1, 3.6), (4.3, 3.6))
    axis.text(3.2, 3.75, "every mark", ha="center", fontsize=11)
    box(axis, 4.4, 3.15, 2, 0.9, "Work")
    axis.text(0, 2.15, "Making a system", fontsize=14, weight="bold", color=TEAL)
    box(axis, 0, 0.75, 2, 0.9, "Artist")
    arrow(axis, (2.1, 1.2), (3.3, 1.2))
    axis.text(2.7, 1.35, "rules", ha="center", fontsize=11)
    box(axis, 3.4, 0.75, 2, 0.9, "System", fill=SOFT, edge=TEAL, weight="bold")
    axis.text(4.4, 0.42, "runs with some autonomy", ha="center", fontsize=11)
    for y, label in ((1.75, "Work 1"), (0.95, "Work 2"), (0.15, "Work 3")):
        arrow(axis, (5.5, 1.2), (7.2, y + 0.3))
        box(axis, 7.3, y, 1.7, 0.6, label, size=12)
    axis.text(9.15, 0.45, "...", fontsize=18, va="center")
    figure.tight_layout()
    figure.savefig("making_versus_system.png", facecolor=PAPER)
    plt.close(figure)


def order_and_disorder():
    figure = plt.figure(figsize=(9, 6.4), dpi=100)
    chart = figure.add_axes([0.07, 0.40, 0.88, 0.55])
    disorder = np.linspace(0, 1, 400)
    # A sketch of the idea, not a measurement: low at both ends, high in between.
    complexity = np.exp(-((disorder - 0.5) / 0.17) ** 2)
    chart.plot(disorder, complexity, color=TEAL, linewidth=2.5)
    chart.fill_between(disorder, complexity, color=SOFT)
    chart.set_xticks([0, 0.5, 1], ["Total order", "In between", "Total disorder"], fontsize=12)
    # Align the end labels inward so neither is cut off at the figure's edge.
    chart.get_xticklabels()[0].set_ha("left")
    chart.get_xticklabels()[2].set_ha("right")
    chart.set_yticks([])
    chart.set_ylabel("Effective complexity", fontsize=12)
    chart.set_xlim(0, 1)
    chart.set_ylim(0, 1.1)
    chart.spines[["top", "right"]].set_visible(False)
    panels = [(0.0, 0.10, "DISORDER = 0"), (0.08, 0.40, "DISORDER = 0.08"), (1.0, 0.70, "DISORDER = 1")]
    for value, left, label in panels:
        axis = figure.add_axes([left, 0.02, 0.22, 0.30])
        axis.imshow(nested_squares(value), cmap="gray", vmin=0, vmax=255)
        axis.set_title(label, fontsize=11)
        axis.axis("off")
    figure.savefig("order_and_disorder_chart.png", facecolor=PAPER)
    plt.close(figure)


def rows_of_squares():
    """Rows of squares that lose their order toward the bottom, drawn after Georg Nees's 1960s plotter prints."""
    random_numbers = np.random.default_rng(1968)
    cell, columns, rows = 40, 12, 22
    image = Image.new("L", (cell * (columns + 2), cell * (rows + 2)), 255)
    draw = ImageDraw.Draw(image)
    for row in range(rows):
        for column in range(columns):
            # The dial moves with the row number: same rule, more disorder further down.
            amount = row / (rows - 1)
            turn = random_numbers.uniform(-1, 1) * amount * np.pi / 3
            centre_x = (column + 1.5) * cell + random_numbers.uniform(-1, 1) * amount * cell * 0.4
            centre_y = (row + 1.5) * cell + random_numbers.uniform(-1, 1) * amount * cell * 0.4
            corners = []
            for corner in range(4):
                angle = turn + np.pi / 4 + corner * np.pi / 2
                corners.append((centre_x + cell * 0.7 * np.cos(angle), centre_y + cell * 0.7 * np.sin(angle)))
            draw.polygon(corners, outline=20)
    image.save("rows_of_squares.png", optimize=True)


def system_over_time():
    figure, axis = plt.subplots(figsize=(9, 3.1), dpi=100)
    axis.set_xlim(-0.1, 12.1)
    axis.set_ylim(0, 3.1)
    axis.axis("off")
    forms = [("1790s", "Dice table"), ("1965", "Plotter\nprogram"), ("1967", "Written\ninstruction"),
             ("1973", "Rule\nbase"), ("2020", "Seeded\nscript"), ("2022", "Trained\nmodel")]
    for position, (year, form) in enumerate(forms):
        left = position * 2
        axis.text(left + 0.95, 2.8, year, ha="center", fontsize=12, weight="bold")
        last = position == len(forms) - 1
        box(axis, left + 0.05, 1.3, 1.8, 1.15, form, fill=SOFT if last else PAPER, edge=TEAL if last else INK, size=11.5)
    # The bars carry the lesson's point: only the final form was not written out by hand.
    axis.plot([0.05, 9.85], [0.9, 0.9], color=INK, linewidth=4, solid_capstyle="butt")
    axis.text(4.95, 0.4, "A person writes the rules", ha="center", fontsize=12)
    axis.plot([10.05, 11.85], [0.9, 0.9], color=TEAL, linewidth=4, solid_capstyle="butt")
    axis.text(10.95, 0.4, "Rules from data", ha="center", fontsize=12, color=TEAL)
    figure.tight_layout()
    figure.savefig("system_over_time.png", facecolor=PAPER)
    plt.close(figure)


if __name__ == "__main__":
    three_runs()
    making_versus_system()
    order_and_disorder()
    rows_of_squares()
    system_over_time()
    print("Figures saved.")

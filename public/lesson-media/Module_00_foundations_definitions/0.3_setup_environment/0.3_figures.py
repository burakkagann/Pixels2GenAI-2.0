"""
Draws the diagrams for lesson 0.3: what each stage of the course needs, and what a
virtual environment keeps apart.

Run it in the lesson's folder. It needs Matplotlib.

Author: Pixels2GenAI Project
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1C1B19"
TEAL = "#00838A"
FEDERAL_BLUE = "#3D5588"
FLUO_PINK = "#D6248C"
SOFT_TEAL = "#D6ECEC"
SOFT_GREY = "#F3F3F1"
PAPER = "#FFFFFF"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK})


def what_each_stage_needs():
    figure, axis = plt.subplots(figsize=(9, 3.9), dpi=100)
    axis.set_xlim(-5.2, 13.1)
    axis.set_ylim(-1.1, 5)
    axis.axis("off")
    # One row per tool and one column per module, read as: this tool, in these modules.
    rows = [
        ("Only a browser (Run button)", 0, 9, TEAL),
        ("Python + core kit", 0, 13, FEDERAL_BLUE),
        ("TouchDesigner", 10, 11, "#5B5B57"),
        ("Camera kit", 11, 12, "#5B5B57"),
        ("Model kit (a GPU helps)", 12, 13, FLUO_PINK),
    ]
    for position, (label, first, last, colour) in enumerate(rows):
        y = 4 - position
        axis.text(-0.3, y + 0.35, label, ha="right", va="center", fontsize=12)
        axis.add_patch(FancyBboxPatch((first + 0.04, y + 0.06), last - first - 0.08, 0.58,
                                      boxstyle="round,pad=0.01,rounding_size=0.06",
                                      facecolor=colour, edgecolor=colour))
    for module in range(13):
        axis.text(module + 0.5, -0.4, str(module), ha="center", fontsize=11)
    axis.text(6.5, -1.0, "Module", ha="center", fontsize=11)
    figure.tight_layout()
    figure.savefig("what_each_stage_needs.png", facecolor=PAPER)
    plt.close(figure)


def frame(axis, x, y, width, height, title, fill, edge):
    axis.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02,rounding_size=0.1",
                                  facecolor=fill, edgecolor=edge, linewidth=1.6))
    axis.text(x + 0.2, y + height - 0.32, title, fontsize=12.5, weight="bold", va="center")


def what_a_venv_keeps_apart():
    figure, axis = plt.subplots(figsize=(9, 3.6), dpi=100)
    axis.set_xlim(-0.1, 10.1)
    axis.set_ylim(-0.1, 4)
    axis.axis("off")
    frame(axis, 0, 0, 10, 3.9, "Your computer", PAPER, INK)
    frame(axis, 0.3, 0.3, 3.5, 2.8, "Python on the system", SOFT_GREY, INK)
    axis.text(0.5, 1.5, "Left as it is.\nOther programs may\ndepend on it.", fontsize=11.5, va="center")
    frame(axis, 4.2, 0.3, 5.5, 2.8, "pixels2genai/ (your course folder)", PAPER, TEAL)
    frame(axis, 4.5, 0.55, 2.5, 1.85, ".venv/", SOFT_TEAL, TEAL)
    axis.text(4.7, 1.3, "Its own Python\nand packages", fontsize=11, va="center")
    axis.text(7.25, 1.5, "Your scripts\nand the images\nthey save", fontsize=11, va="center")
    figure.tight_layout()
    figure.savefig("what_a_venv_keeps_apart.png", facecolor=PAPER)
    plt.close(figure)


if __name__ == "__main__":
    what_each_stage_needs()
    what_a_venv_keeps_apart()
    print("Figures saved.")

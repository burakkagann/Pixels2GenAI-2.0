"""
Draws the diagrams for lesson 0.2: who writes the rule, how the terms nest, and
the course's three paths.

Run it in the lesson's folder. It needs Matplotlib.

Author: Pixels2GenAI Project
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch

INK = "#1C1B19"
TEAL = "#00838A"
FEDERAL_BLUE = "#3D5588"
FLUO_PINK = "#D6248C"   # Darker than the print ink, so white text stays readable
SOFT_TEAL = "#D6ECEC"
SOFT_BLUE = "#DDE3EF"
SOFT_PINK = "#FBDDEE"
PAPER = "#FFFFFF"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK})


def box(axis, x, y, width, height, text, fill=PAPER, edge=INK, size=12, weight="normal", colour=INK):
    axis.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02,rounding_size=0.08",
                                  facecolor=fill, edgecolor=edge, linewidth=1.6))
    axis.text(x + width / 2, y + height / 2, text, ha="center", va="center",
              fontsize=size, weight=weight, color=colour)


def arrow(axis, start, end, colour=INK):
    axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=18, color=colour, linewidth=1.6))


def who_writes_the_rule():
    figure, axis = plt.subplots(figsize=(9, 4.4), dpi=100)
    axis.set_xlim(-0.1, 10)
    axis.set_ylim(0, 5)
    axis.axis("off")

    axis.text(0, 4.55, "Algorithm: a person writes the rule", fontsize=14, weight="bold", color=TEAL)
    box(axis, 0, 3.35, 1.9, 0.75, "Input")
    box(axis, 0, 2.5, 1.9, 0.75, "Rule", fill=SOFT_TEAL, edge=TEAL, weight="bold")
    box(axis, 3.3, 2.92, 2.1, 0.75, "Program")
    box(axis, 6.8, 2.92, 2.1, 0.75, "Output")
    arrow(axis, (2.0, 3.72), (3.2, 3.35))
    arrow(axis, (2.0, 2.88), (3.2, 3.22))
    arrow(axis, (5.5, 3.3), (6.7, 3.3))

    axis.text(0, 1.75, "Machine learning: the rule comes out of the data", fontsize=14,
              weight="bold", color=FEDERAL_BLUE)
    box(axis, 0, 0.85, 1.9, 0.6, "Input")
    box(axis, 0, 0.1, 1.9, 0.6, "Examples of output", size=10.5)
    box(axis, 3.3, 0.4, 2.1, 0.75, "Learning step")
    box(axis, 6.8, 0.4, 2.1, 0.75, "Rule", fill=SOFT_BLUE, edge=FEDERAL_BLUE, weight="bold")
    arrow(axis, (2.0, 1.15), (3.2, 0.87))
    arrow(axis, (2.0, 0.4), (3.2, 0.68))
    arrow(axis, (5.5, 0.77), (6.7, 0.77))

    figure.tight_layout()
    figure.savefig("who_writes_the_rule.png", facecolor=PAPER)
    plt.close(figure)


def how_the_terms_nest():
    figure, axis = plt.subplots(figsize=(9, 5.2), dpi=100)
    axis.set_xlim(0, 10)
    axis.set_ylim(0, 5.8)
    axis.axis("off")

    rings = [
        (3.6, 2.9, 7.0, 5.6, "#F3F3F1", INK, "Artificial intelligence", 5.25),
        (3.6, 2.45, 5.5, 4.4, SOFT_TEAL, TEAL, "Machine learning", 4.25),
        (3.6, 2.0, 4.0, 3.2, SOFT_BLUE, FEDERAL_BLUE, "Deep learning", 3.2),
        (3.6, 1.55, 2.6, 2.0, SOFT_PINK, FLUO_PINK, "Generative\nmodels", 1.55),
    ]
    for centre_x, centre_y, width, height, fill, edge, label, label_y in rings:
        axis.add_patch(Ellipse((centre_x, centre_y), width, height, facecolor=fill, edgecolor=edge, linewidth=1.6))
        axis.text(centre_x, label_y, label, ha="center", va="center", fontsize=12, weight="bold")

    # Algorithms are not a ring: they sit under every level, and outside the rings too.
    box(axis, 7.5, 1.0, 2.4, 3.6, "Algorithms\n\nprecise steps,\nused at every\nlevel and well\nbeyond AI",
        fill=PAPER, edge=INK, size=11.5)
    figure.tight_layout()
    figure.savefig("how_the_terms_nest.png", facecolor=PAPER)
    plt.close(figure)


def three_paths():
    figure, axis = plt.subplots(figsize=(9, 3.1), dpi=100)
    axis.set_xlim(-0.1, 10.1)
    axis.set_ylim(0, 3.1)
    axis.axis("off")
    paths = [
        (0.0, TEAL, "Foundations", "Modules 0 to 5", "You write the rule."),
        (3.4, FEDERAL_BLUE, "Machine Learning", "Modules 6 to 11", "The data writes the rule."),
        (6.8, FLUO_PINK, "Generative AI", "Modules 12 to 15", "The model makes the image."),
    ]
    for left, colour, name, modules, line in paths:
        axis.add_patch(FancyBboxPatch((left, 0.25), 3.0, 2.5, boxstyle="round,pad=0.02,rounding_size=0.08",
                                      facecolor=colour, edgecolor=colour))
        axis.text(left + 1.5, 2.15, name, ha="center", color="white", fontsize=14, weight="bold")
        axis.text(left + 1.5, 1.6, modules, ha="center", color="white", fontsize=12)
        axis.text(left + 1.5, 0.75, line, ha="center", color="white", fontsize=10.5, weight="bold")
    figure.tight_layout()
    figure.savefig("three_paths.png", facecolor=PAPER)
    plt.close(figure)


if __name__ == "__main__":
    who_writes_the_rule()
    how_the_terms_nest()
    three_paths()
    print("Figures saved.")

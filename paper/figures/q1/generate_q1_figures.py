#!/usr/bin/env python3
"""Render and validate the two Problem 1 figures from fixed JSON inputs."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, ConnectionPatch, Polygon, Rectangle
from PIL import Image


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"

FIG1_INPUT = DATA_DIR / "Q1_Fig1_Hexagon_Source.json"
FIG2_INPUT = DATA_DIR / "Q1_Fig2_Normalized_Analytic.json"

EXPECTED_HASHES = {
    FIG1_INPUT.name: "d9cc41a57b3e8ad97e3c89cd0b7fe305f374f092914e3077c73bfb0050c2df5e",
    FIG2_INPUT.name: "1b9550fb4428492a00bf70894e4f9e8ded4901c5723e8e64489b49056fbc13d9",
}

BLUE = "#0072B2"
BLUE_FILL = "#E7F1F7"
DARK = "#222222"
SENSOR = "#444444"
CENTER_LINE = "#8C98A3"
WEDGE_EDGE = "#A9B8C5"
REFERENCE = "#777777"
REFERENCE_MUTED = "#B8B8B8"
ORANGE = "#D55E00"
GREEN = "#009E73"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_inputs() -> tuple[dict, dict]:
    for path in (FIG1_INPUT, FIG2_INPUT):
        actual = sha256(path)
        expected = EXPECTED_HASHES[path.name]
        if actual != expected:
            raise ValueError(f"Input hash mismatch for {path.name}: {actual} != {expected}")
    return (
        json.loads(FIG1_INPUT.read_text(encoding="utf-8")),
        json.loads(FIG2_INPUT.read_text(encoding="utf-8")),
    )


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial", "DejaVu Sans"],
            "font.size": 9,
            "axes.titlesize": 9,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.linewidth": 0.65,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "WI-033-Q1-fixed",
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )


def angular_error_degrees(origin: np.ndarray, target: np.ndarray, bearing: float) -> float:
    angle = math.degrees(math.atan2(target[1] - origin[1], target[0] - origin[0]))
    return (bearing - angle + 180.0) % 360.0 - 180.0


def validate_figure1(data: dict) -> dict:
    vertices = np.asarray(data["vertices_counterclockwise"], dtype=float)
    observations = np.asarray(data["inputs"]["sensors_x_y_bearing_degrees"], dtype=float)
    halfplanes = np.asarray(data["halfplanes_a_b_c"], dtype=float)
    tolerance = float(data["containment_tolerance"])

    if vertices.shape != (6, 2):
        raise ValueError(f"Expected six 2-D vertices, got {vertices.shape}")
    if observations.shape != (3, 3):
        raise ValueError(f"Expected three observations, got {observations.shape}")

    signed_double_area = float(
        np.sum(vertices[:, 0] * np.roll(vertices[:, 1], -1))
        - np.sum(vertices[:, 1] * np.roll(vertices[:, 0], -1))
    )
    if signed_double_area <= 0:
        raise ValueError("Figure 1 vertices are not counterclockwise")

    residuals = (
        halfplanes[:, 0, None] * vertices[:, 0]
        + halfplanes[:, 1, None] * vertices[:, 1]
        + halfplanes[:, 2, None]
    )
    minimum_residual = float(np.min(residuals))
    if minimum_residual < -tolerance:
        raise ValueError(f"A Figure 1 vertex violates a half-plane: {minimum_residual}")

    pair_rows: list[tuple[float, int, int]] = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            pair_rows.append((float(np.linalg.norm(vertices[j] - vertices[i])), i, j))
    pair_rows.sort(reverse=True)
    farthest_distance, farthest_i, farthest_j = pair_rows[0]
    if (farthest_i, farthest_j) != (0, 3):
        raise ValueError(f"Unexpected farthest pair: {(farthest_i + 1, farthest_j + 1)}")
    recorded_distance = float(data["pair_distances_descending"][0][0])
    if not math.isclose(farthest_distance, recorded_distance, rel_tol=0, abs_tol=1e-12):
        raise ValueError("Computed and recorded Figure 1 diameters differ")

    truth = np.asarray(data["inputs"]["compatible_truth"], dtype=float)
    bearing_errors = [
        angular_error_degrees(row[:2], truth, float(row[2])) for row in observations
    ]
    delta = float(data["inputs"]["delta_degrees"])
    if any(abs(error) > delta for error in bearing_errors):
        raise ValueError(f"Compatible truth is outside a bearing wedge: {bearing_errors}")

    return {
        "six_vertices": True,
        "counterclockwise": True,
        "minimum_halfplane_residual": minimum_residual,
        "containment_tolerance": tolerance,
        "farthest_pair_one_based": [farthest_i + 1, farthest_j + 1],
        "diameter_m": farthest_distance,
        "display_diameter_m": round(farthest_distance, 2),
        "bearing_errors_degrees": bearing_errors,
        "all_bearing_errors_within_delta": True,
    }


def validate_figure2(data: dict) -> dict:
    shared = data["shared"]
    panels = data["panels"]
    a = np.asarray(shared["A"], dtype=float)
    b = np.asarray(shared["B"], dtype=float)
    o = np.asarray(shared["O"], dtype=float)
    c_a = np.asarray(panels["a"]["C"], dtype=float)
    c_b = np.asarray(panels["b"]["C"], dtype=float)
    c_c = np.asarray(panels["c"]["C"], dtype=float)
    j = np.asarray(panels["c"]["J"], dtype=float)
    reference_radius = float(shared["reference_circle_radius"])
    minimum_radius = float(panels["c"]["minimum_circle_radius"])

    ab = float(np.linalg.norm(b - a))
    a_radius = [float(np.linalg.norm(point - o)) for point in (a, b, c_a)]
    b_oc = float(np.linalg.norm(c_b - o))
    c_support = [float(np.linalg.norm(point - j)) for point in (a, b, c_c)]

    checks = {
        "AB_equals_one": math.isclose(ab, 1.0, rel_tol=0, abs_tol=1e-12),
        "panel_a_vertices_on_reference_circle": all(
            math.isclose(value, reference_radius, rel_tol=0, abs_tol=1e-12)
            for value in a_radius
        ),
        "panel_b_C_outside_reference_circle": b_oc > reference_radius,
        "panel_b_and_c_same_triangle": np.allclose(c_b, c_c, rtol=0, atol=1e-15),
        "panel_c_three_support_points": all(
            math.isclose(value, minimum_radius, rel_tol=0, abs_tol=1e-12)
            for value in c_support
        ),
        "panel_c_centers_distinct": not np.allclose(o, j, rtol=0, atol=1e-15),
        "minimum_radius_exceeds_half": minimum_radius > reference_radius,
    }
    if not all(checks.values()):
        raise ValueError(f"Figure 2 analytic checks failed: {checks}")

    return {
        **checks,
        "AB": ab,
        "OC_panel_b": b_oc,
        "reference_radius": reference_radius,
        "minimum_radius": minimum_radius,
        "support_distances_from_J": c_support,
    }


def panel_heading(ax: plt.Axes, letter: str, title: str) -> None:
    ax.text(
        0.0,
        1.035,
        rf"$\mathbf{{({letter})}}$ {title}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=10,
    )


def plot_forward_wedge(ax: plt.Axes, x: float, y: float, bearing: float, delta: float) -> None:
    length = 2300.0
    center = math.radians(bearing)
    low = math.radians(bearing - delta)
    high = math.radians(bearing + delta)
    sensor = np.array([x, y])
    low_point = sensor + length * np.array([math.cos(low), math.sin(low)])
    high_point = sensor + length * np.array([math.cos(high), math.sin(high)])
    center_point = sensor + length * np.array([math.cos(center), math.sin(center)])

    ax.add_patch(
        Polygon(
            [sensor, low_point, high_point],
            closed=True,
            facecolor=WEDGE_EDGE,
            edgecolor="none",
            alpha=0.075,
            zorder=0,
        )
    )
    ax.plot(
        [sensor[0], low_point[0]],
        [sensor[1], low_point[1]],
        color=WEDGE_EDGE,
        linewidth=0.6,
        zorder=1,
    )
    ax.plot(
        [sensor[0], high_point[0]],
        [sensor[1], high_point[1]],
        color=WEDGE_EDGE,
        linewidth=0.6,
        zorder=1,
    )
    ax.plot(
        [sensor[0], center_point[0]],
        [sensor[1], center_point[1]],
        color=CENTER_LINE,
        linewidth=0.55,
        linestyle="-.",
        zorder=1,
    )


def draw_figure1(data: dict) -> plt.Figure:
    observations = np.asarray(data["inputs"]["sensors_x_y_bearing_degrees"], dtype=float)
    delta = float(data["inputs"]["delta_degrees"])
    vertices = np.asarray(data["vertices_counterclockwise"], dtype=float)

    fig = plt.figure(figsize=(170 / 25.4, 82 / 25.4))
    grid = fig.add_gridspec(1, 2, width_ratios=[0.40, 0.60], wspace=0.34)
    ax_wedges = fig.add_subplot(grid[0, 0])
    ax_region = fig.add_subplot(grid[0, 1])

    for x, y, bearing in observations:
        plot_forward_wedge(ax_wedges, x, y, bearing, delta)

    sensor_offsets = [(-38, -25), (18, -25), (18, 18)]
    for index, ((x, y, _), (dx, dy)) in enumerate(zip(observations, sensor_offsets), start=1):
        ax_wedges.plot(x, y, marker="s", markersize=3.8, color=SENSOR, zorder=4)
        ax_wedges.annotate(
            rf"$S_{index}$",
            (x, y),
            xytext=(dx, dy),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=9,
        )

    zoom_x = (-18.0, 18.0)
    zoom_y = (-16.0, 16.0)
    zoom_rect = Rectangle(
        (zoom_x[0], zoom_y[0]),
        zoom_x[1] - zoom_x[0],
        zoom_y[1] - zoom_y[0],
        facecolor=BLUE_FILL,
        edgecolor=BLUE,
        linewidth=0.9,
        zorder=5,
    )
    ax_wedges.add_patch(zoom_rect)
    ax_wedges.annotate("P", (zoom_x[1], zoom_y[1]), xytext=(6, 4), textcoords="offset points")
    ax_wedges.text(-465, -122, "±1°", color=CENTER_LINE, fontsize=8)

    ax_wedges.set_xlim(-700, 700)
    ax_wedges.set_ylim(-350, 750)
    ax_wedges.set_xticks([-600, 0, 600])
    ax_wedges.set_yticks([-300, 200, 700])
    ax_wedges.set_xlabel("x (m)")
    ax_wedges.set_ylabel("y (m)")
    ax_wedges.set_aspect("equal", adjustable="box")
    panel_heading(ax_wedges, "a", "测向约束")

    polygon = Polygon(
        vertices,
        closed=True,
        facecolor=BLUE_FILL,
        edgecolor=BLUE,
        linewidth=0.9,
        zorder=1,
    )
    ax_region.add_patch(polygon)
    ax_region.scatter(vertices[:, 0], vertices[:, 1], s=2.8**2, color=BLUE, zorder=3)

    point_a = vertices[0]
    point_b = vertices[3]
    ax_region.plot(
        [point_a[0], point_b[0]],
        [point_a[1], point_b[1]],
        color=DARK,
        linewidth=1.6,
        marker="o",
        markersize=4,
        zorder=4,
    )
    ax_region.annotate("A", point_a, xytext=(-11, -8), textcoords="offset points", fontsize=9)
    ax_region.annotate("B", point_b, xytext=(6, 4), textcoords="offset points", fontsize=9)
    midpoint = (point_a + point_b) / 2
    ax_region.annotate(
        r"$D_P\approx 27.68\ \mathrm{m}$",
        midpoint,
        xytext=(7.2, -12.2),
        textcoords="data",
        ha="left",
        va="center",
        arrowprops={"arrowstyle": "-", "color": DARK, "linewidth": 0.65},
        fontsize=9,
    )
    ax_region.text(
        0.5,
        -0.18,
        r"$D_P=\max_{v_i,v_j\in V}\Vert v_i-v_j\Vert$",
        transform=ax_region.transAxes,
        ha="center",
        va="top",
        fontsize=9,
    )
    ax_region.set_xlim(*zoom_x)
    ax_region.set_ylim(*zoom_y)
    ax_region.set_xticks([-15, 0, 15])
    ax_region.set_yticks([-15, 0, 15])
    ax_region.set_xlabel("x (m)")
    ax_region.set_ylabel("y (m)")
    ax_region.set_aspect("equal", adjustable="box")
    panel_heading(ax_region, "b", "区域与直径")

    for y_value in zoom_y:
        fig.add_artist(
            ConnectionPatch(
                xyA=(zoom_x[1], y_value),
                coordsA=ax_wedges.transData,
                xyB=(zoom_x[0], y_value),
                coordsB=ax_region.transData,
                color="#C2C8CD",
                linewidth=0.55,
                zorder=0,
                clip_on=False,
            )
        )
    fig.text(
        0.45,
        0.52,
        "局部放大",
        color="#7A838A",
        fontsize=8,
        ha="center",
        va="center",
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.2, "alpha": 0.92},
    )
    fig.subplots_adjust(left=0.10, right=0.985, bottom=0.21, top=0.88)
    return fig


def draw_triangle(ax: plt.Axes, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> None:
    ax.add_patch(
        Polygon(
            [a, b, c],
            closed=True,
            facecolor=BLUE_FILL,
            edgecolor=BLUE,
            linewidth=0.9,
            zorder=1,
        )
    )
    ax.plot([a[0], b[0]], [a[1], b[1]], color=DARK, linewidth=1.6, zorder=2)


def draw_common_points(
    ax: plt.Axes,
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    o: np.ndarray,
    *,
    highlighted_c: bool = False,
) -> None:
    ax.scatter([a[0], b[0]], [a[1], b[1]], s=2.8**2, color=BLUE, zorder=4)
    if highlighted_c:
        ax.plot(c[0], c[1], marker="^", markersize=4.5, color=ORANGE, linestyle="none", zorder=5)
    else:
        ax.scatter([c[0]], [c[1]], s=2.8**2, color=BLUE, zorder=4)
    ax.scatter([o[0]], [o[1]], s=2.8**2, color=REFERENCE, zorder=4)
    ax.annotate("A", a, xytext=(-11, -10), textcoords="offset points", fontsize=8)
    ax.annotate("B", b, xytext=(5, -10), textcoords="offset points", fontsize=8)
    ax.annotate("C", c, xytext=(5, 4), textcoords="offset points", fontsize=8, color=ORANGE if highlighted_c else DARK)
    ax.annotate("O", o, xytext=(5, -11), textcoords="offset points", fontsize=8, color=REFERENCE)


def draw_right_angle(ax: plt.Axes, c: np.ndarray, a: np.ndarray, b: np.ndarray) -> None:
    size = 0.075
    u_a = (a - c) / np.linalg.norm(a - c)
    u_b = (b - c) / np.linalg.norm(b - c)
    points = np.vstack([c + size * u_a, c + size * (u_a + u_b), c + size * u_b])
    ax.plot(points[:, 0], points[:, 1], color=DARK, linewidth=0.7, zorder=5)


def draw_figure2(data: dict) -> plt.Figure:
    shared = data["shared"]
    panels = data["panels"]
    limits = data["axis_limits"]
    a = np.asarray(shared["A"], dtype=float)
    b = np.asarray(shared["B"], dtype=float)
    o = np.asarray(shared["O"], dtype=float)
    reference_radius = float(shared["reference_circle_radius"])

    fig, axes = plt.subplots(1, 3, figsize=(170 / 25.4, 80 / 25.4))
    fig.subplots_adjust(left=0.025, right=0.985, bottom=0.13, top=0.87, wspace=0.16)

    for ax in axes:
        ax.set_xlim(*limits["x"])
        ax.set_ylim(*limits["y"])
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")

    c_a = np.asarray(panels["a"]["C"], dtype=float)
    axes[0].add_patch(Circle(o, reference_radius, fill=False, edgecolor=REFERENCE, linestyle="--", linewidth=0.85, zorder=0))
    draw_triangle(axes[0], a, b, c_a)
    draw_common_points(axes[0], a, b, c_a, o)
    draw_right_angle(axes[0], c_a, a, b)
    relation_box = {"facecolor": "white", "edgecolor": "none", "pad": 1.0, "alpha": 0.92}
    axes[0].text(
        0.5,
        0.07,
        r"$r_*=1/2$",
        transform=axes[0].transAxes,
        ha="center",
        va="bottom",
        fontsize=9,
        bbox=relation_box,
    )
    panel_heading(axes[0], "a", "覆盖成立")

    c_b = np.asarray(panels["b"]["C"], dtype=float)
    axes[1].add_patch(Circle(o, reference_radius, fill=False, edgecolor=REFERENCE, linestyle="--", linewidth=0.85, zorder=0))
    draw_triangle(axes[1], a, b, c_b)
    axes[1].plot([o[0], c_b[0]], [o[1], c_b[1]], color=REFERENCE, linewidth=0.65, zorder=2)
    draw_common_points(axes[1], a, b, c_b, o, highlighted_c=True)
    axes[1].text(
        0.5,
        0.07,
        r"$OC=\sqrt{3}/2>1/2$",
        transform=axes[1].transAxes,
        ha="center",
        va="bottom",
        fontsize=8.5,
        bbox=relation_box,
    )
    panel_heading(axes[1], "b", "覆盖失效")

    c_c = np.asarray(panels["c"]["C"], dtype=float)
    j = np.asarray(panels["c"]["J"], dtype=float)
    minimum_radius = float(panels["c"]["minimum_circle_radius"])
    axes[2].add_patch(Circle(o, reference_radius, fill=False, edgecolor=REFERENCE_MUTED, linestyle="--", linewidth=0.85, zorder=0))
    draw_triangle(axes[2], a, b, c_c)
    axes[2].add_patch(Circle(j, minimum_radius, fill=False, edgecolor=GREEN, linewidth=1.1, zorder=2))
    axes[2].plot([o[0], j[0]], [o[1], j[1]], color=REFERENCE_MUTED, linewidth=0.6, zorder=2)
    axes[2].plot([j[0], b[0]], [j[1], b[1]], color=GREEN, linewidth=0.75, zorder=3)
    draw_common_points(axes[2], a, b, c_c, o)
    axes[2].plot(j[0], j[1], marker="D", markersize=4, color=GREEN, linestyle="none", zorder=5)
    axes[2].annotate("J", j, xytext=(-13, 5), textcoords="offset points", fontsize=8, color=GREEN)
    axes[2].text(
        0.5,
        0.07,
        r"$r_*=1/\sqrt{3}>1/2$",
        transform=axes[2].transAxes,
        ha="center",
        va="bottom",
        fontsize=9,
        bbox=relation_box,
    )
    panel_heading(axes[2], "c", "最小覆盖圆")
    return fig


def export_figure(fig: plt.Figure, stem: str) -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    fixed_datetime = datetime(2026, 9, 13, tzinfo=timezone.utc)
    common_creator = "WI-033 deterministic Matplotlib renderer"
    for extension, options in (
        (
            "pdf",
            {
                "metadata": {
                    "Title": stem,
                    "Author": "Q1 figure production",
                    "Creator": common_creator,
                    "CreationDate": fixed_datetime,
                    "ModDate": fixed_datetime,
                }
            },
        ),
        ("svg", {"metadata": {"Title": stem, "Creator": common_creator, "Date": "2026-09-13"}}),
        ("png", {"dpi": 600, "metadata": {"Software": common_creator}}),
    ):
        path = OUTPUT_DIR / f"{stem}.{extension}"
        fig.savefig(path, **options)
        if extension == "svg":
            svg_text = path.read_text(encoding="utf-8")
            path.write_text(
                "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
                encoding="utf-8",
            )
        outputs.append(path)
    plt.close(fig)
    return outputs


def output_metadata(path: Path) -> dict:
    metadata = {"sha256": sha256(path), "bytes": path.stat().st_size}
    if path.suffix.lower() == ".png":
        with Image.open(path) as image:
            metadata["pixels"] = list(image.size)
            dpi = image.info.get("dpi")
            metadata["dpi"] = [float(value) for value in dpi] if dpi else None
    return metadata


def validate_exports(outputs: list[Path]) -> dict:
    expected_png_pixels = {
        "Q1_Fig1_Intersection_Diameter.png": [int(170 / 25.4 * 600), int(82 / 25.4 * 600)],
        "Q1_Fig2_Diameter_Coverage.png": [int(170 / 25.4 * 600), int(80 / 25.4 * 600)],
    }
    names = {path.name for path in outputs}
    required_names = {
        f"{stem}.{extension}"
        for stem in ("Q1_Fig1_Intersection_Diameter", "Q1_Fig2_Diameter_Coverage")
        for extension in ("pdf", "svg", "png")
    }
    if names != required_names:
        raise ValueError(f"Unexpected export set: {sorted(names)}")

    png_checks = {}
    for path in outputs:
        if path.suffix.lower() != ".png":
            continue
        metadata = output_metadata(path)
        expected_pixels = expected_png_pixels[path.name]
        if metadata["pixels"] != expected_pixels:
            raise ValueError(
                f"Unexpected PNG size for {path.name}: {metadata['pixels']} != {expected_pixels}"
            )
        dpi = metadata["dpi"]
        if dpi is None or any(abs(value - 600.0) > 1.0 for value in dpi):
            raise ValueError(f"Unexpected PNG DPI for {path.name}: {dpi}")
        png_checks[path.name] = {
            "pixels": metadata["pixels"],
            "dpi": dpi,
            "target_pixels": expected_pixels,
        }
    return {"required_formats_present": True, "png": png_checks}


def main() -> None:
    configure_style()
    figure1_data, figure2_data = load_inputs()
    checks = {
        "figure1": validate_figure1(figure1_data),
        "figure2": validate_figure2(figure2_data),
    }

    outputs = []
    outputs.extend(export_figure(draw_figure1(figure1_data), "Q1_Fig1_Intersection_Diameter"))
    outputs.extend(export_figure(draw_figure2(figure2_data), "Q1_Fig2_Diameter_Coverage"))
    checks["exports"] = validate_exports(outputs)

    record = {
        "status": "PASS",
        "scope": "Fixed-input geometric and export checks; not a general-program correctness claim",
        "python": sys.version,
        "platform": platform.platform(),
        "matplotlib": matplotlib.__version__,
        "numpy": np.__version__,
        "inputs": {path.name: sha256(path) for path in (FIG1_INPUT, FIG2_INPUT)},
        "checks": checks,
        "target_sizes_mm": {
            "Q1_Fig1_Intersection_Diameter": [170, 82],
            "Q1_Fig2_Diameter_Coverage": [170, 80],
        },
        "outputs": {path.name: output_metadata(path) for path in outputs},
    }
    record_path = OUTPUT_DIR / "Q1_Figure_Validation.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False, indent=2))
    print(f"Validation record: {record_path}")


if __name__ == "__main__":
    main()

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Arc
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import argparse
from pathlib import Path
import math


def get_image_path(section_name, image_dir):
    "cleaning up the image path for getting the images"
    name_lower = section_name.lower().replace(' ', '_')
    for ext in ['.png', '.jpg', '.jpeg', '.svg']:
        path = image_dir / f"{name_lower }{ext}"
        if path.exists():
            return path
    return None


def generate_positions(sections, row_base_radius=1.2, row_spacing=0.7):
    """
    changing the config information positional info for the graph
    """
    row_groups = {}
    for section in sections:
        row = section['row']
        if row not in row_groups:
            row_groups[row] = []
        row_groups[row].append(section)

    all_musicians = []
    section_info = {}
    row_info = {}

    for row_num, row_sections in sorted(row_groups.items()):
        row_sections.sort(key=lambda s: s['start_index'])

        row_names = []
        row_sections_map = []
        for section in row_sections:
            for name in section['names']:
                row_names.append(name)
                row_sections_map.append(section['name'])

        n_row = len(row_names)
        radius = row_base_radius + (row_num - 1) * row_spacing

        if n_row == 1:
            angles = [np.pi / 2]
        else:
            angles = np.linspace(0, np.pi, n_row)

        sections_in_row = {}
        idx = 0
        for section in row_sections:
            n = len(section['names'])
            section_name = section['name']
            for i in range(n):
                angle = angles[idx + i]
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                name = section['names'][i]
                all_musicians.append({
                    'name': name,
                    'section': section_name,
                    'x': x,
                    'y': y,
                    'color': section['color'],
                    'image': section.get('image', None),
                    'visible': name.strip() != ''
                })
            sections_in_row[section_name] = angles[idx:idx + n]
            idx += n

        for section_name, sect_angles in sections_in_row.items():
            mid_angle = np.mean(sect_angles)
            section_info[section_name] = {
                'angle': mid_angle,
                'radius': radius
            }

        row_info[row_num] = {'radius': radius, 'angles': angles}

    return all_musicians, section_info, row_info


def draw_orchestra(
    musicians,
    section_info,
    row_info,
    config,
    output_path='orchestra_layout.png',
    show_labels=True, 
    use_images=False,
    show_row_counts=False,
    title='Orchestra Seating Layout',
    show_plot=False
):
    """
    creating the actual graph
    """
    font_size = config.get('font_size', 9)
    icon_size = config.get('icon_size', 400)
    image_dir = Path(config.get('image_dir', 'figs'))
    use_images = config.get('use_images', False)

    conductor_config = config.get('conductor', {})
    conductor_name = conductor_config.get('name', 'Conductor')
    conductor_color = conductor_config.get('color', '#8b4513')
    conductor_image = conductor_config.get('image', None)

    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_aspect('equal')
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#f8f9fa')

    section_colors = {}
    for m in musicians:
        section_colors[m['section']] = m['color']

    visible_musicians = [m for m in musicians if m['visible']]
    row_counts = {}
    for m in visible_musicians:
        dist = (m['x']**2 + m['y']**2)**0.5
        closest_row = min(row_info.keys(), key=lambda r: abs(row_info[r]['radius'] - dist))
        row_counts[closest_row] = row_counts.get(closest_row, 0) + 1

    for row_num, info in row_info.items():
        radius = info['radius']
        arc = Arc((0, 0), radius * 2, height=radius * 2, angle=0, theta1=0, theta2=180,
                  linewidth=1, linestyle='--', color='#d5d8dc', alpha=0.6)
        ax.add_patch(arc)

    zoom = np.sqrt(icon_size) / 100

    # Draw musicians
    for m in musicians:
        if not m['visible']:
            continue

        x, y = m['x'], m['y']
        color = m['color']

        draw_circle = True
        label_offset = -1
        
        if use_images:
            image_path = m.get('image') or get_image_path(m['section'], image_dir)
            if image_path:
                try:
                    img = plt.imread(str(image_path))
                    imagebox = OffsetImage(img, zoom=zoom)
                    ab = AnnotationBbox(imagebox, (x, y), frameon=False, zorder=5)
                    ax.add_artist(ab)
                    img_height_pts = img.shape[0] * zoom * 0.75  # approx image half-height in points
                    label_offset = -(img_height_pts / 2 + 7)
                    draw_circle = False  # Image was successfully added
                except Exception:
                    print(f"No image found for: {m['section']}")
        
        # If no images needed or no image found => draw circle in the nice color
        if draw_circle:
            ax.scatter(x, y, c=color, s=icon_size, zorder=5,
                       edgecolors='white', linewidth=2.5, alpha=0.9)

            label_offset = -(math.sqrt(icon_size) / 2 + 4)


        ax.annotate(
            m['name'],
            (x, y),
            textcoords="offset points",
            xytext=(0, int(label_offset)),
            ha='center',
            va='top',
            fontsize=font_size,
            fontweight='bold',
            color='#2c3e50',
            path_effects=[pe.withStroke(linewidth=2, foreground='white')]
        )

    # Draw section labels
    if show_labels:
        for section_name, info in section_info.items():
            angle = info['angle']
            radius = info['radius']
            label_radius = radius + 0.15

            label_x = label_radius * np.cos(angle)
            label_y = label_radius * np.sin(angle)

            color = section_colors.get(section_name, '#bdc3c7')

            ax.annotate(
                section_name,
                (label_x, label_y),
                ha='center',
                va='center',
                fontsize=font_size - 1,
                fontweight='bold',
                color='white',
                bbox=dict(boxstyle='round,pad=0.25', facecolor=color,
                          edgecolor='none', alpha=0.95)
            )


    # Draw conductor
    conductor_pos = (0, -0.3)

    draw_conductor = True

    if conductor_image:
        conductor_path = Path(conductor_image)
        if not conductor_path.is_absolute():
            conductor_path = image_dir / conductor_path
        if conductor_path.exists():
            try:
                img = plt.imread(str(conductor_path))
                conductor_zoom = zoom * 0.8
                imagebox = OffsetImage(img, zoom=conductor_zoom)
                ab = AnnotationBbox(imagebox, conductor_pos, frameon=False, zorder=6)
                ax.add_artist(ab)
                draw_conductor = False
            except Exception:
                print("No image found for conductor")


    if draw_conductor:
        ax.scatter(*conductor_pos, c=conductor_color, s=icon_size * 0.35,
                   marker='s', zorder=6, edgecolors='white', linewidth=2.5)

    ax.annotate(conductor_name, conductor_pos,
                textcoords="offset points", xytext=(0, int(-font_size * 3)),
                ha='center', va='top', fontsize=font_size + 1,
                fontweight='bold', color='#2c3e50')

    if show_row_counts:
        legend_y = 0.95
        legend_x = 0.02
        sorted_rows = sorted(row_counts.keys())
        for i, row_num in enumerate(sorted_rows):
            count = row_counts[row_num]
            y_pos = legend_y - (i * 0.04)
            ax.text(legend_x, y_pos, f"Row {row_num}: {count} musicians",
                    transform=ax.transAxes, fontsize=font_size,
                    color='#5d6d7e', ha='left', va='top',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                              edgecolor='#d5d8dc', alpha=0.9))

    max_y = max(m['y'] for m in musicians) + 0.8
    min_x = min(m['x'] for m in musicians) - 1.0
    max_x = max(m['x'] for m in musicians) + 1.0
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(-1, max_y)

    ax.set_title(title, fontsize=font_size + 8, fontweight='bold',
                 pad=25, color='#2c3e50')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    if show_plot:
        plt.show()
    plt.close()
    print(f"Layout saved to {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate orchestra seating layout')
    parser.add_argument('-i', '--input', default='orchestra.json', help='Input JSON file')
    parser.add_argument('-o', '--output', default='orchestra.png', help='Output image file')
    parser.add_argument('--no-labels', action='store_true', help='Hide section labels')
    parser.add_argument('--use-images', action='store_true', help='Use instrument images instead of dots')
    parser.add_argument('--show-row-counts', action='store_true', help='Show musician count per row')
    parser.add_argument('--show-image', action='store_true', help='Show the image immediatly, else it just gets stored')
    parser.add_argument('--title', default='Orchestra Seating Layout', help='Give a title to the plot')
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        data = json.load(f)

    musicians, section_info, row_info = generate_positions(data['sections'])
    # print(f"Musicians: \n{musicians}")
    # print(f"Sections: \n{section_info}")
    # print(f"Row: \n{row_info}")

    draw_orchestra(musicians, section_info, row_info, data, args.output,
                   show_labels=not args.no_labels, use_images=args.use_images,
                   show_row_counts=args.show_row_counts,
                   title=args.title, show_plot=args.show_image)


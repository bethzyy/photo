"""
生成 PWA 图标的脚本
需要安装 Pillow: pip install Pillow
"""

import os
from PIL import Image, ImageDraw

def create_icon(size, output_path):
    """创建指定尺寸的图标"""
    # 创建图像
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 背景颜色
    bg_color = (74, 144, 217, 255)  # #4A90D9
    white = (255, 255, 255, 255)

    # 绘制圆角矩形背景
    radius = size // 6
    draw.rounded_rectangle([0, 0, size-1, size-1], radius=radius, fill=bg_color)

    # 计算缩放比例
    scale = size / 512

    # 绘制文件夹（简化版）
    folder_color = (255, 255, 255, 230)

    # 文件夹主体
    f_left = int(107 * scale)
    f_top = int(160 * scale)
    f_right = int(405 * scale)
    f_bottom = int(400 * scale)
    draw.rounded_rectangle([f_left, f_top, f_right, f_bottom], radius=int(10 * scale), fill=folder_color)

    # 绘制照片图标
    photo_bg = bg_color
    p_left = int(160 * scale)
    p_top = int(200 * scale)
    p_right = int(352 * scale)
    p_bottom = int(347 * scale)
    draw.rounded_rectangle([p_left, p_top, p_right, p_bottom], radius=int(11 * scale), fill=photo_bg)

    # 太阳（圆形）
    sun_center = (int(208 * scale), int(253 * scale))
    sun_radius = int(21 * scale)
    draw.ellipse([sun_center[0] - sun_radius, sun_center[1] - sun_radius,
                  sun_center[0] + sun_radius, sun_center[1] + sun_radius], fill=white)

    # 山（三角形）
    mountain_points = [
        (int(160 * scale), int(333 * scale)),
        (int(227 * scale), int(267 * scale)),
        (int(267 * scale), int(307 * scale)),
        (int(320 * scale), int(253 * scale)),
        (int(352 * scale), int(293 * scale)),
        (int(352 * scale), int(333 * scale)),
    ]
    draw.polygon(mountain_points, fill=white)

    # 保存图像
    img.save(output_path, 'PNG')
    print(f'已生成: {output_path}')

def main():
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, 'icons')

    # 确保 icons 目录存在
    os.makedirs(icons_dir, exist_ok=True)

    # 生成图标
    create_icon(192, os.path.join(icons_dir, 'icon-192.png'))
    create_icon(512, os.path.join(icons_dir, 'icon-512.png'))

    print('\n图标生成完成!')
    print(f'图标保存在: {icons_dir}')

if __name__ == '__main__':
    try:
        from PIL import Image, ImageDraw
        main()
    except ImportError:
        print('错误: 需要安装 Pillow 库')
        print('请运行: pip install Pillow')

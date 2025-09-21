import tkinter as tk
import math
import random
from datetime import datetime, timedelta

# 冰岛一周日期和模拟Kp强度数据
days = 7
date_list = [(datetime.now() - timedelta(days=days-i-1)).strftime('%m-%d') for i in range(days)]
kp_values = [random.uniform(1.5, 6.5) for _ in range(days)]

# 丰富冷色系（蓝、青、绿、紫、青绿）
COLD_COLORS = [
    "#b3e0ff", "#80d4ff", "#4dc3ff", "#00bfff", "#00aaff", "#0099cc", "#00eaff", "#00ffd0", "#00ffb2", "#00ff6a",
    "#2affff", "#2adfff", "#2aafff", "#2a6aff", "#6a8fff", "#8f6aff", "#b26aff", "#6a8fb2", "#6affb2", "#6afff6"
]

WIDTH, HEIGHT = 800, 400
BAR_WIDTH = 60
MAX_KP = 9

root = tk.Tk()
root.title("Iceland Aurora Intensity Animation")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

import colorsys
def draw_gradient():
    for i in range(HEIGHT):
        # 梦幻浅蓝紫渐变，饱和度略高
        h = 0.62 + 0.18 * i / HEIGHT  # 0.62~0.8 (浅蓝到浅紫)
        s = 0.55  # 饱和度略高
        v = 0.7 - 0.18 * i / HEIGHT  # 浅色到稍暗
        r, g, b = [int(x*255) for x in colorsys.hsv_to_rgb(h, s, v)]
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, WIDTH, i, fill=color)

draw_gradient()

# 生成星空点
STAR_NUM = 80
star_coords = [(random.randint(10, WIDTH-10), random.randint(10, HEIGHT-10)) for _ in range(STAR_NUM)]
star_objs = []

# 流星参数
METEOR_NUM = 3
meteor_objs = []
meteor_data = []
def spawn_meteor():
    # 随机生成流星起点、方向、长度、速度、弯曲度
    x0 = random.randint(0, WIDTH)
    y0 = random.randint(0, HEIGHT//2)
    angle = random.uniform(math.pi/6, math.pi/3)
    length = random.randint(120, 220)
    speed = random.uniform(10, 18)
    curve = random.uniform(-0.08, 0.08)  # 弯曲度
    color = random.choice(COLD_COLORS)
    meteor_data.append({
        'x0': x0, 'y0': y0, 'angle': angle, 'length': length, 'speed': speed, 'progress': 0.0, 'color': color, 'curve': curve
    })

# 动画帧数据（模拟每日强度波动）
frames = 60
frame = 0
bar_objs = []
text_objs = []

def animate():
    global frame, bar_objs, text_objs, star_objs, meteor_objs
    for obj in bar_objs + text_objs + star_objs + meteor_objs:
        canvas.delete(obj)
    bar_objs = []
    text_objs = []
    star_objs = []
    meteor_objs = []
    # 绘制星空闪烁
    for idx, (sx, sy) in enumerate(star_coords):
        brightness = 160 + int(50 * math.sin(frame * 2 * math.pi / frames + idx))
        star_color = f'#{brightness:02x}{brightness:02x}{220:02x}'
        size = 2 + int(2 * (0.5 + 0.5 * math.sin(frame * 2 * math.pi / frames + idx)))
        star_objs.append(canvas.create_oval(sx-size, sy-size, sx+size, sy+size, fill=star_color, outline=""))
    # 流星动画
    # 随机生成流星
    if frame % 20 == 0 and len(meteor_data) < METEOR_NUM:
        spawn_meteor()
    # 更新流星位置
    for meteor in meteor_data[:]:
        meteor['progress'] += meteor['speed'] * (0.7 + 0.3 * math.sin(frame * 0.2))
        if meteor['progress'] > meteor['length']:
            meteor_data.remove(meteor)
            continue
        x0, y0 = meteor['x0'], meteor['y0']
        curve = meteor['curve']
        # 轨迹有轻微弯曲
        steps = 12
        points = []
        for s in range(steps):
            t = meteor['progress'] * s / steps
            dx = t * math.cos(meteor['angle'])
            dy = t * math.sin(meteor['angle']) + curve * t**1.2
            points.append((x0 + dx, y0 + dy))
        # 亮度和尾部渐变
        for i in range(steps-1):
            fade = int(180 - 160 * i / steps)
            color = meteor['color']
            meteor_objs.append(canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=color, width=4-i//3, capstyle=tk.ROUND))
    # 极光重影波浪动画
    shadow_layers = 5
    for layer in range(shadow_layers):
        points = []
        offset = layer * 8
        opacity = 0.55 - layer * 0.09 + 0.18 * math.sin(frame * 2 * math.pi / frames + layer)
        for i, kp in enumerate(kp_values):
            freq1 = 1.0 + 0.2 * layer
            freq2 = 2.0 + 0.3 * layer
            freq3 = 3.0 + 0.4 * layer
            phase = frame * 2 * math.pi / frames
            kp_anim = kp \
                + 0.5 * math.sin(phase + i * freq1 + layer * 0.5) \
                + 0.2 * math.sin(phase * 1.3 + i * freq2 + layer) \
                + 0.1 * math.sin(phase * 2.1 + i * freq3 - layer)
            kp_anim = max(0, min(kp_anim, MAX_KP))
            color_idx = min(max(int((kp_anim / MAX_KP + 0.2 * math.sin(phase + i + layer)) * (len(COLD_COLORS)-1)), 0), len(COLD_COLORS)-1)
            color = COLD_COLORS[(color_idx + layer*2) % len(COLD_COLORS)]
            x = 80 + i * (BAR_WIDTH + 20)
            y = HEIGHT - 60 - kp_anim / MAX_KP * (HEIGHT - 120) + offset
            points.append((x + BAR_WIDTH//2, y, color, kp_anim))
        # 绘制极光面（多边形填充）
        poly_points = [(x, y) for x, y, _, _ in points]
        # 补充底部点形成封闭区域
        poly_points += [(poly_points[-1][0], HEIGHT-60+offset), (poly_points[0][0], HEIGHT-60+offset)]
        # 计算渐变色（降低饱和度，模拟光影）
        def desaturate(hex_color, factor=0.5):
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            avg = int((r+g+b)/3)
            r = int(r*factor + avg*(1-factor))
            g = int(g*factor + avg*(1-factor))
            b = int(b*factor + avg*(1-factor))
            return f'#{r:02x}{g:02x}{b:02x}'
        # 顶部主色，底部更淡色
        top_color = desaturate(points[0][2], 0.45)
        bottom_color = desaturate(points[0][2], 0.18)
        # 用多层半透明多边形模拟渐变和光影
        # 只绘制前4层渐变面，最后一端不绘制
        for grad in range(4):
            interp = grad/4
            grad_color = desaturate(points[0][2], 0.45-interp*0.27)
            grad_poly = [(x, y + interp*(HEIGHT-60-y+offset)) for x, y, _, _ in points]
            grad_poly += [(grad_poly[-1][0], HEIGHT-60+offset), (grad_poly[0][0], HEIGHT-60+offset)]
            bar_objs.append(canvas.create_polygon(grad_poly, fill=grad_color, outline="", stipple="gray25"))
        # 绘制波浪曲线
        for i in range(len(points)-1):
            x1, y1, c1, _ = points[i]
            x2, y2, c2, _ = points[i+1]
            bar_objs.append(canvas.create_line(x1, y1, x2, y2, fill=c1, width=7-layer*1.5, capstyle=tk.ROUND))
        # 绘制点
        for idx, (x, y, color, _) in enumerate(points):
            # 星星闪烁效果
            star_size = 8 - layer*1.5 + 2 * (0.5 + 0.5 * math.sin(frame * 2 * math.pi / frames + idx + layer))
            brightness = min(255, int(180 + 60 * math.sin(frame * 2 * math.pi / frames + idx + layer)))
            # 用主色调和亮度混合
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = min(255, int(r * 0.7 + brightness * 0.3))
            g = min(255, int(g * 0.7 + brightness * 0.3))
            b = min(255, int(b * 0.7 + brightness * 0.3))
            star_color = f'#{r:02x}{g:02x}{b:02x}'
            # 绘制星星（五角星）
            def star_points(cx, cy, size):
                pts = []
                for i in range(5):
                    angle = math.pi/2 + i * 2*math.pi/5
                    pts.append((cx + size * math.cos(angle), cy - size * math.sin(angle)))
                    angle = math.pi/2 + (i + 0.5) * 2*math.pi/5
                    pts.append((cx + size*0.45 * math.cos(angle), cy - size*0.45 * math.sin(angle)))
                return pts
            bar_objs.append(canvas.create_polygon(star_points(x, y, star_size), fill=star_color, outline="", width=0))
    # 主标签和数值
    for i, kp in enumerate(kp_values):
        kp_anim = kp + 0.5 * math.sin(frame * 2 * math.pi / frames + i)
        kp_anim = max(0, min(kp_anim, MAX_KP))
        color_idx = min(max(int(kp_anim / MAX_KP * (len(COLD_COLORS)-1)), 0), len(COLD_COLORS)-1)
        color = COLD_COLORS[color_idx]
        x = 80 + i * (BAR_WIDTH + 20)
        y = HEIGHT - 60 - kp_anim / MAX_KP * (HEIGHT - 120)
        text_objs.append(canvas.create_text(x + BAR_WIDTH//2, HEIGHT - 22, text=date_list[i], fill="white", font=("Arial", 14)))
        text_objs.append(canvas.create_text(x + BAR_WIDTH//2, y - 18, text=f"{kp_anim:.1f}", fill=color, font=("Arial", 14, "bold")))
    text_objs.append(canvas.create_text(WIDTH//2, 30, text="Iceland Aurora Intensity (Kp) - Last 7 Days", fill="white", font=("Arial", 18, "bold")))
    frame = (frame + 1) % frames
    root.after(80, animate)

animate()
root.mainloop()

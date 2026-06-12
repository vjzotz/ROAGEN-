import customtkinter as ctk
from tkinter import filedialog, messagebox
from bs4 import BeautifulSoup
import uuid
import os
import platform
import re
import sys
import svgwrite

# Render SVG→PNG: intentamos svglib+reportlab (portable), fallback cairosvg
def svg_to_png(svg_path, png_path):
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        drawing = svg2rlg(svg_path)
        if drawing is None:
            raise ValueError("svglib no pudo leer el SVG")
        renderPM.drawToFile(drawing, png_path, fmt="PNG")
        return True
    except Exception as e1:
        try:
            import cairosvg
            cairosvg.svg2png(url=svg_path, write_to=png_path)
            return True
        except Exception as e2:
            raise RuntimeError(
                f"No se pudo exportar PNG.\n"
                f"svglib: {e1}\n"
                f"cairosvg: {e2}"
            )


LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAACEAAAAhCAYAAABX5MJvAAAACXBIWXMAAAsSAAALEgHS3X78AAAFX0lEQVRYhe2XfWxV9RnHP885596297aShRa9xSogE7glvF2gYGmRzFG2OZdJxFhfQqIQjBsOFl+QzUyz8cdeeDFbiKvCYoj4AoFAohKFCi0aay20hQyQlBpssQgoS3uL7T3n6x+3UxCopZM5k32T54/z+maze7+95zi/HJPFty/m2AeD/EF/quwHxWbLD+2Dxgw+den5d6b+amjIvB4T1Nh2nj7Vmrbn1Zy+Wvlf7Uz9925ns/FhD5oTEnswJiZqcG6a9mxGP/zMcy09dFojuzk5vxdSJW+3ggVkFfsArPqwPYJTBOINJBqUOCD68cu1zc4M9dWOj00p2R4qm1IVj+d3fCMQ/ym9ffnLThkVVvsj1xQiDh324wcAHGgTbPdQQjTbWJ5Mjf2wKXykIw+mMkSN3Z980c0d26fQ3o9NK6kO5eb06dUGIv5XPWdK+aeMfdqdk1b7IFrzkweM+LHXhER/ucKETaDajVCJu0AycEcQNNgcwxeAqoyM0+Oq66I0zajLihXsik4tqopOLDjtZWbooxPMPLPht29qKJ6tTYnu3ON1zfosHBcBvAhhuMMOFNYFRjvAd2CFjjsRbSidfEMA8BwYBtWYUGmQFYhQQjUQOjD/dMerfOc+ZjnULf/FA65qKJ95JiV2pLwEcoBH4uyAC/MCB5wIjYumqNwTGdl/UCVzgY4ObPcN3jMEG+UCtL37vQxN0Ffxlxa/PzvsFxLanVs7+qGL1qhpfVpkSJ3oMcoE7Q8YLAdQGsMSBk4JcIBkIA/b6oiWA8QZJQQvGR4JKH3KVvp4wuN+FGfPm/y73vvmvXLAnVo8Yuq2m+YOZ27rFsR6AKFAeNt5IiaGOMc6BVEpc1+NArKdJD/Y48L5gmMEzgiOC44IXXKgQPOEA11yzI954YKaTleVfEOLTY605ZUVFlTVHP0wADHNgkmtdu1IKl4WMkwEMlKgP4IQgz+BjwQCDIcAnpI+XexAGDgm6DEoMVgZo/nXDXp/6ZtXtoVj+p3xVkr6I2traIZFI5OQ4B/1qTOFLox1OPZZhmuiixRmmp0PoWQ8tdtFeD+0LoWoPrXHRow66zUFjDA0AjTY0x0HLciJNNU+tnHl2nq/GedNRtfHlCV1HmuKN214rrdu5c95RwRgXtnSLAsGfXbhfMBg4JYgqvSzXAldbejnygINw6pmxifXLS4r3FK5Y9ex51V/MibPjT3Pvufe+sH02N2zKBuWABht6z0NLQ6bdHvq+ITg3YqDGEJptpF508Y+vWn5Lby5IuvgGNnrg9/L2+Qqv7xKeQY5BpsF+wA1Eg6DIzn/uETf9oRpquFPuuvPJvIWLtvTqQm9OHG9rCxcnEq8ONFRgaISDxrumhz203UMPuajCPdeFBQ5a66LZhg5Nm7LBTybt61yQdHEISRxtbs4qHnLtu4WOaaJrKnFNZS5qCKGFXro5oz0ANxva6aEfGqq/IvJ+V2vLFX0B+FoISRzevy9v1lWDDpW4pqmuabxretlDi1y0y0Nllp6ISg/daOiNaEZbe3XV8L4C9AlCEtVbt4yZ7FrnWNc00jEtctFqFy1z0WYPveah6YY2ewQnKp7+yaUA9BlCEiuXPlY+wrFgiIMmOajKQz8yVB9Cv3TQX1105Laf//FSAS4JQhIL775r2SBDAyxdfbGhJQ560EGHpxev85NJ57JDdCaTTkkisTUD9LiDFjvpRtxfEHvH72j3+gNwyRCSaG1picbj8cqbDNV5aG9OZlv7228N6y9AvyAk0dzcnDM8FjtY53Hmk00bi/4TAOkCe0dfVV1dfX2ko92ZUDbrQL9ecJb6DfFN6rvxB/bf0P8ExOcvOem8wvBi4wAAAABJRU5ErkJggg=="

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ROAGEN(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ROAGEN v1.1")
        self.geometry("480x680")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Ícono: aplicar después de que CTk termine de inicializar la ventana
        self.after(500, self._set_icon)

        self.colors = {
            "bg_dark": "#000000",
            "bg_sub":  "#101010",
            "m1":      "#081700",
            "m2":      "#0b2300",
            "primary": "#FF0000",
            "accent":  "#00FF00",
            "guide":   "#FFA500",
        }

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(10, 5))
        ctk.CTkLabel(self.header_frame, text="ROAGEN", font=("Arial", 36, "bold")).pack()
        ctk.CTkLabel(self.header_frame, text="by vjzotz", font=("Arial", 13, "italic"), text_color="#888").pack()

        self.create_section_label("PARÁMETROS DE RESOLUCIÓN")
        self.dim_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dim_frame.pack(pady=2)

        ctk.CTkLabel(self.dim_frame, text="Composición (Input)", font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=2)
        self.comp_w = ctk.CTkEntry(self.dim_frame, width=120, justify="center")
        self.comp_w.grid(row=1, column=0, padx=5, pady=1); self.comp_w.insert(0, "1920")
        self.comp_h = ctk.CTkEntry(self.dim_frame, width=120, justify="center")
        self.comp_h.grid(row=1, column=1, padx=5, pady=1); self.comp_h.insert(0, "1080")

        ctk.CTkLabel(self.dim_frame, text="Salida (Output)", font=("Arial", 11, "bold")).grid(row=2, column=0, columnspan=2, pady=(10, 2))
        self.out_w = ctk.CTkEntry(self.dim_frame, width=120, justify="center")
        self.out_w.grid(row=3, column=0, padx=5, pady=1); self.out_w.insert(0, "1920")
        self.out_h = ctk.CTkEntry(self.dim_frame, width=120, justify="center")
        self.out_h.grid(row=3, column=1, padx=5, pady=1); self.out_h.insert(0, "1080")

        self.create_section_label("FIRMA TÉCNICA (GRILLA)")
        self.f_tag = ctk.CTkEntry(self, width=280, justify="center")
        self.f_tag.pack(pady=3); self.f_tag.insert(0, "@vjzotz")

        self.create_section_label("DENSIDAD px/m")
        self.density = ctk.CTkEntry(self, width=280, justify="center")
        self.density.pack(pady=3); self.density.insert(0, "256")

        self.create_section_label("ARCHIVOS SVG")
        self.file_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.file_frame.pack(pady=2)

        self.btn_input = ctk.CTkButton(self.file_frame, text="CARGAR SVG INPUT", command=self.load_input, width=280, height=40, fg_color="#34495e")
        self.btn_input.pack(pady=(5, 2))
        self.lbl_input = ctk.CTkLabel(self.file_frame, text="No se cargó archivo", font=("Arial", 10), text_color="#7f8c8d")
        self.lbl_input.pack()

        self.btn_output = ctk.CTkButton(self.file_frame, text="CARGAR SVG OUTPUT (OPCIONAL)", command=self.load_output, width=280, height=40, fg_color="transparent", border_width=1)
        self.btn_output.pack(pady=(5, 2))
        self.lbl_output = ctk.CTkLabel(self.file_frame, text="Modo: Match Input Shape", font=("Arial", 10), text_color="#7f8c8d")
        self.lbl_output.pack()

        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=(8, 8))
        ctk.CTkButton(self.action_frame, text="GENERAR GRILLA", fg_color="#3498db", width=160, height=45, command=self.generate_grid).grid(row=0, column=0, padx=10)
        ctk.CTkButton(self.action_frame, text="GENERAR XML", fg_color="#27ae60", width=160, height=45, font=("Arial", 12, "bold"), command=self.generate_xml).grid(row=0, column=1, padx=10)

        self.input_path = self.output_path = None

    def _set_icon(self):
        """Aplica el ícono embebido en base64 via archivo temporal .ico"""
        try:
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("vjzotz.roagen.1.1")

            import base64, io, tempfile
            from PIL import Image
            img_data = base64.b64decode(LOGO_B64)
            img = Image.open(io.BytesIO(img_data))

            # Guardar como .ico temporal y aplicar con wm_iconbitmap
            tmp = tempfile.NamedTemporaryFile(suffix='.ico', delete=False)
            img.save(tmp.name, format='ICO', sizes=[(32,32),(16,16)])
            tmp.close()
            self.wm_iconbitmap(tmp.name)
            self._tmp_icon = tmp.name  # guardar referencia
        except Exception:
            pass

    def create_section_label(self, text):
        ctk.CTkLabel(self, text=text, font=("Arial", 10, "bold"), text_color="#555").pack(pady=(10, 0))

    def load_input(self):
        p = filedialog.askopenfilename(filetypes=[("SVG files", "*.svg")])
        if p:
            self.input_path = p
            self.lbl_input.configure(text=os.path.basename(p), text_color="#3498db")

    def load_output(self):
        p = filedialog.askopenfilename(filetypes=[("SVG files", "*.svg")])
        if p:
            self.output_path = p
            self.lbl_output.configure(text=os.path.basename(p), text_color="#3498db")

    # ═══════════════════════════════════════════════════════════════
    # UTILIDADES
    # ═══════════════════════════════════════════════════════════════

    def new_id(self):
        return str(uuid.uuid4().int)[:13]

    def fmt(self, v):
        return str(int(v)) if float(v) == int(float(v)) else str(v)

    def is_rect_shape(self, pts):
        if len(pts) != 4:
            return False
        xs = [round(p[0], 4) for p in pts]
        ys = [round(p[1], 4) for p in pts]
        return len(set(xs)) == 2 and len(set(ys)) == 2

    def normalize_rect_pts(self, pts):
        xs = sorted(set(round(p[0], 4) for p in pts))
        ys = sorted(set(round(p[1], 4) for p in pts))
        return [(xs[0], ys[0]), (xs[1], ys[0]), (xs[1], ys[1]), (xs[0], ys[1])]

    def parse_path_d(self, d):
        """
        Parsea 'd' de <path> SVG soportando M,L,H,V,C,S,Z absolutos y relativos.
        Curvas Bezier se aproximan con 32 puntos.
        Retorna lista de (x,y) o None si el path está vacío.
        """
        CURVE_SAMPLES = 32

        def bezier_cubic(p0, p1, p2, p3, n):
            pts = []
            for i in range(n + 1):
                t = i / n; mt = 1 - t
                x = mt**3*p0[0] + 3*mt**2*t*p1[0] + 3*mt*t**2*p2[0] + t**3*p3[0]
                y = mt**3*p0[1] + 3*mt**2*t*p1[1] + 3*mt*t**2*p2[1] + t**3*p3[1]
                pts.append((x, y))
            return pts

        tokens = re.findall(r"[MmLlHhVvCcSsZz]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", d)
        pts = []; i = 0; cmd = 'M'
        cx, cy = 0.0, 0.0
        start_x, start_y = 0.0, 0.0
        last_cp = None

        while i < len(tokens):
            t = tokens[i]
            if re.match(r"[MmLlHhVvCcSsZz]", t):
                cmd = t; i += 1; continue
            try:
                if cmd == 'M':
                    x,y=float(tokens[i]),float(tokens[i+1])
                    pts.append((x,y)); cx,cy=x,y; start_x,start_y=x,y; last_cp=None; i+=2; cmd='L'
                elif cmd == 'm':
                    x,y=cx+float(tokens[i]),cy+float(tokens[i+1])
                    pts.append((x,y)); cx,cy=x,y; start_x,start_y=x,y; last_cp=None; i+=2; cmd='l'
                elif cmd == 'L':
                    x,y=float(tokens[i]),float(tokens[i+1])
                    pts.append((x,y)); cx,cy=x,y; last_cp=None; i+=2
                elif cmd == 'l':
                    x,y=cx+float(tokens[i]),cy+float(tokens[i+1])
                    pts.append((x,y)); cx,cy=x,y; last_cp=None; i+=2
                elif cmd == 'H':
                    x=float(tokens[i]); pts.append((x,cy)); cx=x; last_cp=None; i+=1
                elif cmd == 'h':
                    x=cx+float(tokens[i]); pts.append((x,cy)); cx=x; last_cp=None; i+=1
                elif cmd == 'V':
                    y=float(tokens[i]); pts.append((cx,y)); cy=y; last_cp=None; i+=1
                elif cmd == 'v':
                    y=cy+float(tokens[i]); pts.append((cx,y)); cy=y; last_cp=None; i+=1
                elif cmd == 'C':
                    x1,y1=float(tokens[i]),float(tokens[i+1])
                    x2,y2=float(tokens[i+2]),float(tokens[i+3])
                    x,y=float(tokens[i+4]),float(tokens[i+5])
                    pts.extend(bezier_cubic((cx,cy),(x1,y1),(x2,y2),(x,y),CURVE_SAMPLES)[1:])
                    last_cp=(x2,y2); cx,cy=x,y; i+=6
                elif cmd == 'c':
                    x1,y1=cx+float(tokens[i]),cy+float(tokens[i+1])
                    x2,y2=cx+float(tokens[i+2]),cy+float(tokens[i+3])
                    x,y=cx+float(tokens[i+4]),cy+float(tokens[i+5])
                    pts.extend(bezier_cubic((cx,cy),(x1,y1),(x2,y2),(x,y),CURVE_SAMPLES)[1:])
                    last_cp=(x2,y2); cx,cy=x,y; i+=6
                elif cmd == 'S':
                    rx=2*cx-last_cp[0] if last_cp else cx
                    ry=2*cy-last_cp[1] if last_cp else cy
                    x2,y2=float(tokens[i]),float(tokens[i+1])
                    x,y=float(tokens[i+2]),float(tokens[i+3])
                    pts.extend(bezier_cubic((cx,cy),(rx,ry),(x2,y2),(x,y),CURVE_SAMPLES)[1:])
                    last_cp=(x2,y2); cx,cy=x,y; i+=4
                elif cmd == 's':
                    rx=2*cx-last_cp[0] if last_cp else cx
                    ry=2*cy-last_cp[1] if last_cp else cy
                    x2,y2=cx+float(tokens[i]),cy+float(tokens[i+1])
                    x,y=cx+float(tokens[i+2]),cy+float(tokens[i+3])
                    pts.extend(bezier_cubic((cx,cy),(rx,ry),(x2,y2),(x,y),CURVE_SAMPLES)[1:])
                    last_cp=(x2,y2); cx,cy=x,y; i+=4
                elif cmd in ('Z','z'):
                    i+=1; continue
                else:
                    i+=1
            except (IndexError, ValueError):
                i+=1

        if len(pts) > 1 and pts[0] == pts[-1]:
            pts = pts[:-1]
        return pts if len(pts) >= 3 else None

    def ellipse_to_polygon(self, cx, cy, rx, ry, n=32):
        """Aproxima una elipse como polígono de n puntos."""
        import math
        return [(cx + rx * math.cos(2*math.pi*i/n),
                 cy + ry * math.sin(2*math.pi*i/n)) for i in range(n)]

    # ═══════════════════════════════════════════════════════════════
    # PARSEO SVG
    # ═══════════════════════════════════════════════════════════════

    def apply_transform(self, pts, transform_str):
        """
        Aplica un atributo transform SVG a una lista de puntos.
        Soporta: translate, rotate, scale, matrix y combinaciones.
        """
        import math

        def mat_mul(m, p):
            """Multiplica matriz 2x3 por punto (x,y)."""
            x = m[0]*p[0] + m[2]*p[1] + m[4]
            y = m[1]*p[0] + m[3]*p[1] + m[5]
            return (x, y)

        def mat_compose(a, b):
            """Compone dos matrices 2x3: resultado = a * b."""
            return [
                a[0]*b[0] + a[2]*b[1],
                a[1]*b[0] + a[3]*b[1],
                a[0]*b[2] + a[2]*b[3],
                a[1]*b[2] + a[3]*b[3],
                a[0]*b[4] + a[2]*b[5] + a[4],
                a[1]*b[4] + a[3]*b[5] + a[5],
            ]

        # Matriz identidad
        matrix = [1, 0, 0, 1, 0, 0]

        # Parsear cada transformación en orden
        for m in re.finditer(r'(matrix|translate|rotate|scale|skewX|skewY)\s*\(([^)]+)\)', transform_str):
            op = m.group(1)
            args = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", m.group(2))]

            if op == 'matrix' and len(args) >= 6:
                t = args[:6]
            elif op == 'translate':
                tx = args[0] if len(args) > 0 else 0
                ty = args[1] if len(args) > 1 else 0
                t = [1, 0, 0, 1, tx, ty]
            elif op == 'rotate':
                angle = math.radians(args[0])
                cx = args[1] if len(args) > 1 else 0
                cy = args[2] if len(args) > 2 else 0
                cos_a, sin_a = math.cos(angle), math.sin(angle)
                # rotate(a, cx, cy) = translate(cx,cy) * rotate(a) * translate(-cx,-cy)
                t = [cos_a, sin_a, -sin_a, cos_a,
                     cx - cos_a*cx + sin_a*cy,
                     cy - sin_a*cx - cos_a*cy]
            elif op == 'scale':
                sx = args[0] if len(args) > 0 else 1
                sy = args[1] if len(args) > 1 else sx
                t = [sx, 0, 0, sy, 0, 0]
            elif op == 'skewX':
                t = [1, 0, math.tan(math.radians(args[0])), 1, 0, 0]
            elif op == 'skewY':
                t = [1, math.tan(math.radians(args[0])), 0, 1, 0, 0]
            else:
                continue

            matrix = mat_compose(matrix, t)

        return [mat_mul(matrix, p) for p in pts]

    def resample_polygon(self, pts, max_pts=64):
        """Reduce un polígono a max_pts puntos manteniendo la forma lo más fiel posible."""
        if len(pts) <= max_pts:
            return pts
        import math
        # Calcular longitud total del perímetro
        def dist(a, b): return math.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2)
        n = len(pts)
        perimeter = sum(dist(pts[i], pts[(i+1)%n]) for i in range(n))
        step = perimeter / max_pts
        result = [pts[0]]
        accum = 0.0
        i = 0
        while len(result) < max_pts:
            j = (i+1) % n
            seg = dist(pts[i], pts[j])
            if accum + seg >= step:
                t = (step - accum) / seg
                x = pts[i][0] + t*(pts[j][0]-pts[i][0])
                y = pts[i][1] + t*(pts[j][1]-pts[i][1])
                result.append((x, y))
                accum = 0.0
                pts = list(pts)
                pts.insert(j, (x, y))
                n = len(pts)
                i = j
            else:
                accum += seg
                i = j
                if i == 0:
                    break
        return result

    def get_shapes(self, svg_path):
        if not svg_path:
            return []
        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')

            stroke_paths = set()
            for g in soup.find_all('g'):
                siblings = g.find_all(['rect', 'polygon', 'path'], recursive=False)
                has_shape = any(s.name in ['rect', 'polygon'] for s in siblings)
                has_path  = any(s.name == 'path' for s in siblings)
                if has_shape and has_path:
                    for p in g.find_all('path', recursive=False):
                        stroke_paths.add(id(p))

            res = []; idx = 0
            for e in soup.find_all(['rect', 'polygon', 'path', 'ellipse']):
                idx += 1
                name = e.get('id') or f"Slice_{idx}"

                transform_str = e.get('transform', '')

                if e.name == 'rect':
                    x, y = float(e.get('x', 0)), float(e.get('y', 0))
                    w, h  = float(e.get('width', 0)), float(e.get('height', 0))
                    if w > 0 and h > 0:
                        pts = [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
                        if transform_str:
                            pts = self.apply_transform(pts, transform_str)
                        # Un rect transformado puede ya no ser axis-aligned
                        if self.is_rect_shape(pts):
                            res.append({'pts': self.normalize_rect_pts(pts), 'name': name, 'type': 'rect'})
                        else:
                            res.append({'pts': pts, 'name': name, 'type': 'polygon'})

                elif e.name == 'polygon':
                    raw = e.get('points', '').replace(',', ' ')
                    c = re.findall(r"[-+]?\d*\.?\d+", raw)
                    if len(c) < 6:
                        continue
                    pts = [(float(c[i]), float(c[i+1])) for i in range(0, len(c)-1, 2)]
                    if len(pts) > 1 and pts[0] == pts[-1]:
                        pts = pts[:-1]
                    if transform_str:
                        pts = self.apply_transform(pts, transform_str)
                    if self.is_rect_shape(pts):
                        res.append({'pts': self.normalize_rect_pts(pts), 'name': name, 'type': 'rect'})
                    else:
                        res.append({'pts': pts, 'name': name, 'type': 'polygon'})

                elif e.name == 'path':
                    if id(e) in stroke_paths:
                        continue
                    pts = self.parse_path_d(e.get('d', ''))
                    if not pts or len(pts) < 3:
                        continue
                    if transform_str:
                        pts = self.apply_transform(pts, transform_str)
                    pts = self.resample_polygon(pts, max_pts=64)
                    if self.is_rect_shape(pts):
                        res.append({'pts': self.normalize_rect_pts(pts), 'name': name, 'type': 'rect'})
                    else:
                        res.append({'pts': pts, 'name': name, 'type': 'polygon'})

                elif e.name == 'ellipse':
                    cx = float(e.get('cx', 0)); cy = float(e.get('cy', 0))
                    rx = float(e.get('rx', 0)); ry = float(e.get('ry', 0))
                    if rx == 0 or ry == 0:
                        continue
                    pts = self.ellipse_to_polygon(cx, cy, rx, ry)
                    if transform_str:
                        pts = self.apply_transform(pts, transform_str)
                    res.append({'pts': pts, 'name': name, 'type': 'polygon'})

            return res
        except Exception as ex:
            messagebox.showerror("Error SVG", str(ex))
            return []

    # ═══════════════════════════════════════════════════════════════
    # BLOQUES XML
    # ═══════════════════════════════════════════════════════════════

    def param_range(self, name, default, value, min_v, max_v, indent, alt_name=None):
        alt = f' altName="{alt_name}"' if alt_name else ''
        t = '\t' * indent
        return '\n'.join([
            f'{t}<ParamRange name="{name}"{alt} T="DOUBLE" default="{default}" value="{value}">',
            f'{t}\t<PhaseSourceStatic name="PhaseSourceStatic"/>',
            f'{t}\t<BehaviourDouble name="BehaviourDouble"/>',
            f'{t}\t<ValueRange name="defaultRange" min="{min_v}" max="{max_v}"/>',
            f'{t}\t<ValueRange name="minMax" min="{min_v}" max="{max_v}"/>',
            f'{t}\t<ValueRange name="startStop" min="{min_v}" max="{max_v}"/>',
            f'{t}</ParamRange>',
        ])

    def screen_output_params(self, indent):
        t = '\t' * indent
        lines = [f'{t}<Params name="Output">']
        for name, d, v, mn, mx in [
            ("Opacity",    "1", "1", "0",  "1"),
            ("Brightness", "0", "0", "-1", "1"),
            ("Contrast",   "0", "0", "-1", "1"),
            ("Red",        "0", "0", "-1", "1"),
            ("Green",      "0", "0", "-1", "1"),
            ("Blue",       "0", "0", "-1", "1"),
        ]:
            lines.append(self.param_range(name, d, v, mn, mx, indent+1))
        lines.append(f'{t}</Params>')
        return '\n'.join(lines)

    def slice_output_params(self, indent, include_softedge=True):
        t = '\t' * indent
        lines = [f'{t}<Params name="Output">',
                 f'{t}\t<Param name="Flip" T="UINT8" default="0" value="0"/>']
        for name, d, v, mn, mx in [
            ("Brightness", "0", "0", "-1", "1"),
            ("Contrast",   "0", "0", "-1", "1"),
            ("Red",        "0", "0", "-1", "1"),
            ("Green",      "0", "0", "-1", "1"),
            ("Blue",       "0", "0", "-1", "1"),
        ]:
            lines.append(self.param_range(name, d, v, mn, mx, indent+1))
        lines += [
            f'{t}\t<Param name="Is Key" T="BOOL" default="0" value="0"/>',
            f'{t}\t<Param name="Black BG" T="BOOL" default="0" value="0"/>',
        ]
        if include_softedge:
            se_max = "0.4000000000000000222"
            lines.append(self.param_range("BRed",   "0", "0", "0", se_max, indent+1, alt_name="Red"))
            lines.append(self.param_range("BGreen",  "0", "0", "0", se_max, indent+1, alt_name="Green"))
            lines.append(self.param_range("BBlue",   "0", "0", "0", se_max, indent+1, alt_name="Blue"))
        lines.append(f'{t}</Params>')
        return '\n'.join(lines)

    def warper_block(self, pts, indent):
        t = '\t' * indent
        x0,y0 = pts[0]; x1,y1 = pts[1]; x2,y2 = pts[2]; x3,y3 = pts[3]
        def lerp(a, b, f): return a + (b-a)*f
        vertices = []
        for row in range(4):
            tr = row/3.0
            for col in range(4):
                tc = col/3.0
                vertices.append((
                    lerp(lerp(x0,x1,tc), lerp(x3,x2,tc), tr),
                    lerp(lerp(y0,y1,tc), lerp(y3,y2,tc), tr),
                ))
        lines = [
            f'{t}<Warper>',
            f'{t}\t<Params name="Warper">',
            f'{t}\t\t<ParamChoice name="Point Mode" default="PM_LINEAR" value="PM_LINEAR" storeChoices="0"/>',
            f'{t}\t\t<Param name="Flip" T="UINT8" default="0" value="0"/>',
            f'{t}\t</Params>',
            f'{t}\t<BezierWarper controlWidth="4" controlHeight="4">',
            f'{t}\t\t<vertices>',
        ]
        for vx,vy in vertices:
            lines.append(f'{t}\t\t\t<v x="{vx}" y="{vy}"/>')
        lines += [f'{t}\t\t</vertices>', f'{t}\t</BezierWarper>', f'{t}\t<Homography>', f'{t}\t\t<src>']
        for p in pts: lines.append(f'{t}\t\t\t<v x="{p[0]}" y="{p[1]}"/>')
        lines += [f'{t}\t\t</src>', f'{t}\t\t<dst>']
        for p in pts: lines.append(f'{t}\t\t\t<v x="{p[0]}" y="{p[1]}"/>')
        lines += [f'{t}\t\t</dst>', f'{t}\t</Homography>', f'{t}</Warper>']
        return '\n'.join(lines)

    def softedging_block(self):
        lines = ['\t\t<SoftEdging>', '\t\t\t<Params name="Soft Edge">']
        lines.append(self.param_range("Gamma Red",   "2",   "2",                    "1", "3", 4))
        lines.append(self.param_range("Gamma Green", "2",   "2",                    "1", "3", 4))
        lines.append(self.param_range("Gamma Blue",  "2",   "2",                    "1", "3", 4))
        lines.append(self.param_range("Gamma",       "1",   "1",                    "0", "1", 4))
        lines.append(self.param_range("Luminance",   "0.5", "0.5",                  "0", "1", 4))
        lines.append(self.param_range("Power",       "2",   "1.999999999999999778",
                                      "0.10000000000000000555", "7", 4))
        lines += ['\t\t\t</Params>', '\t\t</SoftEdging>']
        return '\n'.join(lines)

    # ═══════════════════════════════════════════════════════════════
    # GENERAR GRILLA
    # ═══════════════════════════════════════════════════════════════

    def generate_grid(self):
        if not self.input_path:
            messagebox.showwarning("Atención", "Cargá un SVG de input primero.")
            return
        try:
            cw, ch = int(self.comp_w.get()), int(self.comp_h.get())
            shapes = self.get_shapes(self.input_path)
            if not shapes:
                messagebox.showwarning("Atención", "No se encontraron formas en el SVG.")
                return
            tag = self.f_tag.get()
            save_path = filedialog.asksaveasfilename(
                defaultextension=".svg", filetypes=[("SVG files", "*.svg")]
            )
            if not save_path:
                return

            dwg = svgwrite.Drawing(save_path, size=(cw, ch), profile='full')
            c = self.colors
            dwg.add(dwg.rect(insert=(0,0), size=(cw,ch), fill=c["bg_dark"]))
            try:
                px_per_m = int(self.density.get().strip())
            except:
                px_per_m = 256
            # grid_unit = 1 modulo de la densidad (1/4 de px/m, limitado entre 32 y 128)
            grid_unit = px_per_m // 4
            while grid_unit > 128: grid_unit //= 2
            while grid_unit < 32:  grid_unit *= 2
            margin = grid_unit

            for s in shapes:
                pts = s['pts']
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                min_x, max_x = int(min(xs)), int(max(xs))
                min_y, max_y = int(min(ys)), int(max(ys))
                # Centroide real de la forma (no el centro de la bounding box)
                n_pts = len(pts)
                cx = sum(p[0] for p in pts) / n_pts
                cy = sum(p[1] for p in pts) / n_pts
                # Radio basado en el área real, no en la bounding box
                import math
                # Área por fórmula de Shoelace
                area = abs(sum(pts[i][0]*(pts[(i+1)%n_pts][1]-pts[(i-1)%n_pts][1]) 
                               for i in range(n_pts))) / 2
                radius = math.sqrt(area / math.pi)
                m_id = f"m_{uuid.uuid4().hex[:6]}"
                mask = dwg.defs.add(dwg.clipPath(id=m_id))
                mask.add(dwg.polygon(points=pts))
                group = dwg.g(clip_path=f"url(#{m_id})")
                for y in range(min_y, max_y+grid_unit, grid_unit):
                    for x in range(min_x, max_x+grid_unit, grid_unit):
                        is_m = (x < min_x+margin or x >= max_x-margin or
                                y < min_y+margin or y >= max_y-margin)
                        is_p = (x//grid_unit + y//grid_unit) % 2 == 0
                        fill_c = (c['m1'] if is_p else c['m2']) if is_m else (c['bg_dark'] if is_p else c['bg_sub'])
                        group.add(dwg.rect(insert=(x,y), size=(grid_unit,grid_unit), fill=fill_c))
                group.add(dwg.circle(center=(cx,cy), r=radius, stroke=c['primary'], fill="none", stroke_width=1))
                for y in range(min_y, max_y+grid_unit, grid_unit):
                    group.add(dwg.line(start=(min_x,y), end=(max_x,y), stroke=c['primary'], opacity=0.3))
                for x in range(min_x, max_x+grid_unit, grid_unit):
                    group.add(dwg.line(start=(x,min_y), end=(x,max_y), stroke=c['primary'], opacity=0.3))
                group.add(dwg.line(start=(min_x,cy), end=(max_x,cy), stroke=c['guide'], stroke_width=2))
                group.add(dwg.line(start=(cx,min_y), end=(cx,max_y), stroke=c['guide'], stroke_width=2))
                dwg.add(group)
                dwg.add(dwg.polygon(points=pts, id=s['name'].replace(' ', '_'), stroke=c['accent'], fill="none", stroke_width=4))
                dwg.add(dwg.text(s['name'].upper(), insert=(cx,cy), font_size="24px", fill="#fff",
                                 text_anchor="middle", font_family="Arial", font_weight="bold"))

            dwg.add(dwg.text(tag, insert=(cw/2, ch-20), font_size="15px", fill=c['primary'],
                             text_anchor="middle", font_weight="bold"))
            dwg.save()

            # Render PNG con fallback automático
            png_path = save_path.replace(".svg", ".png")
            try:
                svg_to_png(save_path, png_path)
                msg = f"SVG y PNG generados:\n{os.path.basename(save_path)}"
            except Exception as png_err:
                msg = f"SVG generado (PNG falló: {png_err}):\n{os.path.basename(save_path)}"

            if platform.system() == "Windows":
                os.startfile(os.path.dirname(save_path))
            messagebox.showinfo("Grilla generada", msg)

        except Exception as ex:
            messagebox.showerror("Error Grilla", str(ex))

    # ═══════════════════════════════════════════════════════════════
    # GENERAR XML
    # ═══════════════════════════════════════════════════════════════

    def generate_xml(self):
        if not self.input_path:
            messagebox.showwarning("Atención", "Cargá un SVG de input primero.")
            return

        cw = self.comp_w.get().strip(); ch = self.comp_h.get().strip()
        ow = self.out_w.get().strip();  oh = self.out_h.get().strip()
        if not all([cw, ch, ow, oh]):
            messagebox.showwarning("Atención", "Completá todos los campos de resolución.")
            return

        in_s  = self.get_shapes(self.input_path)
        out_s = self.get_shapes(self.output_path) if self.output_path else in_s
        if not in_s:
            return

        screen_id = self.new_id()
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<XmlState name="ROAGEN">',
            '\t<versionInfo name="Resolume Arena" majorVersion="7" minorVersion="26" microVersion="1" revision="7833"/>',
            '\t<ScreenSetup name="ScreenSetup">',
            '\t\t<Params name="ScreenSetupParams"/>',
            f'\t\t<CurrentCompositionTextureSize width="{cw}" height="{ch}"/>',
            '\t\t<screens>',
            f'\t\t\t<Screen name="Screen 1" uniqueId="{screen_id}">',
            '\t\t\t\t<Params name="Params">',
            '\t\t\t\t\t<Param name="Name" T="STRING" default="" value="Screen 1"/>',
            '\t\t\t\t\t<Param name="Enabled" T="BOOL" default="1" value="1"/>',
            '\t\t\t\t\t<Param name="Hidden" T="BOOL" default="0" value="0"/>',
            '\t\t\t\t</Params>',
            self.screen_output_params(4),
            '\t\t\t\t<guides>',
            '\t\t\t\t\t<ScreenGuide name="ScreenGuide" type="0">',
            '\t\t\t\t\t\t<Params name="Params">',
            '\t\t\t\t\t\t\t<ParamPixels name="Image"/>',
            self.param_range("Opacity", "0.25", "0.25", "0", "1", 7),
            '\t\t\t\t\t\t</Params>',
            '\t\t\t\t\t</ScreenGuide>',
            '\t\t\t\t\t<ScreenGuide name="ScreenGuide" type="1">',
            '\t\t\t\t\t\t<Params name="Params">',
            '\t\t\t\t\t\t\t<ParamPixels name="Image"/>',
            self.param_range("Opacity", "0.25", "0.25", "0", "1", 7),
            '\t\t\t\t\t\t</Params>',
            '\t\t\t\t\t</ScreenGuide>',
            '\t\t\t\t</guides>',
            '\t\t\t\t<layers>',
        ]

        for i, shape_in in enumerate(in_s):
            shape_out  = out_s[i] if i < len(out_s) else shape_in
            pts_in     = shape_in['pts']
            pts_out    = shape_out['pts']
            is_rect    = (shape_in['type'] == 'rect')
            tag        = 'Slice' if is_rect else 'Polygon'
            uid        = self.new_id()
            name       = shape_in['name']

            if is_rect:
                rect_in_pts  = pts_in
                rect_out_pts = pts_out
            else:
                def bbox(pts):
                    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
                    return [(min(xs),min(ys)),(max(xs),min(ys)),(max(xs),max(ys)),(min(xs),max(ys))]
                rect_in_pts  = bbox(pts_in)
                rect_out_pts = bbox(pts_out)

            virgin = '' if is_rect else ' IsVirgin="0"'
            lines.append(f'\t\t\t\t\t<{tag} uniqueId="{uid}"{virgin}>')
            lines += [
                '\t\t\t\t\t\t<Params name="Common">',
                f'\t\t\t\t\t\t\t<Param name="Name" T="STRING" default="Layer" value="{name}"/>',
                '\t\t\t\t\t\t\t<Param name="Enabled" T="BOOL" default="1" value="1"/>',
                '\t\t\t\t\t\t</Params>',
            ]
            inp = [
                '\t\t\t\t\t\t<Params name="Input">',
                '\t\t\t\t\t\t\t<ParamChoice name="Input Source" default="0:1" value="0:1" storeChoices="0"/>',
                '\t\t\t\t\t\t\t<Param name="Input Opacity" T="BOOL" default="1" value="1"/>',
                '\t\t\t\t\t\t\t<Param name="Input Bypass/Solo" T="BOOL" default="1" value="1"/>',
            ]
            if is_rect:
                inp.append('\t\t\t\t\t\t\t<Param name="SoftEdgeEnable" T="BOOL" default="0" value="0"/>')
            inp.append('\t\t\t\t\t\t</Params>')
            lines += inp
            lines.append(self.slice_output_params(6, include_softedge=is_rect))

            lines.append('\t\t\t\t\t\t<InputRect orientation="0">')
            for p in rect_in_pts:
                lines.append(f'\t\t\t\t\t\t\t<v x="{self.fmt(p[0])}" y="{self.fmt(p[1])}"/>')
            lines.append('\t\t\t\t\t\t</InputRect>')

            lines.append('\t\t\t\t\t\t<OutputRect orientation="0">')
            for p in rect_out_pts:
                lines.append(f'\t\t\t\t\t\t\t<v x="{self.fmt(p[0])}" y="{self.fmt(p[1])}"/>')
            lines.append('\t\t\t\t\t\t</OutputRect>')

            if is_rect:
                lines.append(self.warper_block(rect_out_pts, 6))
            else:
                for mode, pts in [("Input", pts_in), ("Output", pts_out)]:
                    lines.append(f'\t\t\t\t\t\t<{mode}Contour closed="1">')
                    lines.append('\t\t\t\t\t\t\t<points>')
                    for p in pts:
                        lines.append(f'\t\t\t\t\t\t\t\t<v x="{self.fmt(p[0])}" y="{self.fmt(p[1])}"/>')
                    lines.append('\t\t\t\t\t\t\t</points>')
                    lines.append(f'\t\t\t\t\t\t\t<segments>{"L"*len(pts)}</segments>')
                    lines.append(f'\t\t\t\t\t\t</{mode}Contour>')

            lines.append(f'\t\t\t\t\t</{tag}>')

        id_hash = str(uuid.uuid4().int)[:20]
        lines += [
            '\t\t\t\t</layers>',
            '\t\t\t\t<OutputDevice>',
            f'\t\t\t\t\t<OutputDeviceVirtual name="Screen 1" deviceId="VirtualScreen 1" idHash="{id_hash}" width="{ow}" height="{oh}">',
            '\t\t\t\t\t\t<Params name="Params">',
            self.param_range("Width",  "1920", ow, "1", "32768", 7),
            self.param_range("Height", "1080", oh, "1", "32768", 7),
            '\t\t\t\t\t\t</Params>',
            '\t\t\t\t\t</OutputDeviceVirtual>',
            '\t\t\t\t</OutputDevice>',
            '\t\t\t</Screen>',
            '\t\t</screens>',
            self.softedging_block(),
            '\t</ScreenSetup>',
            '</XmlState>',
        ]

        save_path = filedialog.asksaveasfilename(
            defaultextension=".xml", filetypes=[("XML files", "*.xml")],
            initialfile="output_resolume.xml"
        )
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            if platform.system() == "Windows":
                os.startfile(os.path.dirname(save_path))
            messagebox.showinfo("Éxito", f"XML generado:\n{os.path.basename(save_path)}")


if __name__ == "__main__":
    ROAGEN().mainloop()
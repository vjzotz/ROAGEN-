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


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ROAGEN(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ROAGEN v1.5")
        self.geometry("480x680")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Ícono: aplicar después de que CTk termine de inicializar la ventana
        self.after(0, self._set_icon)

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
        self.header_frame.pack(pady=(20, 10))
        ctk.CTkLabel(self.header_frame, text="ROAGEN", font=("Arial", 36, "bold")).pack()
        ctk.CTkLabel(self.header_frame, text="by vjzotz", font=("Arial", 13, "italic"), text_color="#888").pack()

        self.create_section_label("PARÁMETROS DE RESOLUCIÓN")
        self.dim_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dim_frame.pack(pady=5)

        ctk.CTkLabel(self.dim_frame, text="Composición (Input)", font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=2)
        self.comp_w = ctk.CTkEntry(self.dim_frame, width=120, justify="center")
        self.comp_w.grid(row=1, column=0, padx=5); self.comp_w.insert(0, "1920")
        self.comp_h = ctk.CTkEntry(self.dim_frame, width=120, justify="center")
        self.comp_h.grid(row=1, column=1, padx=5); self.comp_h.insert(0, "1080")

        ctk.CTkLabel(self.dim_frame, text="Salida (Output)", font=("Arial", 11, "bold")).grid(row=2, column=0, columnspan=2, pady=(10, 2))
        self.out_w = ctk.CTkEntry(self.dim_frame, width=120, justify="center")
        self.out_w.grid(row=3, column=0, padx=5); self.out_w.insert(0, "1920")
        self.out_h = ctk.CTkEntry(self.dim_frame, width=120, justify="center")
        self.out_h.grid(row=3, column=1, padx=5); self.out_h.insert(0, "1080")

        self.create_section_label("FIRMA TÉCNICA (GRILLA)")
        self.f_tag = ctk.CTkEntry(self, width=280, justify="center")
        self.f_tag.pack(pady=5); self.f_tag.insert(0, "@vjzotz")

        self.create_section_label("ARCHIVOS SVG")
        self.file_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.file_frame.pack(pady=5)

        self.btn_input = ctk.CTkButton(self.file_frame, text="CARGAR SVG INPUT", command=self.load_input, width=280, height=40, fg_color="#34495e")
        self.btn_input.pack(pady=(10, 2))
        self.lbl_input = ctk.CTkLabel(self.file_frame, text="No se cargó archivo", font=("Arial", 10), text_color="#7f8c8d")
        self.lbl_input.pack()

        self.btn_output = ctk.CTkButton(self.file_frame, text="CARGAR SVG OUTPUT (OPCIONAL)", command=self.load_output, width=280, height=40, fg_color="transparent", border_width=1)
        self.btn_output.pack(pady=(10, 2))
        self.lbl_output = ctk.CTkLabel(self.file_frame, text="Modo: Match Input Shape", font=("Arial", 10), text_color="#7f8c8d")
        self.lbl_output.pack()

        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=(25, 20))
        ctk.CTkButton(self.action_frame, text="GENERAR GRILLA", fg_color="#3498db", width=160, height=45, command=self.generate_grid).grid(row=0, column=0, padx=10)
        ctk.CTkButton(self.action_frame, text="GENERAR XML", fg_color="#27ae60", width=160, height=45, font=("Arial", 12, "bold"), command=self.generate_xml).grid(row=0, column=1, padx=10)

        self.input_path = self.output_path = None

    def _set_icon(self):
        """Aplica el ícono a la ventana y taskbar de Windows correctamente con CTk."""
        ico = resource_path("logo.ico")
        try:
            # wm_iconbitmap funciona mejor que iconbitmap con CustomTkinter
            self.wm_iconbitmap(ico)
            # En Windows, también forzar el ícono de la taskbar vía ctypes
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("vjzotz.roagen.1.5")
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
        if re.findall(r"[mlhvcsqta]", d):
            return None
        pts = []
        tokens = re.findall(r"[MLHVCSQTAZ]|[-+]?\d*\.?\d+", d)
        i = 0; cmd = 'M'
        while i < len(tokens):
            t = tokens[i]
            if re.match(r"[A-Z]", t):
                cmd = t; i += 1; continue
            if cmd in ('M', 'L'):
                try:
                    pts.append((float(tokens[i]), float(tokens[i+1]))); i += 2
                except:
                    i += 1
            else:
                i += 1
        if len(pts) > 1 and pts[0] == pts[-1]:
            pts = pts[:-1]
        return pts

    # ═══════════════════════════════════════════════════════════════
    # PARSEO SVG
    # ═══════════════════════════════════════════════════════════════

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
            for e in soup.find_all(['rect', 'polygon', 'path']):
                idx += 1
                name = e.get('id') or f"{e.name.capitalize()} {idx}"

                if e.name == 'rect':
                    x, y = float(e.get('x', 0)), float(e.get('y', 0))
                    w, h  = float(e.get('width', 0)), float(e.get('height', 0))
                    if w > 0 and h > 0:
                        res.append({'pts': [(x,y),(x+w,y),(x+w,y+h),(x,y+h)], 'name': name, 'type': 'rect'})

                elif e.name == 'polygon':
                    raw = e.get('points', '').replace(',', ' ')
                    c = re.findall(r"[-+]?\d*\.?\d+", raw)
                    if len(c) < 6:
                        continue
                    pts = [(float(c[i]), float(c[i+1])) for i in range(0, len(c)-1, 2)]
                    if len(pts) > 1 and pts[0] == pts[-1]:
                        pts = pts[:-1]
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
                    if self.is_rect_shape(pts):
                        res.append({'pts': self.normalize_rect_pts(pts), 'name': name, 'type': 'rect'})
                    else:
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
            grid_unit = 64; margin = grid_unit

            for s in shapes:
                pts = s['pts']
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                min_x, max_x = int(min(xs)), int(max(xs))
                min_y, max_y = int(min(ys)), int(max(ys))
                cx, cy = min_x + (max_x-min_x)/2, min_y + (max_y-min_y)/2
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
                radius = (max_y-min_y)/2
                group.add(dwg.circle(center=(cx,cy), r=radius, stroke=c['primary'], fill="none", stroke_width=1))
                for y in range(min_y, max_y+grid_unit, grid_unit):
                    group.add(dwg.line(start=(min_x,y), end=(max_x,y), stroke=c['primary'], opacity=0.3))
                for x in range(min_x, max_x+grid_unit, grid_unit):
                    group.add(dwg.line(start=(x,min_y), end=(x,max_y), stroke=c['primary'], opacity=0.3))
                group.add(dwg.line(start=(min_x,cy), end=(max_x,cy), stroke=c['guide'], stroke_width=2))
                group.add(dwg.line(start=(cx,min_y), end=(cx,max_y), stroke=c['guide'], stroke_width=2))
                dwg.add(group)
                dwg.add(dwg.polygon(points=pts, stroke=c['accent'], fill="none", stroke_width=4))
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
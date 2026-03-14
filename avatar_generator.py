from PIL import Image, ImageDraw, ImageTk
import random
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, StringVar

VALID_CMAPS = [m for m in plt.colormaps() if not m.endswith(('_r', '_shifted')) 
              and m not in ('flag', 'prism', 'Pastel1', 'Pastel2', 'Accent')]

class RectangleSplitter:
    @staticmethod
    def split_region(x0, y0, x1, y1, split_count, algorithm='random', **kwargs):
        if algorithm == 'complete_down':
            return RectangleSplitter._complete_split(x0, y0, x1, y1, split_count, 'vertical')
        elif algorithm == 'complete_line':
            return RectangleSplitter._complete_split(x0, y0, x1, y1, split_count, 'horizontal')
        elif algorithm == 'random':
            return RectangleSplitter._random_split(x0, y0, x1, y1, split_count)
        elif algorithm == 'average':
            return RectangleSplitter._average_split(x0, y0, x1, y1, split_count, kwargs.get('square_mode', False))
        elif algorithm == 'mondrian':
            return RectangleSplitter._mondrian_split(x0, y0, x1, y1, split_count)
        return [(x0, y0, x1, y1)]

    @staticmethod
    def _random_split(x0, y0, x1, y1, split_count):
        regions = [(x0, y0, x1, y1)]
        for _ in range(split_count-1):
            idx = random.randint(0, len(regions)-1)
            rect = regions.pop(idx)
            
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            if width / height > 1.5:
                split_vertical = True
            elif height / width > 1.5:
                split_vertical = False
            else:
                split_vertical = random.choice([True, False])
                
            if split_vertical:
                split_pos = random.randint(int(rect[0]+width*0.3), int(rect[2]-width*0.3))
                regions.append((rect[0], rect[1], split_pos, rect[3]))
                regions.append((split_pos, rect[1], rect[2], rect[3]))
            else:
                split_pos = random.randint(int(rect[1]+height*0.3), int(rect[3]-height*0.3))
                regions.append((rect[0], rect[1], rect[2], split_pos))
                regions.append((rect[0], split_pos, rect[2], rect[3]))
        return regions

    @staticmethod
    def _complete_split(x0, y0, x1, y1, split_count, direction):
        """完全分割算法"""
        divisions = []
        if direction == 'vertical':
            step = (x1 - x0) / split_count
            return [(x0 + i*step, y0, x0 + (i+1)*step, y1) for i in range(split_count)]
        else:
            step = (y1 - y0) / split_count
            return [(x0, y0 + i*step, x1, y0 + (i+1)*step) for i in range(split_count)]

    @staticmethod
    def _average_split(x0, y0, x1, y1, split_count, square_mode):
        if square_mode:
            # 正方形模式：n×n网格
            n = int(split_count**0.5)
            col_split = row_split = n
        else:
            # 长方形模式：正态分布分割
            base = max(1, int(random.gauss(split_count, split_count*0.2)))
            col_split = min(base, split_count)
            row_split = max(0, split_count - col_split)

        # 生成坐标分割点
        col_step = (x1 - x0) / (2**col_split)
        row_step = (y1 - y0) / (2**row_split)
        
        return [
            (x0 + i*col_step, y0 + j*row_step, 
             x0 + (i+1)*col_step, y0 + (j+1)*row_step)
            for i in range(2**col_split)
            for j in range(2**row_split)
        ]

        regions = []
        col_split = row_split = 0
        
        if square_mode:
            aspect_ratio = (x1 - x0) / (y1 - y0)
            total_splits = split_count * 2
            col_split = min(split_count, int(total_splits * aspect_ratio))
            row_split = split_count - col_split
        else:
            col_split = split_count
            row_split = 0

        col_divisions = [x0 + (x1-x0)*i//(2**col_split) for i in range(1, 2**col_split)]
        col_divisions = [x0] + sorted(col_divisions) + [x1]
        
        row_divisions = [y0 + (y1-y0)*i//(2**row_split) for i in range(1, 2**row_split)]
        row_divisions = [y0] + sorted(row_divisions) + [y1]

        for i in range(len(col_divisions)-1):
            for j in range(len(row_divisions)-1):
                regions.append((
                    col_divisions[i],
                    row_divisions[j],
                    col_divisions[i+1],
                    row_divisions[j+1]
                ))
        return regions

    @staticmethod
    def _mondrian_split(x0, y0, x1, y1, split_count):
        regions = [(x0, y0, x1, y1)]
        for _ in range(split_count):
            idx = random.randint(0, len(regions)-1)
            rect = regions.pop(idx)
            
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            
            if max(width, height) < 100:
                regions.append(rect)
                continue
                
            split_vertical = random.random() < 0.6 if width > height else random.random() < 0.4
            if split_vertical:
                split_pos = random.randint(int(rect[0]+width*0.2), int(rect[2]-width*0.2))
                regions.append((rect[0], rect[1], split_pos, rect[3]))
                regions.append((split_pos, rect[1], rect[2], rect[3]))
            else:
                split_pos = random.randint(int(rect[1]+height*0.2), int(rect[3]-height*0.2))
                regions.append((rect[0], rect[1], rect[2], split_pos))
                regions.append((rect[0], split_pos, rect[2], rect[3]))
        return regions

def generate_avatar(output_path, size, color_mode='colormap', split_count=5, 
                   colormap_name='viridis', border_size=0, split_algorithm='random', **kwargs):  # 修改默认边框为0
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)
    
    actual_splits = max(1, int(split_count))
    regions = RectangleSplitter.split_region(0, 0, size, size, actual_splits, 
                                           algorithm=split_algorithm, **kwargs)
    
    for rect in regions:
        if color_mode == 'colormap':
            if ',' in colormap_name:
                cmap = cm.get_cmap(random.choice(colormap_name.split(',')))
            else:
                cmap = cm.get_cmap(colormap_name)
            color = cmap(random.random())[:3]
            color = tuple(int(255 * x) for x in color)
        elif color_mode == 'random':
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            gray = random.randint(0, 255)
            color = (gray, gray, gray)
        
        draw.rectangle(rect, fill=color)
        # 完全移除以下边框绘制代码
        # if border_size > 0:
        #     border_color = (0, 0, 0) if color_mode != 'grayscale' else (255, 255, 255)
        #     draw.rectangle([
        #         rect[0] - border_size,
        #         rect[1] - border_size,
        #         rect[2] + border_size,
        #         rect[3] + border_size
        #     ], outline=border_color, width=border_size)
    
    try:
        img.save(output_path)
    except Exception as e:
        raise RuntimeError(f"文件保存失败: {str(e)}")

class AvatarGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("几何分割生成器")
        self.preview_label = None
        self.create_widgets()
        self.algorithm_var.trace_add('write', self.toggle_square_mode)

    def toggle_square_mode(self, *args):
        if self.algorithm_var.get() == 'average':
            self.square_mode_label.grid()
            self.square_mode_combobox.grid()
        else:
            self.square_mode_label.grid_remove()
            self.square_mode_combobox.grid_remove()

    def create_widgets(self):
        tk.Label(self.master, text="分割算法:").grid(row=0, column=0, sticky=tk.W)
        self.algorithm_var = StringVar(value="random")
        algo_combobox = ttk.Combobox(self.master, textvariable=self.algorithm_var,
                                   values=['random', 'average', 'mondrian', 'complete_down', 'complete_line'],
                                   state='readonly')
        algo_combobox.grid(row=0, column=1, columnspan=2)

        tk.Label(self.master, text="尺寸:").grid(row=1, column=0, sticky=tk.W)
        self.size_var = StringVar(value="512")
        ttk.Combobox(self.master, textvariable=self.size_var, 
                    values=['256', '512', '1024', '2048']).grid(row=1, column=1, columnspan=2)

        self.square_mode_var = StringVar(value="rectangle")
        self.square_mode_label = tk.Label(self.master, text="平均模式:")
        self.square_mode_combobox = ttk.Combobox(self.master, textvariable=self.square_mode_var,
                                               values=['rectangle', 'square'], state='readonly')
        self.square_mode_label.grid(row=2, column=0, sticky=tk.W)
        self.square_mode_combobox.grid(row=2, column=1, columnspan=2)
        self.square_mode_label.grid_remove()
        self.square_mode_combobox.grid_remove()

        tk.Label(self.master, text="颜色模式:").grid(row=3, column=0, sticky=tk.W)
        self.color_mode_var = StringVar(value="colormap")
        ttk.Combobox(self.master, textvariable=self.color_mode_var,
                    values=['colormap', 'random', 'grayscale']).grid(row=3, column=1, columnspan=2)

        tk.Label(self.master, text="色系选择:").grid(row=4, column=0, sticky=tk.W)
        self.cmap_var = StringVar(value='viridis')
        self.cmap_combobox = ttk.Combobox(self.master, textvariable=self.cmap_var,
                                        values=VALID_CMAPS, state='readonly')
        self.cmap_combobox.grid(row=4, column=1, columnspan=2)

        tk.Label(self.master, text="分割次数:").grid(row=5, column=0, sticky=tk.W)
        self.density_var = StringVar(value="5")
        tk.Entry(self.master, textvariable=self.density_var).grid(row=5, column=1, columnspan=2)
        tk.Label(self.master, text="输入分割次数（≥1）").grid(row=6, column=0, columnspan=3)

        tk.Label(self.master, text="保存路径:").grid(row=7, column=0, sticky=tk.W)
        self.path_var = StringVar()
        tk.Entry(self.master, textvariable=self.path_var).grid(row=7, column=1)
        ttk.Button(self.master, text="浏览...", command=self.select_path).grid(row=7, column=2)

        ttk.Button(self.master, text="生成图像", command=self.generate).grid(row=8, column=1, pady=10)
        ttk.Button(self.master, text="实时预览", command=self.show_preview).grid(row=8, column=2, pady=10)

    def select_path(self):
        file_types = [('JPEG 文件', '*.jpg'), ('PNG 文件', '*.png'), ('WebP 文件', '*.webp')]
        path = filedialog.asksaveasfilename(filetypes=file_types, defaultextension='.jpg')
        if path: self.path_var.set(path)

    def show_preview(self):
        try:
            generate_avatar("preview_temp.jpg", 256,
                          self.color_mode_var.get(),
                          int(self.density_var.get()),
                          self.cmap_var.get(),
                          border_size=0,  # 预览也移除边框
                          split_algorithm=self.algorithm_var.get(),
                          square_mode=(self.square_mode_var.get() == 'square'))
            
            preview_img = Image.open("preview_temp.jpg")
            preview_img.thumbnail((200, 200))
            preview = ImageTk.PhotoImage(preview_img)
            
            if not self.preview_label:
                self.preview_label = tk.Label(self.master, image=preview)
                self.preview_label.image = preview
                self.preview_label.grid(row=9, column=1, pady=10)
            else:
                self.preview_label.configure(image=preview)
                self.preview_label.image = preview
        except Exception as e:
            messagebox.showerror("预览错误", str(e))

    def generate(self):
        try:
            params = {
                'output_path': self.path_var.get(),
                'size': int(self.size_var.get()),
                'color_mode': self.color_mode_var.get(),
                'split_count': int(self.density_var.get()),
                'colormap_name': self.cmap_var.get(),
                'border_size': 2,
                'split_algorithm': self.algorithm_var.get(),
                'square_mode': (self.square_mode_var.get() == 'square')
            }
            
            if not params['output_path']: raise ValueError("请选择保存路径")
            if not params['output_path'].lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                raise ValueError("请保存为支持的图像格式（jpg/png/webp）")
            if params['color_mode'] == 'colormap' and params['colormap_name'] not in VALID_CMAPS:
                raise ValueError("无效的colormap选择")
            if params['split_count'] < 1: raise ValueError("分割次数必须≥1")
                
            generate_avatar(**params)
            messagebox.showinfo("成功", "图像生成成功！")
        except ValueError as ve: messagebox.showerror("输入错误", str(ve))
        except Exception as e: messagebox.showerror("运行时错误", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AvatarGeneratorApp(root)
    root.mainloop()

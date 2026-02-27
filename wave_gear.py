#!python3
import tkinter as tk
from tkinter import ttk, messagebox
from dxfwrite import DXFEngine as dxf
from math import *
import os

# функция расчёта точки волновой передачи
def tochka(D_generatora=15, D_tela_kacenia=4.5, a=0.9, u_vpadin=10, povorot_vhod_zvena=0):
    """Расчет одной точки профиля"""
    R = 0.5 * (D_generatora + D_tela_kacenia)  # Приведенный радиус
    Y = a * cos(povorot_vhod_zvena) + (R**2 - a**2 * sin(povorot_vhod_zvena)**2)**(1/2)
    alfa = atan(u_vpadin * a * sin(povorot_vhod_zvena) / (R**2 - a**2 * sin(povorot_vhod_zvena) * 2)**(1/2))
    Xn = Y * sin(povorot_vhod_zvena / u_vpadin) + 0.5 * D_tela_kacenia * sin(alfa + povorot_vhod_zvena / u_vpadin)
    Yn = Y * cos(povorot_vhod_zvena / u_vpadin) + 0.5 * D_tela_kacenia * cos(alfa + povorot_vhod_zvena / u_vpadin)
    return [Xn, Yn]

# функция расчета массива точек
def massiv_tocheck(D_generatora=25, D_tela_kacenia=4.5, a=0.9, u_vpadin=10, kolichestvo_tochek=1000):
    """Генерация массива точек профиля"""
    i = -pi * u_vpadin
    massiv = []
    step = 2 * pi * u_vpadin / kolichestvo_tochek
    
    while i <= pi * u_vpadin:
        t1 = tochka(D_generatora, D_tela_kacenia, a, u_vpadin, povorot_vhod_zvena=i)
        i += step
        massiv.append(t1)
    return massiv

# функция проверки пересечений
def check_intersections(points, tolerance=0.1):
    """Проверка на самопересечения профиля"""
    intersections = []
    n = len(points)
    
    for i in range(n-1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        
        for j in range(i+2, n-1):
            x3, y3 = points[j]
            x4, y4 = points[j+1]
            
            # Проверка пересечения отрезков
            denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(denominator) < 1e-10:  # Параллельны
                continue
                
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
            
            if 0 < t < 1 and 0 < u < 1:
                # Находим точку пересечения
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                intersections.append((x, y, i, j))
    
    return intersections

# функция записи в DXF
def dxfwrite(t1, filename="profile.dxf"):
    """Сохранение профиля в DXF файл"""
    try:
        t1_copy = t1.copy()
        t1_copy.append(t1_copy[0])  # замыкаем контур
        drawing = dxf.drawing(filename)
        drawing.add_layer('PROFILE')
        
        for i in range(len(t1_copy)-1):
            drawing.add(dxf.line(
                (t1_copy[i][0], t1_copy[i][1]), 
                (t1_copy[i+1][0], t1_copy[i+1][1]), 
                color=7, 
                layer='PROFILE'
            ))
        drawing.save()
        return True, f"Файл сохранен как {filename}"
    except Exception as e:
        return False, f"Ошибка сохранения: {str(e)}"

class WaveReducerCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Расчет волнового редуктора")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Переменные для хранения значений
        self.D_generatora = tk.StringVar(value="20")
        self.D_tela_kacenia = tk.StringVar(value="4.5")
        self.a = tk.StringVar(value="0.7")
        self.u_vpadin = tk.StringVar(value="10")
        self.kolichestvo_tochek = tk.StringVar(value="2000")
        
        # Переменные для отображения впадины
        self.show_vpadina = tk.BooleanVar(value=True)
        self.vpadina_number = tk.IntVar(value=0)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Создаем главный фрейм с отступами
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель - параметры
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Фрейм для ввода параметров
        input_frame = ttk.LabelFrame(left_panel, text="Параметры расчета", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Создаем поля ввода с метками
        labels = [
            "Диаметр генератора (мм):",
            "Диаметр тела качения (мм):",
            "Эксцентриситет:",
            "Количество впадин в коронке:",
            "Количество точек:"
        ]
        
        variables = [
            self.D_generatora,
            self.D_tela_kacenia,
            self.a,
            self.u_vpadin,
            self.kolichestvo_tochek
        ]
        
        for i, (label_text, var) in enumerate(zip(labels, variables)):
            # Метка
            label = ttk.Label(input_frame, text=label_text)
            label.grid(row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            
            # Поле ввода
            entry = ttk.Entry(input_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky=tk.W, pady=5)
            
            # Кнопка сброса к значению по умолчанию
            default_btn = ttk.Button(
                input_frame, 
                text="↺",
                width=3,
                command=lambda v=var, idx=i: self.reset_to_default(v, idx)
            )
            default_btn.grid(row=i, column=2, padx=(5, 0), pady=5)
        
        # Фрейм для настроек отображения
        view_frame = ttk.LabelFrame(left_panel, text="Настройки отображения", padding="10")
        view_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Чекбокс для отображения впадины
        ttk.Checkbutton(
            view_frame,
            text="Показать увеличенную впадину",
            variable=self.show_vpadina,
            command=self.toggle_vpadina
        ).pack(anchor=tk.W, pady=5)
        
        # Выбор номера впадины
        ttk.Label(view_frame, text="Номер впадины:").pack(anchor=tk.W)
        vpadina_spinbox = ttk.Spinbox(
            view_frame,
            from_=0,
            to=100,
            textvariable=self.vpadina_number,
            width=10,
            command=self.on_vpadina_change
        )
        vpadina_spinbox.pack(anchor=tk.W, pady=5)
        
        # Фрейм для кнопок управления
        button_frame = ttk.LabelFrame(left_panel, text="Управление", padding="10")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки
        self.calc_btn = ttk.Button(
            button_frame, 
            text="Рассчитать",
            command=self.calculate_and_display,
            width=20
        )
        self.calc_btn.pack(pady=5)
        
        self.save_btn = ttk.Button(
            button_frame,
            text="Сохранить в DXF",
            command=self.save_to_dxf,
            state=tk.DISABLED,
            width=20
        )
        self.save_btn.pack(pady=5)
        
        self.clear_btn = ttk.Button(
            button_frame,
            text="Очистить",
            command=self.clear_canvas,
            width=20
        )
        self.clear_btn.pack(pady=5)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(left_panel, text="Информация", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем фрейм для текста и скроллбара
        text_frame = ttk.Frame(info_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Текстовое поле
        self.info_text = tk.Text(text_frame, height=10, width=30, wrap=tk.WORD)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Скроллбар
        info_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Настройка скроллбара
        self.info_text.config(yscrollcommand=info_scrollbar.set)
        
        # Правая панель - холсты
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Верхний холст - общий вид
        top_frame = ttk.LabelFrame(right_panel, text="Общий вид профиля", padding="5")
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.main_canvas = tk.Canvas(
            top_frame,
            bg='white',
            highlightthickness=1,
            highlightbackground='gray'
        )
        self.main_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Нижний холст - увеличенная впадина
        bottom_frame = ttk.LabelFrame(right_panel, text="Увеличенная впадина", padding="5")
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        self.zoom_canvas = tk.Canvas(
            bottom_frame,
            bg='white',
            highlightthickness=1,
            highlightbackground='gray',
            height=200
        )
        self.zoom_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Статусная строка
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # Привязываем события изменения размера
        self.main_canvas.bind('<Configure>', self.on_main_canvas_resize)
        self.zoom_canvas.bind('<Configure>', self.on_zoom_canvas_resize)
        
        # Переменные для хранения данных
        self.points = []
        self.intersections = []
        self.current_dxf_file = "profile.dxf"
        
    def reset_to_default(self, var, index):
        """Сброс поля к значению по умолчанию"""
        defaults = ["20", "4.5", "0.7", "10", "2000"]
        var.set(defaults[index])
        self.status_var.set(f"Поле {index+1} сброшено к значению по умолчанию")
    
    def toggle_vpadina(self):
        """Включение/выключение отображения впадины"""
        if self.points:
            if self.show_vpadina.get():
                self.draw_zoomed_vpadina()
            else:
                self.zoom_canvas.delete("all")
    
    def on_vpadina_change(self):
        """Обработчик изменения номера впадины"""
        if self.points and self.show_vpadina.get():
            self.draw_zoomed_vpadina()
        
    def validate_inputs(self):
        """Проверка корректности введенных данных"""
        try:
            D_gen = float(self.D_generatora.get())
            D_telo = float(self.D_tela_kacenia.get())
            a_val = float(self.a.get())
            u_val = float(self.u_vpadin.get())
            k_tochek = int(self.kolichestvo_tochek.get())
            
            if D_gen <= 0 or D_telo <= 0 or a_val <= 0 or u_val <= 0 or k_tochek <= 0:
                raise ValueError("Все значения должны быть положительными")
            
            if D_telo >= D_gen:
                messagebox.showwarning(
                    "Предупреждение",
                    "Диаметр тела качения больше или равен диаметру генератора"
                )
            
            return True, (D_gen, D_telo, a_val, u_val, k_tochek)
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Проверьте правильность введенных данных:\n{str(e)}")
            return False, None
            
    def calculate_and_display(self):
        """Расчет и отображение профиля"""
        valid, values = self.validate_inputs()
        if not valid:
            return
            
        D_gen, D_telo, a_val, u_val, k_tochek = values
        
        try:
            self.status_var.set("Выполняется расчет...")
            self.root.update()
            
            # Расчет точек
            self.points = massiv_tocheck(D_gen, D_telo, a_val, u_val, k_tochek)
            
            # Проверка на пересечения
            self.intersections = check_intersections(self.points)
            
            # Отображение на холстах
            self.draw_main_profile()
            if self.show_vpadina.get():
                self.draw_zoomed_vpadina()
            
            # Обновление информационной панели
            self.update_info()
            
            # Проверка наличия пересечений
            if self.intersections:
                self.status_var.set(f"ВНИМАНИЕ! Обнаружено {len(self.intersections)} самопересечений!")
                messagebox.showwarning(
                    "Обнаружены пересечения",
                    f"В профиле найдено {len(self.intersections)} самопересечений!\n"
                    "Проверьте параметры расчета."
                )
            else:
                self.status_var.set(f"Расчет выполнен успешно. Получено {len(self.points)} точек")
            
            self.save_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Ошибка расчета", str(e))
            self.status_var.set("Ошибка при расчете")
            
    def draw_main_profile(self):
        """Отрисовка основного профиля"""
        if not self.points:
            return
            
        # Очищаем холст
        self.main_canvas.delete("all")
        
        # Получаем размеры холста
        w = self.main_canvas.winfo_width()
        h = self.main_canvas.winfo_height()
        
        if w <= 1 or h <= 1:
            w, h = 600, 400
        
        # Находим границы профиля
        x_coords = [p[0] for p in self.points]
        y_coords = [p[1] for p in self.points]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        # Добавляем отступы
        padding = 30
        range_x = max_x - min_x or 1
        range_y = max_y - min_y or 1
        
        # Масштабируем
        scale_x = (w - 2*padding) / range_x
        scale_y = (h - 2*padding) / range_y
        scale = min(scale_x, scale_y)
        
        # Функция преобразования координат
        def transform(x, y):
            canvas_x = padding + (x - min_x) * scale
            canvas_y = h - padding - (y - min_y) * scale
            return canvas_x, canvas_y
        
        # Рисуем профиль
        for i in range(len(self.points) - 1):
            x1, y1 = transform(self.points[i][0], self.points[i][1])
            x2, y2 = transform(self.points[i+1][0], self.points[i+1][1])
            
            # Выбираем цвет в зависимости от наличия пересечений
            color = 'red' if self.check_segment_intersection(i) else 'blue'
            
            self.main_canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=2,
                tags="profile"
            )
        
        # Замыкаем контур
        x1, y1 = transform(self.points[-1][0], self.points[-1][1])
        x2, y2 = transform(self.points[0][0], self.points[0][1])
        
        color = 'red' if self.check_segment_intersection(len(self.points)-1) else 'blue'
        self.main_canvas.create_line(
            x1, y1, x2, y2,
            fill=color,
            width=2,
            tags="profile"
        )
        
        # Отмечаем точки пересечения
        for x, y, i, j in self.intersections:
            cx, cy = transform(x, y)
            self.main_canvas.create_oval(
                cx-3, cy-3, cx+3, cy+3,
                fill='yellow',
                outline='red',
                width=2,
                tags="intersection"
            )
        
        self.draw_main_grid(w, h, padding)
        
    def draw_zoomed_vpadina(self):
        """Отрисовка увеличенной впадины"""
        if not self.points:
            return
            
        # Очищаем холст
        self.zoom_canvas.delete("all")
        
        # Получаем размеры холста
        w = self.zoom_canvas.winfo_width()
        h = self.zoom_canvas.winfo_height()
        
        if w <= 1 or h <= 1:
            w, h = 600, 200
        
        # Определяем диапазон для одной впадины
        u_val = int(self.u_vpadin.get())
        points_per_vpadina = len(self.points) // u_val
        
        vpadina_idx = self.vpadina_number.get()
        start_idx = vpadina_idx * points_per_vpadina
        end_idx = min((vpadina_idx + 1) * points_per_vpadina, len(self.points))
        
        if start_idx >= len(self.points):
            start_idx = 0
            end_idx = points_per_vpadina
            self.vpadina_number.set(0)
        
        vpadina_points = self.points[start_idx:end_idx]
        
        if not vpadina_points:
            return
        
        # Находим границы впадины
        x_coords = [p[0] for p in vpadina_points]
        y_coords = [p[1] for p in vpadina_points]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        # Добавляем отступы
        padding = 20
        range_x = max_x - min_x or 1
        range_y = max_y - min_y or 1
        
        # Масштабируем с увеличением
        scale_x = (w - 2*padding) / range_x
        scale_y = (h - 2*padding) / range_y
        scale = min(scale_x, scale_y)
        
        # Функция преобразования координат
        def transform(x, y):
            canvas_x = padding + (x - min_x) * scale
            canvas_y = h - padding - (y - min_y) * scale
            return canvas_x, canvas_y
        
        # Рисуем впадину
        for i in range(len(vpadina_points) - 1):
            x1, y1 = transform(vpadina_points[i][0], vpadina_points[i][1])
            x2, y2 = transform(vpadina_points[i+1][0], vpadina_points[i+1][1])
            
            # Проверяем пересечения в этой впадине
            color = 'red' if self.check_vpadina_intersection(start_idx + i) else 'darkgreen'
            
            self.zoom_canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=3,
                tags="vpadina"
            )
        
        # Добавляем размеры
        self.zoom_canvas.create_text(
            w//2, 20,
            text=f"Впадина {vpadina_idx} (увеличено в {int(scale/10)+1}x)",
            fill='black',
            font=('Arial', 10, 'bold')
        )
        
        self.draw_zoom_grid(w, h, padding)
        
    def check_segment_intersection(self, segment_idx):
        """Проверка, есть ли пересечения на данном сегменте"""
        for _, _, i, j in self.intersections:
            if i == segment_idx or j == segment_idx:
                return True
        return False
    
    def check_vpadina_intersection(self, point_idx):
        """Проверка, есть ли пересечения в данной точке впадины"""
        for _, _, i, j in self.intersections:
            if abs(i - point_idx) < 10 or abs(j - point_idx) < 10:
                return True
        return False
    
    def draw_main_grid(self, w, h, padding):
        """Рисует координатную сетку на основном холсте"""
        # Горизонтальные линии
        for y in range(padding, h-padding+1, 50):
            self.main_canvas.create_line(
                padding, y, w-padding, y,
                fill='lightgray',
                dash=(2, 4),
                tags="grid"
            )
        
        # Вертикальные линии
        for x in range(padding, w-padding+1, 50):
            self.main_canvas.create_line(
                x, padding, x, h-padding,
                fill='lightgray',
                dash=(2, 4),
                tags="grid"
            )
    
    def draw_zoom_grid(self, w, h, padding):
        """Рисует сетку на увеличенном холсте"""
        # Горизонтальные линии
        for y in range(padding, h-padding+1, 30):
            self.zoom_canvas.create_line(
                padding, y, w-padding, y,
                fill='lightgray',
                dash=(2, 4),
                tags="zoom_grid"
            )
        
        # Вертикальные линии
        for x in range(padding, w-padding+1, 30):
            self.zoom_canvas.create_line(
                x, padding, x, h-padding,
                fill='lightgray',
                dash=(2, 4),
                tags="zoom_grid"
            )
    
    def update_info(self):
        """Обновление информационной панели"""
        self.info_text.delete(1.0, tk.END)
        
        if not self.points:
            return
        
        info = f"Параметры профиля:\n"
        info += f"{'='*30}\n"
        info += f"Всего точек: {len(self.points)}\n"
        info += f"Пересечений: {len(self.intersections)}\n\n"
        
        if self.intersections:
            info += f"Места пересечений:\n"
            for i, (x, y, seg1, seg2) in enumerate(self.intersections[:5]):
                info += f"{i+1}. X={x:.3f}, Y={y:.3f}\n"
                info += f"   сегменты: {seg1}-{seg2}\n"
        
        info += f"\nРазмеры профиля:\n"
        info += f"{'='*30}\n"
        
        x_coords = [p[0] for p in self.points]
        y_coords = [p[1] for p in self.points]
        
        info += f"X: min={min(x_coords):.3f}, max={max(x_coords):.3f}\n"
        info += f"Y: min={min(y_coords):.3f}, max={max(y_coords):.3f}\n"
        info += f"Ширина: {max(x_coords)-min(x_coords):.3f}\n"
        info += f"Высота: {max(y_coords)-min(y_coords):.3f}\n"
        
        self.info_text.insert(1.0, info)
        
    def save_to_dxf(self):
        """Сохранение в DXF файл"""
        if not self.points:
            return
            
        # Диалог выбора файла
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".dxf",
            filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")],
            initialfile="profile.dxf"
        )
        
        if filename:
            success, message = dxfwrite(self.points, filename)
            if success:
                self.status_var.set(message)
                messagebox.showinfo("Успешно", message)
            else:
                messagebox.showerror("Ошибка", message)
                self.status_var.set(message)
    
    def clear_canvas(self):
        """Очистка холстов"""
        self.main_canvas.delete("all")
        self.zoom_canvas.delete("all")
        self.points = []
        self.intersections = []
        self.save_btn.config(state=tk.DISABLED)
        self.status_var.set("Холст очищен")
        self.info_text.delete(1.0, tk.END)
    
    def on_main_canvas_resize(self, event):
        """Обработчик изменения размера основного холста"""
        if self.points:
            self.draw_main_profile()
    
    def on_zoom_canvas_resize(self, event):
        """Обработчик изменения размера увеличенного холста"""
        if self.points and self.show_vpadina.get():
            self.draw_zoomed_vpadina()

def main():
    root = tk.Tk()
    app = WaveReducerCalculator(root)
    
    # Центрируем окно
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()

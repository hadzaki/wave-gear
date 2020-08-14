# подключаем библитеку для GUI
from tkinter import *
# подключаем библитеку для сохранения в формате dxf
from dxfwrite import DXFEngine as dxf
# подключаем прочие библиоткеи
from math import *
import time

# функция рачёта точки волновой передачи
def tochka(D_generatora=15, D_tela_kacenia=4.5, a=0.9, u_vpadin=10, povorot_vhod_zvena=0):
  """D_generatora=19, #мм диаметр герератора 
  D_tela_kacenia=4.5, #мм диаметр тела качения
  a=0.9, # экцентросиситет
  u_vpadin=10, # коллическо впадин в коронке
  povorot_vhod_zvena=0, # угол поворота входного звена
  R=0.5*(D_generatora+D_tela_kacenia) # Приведенный радиус"""
  R=0.5*(D_generatora+D_tela_kacenia) # Приведенный радиус
  Y=a*cos(povorot_vhod_zvena)+(R**2-a**2*sin(povorot_vhod_zvena)**2)**(1/2)
  alfa=atan(u_vpadin*a*sin(povorot_vhod_zvena)/(R**2-a**2*sin(povorot_vhod_zvena)*2)**(1/2))
  Xn=Y*sin(povorot_vhod_zvena/u_vpadin)+0.5*D_tela_kacenia*sin(alfa+povorot_vhod_zvena/u_vpadin)
  Yn=Y*cos(povorot_vhod_zvena/u_vpadin)+0.5*D_tela_kacenia*cos(alfa+povorot_vhod_zvena/u_vpadin)
  koordinat=[Xn,Yn]
  return koordinat
# функция расчета точек
def massiv_tocheck(D_generatora=25, D_tela_kacenia=4.5, a=0.9, u_vpadin=10,kolichestvo_tochek=1000):
  i=-pi*u_vpadin
  print("Начало")
  massiv=[]
  while i<=pi*u_vpadin:
    t1=tochka(D_generatora, D_tela_kacenia, a, u_vpadin, povorot_vhod_zvena=i)
    i=i+2*pi*u_vpadin/kolichestvo_tochek
    massiv.append(t1)
  return massiv
# функция записи точекиии
def dxfwrite(t1):
  i=0
  n=len(t1)-1
  print("Начало")
  drawing = dxf.drawing('test.dxf')
  drawing.add_layer('LINES')
  while i<n:
    drawing.add(dxf.line((t1[i][0], t1[i][1]), (t1[i+1][0], t1[i+1][1]), color=7, layer='LINES'))
    i=i+1
  drawing.save()

root = Tk()
root.title("Расчет волнового редуктора ")
# поле ввода диаметр герератора
e0 = Entry(width=20)
e0.insert(0,"20") # значение по умолчанию
# поле ввода диаметр тела качения
e1 = Entry(width=20)
e1.insert(0,"4.5")# значение по умолчанию
# поле ввода экцентросиситет
e2 = Entry(width=20)
e2.insert(0,"0.7")# значение по умолчанию
# поле ввода коллическо впадин в коронке
e3 = Entry(width=20)
e3.insert(0,"10")# значение по умолчанию
# поле ввода коллическо впадин в коронке
e4 = Entry(width=20)
e4.insert(0,"2000")# значение по умолчанию
# кнопка нажатия расчёта
b = Button(text="Расчитать")

p_width_height=600
canvas = Canvas(width=p_width_height,height=p_width_height,bg="gray", cursor="pencil")
l0 = Label(bg='black', fg='white', width=20, text="Диаметр герератора")
l1 = Label(bg='black', fg='white', width=20, text="Диаметр тела качения")
l2 = Label(bg='black', fg='white', width=20, text="Экцентросиситет")
l3 = Label(bg='black', fg='white', width=20, text="Коллическо впадин в коронке")
l4 = Label(bg='black', fg='white', width=20, text="Коллическо точек")
l5 = Label(bg='black', fg='white', width=100)
def strToSortlist(event,p_=p_width_height):
    s = massiv_tocheck(float(e0.get()),float(e1.get()),float(e2.get()),float(e3.get()),float(e4.get()))
    i=0
    # поиск максимального значения x и y
    s_x=[]
    s_y=[]
    drawing = dxf.drawing('test.dxf')
    drawing.add_layer('LINES')
    for prom in s:
    	s_x.append(prom[0])
    	s_y.append(prom[1])
    d_s_x=max(s_x)-min(s_x)+5
    d_s_y=max(s_y)-min(s_y)+5
    # очистка канваса
    canvas.delete("all")
    # рисуем линии
    while i<len(s)-1:
        canvas.create_line(p_/2+s[i][0]*p_/d_s_x, p_/2 + s[i][1]*p_/d_s_y, 
        	               p_/2+s[i+1][0]*p_/d_s_x, p_/2 + s[i+1][1]*p_/d_s_y)
        i=i+1
    # рисуем две впадину для проверки пересечении
    kk=int(len(s)/float(e3.get()))*2
    min_s_x=min(s_x[0:kk+1])
    max_s_x=max(s_x[0:kk+1])
    min_s_y=min(s_y[0:kk+1])
    max_s_y=max(s_y[0:kk+1])
    d_s_x=max_s_x-min_s_x
    d_s_y=max_s_y-min_s_y
    print (kk)
    print(d_s_y)
    print(d_s_x)
    # рисуем линии
    i=0
    while i<kk-1:
        canvas.create_line((s[i][0]-min_s_x)*p_/max([d_s_x,d_s_y]),      (s[i][1]-min_s_y)*p_/max([d_s_x,d_s_y]), 
        	               (s[i+1][0]-min_s_x)*p_/max([d_s_x,d_s_y]),    (s[i+1][1]-min_s_y)*p_/max([d_s_x,d_s_y]),
                         fill="red")
        i=i+1
    try:
      dxfwrite(s)
      l5['text'] = ' '.join("Записал")
    except:
      l5['text'] = ' '.join("Ошибка записи")
b.bind('<Button-1>', strToSortlist)
l0.pack()
e0.pack()
l1.pack()
e1.pack()
l2.pack()
e2.pack()
l3.pack()
e3.pack()
l4.pack()
e4.pack()
b.pack()
l5.pack()
canvas.pack()
root.mainloop()
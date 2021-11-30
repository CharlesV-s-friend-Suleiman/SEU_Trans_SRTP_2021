import tkinter
import tkinter.messagebox
from tkinter import *
from PIL import Image, ImageTk
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os
from tkinter import filedialog,ttk
import GUI_tools.menutools as menutools
import GUI_tools.mathtools as mathtools

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
from os.path import join as pjoin


root = tkinter.Tk()
root.geometry('500x400')
root.title("Visualize Highyway Graphing System")

fpath = tkinter.StringVar()


def getfile():
    file_path = filedialog.askopenfilename()
    fpath.set(file_path)
    img = Image.open(fpath.get())
    openimage = ImageTk.PhotoImage(img)
    imLabel = tkinter.Label(root, image=openimage, height=310, width=480).grid(row=1, column=0)
    button2 = ttk.Button(root, text='打开', command=endroot).grid(row=2, column=0)
    root.mainloop()


def endroot():
    root.destroy()


button1 = ttk.Button(root, text='浏览..', command=getfile).grid(row=0, column=0)
root.mainloop()

myWindow = Tk()
myWindow.title("可视化互动路网交通状态预测界面")  # 设置标题
myWindow.resizable(False, False)




# 菜单栏，以后GUI优化主要在于丰富菜单栏
menubar = tkinter.Menu(myWindow)

filemenu = tkinter.Menu(menubar, tearoff=0)  # tear off下拉
modelmenu = tkinter.Menu(menubar, tearoff=0)
helpmenu = tkinter.Menu(menubar, tearoff=0)
about_us_menu = tkinter.Menu(menubar, tearoff=0)

menubar.add_cascade(label='地图操作', menu=filemenu)
menubar.add_cascade(label='模型选择', menu=modelmenu)
menubar.add_cascade(label='帮助', menu=helpmenu, command = menutools.open_help_file)
menubar.add_cascade(label='关于我们', menu=about_us_menu)


# 完善文件菜单工具， 这些都是后期（21年jzh的）工作了,


def save():
    mbx_save = tkinter.messagebox.showinfo(title='提示',
                                           message='图结构已经成功保存')
    print(mbx_save)

    martix_adjacency_01 = nx.adjacency_matrix(Graph_map).todense()
    res0 = pd.DataFrame(martix_adjacency_01).drop(0)

    i = martix_adjacency_01.shape[0]
    res1 = pd.read_csv('./dataset/PeMSD7_V_228.csv', usecols=list(j for j in range(i)) )

    # 这里写的比较赶，暂时想不到跨文件传参的方法，先这样了
    pd_i = pd.DataFrame([i])
    pd_i.to_csv('i.csv')

    martixfilename = f'PeMSD7_W_{i}.csv'
    datafilename = f'PeMSD7_V_{i}.csv'
    res0.to_csv(pjoin('./dataset', martixfilename) , index=False)
    res1.to_csv(pjoin('./dataset', datafilename) , index=False)


filemenu.add_command(label='新建虚拟地图', command=menutools.new_virtual_map)
filemenu.add_command(label='打开新地图', command=menutools.new_map)
filemenu.add_command(label='保存当前图与节点01邻接矩阵', command=save)

modelmenu.add_command(label='SVM模型', command=mathtools.SVM)
modelmenu.add_command(label='ARIMA模型', command=mathtools.ARIMA)

# 要是svm arima也要多方法的话也像下面那样再多套一层

subGCNmenu = tkinter.Menu(modelmenu)
modelmenu.add_cascade(label='GCN模型', menu=subGCNmenu)
subGCNmenu.add_command(label='采用点-边0-1邻接矩阵', command = mathtools.GCN_01_adj)
subGCNmenu.add_command(label='采用节点距离定义邻接矩阵')
subGCNmenu.add_command(label='采用自定义0-1邻接矩阵')


# 载入地图作为背景,载入其他GUI要用的图片


image_nodeicon = Image.open('node_icon.png') # 载入表示节点的小图标，这个是我自己画的，能不能找一个高级点的
image_map = Image.open(fpath.get()) # 载入地图，有时间可以改成函数载入
background_image = ImageTk.PhotoImage(image_map)
node_image = ImageTk.PhotoImage(image_nodeicon)
w = 200+background_image.width()
h = background_image.height()
myWindow.geometry('%dx%d+0+0' % (w, h))

# 设置画布，大小和载入的地图一样

X = tkinter.IntVar(value=0)
Y = tkinter.IntVar(value=0)
yesno = tkinter.IntVar(value=0) # 0 no; 1 yes
image = tkinter.PhotoImage()
canvas = tkinter.Canvas(myWindow, width=background_image.width(), height=background_image.height(), bg='pink')
canvas.create_image(0.5 * background_image.width(), 0.5 * background_image.height(), image=background_image)
canvas.pack()

# 对内储存的图数据
Graph_map = nx.Graph()
count_of_node = 0

# 内部实现函数，已经写完了


def add_node_onLeftButtonDown(event): # 画节点函数
    global count_of_node
    count_of_node = count_of_node + 1
    yesno.set(1)
    node_text_id = canvas.create_text(event.x, event.y + 25, text="节点"+str(count_of_node), tag='node_text' ) #画图流程1
    node_icon_id = canvas.create_image(event.x, event.y, image=node_image, tag='node_icon') #画图流程2,两个id都是数字 返回0号位置为id的元祖，
    Graph_map.add_node(count_of_node, nodex=event.x, nodey=event.y ) # count of node是编号 nodex,nodey总会用到的
    print('节点', canvas.coords(node_icon_id))#这行用来验证统一性


def del_node_onLeftButtonDown(event):  # 两个部分，删掉交互界面的，删掉内存里的
    global count_of_node
    if count_of_node>-1:
        nodelist = list(canvas.find_withtag('node_icon'))
        del_dist = float('inf')
        for nodes in nodelist:
            temp_deldist = (canvas.coords(nodes)[0] - event.x) ** 2 + (canvas.coords(nodes)[1] - event.y) ** 2
            if temp_deldist <= del_dist:
                del_dist = temp_deldist
                del_node = nodes
        del_text = canvas.find_withtag(del_node -1)
        del_node_coords = canvas.coords(del_node)
        canvas.delete(del_node),canvas.delete(del_text)
        del_node_id = nodelist.index(del_node) + 1  # 函数会把line判断为node,解决方式是自己写一个方法，而不是用给定的findclosest
        Graph_map.remove_node(del_node_id)

        linelist = list(canvas.find_withtag('line'))
        for line in linelist:
            line_coords1 = canvas.coords(line)[0:2]
            line_coords2 = canvas.coords(line)[2:4]
            d1 = (line_coords1[0]-del_node_coords[0])**2 +(line_coords1[1]-del_node_coords[1])**2
            d2 = (line_coords2[0]-del_node_coords[0])**2 +(line_coords2[1]-del_node_coords[1])**2
            print('test', d1, d2)
            if d1==0 or d2==0 :
                canvas.delete(line)

    else:
        canvas.unbind('<Button-1>')


def add_edge_onLeftButtonDown_from(event):
    global X, Y

    if count_of_node>=2:
        nodelist = list(canvas.find_withtag('node_icon'))
        fdist = float('inf')
        for nodes in nodelist:
            temp_fdist = (canvas.coords(nodes)[0] - event.x)**2 +(canvas.coords(nodes)[1] - event.y)**2
            if temp_fdist<=fdist:
                fdist=temp_fdist
                from_node = nodes
        X.set(canvas.coords(from_node)[0])
        Y.set(canvas.coords(from_node)[1])
    else: canvas.unbind('<Button-1>'),canvas.unbind('<Button-3>')


def add_edge_onRightButtonDown_to(event):
    global X, Y
    nodelist = list(canvas.find_withtag('node_icon'))

    tdist = fdist = float('inf')
    for nodes in nodelist:
        temp_fdist = (canvas.coords(nodes)[0] - X.get())**2 +(canvas.coords(nodes)[1] - Y.get())**2
        temp_tdist = (canvas.coords(nodes)[0] - event.x)**2 +(canvas.coords(nodes)[1] - event.y)**2
        if temp_fdist<=fdist:
            fdist=temp_fdist
            from_node = nodes
        if temp_tdist<=tdist:
            tdist=temp_tdist
            to_node = nodes

    line_id = canvas.create_line(X.get(), Y.get(), canvas.coords(to_node)[0], canvas.coords(to_node)[1],
                                 width= 5,
                                 fill = 'pink',
                                 tag='line')
    print('line id', line_id)  # line_id : int
    from_node_id = nodelist.index(from_node)+1 # 函数会把line判断为node,解决方式是自己写一个方法，而不是用给定的findclosest
    to_node_id = nodelist.index(to_node)+1
    Graph_map.add_edge(from_node_id, to_node_id)  # 之所以n-1/2是因为图上的id里除了有节点还有txt
    print(from_node)


def del_edge_onLeftButtonDown_from(event):
    global count_of_edge
    global X, Y

    if count_of_node >= 2:
        nodelist = list(canvas.find_withtag('node_icon'))
        fdist = float('inf')
        for nodes in nodelist:
            temp_fdist = (canvas.coords(nodes)[0] - event.x) ** 2 + (canvas.coords(nodes)[1] - event.y) ** 2
            if temp_fdist <= fdist:
                fdist = temp_fdist
                from_node = nodes
        X.set(canvas.coords(from_node)[0])
        Y.set(canvas.coords(from_node)[1])
    else:
        canvas.unbind('<Button-1>'), canvas.unbind('<Button-3>')


def del_edge_onRightButtonDown_to(event):
    global X, Y
    nodelist = list(canvas.find_withtag('node_icon'))

    tdist = fdist = float('inf')
    for nodes in nodelist:
        temp_fdist = (canvas.coords(nodes)[0] - X.get()) ** 2 + (canvas.coords(nodes)[1] - Y.get()) ** 2
        temp_tdist = (canvas.coords(nodes)[0] - event.x) ** 2 + (canvas.coords(nodes)[1] - event.y) ** 2
        if temp_fdist <= fdist:
            fdist = temp_fdist
            from_node = nodes
        if temp_tdist <= tdist:
            tdist = temp_tdist
            to_node = nodes
    fcoords = canvas.coords(from_node)
    tcoords = canvas.coords(to_node)
    linelist = list(canvas.find_withtag('line'))
    for lines in linelist:
        #coords1 = coords2 = []
        coords1 = canvas.coords(lines)[0:2]
        coords2 = canvas.coords(lines)[2:4]
        d1 = abs(coords1[0] -  fcoords[0]) +  abs(coords1[1] -  fcoords[1])+\
             abs(coords2[0] -  tcoords[0]) +  abs(coords2[1] -  tcoords[1])
        d2 = abs(coords1[0] - tcoords[0]) + abs(coords1[1] - tcoords[1]) + \
             abs(coords2[0] - fcoords[0]) + abs(coords2[1] - fcoords[1])
        if d1==0 or d2 == 0:
            delline = lines
    canvas.delete(delline)

    from_node_id = nodelist.index(from_node)+1
    to_node_id = nodelist.index(to_node)+1
    Graph_map.remove_edge(from_node_id, to_node_id)


def show_martix_adj(event): # 展示邻接矩阵
    print(Graph_map.number_of_nodes())
    if Graph_map.number_of_nodes()==0:
        print('无邻接矩阵')
    else:
        martix_window = Tk()
        martix_window.title('AdjacenyMartix')
        martix_window.geometry("300x300")
        martix_adj = nx.adjacency_matrix(Graph_map).todense()
        martix_box = Label(martix_window, text = martix_adj)
        martix_box.pack()
        print(nx.adjacency_matrix(Graph_map).todense() ) # 输出的类型为numpy.martix


def show_martix_laplace(event): # 展示邻接矩阵
    print(Graph_map.number_of_nodes())

    if Graph_map.number_of_nodes()==0:
        print('无邻接矩阵，故无拉普拉斯矩阵')
    else:
        martix_window = Tk()
        martix_window.title('LaplaceMartix')
        martix_window.geometry("300x300")
        martix_laplace = nx.laplacian_matrix(Graph_map).todense()
        martix_box = Label(martix_window, text = martix_laplace)
        martix_box.pack()
        print(martix_laplace) # 输出的类型为numpy.martix


# 按钮绑定函数，已经完成6/6


def func_show_martix_laplace():

    Statejudge = True
    for j in Buttonlist:
        if j['state'] == DISABLED: Statejudge = False

    if Statejudge == True:  # 此时激活
        for i in range(len(Buttonlist)):
            if Buttonlist[i] != button_show_martix_laplace:
                Buttonlist[i]['text'] = '已有功能运行中'
                Buttonlist[i]['state'] = DISABLED
            else:
                Buttonlist[i]['text'] = '查看完毕后点击'
        canvas.unbind('<Button-1>')
        canvas.bind('<Button-1>', show_martix_laplace)
    else:
        canvas.unbind('<Button-1>'), canvas.unbind('<Button-3>')
        for i in range(len(Buttonlist)):
            Buttonlist[i]['text'] = labellist[i]
            if Buttonlist[i]['state'] == DISABLED:
                Buttonlist[i]['state'] = NORMAL


def func_show_martix_adj():
    Statejudge = True
    for j in Buttonlist:
        if j['state'] == DISABLED: Statejudge = False

    if Statejudge == True:  # 此时激活
        for i in range(len(Buttonlist)):
            if Buttonlist[i] != button_show_martix_adj:
                Buttonlist[i]['text'] = '已有功能运行中'
                Buttonlist[i]['state'] = DISABLED
            else:
                Buttonlist[i]['text'] = '查看完毕后点击'
        canvas.unbind('<Button-1>')
        canvas.bind('<Button-1>', show_martix_adj)
    else:
        canvas.unbind('<Button-1>'), canvas.unbind('<Button-3>')
        for i in range(len(Buttonlist)):
            Buttonlist[i]['text'] = labellist[i]
            if Buttonlist[i]['state'] == DISABLED:
                Buttonlist[i]['state'] = NORMAL


def func_add_node():# 在画布上增加一个可选择的小图标，同时在networkx提供的图类里增加节点
    Statejudge = True
    for j in Buttonlist:
        if j['state'] ==DISABLED: Statejudge= False

    if Statejudge == True : #此时激活
        for i in range(len(Buttonlist)):
            if Buttonlist[i] != button_add_node :
                Buttonlist[i]['text'] = '已有功能运行中'
                Buttonlist[i]['state'] = DISABLED
            else:
                Buttonlist[i]['text'] = '左键添加节点'
        canvas.unbind('<Button-1>')
        canvas.bind('<Button-1>', add_node_onLeftButtonDown)
    else:
        canvas.unbind('<Button-1>')
        for i in range(len(Buttonlist)):
            Buttonlist[i]['text'] = labellist[i]
            if Buttonlist[i]['state']== DISABLED:
                Buttonlist[i]['state'] = NORMAL


def func_del_node():
    Statejudge = True
    for j in Buttonlist:
        if j['state'] == DISABLED: Statejudge = False

    if Statejudge == True:  # 此时激活
        for i in range(len(Buttonlist)):
            if Buttonlist[i] != button_del_node:
                Buttonlist[i]['text'] = '已有功能运行中'
                Buttonlist[i]['state'] = DISABLED
            else:
                Buttonlist[i]['text'] = '左键删除节点'
        canvas.unbind('<Button-1>')
        canvas.bind('<Button-1>', del_node_onLeftButtonDown)
    else:
        canvas.unbind('<Button-1>')
        for i in range(len(Buttonlist)):
            Buttonlist[i]['text'] = labellist[i]
            if Buttonlist[i]['state'] == DISABLED:
                Buttonlist[i]['state'] = NORMAL


def func_add_edge():
    Statejudge = True
    for j in Buttonlist:
        if j['state'] == DISABLED: Statejudge = False

    if Statejudge == True:  # 此时激活
        for i in range(len(Buttonlist)):
            if Buttonlist[i] != button_add_edge:
                Buttonlist[i]['text'] = '已有功能运行中'
                Buttonlist[i]['state'] = DISABLED
            else:
                Buttonlist[i]['text'] = '左键出点，右键入点'
        canvas.unbind('<Button-1>'),canvas.unbind('<Button-3>')
        canvas.bind('<Button-1>', add_edge_onLeftButtonDown_from)
        canvas.bind('<Button-3>', add_edge_onRightButtonDown_to)
    else:
        canvas.unbind('<Button-1>'),canvas.unbind('<Button-3>')
        for i in range(len(Buttonlist)):
            Buttonlist[i]['text'] = labellist[i]
            if Buttonlist[i]['state'] == DISABLED:
                Buttonlist[i]['state'] = NORMAL


def func_del_edge():
    Statejudge = True
    for j in Buttonlist:
        if j['state'] == DISABLED: Statejudge = False

    if Statejudge == True:  # 此时激活
        for i in range(len(Buttonlist)):
            if Buttonlist[i] != button_del_edge:
                Buttonlist[i]['text'] = '已有功能运行中'
                Buttonlist[i]['state'] = DISABLED
            else:
                Buttonlist[i]['text'] = '左键出点，右键入点'
        canvas.unbind('<Button-1>'), canvas.unbind('<Button-3>')
        canvas.bind('<Button-1>', del_edge_onLeftButtonDown_from)
        canvas.bind('<Button-3>', del_edge_onRightButtonDown_to)
    else:
        canvas.unbind('<Button-1>'), canvas.unbind('<Button-3>')
        for i in range(len(Buttonlist)):
            Buttonlist[i]['text'] = labellist[i]
            if Buttonlist[i]['state'] == DISABLED:
                Buttonlist[i]['state'] = NORMAL


# 6个按钮，command为按钮对应函数

button_add_node = Button(myWindow,
                         command=func_add_node,
                         text="增加新节点到路网中",
                         bg='white',
                         relief='raised',
                         width=15,
                         height=2)
button_add_node.place(x=10, y=10)

button_del_node = Button(myWindow,
                         text="删除已有节点",
                         command=func_del_node,
                         bg='white',
                         relief='raised',
                         width=15,
                         height=2)
button_del_node.place(x=10, y=80)

button_add_edge = Button(myWindow,
                         command=func_add_edge,
                         text="增加新边到路网中",
                         bg='white',
                         relief='raised',
                         width=15,
                         height=2)
button_add_edge.place(x=10, y=150)

button_del_edge = Button(myWindow,
                         command=func_del_edge,
                         text="删除已有边",
                         bg='white',
                         relief='raised',
                         width=15,
                         height=2)
button_del_edge.place(x=10, y=220)

button_show_martix_adj = Button(myWindow,
                         command = func_show_martix_adj,
                         text="路网加权邻接矩阵",
                         bg='white',
                         relief='raised',
                         width=15,
                         height=2)
button_show_martix_adj.place(x=10, y=290)

button_show_martix_laplace = Button(myWindow,
                         command = func_show_martix_laplace,
                         text="路网标准化Laplace矩阵",
                         bg='white',
                         relief='raised',
                         width=15,
                         height=2)
button_show_martix_laplace.place(x=10, y=360)


labellist= ['增加新节点到路网中','删除已有节点','增加新边到路网中','删除已有边','路网加权邻接矩阵','路网标准化Laplace矩阵']
Buttonlist = [button_add_node,button_del_node,button_add_edge,button_del_edge,
              button_show_martix_adj, button_show_martix_laplace] # 按钮合集


myWindow.config(menu=menubar)  # 将菜单栏显示
myWindow.mainloop()
nx.draw(Graph_map, with_labels=True)  # 以下两句为图测试语句
plt.show()

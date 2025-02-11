""" SCRIPTORIUM - app
Author = zah.florian@gmail.com
------------------------------
STATUS: active

TO DO:
[ ] - functia  delete de transferat
[ ] - rearanjeaza noduri dupa stergere
[ ] - creaza o functie compara pentru a nu face atatea salvari in db
      (ca si in BlockNotes)


    #  ==================================================
    #  |File   Edit   Help                   (menu)     |
    #  |------------------------------------------------|
    #  |-frame_stanga | -frame dreapta                  |
    #  |              |                                 |
    #  |              | Editor                          |
    #  | Noduri       |                                 |
    #  |              |                                 |
    #  |              |                                 |
    #  |              |                                 |
    #  |              |                                 |
    #  |              |                                 |
    #  |              |                                 |
    #  |              |                                 |
    #  |              |---------------------------------|
    #  |              | Command line                    |
    #  ==================================================

"""

import tkinter as tk
from tkinter import scrolledtext as sc
from tkinter import filedialog as fd
from tkinter import ttk
import tkinter.font as tkFont
import sqlite3 

class Scriptorium:
    def __init__(self, win):
        self.win = win
        self.win.protocol("WM_DELETE_WINDOW", self.save_at_closing)

        # GUI
        #----------------------------

        pw = ttk.PanedWindow(orient=tk.HORIZONTAL)
        
        # Tree
        self.tree = ttk.Treeview(pw, heigh=21, show='tree')  # show='tree'' = no heading
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.heading('#0', text='>', anchor='w')
        pw.add(self.tree)

        # Editorul
        self.editor = sc.ScrolledText(pw, wrap = tk.WORD, font=('Consolas', 11))
        self.editor.pack(fill=tk.BOTH, expand=True)
        font = tkFont.Font(font=['font'])
        tab_size = font.measure('    ')
        self.editor.config(tabs=tab_size)
        pw.add(self.editor)
        pw.pack(fill=tk.BOTH, expand=True)

        # Right click menu
        self.rMenu = tk.Menu(self.win, tearoff=0)
        self.rMenu.add_command(label='Add above', command=lambda: self.add_node(0))  # 0 = up
        self.rMenu.add_command(label='Add below', command=lambda: self.add_node(1))  # 1 = down
        self.rMenu.add_command(label='Add child', command=lambda: self.add_node(2))  # 2 = child
        self.rMenu.add_separator()
        self.rMenu.add_command(label='Rename', command=self.rename_node)
        self.rMenu.add_command(label='Delete', command=self.delete_node)


        # Binding operation
        self.tree.bind('<Button-1>', self.left_click)
        self.tree.bind('<Button-3>', self.right_click)
        # self.treeview.bing('<Enter>', callback)


        # SQLite
        fisier_db = 'scriptorium.db'
        self.conn = sqlite3.connect(fisier_db)
        self.curr = self.conn.cursor()
        sql_config = '''SELECT * from config'''
        self.curr.execute(sql_config)
        config = self.curr.fetchall()  # -> [(1, 'item_id', '1')]
        self.item_id = int(config[0][2])  # => 1
       
        # FUNCTII PENTRU ACTIVARE DIN __init__
        self.tabel_noduri = self.citeste_noduri_db()
        self.creaza_aranjeaza_noduri(self.tabel_noduri)

    # FUNCTII SI OPERATII GUI
    # =======================
    def left_click(self, event):
        """ Evenimente la left click.
            [PROCEDURI GUI - 3]

        1. Salveaza textul modificat
        2. Extrage textul din tabel: continut; rand: id; coloana: text
        3. Afiseaza textul in editor
        """ 

        # 1. Salveaza textul modificat
        self.save_text()
        self.item_id = self.tree.identify('item', event.x, event.y)  # id item nod activ
        self.nume_nod = self.tree.item(self.item_id, 'text')  # nume item
        # Urmatoarele sunt pentru consola sau status bar; cam asa ceva
        #self.nume_nod_pt_LabelInfo = self.nume_nod + ' -id: ' + self.item_id
        #label_info.config(text=self.nume_nod_pt_LabelInfo)

        # 2. Extrage textul din tabel
        sql = "SELECT text FROM continut WHERE id=?"
        text_din_db = self.curr.execute(sql, (self.item_id,))
        text_din_db = self.curr.fetchone()  # e tuplet

        # 3. Afiseaza textul in editor
        text_editor = text_din_db[0].rstrip('\n')  # -> text
        self.editor.delete('1.0', 'end')
        self.editor.insert('1.0', text_editor)
    

    def save_text(self):
        """ Save text from editor in db when change from tree item to another tree item. 
            [PROCEDURI GUI & SQLITE (apartine de funct. left_click) - 4]
        """
        te_ed = self.editor.get('1.0', 'end').rstrip(' \n')
        # Compara textele: din bd si din editor
        #[ ] - implementare ulterioara
        sql = "UPDATE continut SET text=? WHERE id=?"
        val = (te_ed, self.item_id)
        self.curr.execute(sql, val)
        self.conn.commit()


    def save_at_closing(self):
        """ Save content in db at clicking x(    _ [] X)."""
        te_ed = self.editor.get('1.0', 'end').rstrip(' \n')
        #[ ] - implementare ulterioara
        sql = "UPDATE continut SET text=? WHERE id=?"
        val = (te_ed, self.item_id)
        self.curr.execute(sql, val)
        self.conn.commit()
        self.win.destroy()


    def right_click(self, event):
        """ Evenimente la right click
            [PROCEDURI GUI - 5]

        Args/Kwargs:
            event : type=tkinter.Event -- _description_

        1. Recunoaste item, id, ..., (left click inheritance)  
        2. Extrage textul din tabel: continut; rand: id; coloana: text
        3. Afiseaza textul in editor
        4. Right click specific instructions
        """
        # 1. Recunoaste item, id, ...,
        self.item_id = self.tree.identify('item', event.x, event.y)
        self.nume_nod = self.tree.item(self.item_id, 'text')
        # Urmatoarele sunt pentru consola sau status bar; cam asa ceva
        # self.nume_nod_pt_LabelInfo = self.nume_nod + ' -id ' + self.item_id
        # label_info.config(text=self.nume_nod_pt_LabelInfo)

        # 2. Extrage textul din tabel: cantinut; rand: id; coloana: text
        sql = "SELECT text FROM continut WHERE id=?"
        val = (self.item_id,)
        _t = self.curr.execute(sql, val)
        _t = self.curr.fetchone()  # -> tuplet

        # 3. Afiseaza textul in editor
        t = _t[0]  # textul din editor
        self.editor.delete('1.0', 'end')
        self.editor.insert('1.0', t)

        # 4. Right click specific procedures
        # Get x, y coordinate of mouser pointer
        self.pozitie_mouse = (self.tree.winfo_pointerxy())
       
        # Right click menu
        iid =self.tree.identify_row(event.y)
        if iid:
            # mouse pointer over item
            self.tree.selection_set(iid)
            self.rMenu.post(event.x_root, event.y_root)
        else:
            # mouse pointer not overt item
            # occurs when items do not fill frame
            # no action required
            pass


    def add_node(self, tip):
        """ Add a new node to tree.
            [PROCEDURE GUI - 6]
           
            tip:
                0 = above
                1 = below
                2 = child
        """
        _parent = self.tree.parent(self.item_id)  # -> str
        name_parent = self.tree.item(self.item_id)['text']

        # Determina noul id
        all_nodes = self.get_all_children('')
        self.noul_id = self.ultimul_id(all_nodes) + 1

        #Parent of tree is transformed from '' -> 0
        if _parent == '':
            parent = 0
        else:
            parent = _parent  # parent of current node

        # Item_id is transformed from '' -> 0
        if self.item_id == '':
            id_nod_activ = 0
        else:
            id_nod_activ = int(self.item_id)  # id_nod_activ vechi
        print(f'_parent = {_parent}, - nume: {name_parent}')

        # Take parent id and position/index
        par = self.tree.parent(id_nod_activ)
        poz = self.tree.index(id_nod_activ)
        print(f'Pozitia: {poz}; Parinte: {par}')

        # Node Above
        if tip == 0:
            index_nod_nou = poz
            self.tree.insert(par, index_nod_nou, self.noul_id, text='New Node')
            if par =='':
                par = 0
            else:
                par = par
            self.rearanjeaza_index_noduri_in_parinte_in_sql(par)

        # Node Below
        elif tip == 1:
            index_nod_nou = poz + 1
            self.tree.insert(par, index_nod_nou, self.noul_id, text='New Node')
            if par == '':
                par = 0
            else:
                par = par
            self.rearanjeaza_index_noduri_in_parinte_in_sql(par)

        # Node child
        elif tip == 2:
            par = id_nod_activ
            index_nod_nou = 0
            self.tree.insert(par, index_nod_nou, self.noul_id, text='New Node')
            self.rearanjeaza_index_noduri_in_parinte_in_sql(par)

        else:
            ...


    def get_all_children(self, item):
        """ Get all childrens in tree nodes ???
            [PROCEDURI GUI - 7]""" 

        children = self.tree.get_children(item)
        for child in children:
            children += self.get_all_children(child)  # -> tuple; iid of nodes
            i = self.tree.index(child)
        return children    


    def ultimul_id(self, ids) -> tuple:
        """ Ia ultimul Id. 
            [PROCEDURI - 8]
        """
        toate_id = [int(i) for i in ids]
        cel_mai_mare_id = max(toate_id)
        return cel_mai_mare_id  # type = int


    def rearanjeaza_index_noduri_in_parinte_in_sql(self, parinte):
        """ Rearanjeaza noduri ???
            [PROCEDURI GUI - 9] """
            
        # Ia nodurile din parinte intr-o lista
        childrens = self.tree.get_children(parinte)
        pozitia = self.tree.index(self.noul_id)
        nume = self.tree.item(self.noul_id)['text']
        self.scrie_nod_in_sqlite(parinte, pozitia, nume)

        # Update celelalte itemuri in sqlite
        for child in childrens:
            p = self.tree.index(child)  # pozitia child in bucla
            if int(child) != self.noul_id and p > pozitia:
                self.update_positions(int(child), p)
            else:
                ...


    def update_positions(self, iid, pozitia) -> 'int, int':
        """ Update pozitia.
            [PROCEDURI SQL - 10]"""
            
        sql = """UPDATE noduri
                 SET al_catelea=?
                 WHERE id=?"""
        date = (pozitia, iid)
        self.curr.execute(sql, date)
        self.conn.commit()


    def scrie_nod_in_sqlite(self, parent, pozitia, nume_nod_nou):
        """ Scrie nodul creat in sqlite.
            [PROCEDURI SQLITE - 11] """

        # Sqlite insert with parameters
        sql = """INSERT INTO noduri
                           (id, apartine_de_id, al_catelea, nume)
                           VALUES(?, ?, ?, ?);"""
        date = (self.noul_id, parent, pozitia, nume_nod_nou)
        self.curr.execute(sql, date)

        # Text sqlite
        text_sql = """INSERT INTO continut
                      (id, text)
                      VALUES(?, ?);"""
        te = ''
        date_text = (self.noul_id, te)
        self.curr.execute(text_sql, date_text)
        self.conn.commit()

    def rename_node(self):
        """ Rename node. """
        
        # Function that rename the node name
        def rename():
            new_name = entry_rename_node.get()

            # Write in db
            sql = "UPDATE noduri SET nume = ? WHERE id = ?"
            date = (new_name, self.item_id)
            self.curr.execute(sql, date)
            self.conn.commit()

            # Change name in tree
            self.tree.item(self.item_id, text=new_name)

            # Close windows Rename
            rename_win.destroy()
            self.tree.item(self.item_id, text=new_name)
       
        # Graphic User Interface
        #nonlocal entry_rename_node
        px = self.pozitie_mouse[0]
        py = self.pozitie_mouse[1]
        rename_win = tk.Toplevel(bg='white')
        rename_win.title('Rename')
        rename_win.geometry("{}x{}+{}+{}".format(220, 70, px, py))
        label_old_name = tk.Label(rename_win, text='Old name: ', bg='white')
        label_old_name.grid(row=0, column=0, sticky='w')
        label_name = tk.Label(rename_win, text=self.nume_nod, bg='white')
        label_name.grid(row=0, column=1, sticky='w')
        label_new_name = tk.Label(rename_win, text='New name: ', bg='white')
        label_new_name.grid(row=1, column=0)
        entry_rename_node = tk.Entry(rename_win)
        entry_rename_node.grid(row=1, column=1)
        entry_rename_node.focus()
        ok_rename_node = tk.Button(rename_win, text='Rename', command=rename, relief='flat', fg='blue', bg='white')
        ok_rename_node.grid(row=2, column=0)
        cancel_rename_node = tk.Button(rename_win, text='Cancel', command=lambda: rename_win.destroy(), relief='flat', fg='red', bg='white')
        cancel_rename_node.grid(row=2, column=1)


    def delete_node(self):
        """ Delete a node without WARNING.
            Work together with function: rearanjeaza_noduri_dupa_stergere.

            TO DO:
            [ ] - Add warning at delete
            [ ] - Add warning at node with sub-nodes
            [ ] - If last id delete not permited.

        """
        all_subnodes = list(self.get_all_children(self.item_id))
        all_subnodes.append(self.item_id)
        print(all_subnodes)
        par = self.tree.parent(self.item_id)  # par=parinte
        noul_id = self.tree.prev(self.item_id)
        self.tree.delete(self.item_id)

        # Reactualizare pozitii dupa stergere
        self.rearanjeaza_noduri_dupa_stergere(par, noul_id)

        # Reactualizeaza db (Delete from database)
        for i in all_subnodes:
            sql_3 = "DELETE FROM noduri WHERE id=?"
            sql_4 = "DELETE FROM continut WHERE id=?"
            self.curr.execute(sql_3, (i,))
            self.curr.execute(sql_4, (i,))
        self.conn.commit()


    def rearanjeaza_noduri_dupa_stergere(self, parinte, new_id):
        """ Rearanjeaza nodurile dupa stergere.
            Lucreaza cu functia delete_node.
        """
        # Ia nodurile din parinte intr-o lista
        copii = self.tree.get_children(parinte)
        pozitia = self.tree.index(new_id)
        nume = self.tree.item(new_id)['text']

        # SQL scrie noul item in sqlite db
        # scrie_nod_in_sqlite(new_id, parinte, pozitia, nume)
        # print(f'{copii}')
        # print(f'new_id = {new_id}, parinte = {parinte}, index = {pozitia}, {nume}')

        # Update celelalte itemuri in sqlite
        for copil in copii:
            p = self.tree.index(copil)  # pozitie copil in bucla
            if int(copil) != new_id and p > pozitia:
                self.update_positions(int(copil), p)
            else:
                ...


    # FUNCTII SI OPERATII SQLITE
    # ==========================
    def citeste_noduri_db(self) -> list:
        """Citeste tabelul 'noduri' din db.
           [PROCEDURI SQLITE - 1]
           
        Returns:
       list -- of tuples; a row = a tuplet within list
            Ex: [(id, apartine_de_id, al_catelea, nume), (5, 0, 0, '0'), (7, 0, 1, '1')]
        """
        sql = 'SELECT * from noduri'
        self.curr.execute(sql)
        tabel_noduri = self.curr.fetchall()  # list of tuple; [(1,0,0,'Default'), ...]
        return tabel_noduri

    def creaza_aranjeaza_noduri(self, tabel_noduri):
        """ Creaza si aranjeaza nodurile.
            [PROCEDURI SQLITE - 2]

        Args/Kwargs:
            tabel_noduri: list of tuplets -- extrase din sqlite
        """
        # Creare noduri; adauga items
        # ---------------------------
        # Curatare lista de items
        #for i in list(tree.get_children()):
        #    tree.delete(i)
        # Creare noduri
        for c in tabel_noduri:  # tabel_noduri = (1, 0, 0, 'Default'), ...
            #treeview.insert('',      '1',    'item1', text="Second Item")
            #treeview.insert('parent','index','id',    text="Name")
            self.tree.insert('', c[0]-1, c[0], text=c[3])
            #print('index=',c[0]-1, 'id=', c[0], c[3])
        # Aranjeaza noduri
        # ----------------
        for d in tabel_noduri:
            if d[1] != 0:  # tabel_noduri = (1, 0, 0, 'Default'), ...
                #treeview.move('id_child','id_parent(parent_index?)', 'position')
                #treeview.move('item2',   'item0',                    'end')
                self.tree.move(d[0], d[1], d[2])
            else:
                self.tree.move(d[0], '', d[2])
            
     


def _test():
    '''Build app main window.'''
    win = tk.Tk()
    win.title('Scriptorium')
    win.geometry('600x400+200+200')
    win.configure(background='white')
    app = Scriptorium(win)
    win.mainloop()

if __name__ == "__main__":
    _test()


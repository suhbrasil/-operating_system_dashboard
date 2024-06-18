import tkinter as tk
from tkinter import ttk

class View:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Directory Tree")
        self.tree = ttk.Treeview(self.root)
        self.tree.pack(expand=True, fill='both')
        self.tree.heading("#0", text="Directory Structure", anchor='w')

    def mainloop(self):
        self.root.mainloop()

    def display_directory_tree(self, directory_tree):
        for item in directory_tree:
            self._insert_item('', item)

    def _insert_item(self, parent, item):
        if item['type'] == 'directory':
            node = self.tree.insert(parent, 'end', text=item['name'], open=True)
            for child in item.get('children', []):
                self._insert_item(node, child)
        else:
            self.tree.insert(parent, 'end', text=f"{item['name']} (Size: {item['size']} bytes, Permissions: {item['permissions']}, Last Modified: {item['last_modified']})")

# Exemplo de uso:
if __name__ == "__main__":
    # Exemplo de árvore de diretórios (substitua pelo seu método de obtenção da árvore)
    directory_tree = [
        {'name': 'dir1', 'type': 'directory', 'children': [
            {'name': 'file1.txt', 'type': 'file', 'size': 1024, 'permissions': 'rw-r--r--', 'last_modified': '2024-06-20'},
            {'name': 'file2.txt', 'type': 'file', 'size': 2048, 'permissions': 'rwxr-xr-x', 'last_modified': '2024-06-19'}
        ]},
        {'name': 'dir2', 'type': 'directory', 'children': [
            {'name': 'subdir1', 'type': 'directory', 'children': [
                {'name': 'file3.txt', 'type': 'file', 'size': 4096, 'permissions': 'r--r--r--', 'last_modified': '2024-06-18'}
            ]}
        ]},
        {'name': 'file4.txt', 'type': 'file', 'size': 3072, 'permissions': 'rw-rw-r--', 'last_modified': '2024-06-17'}
    ]

    view = View()
    view.display_directory_tree(directory_tree)
    view.mainloop()

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk

# pyinstaller --onefile --windowed --icon=feliz.ico main.py
# Conectar ao banco de dados SQLite
def connect_db():
    conn = sqlite3.connect('gatos.db')
    return conn

# Criar as tabelas no banco de dados
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Gatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cor TEXT,
        raca TEXT,
        descricao TEXT,
        origem TEXT,
        caminho_imagem TEXT 
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Relacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pai INTEGER,
        id_mae INTEGER,
        id_filho INTEGER,
        id_avos_paternos INTEGER,
        id_avos_maternos INTEGER,
        FOREIGN KEY (id_pai) REFERENCES Gatos(id),
        FOREIGN KEY (id_mae) REFERENCES Gatos(id),
        FOREIGN KEY (id_filho) REFERENCES Gatos(id),
        FOREIGN KEY (id_avos_paternos) REFERENCES Gatos(id),
        FOREIGN KEY (id_avos_maternos) REFERENCES Gatos(id)
    )
    ''')
    conn.commit()
    conn.close()

def choose_image():
    image_path = filedialog.askopenfilename(title="Selecione a imagem do gato")
    if image_path:  # Se o usuário selecionou uma imagem
        entry_caminho_imagem.delete(0, tk.END)  # Limpar campo existente
        entry_caminho_imagem.insert(0, image_path)  # Inserir o caminho da imagem


# Função para adicionar um gato
def add_gato():
    conn = connect_db()
    cursor = conn.cursor()
    # Aqui estamos pegando o caminho da imagem do entry correspondente
    cursor.execute('''
    INSERT INTO Gatos (nome, cor, raca, descricao, origem, caminho_imagem) VALUES (?, ?, ?, ?, ?, ?)
    ''', (entry_nome.get(), entry_cor.get(), entry_raca.get(), entry_descricao.get(), entry_origem.get(), entry_caminho_imagem.get()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Gato adicionado com sucesso!")
    clear_entries()
    refresh_treeview()

# Função para adicionar relações
def add_relacao():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Seleção Inválida", "Selecione um gato para adicionar relações.")
        return
    gato_id = tree.item(selected_item)['values'][0]

    # Obter os IDs de pai, mãe, avós
    id_pai = entry_id_pai.get()
    id_mae = entry_id_mae.get()
    id_avos_paternos = entry_id_avos_paternos.get()
    id_avos_maternos = entry_id_avos_maternos.get()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Relacoes (id_pai, id_mae, id_filho, id_avos_paternos, id_avos_maternos) VALUES (?, ?, ?, ?, ?)
    ''', (id_pai, id_mae, gato_id, id_avos_paternos, id_avos_maternos))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Relação adicionada com sucesso!")
    clear_relacao_entries()

def load_image(caminho):
    try:
        img = Image.open(caminho)
        img = img.resize((200, 150), Image.LANCZOS)  # Redimensionar conforme necessário
        img_tk = ImageTk.PhotoImage(img)

        # Atualizar o label com a nova imagem
        img_label.config(image=img_tk)
        img_label.image = img_tk  # Manter uma referência à imagem
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível carregar a imagem: {e}")

# Função para limpar os campos de entrada de relação
def clear_relacao_entries():
    entry_id_pai.delete(0, tk.END)
    entry_id_mae.delete(0, tk.END)
    entry_id_avos_paternos.delete(0, tk.END)
    entry_id_avos_maternos.delete(0, tk.END)

# Função para visualizar os gatos
def view_gatos():
    for row in tree.get_children():
        tree.delete(row)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Gatos')
    for gato in cursor.fetchall():
        tree.insert('', 'end', values=gato)
    conn.close()

# Função para atualizar um gato
def update_gato():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Seleção Inválida", "Selecione um gato para atualizar.")
        return
    gato_id = tree.item(selected_item)['values'][0]
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE Gatos SET nome=?, cor=?, raca=?, descricao=?, origem=?, caminho_imagem=? WHERE id=?
    ''', (entry_nome.get(), entry_cor.get(), entry_raca.get(), entry_descricao.get(), entry_origem.get(), entry_caminho_imagem.get(), gato_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Gato atualizado com sucesso!")
    clear_entries()
    refresh_treeview()

# Função para excluir um gato
def delete_gato():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Seleção Inválida", "Selecione um gato para excluir.")
        return
    gato_id = tree.item(selected_item)['values'][0]
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Gatos WHERE id=?', (gato_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Gato excluído com sucesso!")
    refresh_treeview()

# Função para limpar os campos de entrada
def clear_entries():
    entry_nome.delete(0, tk.END)
    entry_cor.delete(0, tk.END)
    entry_raca.delete(0, tk.END)
    entry_descricao.delete(0, tk.END)
    entry_origem.delete(0, tk.END)
    entry_caminho_imagem.delete(0, tk.END)

# Função para atualizar a TreeView
def refresh_treeview():
    view_gatos()

# Função para mostrar detalhes do gato e suas relações
def show_gato_details(event):
    selected_item = tree.selection()
    if not selected_item:
        return

    gato_id = tree.item(selected_item)['values'][0]
    conn = connect_db()
    cursor = conn.cursor()

    # Buscar informações do gato selecionado
    cursor.execute('SELECT * FROM Gatos WHERE id=?', (gato_id,))
    gato = cursor.fetchone()

    # Se um gato for encontrado, preencha os campos de entrada
    if gato:
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, gato[1])
        entry_cor.delete(0, tk.END)
        entry_cor.insert(0, gato[2])
        entry_raca.delete(0, tk.END)
        entry_raca.insert(0, gato[3])
        entry_descricao.delete(0, tk.END)
        entry_descricao.insert(0, gato[4])
        entry_origem.delete(0, tk.END)
        entry_origem.insert(0, gato[5])
        entry_caminho_imagem.delete(0, tk.END)
        entry_caminho_imagem.insert(0, gato[6])  # Novo campo para caminho da imagem

        # Carregar e exibir a imagem do gato
        load_image(gato[6])

    # Limpar as relações
    cursor.execute('SELECT id_pai, id_mae, id_avos_paternos, id_avos_maternos FROM Relacoes WHERE id_filho=?', (gato_id,))
    relacoes = cursor.fetchone()

    if relacoes:
        entry_id_pai.delete(0, tk.END)
        entry_id_pai.insert(0, relacoes[0] if relacoes[0] else "")
        entry_id_mae.delete(0, tk.END)
        entry_id_mae.insert(0, relacoes[1] if relacoes[1] else "")
        entry_id_avos_paternos.delete(0, tk.END)
        entry_id_avos_paternos.insert(0, relacoes[2] if relacoes[2] else "")
        entry_id_avos_maternos.delete(0, tk.END)
        entry_id_avos_maternos.insert(0, relacoes[3] if relacoes[3] else "")
    else:
        clear_relacao_entries()

    gato_id = tree.item(selected_item)['values'][0]
    conn = connect_db()
    cursor = conn.cursor()

    # Buscar informações do gato selecionado
    cursor.execute('SELECT * FROM Gatos WHERE id=?', (gato_id,))
    gato = cursor.fetchone()

    # Buscar relações
    cursor.execute('SELECT id_pai, id_mae, id_avos_paternos, id_avos_maternos FROM Relacoes WHERE id_filho=?', (gato_id,))
    relacoes = cursor.fetchone()

    # Exibir informações do gato e suas relações
    detalhes = f"Gato: {gato[1]} (ID: {gato[0]})\nCor: {gato[2]}\nRaça: {gato[3]}\nDescrição: {gato[4]}\nOrigem: {gato[5]}\n\n"

    if relacoes:
        # Obter os IDs dos pais e avós
        pai_id = relacoes[0]
        mae_id = relacoes[1]
        avos_paternos_id = relacoes[2]
        avos_maternos_id = relacoes[3]

        # Buscar os nomes e IDs dos pais
        if pai_id:
            cursor.execute('SELECT nome FROM Gatos WHERE id=?', (pai_id,))
            pai = cursor.fetchone()
            pai_nome = pai[0] if pai else "Desconhecido"
        else:
            pai_nome = "Desconhecido"

        if mae_id:
            cursor.execute('SELECT nome FROM Gatos WHERE id=?', (mae_id,))
            mae = cursor.fetchone()
            mae_nome = mae[0] if mae else "Desconhecido"
        else:
            mae_nome = "Desconhecido"

        # Buscar os nomes e IDs dos avós
        if avos_paternos_id:
            cursor.execute('SELECT nome FROM Gatos WHERE id=?', (avos_paternos_id,))
            avos_paternos = cursor.fetchone()
            avos_paternos_nome = avos_paternos[0] if avos_paternos else "Desconhecido"
        else:
            avos_paternos_nome = "Desconhecido"

        if avos_maternos_id:
            cursor.execute('SELECT nome FROM Gatos WHERE id=?', (avos_maternos_id,))
            avos_maternos = cursor.fetchone()
            avos_maternos_nome = avos_maternos[0] if avos_maternos else "Desconhecido"
        else:
            avos_maternos_nome = "Desconhecido"

        # Adicionar os nomes e IDs às informações
        detalhes += (
            f"Pai: {pai_nome} (ID: {pai_id if pai_id else 'N/A'})\n"
            f"Mãe: {mae_nome} (ID: {mae_id if mae_id else 'N/A'})\n"
            f"Avô Paterno: {avos_paternos_nome} (ID: {avos_paternos_id if avos_paternos_id else 'N/A'})\n"
            f"Avó Materna: {avos_maternos_nome} (ID: {avos_maternos_id if avos_maternos_id else 'N/A'})\n"
        )
    else:
        detalhes += "Relações: Não há informações disponíveis."

    # Buscar filhos do gato selecionado
    cursor.execute('SELECT id_filho FROM Relacoes WHERE id_pai=? OR id_mae=?', (gato_id, gato_id))
    filhos = cursor.fetchall()

    if filhos:
        detalhes += "\nFilhos:\n"
        for filho in filhos:
            filho_id = filho[0]
            cursor.execute('SELECT nome FROM Gatos WHERE id=?', (filho_id,))
            filho_nome = cursor.fetchone()
            if filho_nome:
                detalhes += f"- {filho_nome[0]} (ID: {filho_id})\n"
    else:
        detalhes += "\nFilhos: Não há informações disponíveis."

    messagebox.showinfo("Detalhes do Gato", detalhes)
    conn.close()

# Criar a janela principal
app = tk.Tk()
app.title("Gerenciador de Gatos")
app.geometry("1280x600")

img = Image.open("feliz.png")  
img = img.resize((200, 150), Image.LANCZOS)   
img_tk = ImageTk.PhotoImage(img)

img_label = tk.Label(app, image=img_tk)
img_label.grid(row=0, column=2, rowspan=10) 

# Campos de entrada
tk.Label(app, text="Nome:").grid(row=0, column=0)
entry_nome = tk.Entry(app)
entry_nome.grid(row=0, column=1)

tk.Label(app, text="Cor:").grid(row=1, column=0)
entry_cor = tk.Entry(app)
entry_cor.grid(row=1, column=1)

tk.Label(app, text="Raça:").grid(row=2, column=0)
entry_raca = tk.Entry(app)
entry_raca.grid(row=2, column=1)

tk.Label(app, text="Descrição:").grid(row=3, column=0)
entry_descricao = tk.Entry(app)
entry_descricao.grid(row=3, column=1)

tk.Label(app, text="Origem:").grid(row=4, column=0)
entry_origem = tk.Entry(app)
entry_origem.grid(row=4, column=1)

# Campos para adicionar relações
tk.Label(app, text="ID Pai:").grid(row=5, column=0)
entry_id_pai = tk.Entry(app)
entry_id_pai.grid(row=5, column=1)

tk.Label(app, text="ID Mãe:").grid(row=6, column=0)
entry_id_mae = tk.Entry(app)
entry_id_mae.grid(row=6, column=1)

tk.Label(app, text="ID Avô Paterno:").grid(row=7, column=0)
entry_id_avos_paternos = tk.Entry(app)
entry_id_avos_paternos.grid(row=7, column=1)

tk.Label(app, text="ID Avó Materna:").grid(row=8, column=0)
entry_id_avos_maternos = tk.Entry(app)
entry_id_avos_maternos.grid(row=8, column=1)

# Novo campo para o caminho da imagem
tk.Label(app, text="Caminho da Imagem:").grid(row=9, column=0)
entry_caminho_imagem = tk.Entry(app)
entry_caminho_imagem.grid(row=9, column=1)

# Botões
tk.Button(app, text="Adicionar Gato", command=add_gato).grid(row=10, column=0)
tk.Button(app, text="Adicionar Relação", command=add_relacao).grid(row=10, column=1)
tk.Button(app, text="Atualizar", command=update_gato).grid(row=10, column=2)
tk.Button(app, text="Excluir", command=delete_gato).grid(row=10, column=3)
tk.Button(app, text="Escolher Imagem", command=choose_image).grid(row=10, column=2)


# TreeView para exibir os gatos
tree = ttk.Treeview(app, columns=("ID", "Nome", "Cor", "Raça", "Descrição", "Origem"), show='headings')
tree.grid(row=11, column=0, columnspan=4)
tree.heading("ID", text="ID")
tree.heading("Nome", text="Nome")
tree.heading("Cor", text="Cor")
tree.heading("Raça", text="Raça")
tree.heading("Descrição", text="Descrição")
tree.heading("Origem", text="Origem")

# Vincular o evento de seleção
tree.bind("<Double-1>", show_gato_details)

# Criar as tabelas
create_tables()

# Atualizar a TreeView ao iniciar
refresh_treeview()

# Iniciar a aplicação
app.mainloop()
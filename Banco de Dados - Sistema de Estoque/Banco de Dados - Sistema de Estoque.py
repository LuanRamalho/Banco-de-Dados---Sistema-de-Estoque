import tkinter as tk
from tkinter import ttk  # Para widgets com estilo
from tkinter import messagebox  # Para caixas de mensagens
import json
import os

DATABASE_FILE = "estoque.json"

def carregar_dados():
    """Carrega os dados do arquivo JSON."""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:  # Trata erro se o JSON estiver corrompido
                return {"produtos": []}
    return {"produtos": []}

def salvar_dados(dados):
    """Salva os dados no arquivo JSON."""
    with open(DATABASE_FILE, "w") as f:
        json.dump(dados, f, indent=4)

def cadastrar_produto():
    """Cadastra um novo produto."""
    try:
        preco_custo = float(entry_preco_custo.get())
        preco_venda = float(entry_preco_venda.get())

        dados = carregar_dados()
        produto = {
            "sku": entry_sku.get(),
            "descricao": entry_descricao.get(),
            "fornecedor": entry_fornecedor.get(),
            "preco_custo": preco_custo,
            "preco_venda": preco_venda,
            "unidade": entry_unidade.get(),
            "localizacao": entry_localizacao.get(),
            "estoque": 0
        }
        dados["produtos"].append(produto)
        salvar_dados(dados)
        messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
        limpar_campos_cadastro()  # Limpa os campos após o cadastro
    except ValueError:
        messagebox.showerror("Erro", "Preço de custo e venda devem ser números.")

def limpar_campos_cadastro():
    entry_sku.delete(0, tk.END)
    entry_descricao.delete(0, tk.END)
    entry_fornecedor.delete(0, tk.END)
    entry_preco_custo.delete(0, tk.END)
    entry_preco_venda.delete(0, tk.END)
    entry_unidade.delete(0, tk.END)
    entry_localizacao.delete(0, tk.END)


def entrada_mercadoria():
    try:
        quantidade = int(entry_quantidade.get())
        dados = carregar_dados()
        sku = entry_sku_entrada.get()

        for produto in dados["produtos"]:
            if produto["sku"] == sku:
                produto["estoque"] += quantidade
                salvar_dados(dados)
                messagebox.showinfo("Sucesso", f"Estoque de {produto['descricao']} atualizado. Novo estoque: {produto['estoque']}")
                entry_quantidade.delete(0, tk.END)  # Limpa o campo após a entrada
                return

        messagebox.showerror("Erro", "Produto não encontrado.")
    except ValueError:
        messagebox.showerror("Erro", "Quantidade deve ser um número inteiro.")

def listar_produtos():
    dados = carregar_dados()
    if not dados["produtos"]:
        messagebox.showinfo("Aviso", "Nenhum produto cadastrado.")
        return

    janela_listagem = tk.Toplevel(janela_principal)
    janela_listagem.title("Listagem de Produtos")
    janela_listagem.configure(bg="#3E047F")

    # Barra de Busca
    def buscar_produto():
        termo_busca = entry_busca.get().lower()
        for item in tree.get_children():
            tree.delete(item)
        for produto in dados["produtos"]:
            if termo_busca in produto['descricao'].lower() or termo_busca in produto['sku'].lower():
                tree.insert("", tk.END, values=(produto['sku'], produto['descricao'], produto['estoque'], produto['preco_custo'], produto['preco_venda'], produto['fornecedor'], produto['unidade'], produto['localizacao']))

    tk.Label(janela_listagem, text="Buscar Produto (por Descrição ou SKU):", font=("Arial",12,"bold"), bg="#3E047F", fg="#ffffff").pack(pady=(10,0))
    entry_busca = tk.Entry(janela_listagem, font=("Arial",12,"bold"))
    entry_busca.pack()
    btn_buscar = tk.Button(janela_listagem, text="Buscar", command=buscar_produto, font=("Arial",12,"bold"), bg="#11F700", fg="#150101")
    btn_buscar.pack(pady=(0,10))

    # Frame para o Treeview e a Scrollbar
    frame_tree = ttk.Frame(janela_listagem) # Criando um frame para o treeview e a scrollbar
    frame_tree.pack(fill="both", expand=True) # Expande o frame

    # Treeview (Tabela)
    tree = ttk.Treeview(frame_tree, columns=("SKU", "Descrição", "Estoque", "Preço Custo", "Preço Venda", "Fornecedor", "Unidade", "Localização"), show="headings")

    tree.heading("SKU", text="SKU")
    tree.heading("Descrição", text="Descrição")
    tree.heading("Estoque", text="Estoque")
    tree.heading("Preço Custo", text="Preço Custo")
    tree.heading("Preço Venda", text="Preço Venda")
    tree.heading("Fornecedor", text="Fornecedor")
    tree.heading("Unidade", text="Unidade")
    tree.heading("Localização", text="Localização")

    # Adiciona os dados na tabela
    for produto in dados["produtos"]:
        tree.insert("", tk.END, values=(produto['sku'], produto['descricao'], produto['estoque'], produto['preco_custo'], produto['preco_venda'], produto['fornecedor'], produto['unidade'], produto['localizacao']))

    # Scrollbar Horizontal
    scrollbar_x = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=scrollbar_x.set)

    # Scrollbar Vertical
    scrollbar_y = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar_y.set)

    tree.pack(fill="both", expand=True)  # treeview dentro do frame

    # Função para editar um item
    def editar_item():
        try:
            item_selecionado = tree.selection()[0]
            valores = tree.item(item_selecionado)['values']

            janela_edicao = tk.Toplevel(janela_listagem)
            janela_edicao.title("Editar Produto")

            entradas_edicao = [] #lista para armazenar os entrys
            labels = ["SKU:", "Descrição:", "Estoque:", "Preço Custo:", "Preço Venda:", "Fornecedor:", "Unidade:", "Localização:"]

            for i, label_texto in enumerate(labels):
                tk.Label(janela_edicao, text=label_texto).grid(row=i, column=0, sticky="w")
                entry = tk.Entry(janela_edicao)
                entry.insert(0, valores[i])
                entry.grid(row=i, column=1, padx=5, pady=2)
                entradas_edicao.append(entry)

            def salvar_edicao():
              try:
                  novos_valores = []
                  for i, entrada in enumerate(entradas_edicao):
                    if i == 2:
                      novos_valores.append(int(entrada.get()))
                    elif i == 3 or i == 4:
                      novos_valores.append(float(entrada.get()))
                    else:
                      novos_valores.append(entrada.get())
                  tree.item(item_selecionado, values=novos_valores)
                  for i, produto in enumerate(dados['produtos']):
                      if produto['sku'] == valores[0]:
                          dados['produtos'][i]['sku'] = entradas_edicao[0].get()
                          dados['produtos'][i]['descricao'] = entradas_edicao[1].get()
                          dados['produtos'][i]['estoque'] = int(entradas_edicao[2].get())
                          dados['produtos'][i]['preco_custo'] = float(entradas_edicao[3].get())
                          dados['produtos'][i]['preco_venda'] = float(entradas_edicao[4].get())
                          dados['produtos'][i]['fornecedor'] = entradas_edicao[5].get()
                          dados['produtos'][i]['unidade'] = entradas_edicao[6].get()
                          dados['produtos'][i]['localizacao'] = entradas_edicao[7].get()
                          salvar_dados(dados)
                          break
                  janela_edicao.destroy()
              except ValueError:
                messagebox.showerror("Erro", "Preço de custo e venda e estoque devem ser números.")

            btn_salvar_edicao = ttk.Button(janela_edicao, text="Salvar Edição", command=salvar_edicao)
            btn_salvar_edicao.grid(row=len(labels), column=0, columnspan=2, pady=10)

        except IndexError:
            messagebox.showinfo("Aviso", "Selecione um item para editar.")

    btn_editar = tk.Button(janela_listagem, text="Editar", command=editar_item, font=("Arial",12,"bold"), bg="#F7F401", fg="#2301B8")
    btn_editar.pack()

    def excluir_item():
        try:
            item_selecionado = tree.selection()[0]
            valores = tree.item(item_selecionado)['values']
            confirmacao = messagebox.askyesno("Confirmação", f"Deseja excluir o produto {valores[1]}?")
            if confirmacao:
                tree.delete(item_selecionado)
                for i, produto in enumerate(dados['produtos']):
                    if produto['sku'] == valores[0]:
                        del dados['produtos'][i]
                        salvar_dados(dados)
                        break
        except IndexError:
            messagebox.showinfo("Aviso", "Selecione um item para excluir.")

    btn_excluir = tk.Button(janela_listagem, text="Excluir", command=excluir_item, font=("Arial",12,"bold"), bg="#00F8DE", fg="#205C00")
    btn_excluir.pack()
    

# --- Interface Gráfica (Tkinter) ---
janela_principal = tk.Tk()
janela_principal.title("Sistema de Gestão de Estoque")
janela_principal.configure(bg="#e0f2f7")  # Cor de fundo mais suave

# Frame de Cadastro
frame_cadastro = tk.LabelFrame(janela_principal, text="Cadastro de Produto", bg="#e0f2f7")
frame_cadastro.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

tk.Label(frame_cadastro, text="SKU:", bg="#e0f2f7").grid(row=0, column=0, sticky="w")
entry_sku = tk.Entry(frame_cadastro)
entry_sku.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_cadastro, text="Descrição:", bg="#e0f2f7").grid(row=1, column=0, sticky="w")
entry_descricao = tk.Entry(frame_cadastro)
entry_descricao.grid(row=1, column=1, padx=5, pady=2)

tk.Label(frame_cadastro, text="Fornecedor:", bg="#e0f2f7").grid(row=2, column=0, sticky="w")
entry_fornecedor = tk.Entry(frame_cadastro)
entry_fornecedor.grid(row=2, column=1, padx=5, pady=2)

tk.Label(frame_cadastro, text="Preço Custo:", bg="#e0f2f7").grid(row=3, column=0, sticky="w")
entry_preco_custo = tk.Entry(frame_cadastro)
entry_preco_custo.grid(row=3, column=1, padx=5, pady=2)

tk.Label(frame_cadastro, text="Preço Venda:", bg="#e0f2f7").grid(row=4, column=0, sticky="w")
entry_preco_venda = tk.Entry(frame_cadastro)
entry_preco_venda.grid(row=4, column=1, padx=5, pady=2)

tk.Label(frame_cadastro, text="Unidade:", bg="#e0f2f7").grid(row=5, column=0, sticky="w")
entry_unidade = tk.Entry(frame_cadastro)
entry_unidade.grid(row=5, column=1, padx=5, pady=2)

tk.Label(frame_cadastro, text="Localização:", bg="#e0f2f7").grid(row=6, column=0, sticky="w")
entry_localizacao = tk.Entry(frame_cadastro)
entry_localizacao.grid(row=6, column=1, padx=5, pady=2)

btn_cadastrar = tk.Button(frame_cadastro, text="Cadastrar", command=cadastrar_produto, font=("Arial",12,"bold"), bg="#730018", fg="white")
btn_cadastrar.grid(row=7, column=0, columnspan=2, pady=10)


# Frame de Entrada de Mercadoria
frame_entrada = tk.LabelFrame(janela_principal, text="Entrada de Mercadoria", bg="#e0f2f7")
frame_entrada.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


tk.Label(frame_entrada, text="SKU:", bg="#e0f2f7").grid(row=0, column=0, sticky="w")
entry_sku_entrada = tk.Entry(frame_entrada)
entry_sku_entrada.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_entrada, text="Quantidade:", bg="#e0f2f7").grid(row=1, column=0, sticky="w")
entry_quantidade = tk.Entry(frame_entrada)
entry_quantidade.grid(row=1, column=1, padx=5, pady=2)

btn_entrada = tk.Button(frame_entrada, text="Dar Entrada", command=entrada_mercadoria, font=("Arial",12,"bold"), bg="#B700C7", fg="white")
btn_entrada.grid(row=2, column=0, columnspan=2, pady=10)

# Botão de Listar Produtos
btn_listar = tk.Button(janela_principal, text="Listar Produtos", command=listar_produtos, font=("Arial",12,"bold"), bg="#037426", fg="white")
btn_listar.grid(row=1, column=0, columnspan=2, pady=10)

janela_principal.mainloop()
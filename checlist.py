import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw

# Dados de depósitos e ferramentas
itemsByDeposit = {
    "Depósito 6":["Kit Cinta Arqueamento"],
    "Depósito 9":["Trena","Escova de Aço","Martelo","Estilete","Tesoura","Kit Cinta Arqueamento"],
    "Depósito 13":["Tesoura de Corte","Chave Combinada","Trena","Alicate Universal","Chave de Fenda","Martelo","Estilete","Pé-de-Cabra Torcido","Marreta","Ferramento","Hands Off"],
    "Depósito 24":["Trena","Pé de Cabra Torcido","Tesoura de Corte","Alicate Corta Cabo","Martelo","Escova de Aço","Chave de Fenda","Kit Cinta Arqueamento"],
    "Depósito 25":["Chave de Fenda","Alicate Universal","Martelo","Estilete","Pé de Cabra Torcido","Trena","Kit Cinta Arqueamento","Grampeador"],
    "Carpintaria":["Chave de Fenda","Alicate Universal","Martelo","Estilete","Trena","Torque Armador 12","Esquadro 10 para Carpinteiro","Lápis Carpinteiro","Formão para Madeira","Kit de Chave Combinada","Serra Tico e Teco","Jogo de Brocas e Soquetes","Parafusadeira Elétrica","Lâmina de Serra Tico-Teco"]
}

# Programa principal
class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Checklist de Inspeção de Ferramentas")
        self.photosData = {}  # Fotos por item
        self.sig_image = None

        # Matrícula
        tk.Label(root, text="Matrícula:").grid(row=0,column=0,sticky="w")
        self.matricula_entry = tk.Entry(root)
        self.matricula_entry.grid(row=0,column=1,sticky="ew")

        # Depósito
        tk.Label(root, text="Depósito:").grid(row=1,column=0,sticky="w")
        self.deposit_var = tk.StringVar()
        self.deposit_cb = ttk.Combobox(root, textvariable=self.deposit_var, values=list(itemsByDeposit.keys()))
        self.deposit_cb.grid(row=1,column=1,sticky="ew")
        self.deposit_cb.bind("<<ComboboxSelected>>", self.load_items)

        # Observação geral
        tk.Label(root, text="Observação Geral:").grid(row=2,column=0,sticky="nw")
        self.general_obs = tk.Text(root, height=4, width=50)
        self.general_obs.grid(row=2,column=1,sticky="ew")

        # Frame para itens
        self.items_frame = tk.Frame(root)
        self.items_frame.grid(row=3,column=0,columnspan=2,sticky="nsew")
        self.items_widgets = []

        # Assinatura
        tk.Label(root, text="Assinatura:").grid(row=4,column=0,sticky="w")
        self.sig_canvas = tk.Canvas(root, width=400, height=100, bg="white", borderwidth=1, relief="solid")
        self.sig_canvas.grid(row=4,column=1,sticky="ew")
        self.sig_canvas.bind("<B1-Motion>", self.draw_signature)
        self.sig_image = Image.new("RGB", (400,100), "white")
        self.draw = ImageDraw.Draw(self.sig_image)

        # Botão gerar PDF
        self.generate_btn = tk.Button(root, text="Gerar PDF", command=self.generate_pdf, bg="#2eb872", fg="white")
        self.generate_btn.grid(row=5,column=0,columnspan=2,pady=10)

    def draw_signature(self, event):
        x, y = event.x, event.y
        self.sig_canvas.create_oval(x, y, x+2, y+2, fill="black")
        self.draw.ellipse([x, y, x+2, y+2], fill="black")

    def load_items(self, event):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        self.items_widgets = []
        self.photosData = {}

        deposito = self.deposit_var.get()
        items = itemsByDeposit.get(deposito, [])
        for idx, item_name in enumerate(items):
            frame = tk.Frame(self.items_frame, borderwidth=1, relief="solid", pady=5)
            frame.pack(fill="x", padx=5, pady=2)

            tk.Label(frame, text=f"{idx+1}. {item_name}", font=("Arial",10,"bold")).pack(anchor="w")
            status_var = tk.StringVar(value="Aprovada")
            tk.Radiobutton(frame, text="Aprovada", variable=status_var, value="Aprovada").pack(side="left")
            tk.Radiobutton(frame, text="Reprovada", variable=status_var, value="Reprovada").pack(side="left")

            obs_entry = tk.Entry(frame, width=40)
            obs_entry.pack(side="left", padx=5)
            tk.Button(frame, text="📷 1", command=lambda i=idx: self.add_photo(i,0)).pack(side="left")
            tk.Button(frame, text="📷 2", command=lambda i=idx: self.add_photo(i,1)).pack(side="left")

            self.items_widgets.append({"name":item_name,"status_var":status_var,"obs_entry":obs_entry})
            self.photosData[idx] = [None,None]

    def add_photo(self, index, photo_index):
        file_path = filedialog.askopenfilename(filetypes=[("Imagens","*.png;*.jpg;*.jpeg")])
        if file_path:
            self.photosData[index][photo_index] = file_path
            messagebox.showinfo("Foto", f"Foto {photo_index+1} adicionada ao item {self.items_widgets[index]['name']}")

    def generate_pdf(self):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Checklist_{now}.pdf"
        c = pdfcanvas.Canvas(filename, pagesize=A4)
        width, height = A4
        y = height - 50

        # Cabeçalho
        c.setFont("Helvetica-Bold",14)
        c.drawCentredString(width/2, y, "Checklist de Inspeção de Ferramentas – Depósito")
        y -= 25
        c.setFont("Helvetica",10)
        c.drawString(50,y,f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        c.drawRightString(width-50,y,f"Depósito: {self.deposit_var.get()}")
        y -= 20
        c.drawString(50,y,f"Inspetor: {self.matricula_entry.get()}")
        y -= 20
        c.drawString(50,y,"Observação Geral:")
        y -= 15
        text = self.general_obs.get("1.0","end").strip()
        for line in text.split("\n"):
            c.drawString(60,y,line)
            y -= 12
        y -= 10

        # Itens
        for idx, w in enumerate(self.items_widgets):
            c.setFont("Helvetica-Bold",11)
            c.drawString(50,y,f"{idx+1}. {w['name']}")
            y -= 15
            c.setFont("Helvetica",10)
            c.drawString(60,y,f"Status: {w['status_var'].get()}")
            y -= 12
            c.drawString(60,y,f"Observação: {w['obs_entry'].get()}")
            y -= 12

            # Fotos
            for photo_path in self.photosData[idx]:
                if photo_path:
                    img = Image.open(photo_path)
                    img.thumbnail((150,150))
                    c.drawImage(ImageReader(img), 60, y-150, width=img.width, height=img.height)
                    y -= img.height + 10
            y -= 10
            if y < 150:
                c.showPage()
                y = height - 50

        # Assinatura
        c.drawString(50,y,"Assinatura:")
        sig_path = f"signature_{now}.png"
        self.sig_image.save(sig_path)
        c.drawImage(sig_path,50,y-80, width=200, height=80)
        c.save()
        messagebox.showinfo("PDF gerado", f"PDF salvo como {filename}")

# Executa o programa
root = tk.Tk()
root.geometry("700x800")
app = ChecklistApp(root)
root.mainloop()

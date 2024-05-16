import customtkinter
from customtkinter import CTk, CTkButton, CTkEntry, CTkLabel, CTkScrollbar, CTkTextbox
from tkinter import messagebox
import boto3
from ldap3 import Server, Connection, SAFE_SYNC
from datetime import datetime

class AWS:
    def __init__(self):
        self.janela = CTk()
        self.version = 'V 0.1'
        self.janela.geometry('300x300')
        self.janela.title('Login')

        CTkLabel(self.janela, text=self.version).place(x=270, y=280)

        self.janela.resizable(False, False)

        CTkLabel(self.janela, text='Usuário :').place(x=10, y=30)
        self.user = CTkEntry(self.janela)
        self.user.place(x=75, y=31)

        CTkLabel(self.janela, text='  Senha  :').place(x=10, y=80)
        self.password = CTkEntry(self.janela, show='*')
        self.password.place(x=75, y=81)
        CTkButton(self.janela, command=self.login, text='Entrar').place(x=75, y=120)
        CTkButton(self.janela, text='Sair', command=self.janela.destroy).place(x=75, y=180)

        # Vincula a função de atalho de teclado
        self.janela.bind("<Control-p>", self.parametros)  # Atalho Ctrl + P
        self.janela.mainloop()

    def parametros(self, event):
        print('aa')


    def login(self):
        self.usuario = self.user.get()
        self.senha = self.password.get()
        self.dom = 'gacc'
        server = Server('192.168.0.1')

        try:
            conn = Connection(server, f'{self.dom}\\{self.usuario}', f'{self.senha}', client_strategy=SAFE_SYNC,
                              auto_bind=True)
            status, result, response, _ = conn.search('o=test', '(objectclass=*)')
            log = True

        except:
            messagebox.showinfo(title='Erro', message='Usuário ou Senha incorretos')
            log = False

        if log:
            self.app()
        else:
            pass



    def app(self):
        self.janela.destroy()
        self.home = CTk()
        self.home.geometry('400x300')
        self.home.attributes('-fullscreen', True)
        self.home.title('Home')

        self.objetos_listbox = CTkTextbox(self.home, width=800, height=500)
        self.objetos_listbox.place(x=20, y=50)

        scrollbar = CTkScrollbar(self.home, command=self.objetos_listbox.yview)
        scrollbar.place(x=800, y=50)
        self.objetos_listbox.configure(yscrollcommand=scrollbar.set)

        CTkButton(self.home, text='Verificar Objetos', command=self.verificar_objetos_especificos).place(x=20, y=580)

        #SAIR
        toggle_button = customtkinter.CTkButton(self.home, text="Sair", command=self.home.destroy)
        toggle_button.place(x=1200, y=708)

        self.home.mainloop()
    def verificar_objetos_especificos(self):
        # Criar um cliente S3
        s3 = boto3.client('s3')

        # Dicionário de buckets e objetos esperados
        buckets_objetos_esperados = {
            'gacc-backup-bancos-sem-versionamento': [],
            'gacc-backup-tsv-fusion': [],
            'gacc-backup-bancos': []
        }

        # Limpar a listbox antes de atualizar
        self.limpar_listbox()

        # Data de hoje
        hoje = datetime.utcnow().date()  # Apenas a data, sem informações de hora

        # Iterar sobre os buckets e objetos esperados
        for bucket_name, objetos_esperados in buckets_objetos_esperados.items():
            print(f'Bucket: {bucket_name}')
            self.objetos_listbox.insert('end', 'Bucket: ')
            bucket_start_index = self.objetos_listbox.index('end')  # Obter o índice de início do nome do bucket
            self.objetos_listbox.insert('end', bucket_name)  # Adicionar o nome do bucket
            self.objetos_listbox.insert('end', '\n')  # Inserir uma nova linha para separar o nome do bucket
            bucket_end_index = self.objetos_listbox.index('end')  # Obter o índice de fim do nome do bucket
            # Aplicar estilo ao nome do bucket
            self.objetos_listbox._textbox.tag_add('bucket_name', bucket_start_index, bucket_end_index)
            self.objetos_listbox._textbox.tag_configure('bucket_name', font='TkDefaultFont 9 bold')

            # Listar os objetos dentro do bucket
            response = s3.list_objects_v2(Bucket=bucket_name)

            # Verificar se há objetos no bucket
            if 'Contents' in response:
                # Filtrar os objetos baseados no último momento de modificação
                objetos_presentes = [objeto for objeto in response['Contents'] if
                                     self.eh_hoje(objeto['LastModified'], hoje)]
                for i, objeto_presente in enumerate(objetos_presentes, start=1):
                    print(f'Objeto: {objeto_presente["Key"]} - Encontrado hoje: Sim')
                    self.objetos_listbox.insert('end', f'{i}. Objeto: {objeto_presente["Key"]} --- Encontrado hoje: Sim')
                    self.objetos_listbox.insert('end', '\n')  # Inserir uma nova linha para separar os objetos
            else:
                print(f'O bucket {bucket_name} está vazio ou não existe.')
                self.objetos_listbox.insert('end', f'O bucket {bucket_name} está vazio ou não existe.')
                self.objetos_listbox.insert('end', '\n')  # Inserir uma nova linha
    def eh_hoje(self, last_modified_str, hoje):
        if isinstance(last_modified_str, datetime):
            last_modified = last_modified_str.date()  # Converter datetime em date
        else:
            last_modified = datetime.strptime(last_modified_str, '%Y-%m-%dT%H:%M:%S.%fZ').date()
        return last_modified == hoje
    def limpar_listbox(self):
        if self.objetos_listbox.get('1.0', 'end-1c'):
            self.objetos_listbox.delete('1.0', 'end')

    # Executar a função para verificar os objetos específicos nos buckets

# Executar a função para verificar os objetos específicos nos buckets
AWS()

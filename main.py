from kivy.app import App 
from kivy.lang import Builder #chama as janelas
from telas import *
from botoes import *
import requests #interagir com um link na internet
from bannervenda import BannerVenda
from bannervendedor import BannerVendedor
import os
from functools import partial #permite passar um parametro para uma funcao dentro do botao
from myfirebase import MyFirebase #importar funcoes criar conta e fazer login
from datetime import date


GUI = Builder.load_file('main.kv') #interface visual, carregar arquivo da tela mostrada, sempre depois de tudo e antes do MainApp
class MainApp(App):
    
    cliente = None
    produto = None
    unidade = None
    
    def build(self):
        self.firebase = MyFirebase()
        return GUI #cria interface visual
    
    def on_start(self):
        # carregar as fotos de perfil
        arquivos = os.listdir("icones/fotos_perfil")
        # pega a pagina pelo id dela no main.kv
        pagina_fotoperfil = self.root.ids["fotoperfilpage"]
        # pega o id que quer alterar da pagina fotoperfilpage.kv
        lista_fotos = pagina_fotoperfil.ids["lista_fotos_perfil"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_perfil/{foto}", on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)
            
        # carregar as fotos dos clientes
        arquivos = os.listdir("icones/fotos_clientes")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}", 
                                 on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace('.png', '').capitalize(), 
                                on_release=partial(self.selecionar_cliente, foto_cliente)) #tirando o .png e colocando primeira letra maiuscula
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)
        
        # carregar as fotos dos produtos
        arquivos = os.listdir("icones/fotos_produtos")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        for foto_produto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}", 
                                 on_release=partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace('.png', '').capitalize(), 
                                on_release=partial(self.selecionar_produto, foto_produto)) #tirando o .png e colocando primeira letra maiuscula
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)
            
        # carregar a data
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        label_data = pagina_adicionarvendas.ids['label_data']
        label_data.text = f"Data: {date.today().strftime('%d/%m/%Y')}"
            
        # carregar as infos do usuario     
        self.carregar_infos_usuario()
        
    def carregar_infos_usuario(self):
        try:
            # mantendo o usuario conectado
            with open('refreshtoken.txt', 'r') as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token
            
            #pegar informacoes do usuario
            # ?auth={self.id_token} no link por conta das regras do banco de dados no firebase
            requisicao = requests.get(f"https://appvendashash-b88af-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json() #transformar o get em dicionario
            
            #preencher foto de perfil
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source = f'icones/fotos_perfil/{avatar}'
            
            #preencher o ID unico
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids['ajustespage']
            pagina_ajustes.ids['id_vendedor'].text = f'Seu ID Único: {id_vendedor}'
            
            #preencher o total de vendas
            total_vendas = requisicao_dic['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R$ {total_vendas}[/b]'
            
            #preencher o equipe
            self.equipe = requisicao_dic['equipe']
            
            
            #preencher lista de vendas 
            try:
                # print(requisicao_dic) para ajudar a ver raciocinio
                vendas = requisicao_dic['vendas']
                self.vendas = vendas
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                        produto=venda['produto'], foto_produto=venda['foto_produto'],
                                        data=venda['data'],
                                        preco=venda['preco'],
                                        unidade=venda['unidade'],
                                        quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner) #criando varios itens dinamicos no scrollview
            except Exception as e:
                print(f'ERRO: {e}') #printa o erro
            
            # preecher equipe de vendedores            
            equipe = requisicao_dic['equipe']
            lista_equipe = equipe.split(',') #separando por virgula no banco de dados
            pagina_listavendedores = self.root.ids['listarvendedorespage']
            lista_vendedores = pagina_listavendedores.ids['lista_vendedores'] # id correspondente na pagina listavendedorespage
            
            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != '': #adicionar apenas se nao estiver vazio
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)
                    
            
            self.mudar_tela('homepage')
                 
        except Exception as e:
            print(f'ERRO: {e}') #printa o erro
            pass
    
    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids['screen_manager'] #pega o gerenciador de telas
        gerenciador_telas.current = id_tela #id da tela atual
        
    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{foto}'
        
        # mudando foto no banco de dados
        info = f'{{"avatar": "{foto}"}}' #passar dicionario em formato de texto para funcionar
        requisicao = requests.patch(f'https://appvendashash-b88af-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}', 
                                    data=info)
        
        self.mudar_tela('ajustespage')
        
    def adicionar_vendedor(self, id_vendedor_adcionado):
        # ?orederBy="<parametroDatabase>"&equalTo={<variavel>} -> parametro entre aspas duplas e link inteiro entre aspas simples
        link = f'https://appvendashash-b88af-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adcionado}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        
        pagina_adicionarvendedor = self.root.ids['adicionarvendedorpage']
        mensagem_texto = pagina_adicionarvendedor.ids['mensagem_outrovendedor']
        
        if requisicao_dic == {}:
            mensagem_texto.text = 'Usuário Não Encontrado'
        else:
            equipe = self.equipe.split(',')
            if id_vendedor_adcionado in equipe:
                mensagem_texto.text = 'Vendedor já faz parte da equipe'
            else:
                self.equipe = self.equipe + f',{id_vendedor_adcionado}'
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://appvendashash-b88af-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}", 
                               data=info)
                mensagem_texto.text = 'Vendedor adicionado com Sucesso!'
                
                # atualizar a lista de vendedores adicionando o novo banner
                pagina_listavendedores = self.root.ids['listarvendedorespage']
                lista_vendedores = pagina_listavendedores.ids['lista_vendedores']
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adcionado)
                lista_vendedores.add_widget(banner_vendedor)
                
    def selecionar_cliente(self, foto, *args): #*args para n bugar, pois qnd passa parametros no on_release ele passa outras infos
        self.cliente = foto.replace('.png', '') # armazenar apenas o nome
        # pintar de branco todas as outras letras
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        
        for item in list(lista_clientes.children): #pegando todos os items dentro do gridlayout com id 'lista_clientes'
            item.color = (1, 1, 1, 1) #branco
            
            # pintar de azul a letra do item selecionado
            # foto -> carrefour.png / label -> Carrefour -> carrefour -> carrefour.png
            try:
                texto = item.text
                texto = texto.lower() + '.png'
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1) #azul utilizado
            except:
                pass
            
    def selecionar_produto(self, foto, *args): #*args para n bugar, pois qnd passa parametros no on_release ele passa outras infos
        # pintar de branco todas as outras letras
        self.produto = foto.replace('.png', '') # armazenar apenas o nome
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        
        for item in list(lista_produtos.children): #pegando todos os items dentro do gridlayout com id 'lista_clientes'
            item.color = (1, 1, 1, 1) #branco
            
            # pintar de azul a letra do item selecionado
            try:
                texto = item.text
                texto = texto.lower() + '.png'
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1) #azul utilizado
            except:
                pass
            
    def selecionar_unidade(self, id_label, *args):
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        self.unidade = id_label.replace('unidades_', '')
        
        # pintar de branco todas as outras letras
        pagina_adicionarvendas.ids['unidades_kg'].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids['unidades_unidades'].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids['unidades_litros'].color = (1, 1, 1, 1)
        
        # pintar de azul a letra do item selecionado
        pagina_adicionarvendas.ids[id_label].color = (0, 207/255, 219/255, 1)
        
    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade
        
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        data = pagina_adicionarvendas.ids['label_data'].text.replace('Data: ', '') # pegando apenas a data do texto
        preco = pagina_adicionarvendas.ids['preco_total'].text
        quantidade = pagina_adicionarvendas.ids['quantidade'].text
        
        # caso tenha campos não preenchidos ou errados
        if not cliente:
            pagina_adicionarvendas.ids['label_selecione_cliente'].color = (1, 0, 0, 1)
        if not produto:
            pagina_adicionarvendas.ids['label_selecione_produto'].color = (1, 0, 0, 1)
        if not unidade:
            pagina_adicionarvendas.ids['unidades_kg'].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids['unidades_unidades'].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids['unidades_litros'].color = (1, 0, 0, 1)
        if not preco:
            pagina_adicionarvendas.ids['label_preco'].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionarvendas.ids['label_preco'].color = (1, 0, 0, 1)
        if not quantidade:
            pagina_adicionarvendas.ids['label_quantidade'].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendas.ids['label_quantidade'].color = (1, 0, 0, 1)
        
        # com tudo preenchido corretamente executar o codigo adicionar venda
        if cliente and produto and unidade and preco and quantidade and (type(preco) == float) and (type(quantidade) == float):
            foto_produto = produto + '.png'
            foto_cliente = cliente + '.png'
            
            # armazenando no banco de dados todas as informações
            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", "foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", "preco": "{preco}", "quantidade": "{quantidade}"}}'
            requests.post(f'https://appvendashash-b88af-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}', 
                          data=info)
        
        # adicionando um novo banner na homepage
        banner = BannerVenda(cliente=cliente, produto=produto, foto_cliente=foto_cliente, foto_produto=foto_produto, 
                             data=data, unidade=unidade, preco=preco, quantidade=quantidade)
        pagina_homepage = self.root.ids['homepage']
        lista_vendas = pagina_homepage.ids['lista_vendas']
        lista_vendas.add_widget(banner)
        
        # mudado o total de vendas
        requisicao = requests.get(f'https://appvendashash-b88af-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}')
        total_vendas = float(requisicao.json())
        total_vendas += preco
        info = f'{{"total_vendas": "{total_vendas}"}}'
        requests.patch(f'https://appvendashash-b88af-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}', 
                          data=info)
        homepage = self.root.ids['homepage']
        homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R$ {total_vendas}[/b]'
        
        self.mudar_tela('homepage')
        
        # resetar as informações
        cliente = None 
        produto = None
        unidade = None
        
    def carregar_todas_vendas(self):
        # preencher a pagina todasvendaspage
        pagina_todasvendas = self.root.ids['todasvendaspage']
        lista_vendas = pagina_todasvendas.ids['lista_vendas']
        
        # limpando banners existentes na pagina para retirar bugs
        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)
                    
        # pegar informacoes da empresa
        requisicao = requests.get(f'https://appvendashash-b88af-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json() #transformar o get em dicionario
        
        #preencher foto de perfil da empresa
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/hash.png'
        
        # preencher lista de vendas com um banner para cada venda da empresa
        total_vendas = 0
        for local_id_usuario in requisicao_dic:
            try:
                vendas = requisicao_dic[local_id_usuario]['vendas'] # dicionario vendas de cada ususario
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda['preco'])
                    banner = BannerVenda(cliente=venda['cliente'], produto=venda['produto'], foto_cliente=venda['foto_cliente'], 
                                         foto_produto=venda['foto_produto'], data=venda['data'], unidade=venda['unidade'], 
                                         preco=venda['preco'], quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner)
            except Exception as e:
                print(f'ERRO: {e}')
        
        #preencher o total de vendas
        pagina_todasvendas.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R$ {total_vendas}[/b]'            
    
        # redirecionar para a pagina todasvendaspage
        self.mudar_tela('todasvendaspage')
        
    def sair_todas_vendas(self, id_tela):
        # recolocando a foto de perfil do usuario
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{self.avatar}'
        
        self.mudar_tela(id_tela)
        
    def carregar_vendas_vendedor(self, dic_info_vendedor, *args):
        
        # preencher lista de vendas com um banner para cada venda do outro vendedor
        try:
            vendas = dic_info_vendedor['vendas']
            pagina_vendasoutrovendedor = self.root.ids['vendasoutrovendedorpage']
            lista_vendas = pagina_vendasoutrovendedor.ids['lista_vendas']
            
            # limpando banners existentes na pagina para retirar bugs
            for item in list(lista_vendas.children):
                lista_vendas.remove_widget(item)
            
            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda['cliente'], produto=venda['produto'], foto_cliente=venda['foto_cliente'], 
                                        foto_produto=venda['foto_produto'], data=venda['data'], unidade=venda['unidade'], 
                                        preco=venda['preco'], quantidade=venda['quantidade'])
                lista_vendas.add_widget(banner)
        except Exception as e:
            print(f'ERRO: {e}')
            
        #preencher o total de vendas do outro vendedor
        total_vendas = dic_info_vendedor['total_vendas']
        pagina_vendasoutrovendedor.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R$ {total_vendas}[/b]'
        
        #preencher foto de perfil do outro vendedor
        foto_perfil = self.root.ids['foto_perfil']
        avatar = dic_info_vendedor['avatar']
        foto_perfil.source = f'icones/fotos_perfil/{avatar}'
        
        self.mudar_tela('vendasoutrovendedorpage')
    
    
MainApp().run() #executa o app
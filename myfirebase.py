import requests
from kivy.app import App


class MyFirebase():
    API_KEY = 'AIzaSyDYbwV5CYD8o8OSFvCjl7yIQVAseMtpAUI' #API de authenticação do banco de dados do google
    
    def criar_conta(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        print(email, senha)
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        
        if requisicao.ok: #true se não deu erro, false se deu erro
            print('usuário criado')
            #requisicao_dic['idToken'] -> autenticação 
            #requisicao_dic['refreshToken'] -> token q mantem o usuário logado
            #requisicao_dic['localId'] -> id_usuario
            refresh_token = requisicao_dic['refreshToken']
            local_id = requisicao_dic['localId']
            id_token = requisicao_dic['idToken']
            
            meu_aplicativo = App.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token
            
            with open('refreshtoken.txt', 'w') as arquivo: # criar um arquivo com o nome refreshtoken no modo de escrever(write)
                arquivo.write(refresh_token) # escrever o refreshtoken no arquivo
            
            #id unico para cada usuario    
            req_id = requests.get(f"https://appvendashash-b88af-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={id_token}")
            id_vendedor = req_id.json()

            link = f"https://appvendashash-b88af-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}" #link do banco de dados
            # dicionario padrao a ser mandado para o banco de dados quando criar um usuario
            info_usuario = f'{{"avatar": "foto1.png", "equipe": "", "total_vendas": "0", "vendas": "", "id_vendedor": "{id_vendedor}"}}'
            requisicao_usuario = requests.patch(link, data=info_usuario) #patch no lugar de post para n criar 2 ids para cada usuario
            
            #atualizar o valor do proximo_id_vendedor
            proximo_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor": "{proximo_id_vendedor}"}}'
            requests.patch(f'https://appvendashash-b88af-default-rtdb.firebaseio.com/.json?auth={id_token}', data=info_id_vendedor)
            
            meu_aplicativo.carregar_infos_usuario() #recarrega com as informações do usuario criado
            meu_aplicativo.mudar_tela('homepage') #redireciona para homepage
            
        else:
            mensagem_erro = requisicao_dic['error']['message'] #mensagem de erro caso haja
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids['loginpage']
            pagina_login.ids['mensagem_login'].text = mensagem_erro
            pagina_login.ids['mensagem_login'].color = (1, 0, 0, 1)
        print(requisicao_dic)         
    
    def fazer_login(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        
        if requisicao.ok: #true se não deu erro, false se deu erro
            refresh_token = requisicao_dic['refreshToken']
            local_id = requisicao_dic['localId']
            id_token = requisicao_dic['idToken']
            
            meu_aplicativo = App.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token
            
            with open('refreshtoken.txt', 'w') as arquivo: # criar um arquivo com o nome refreshtoken no modo de escrever(write)
                arquivo.write(refresh_token) # escrever o refreshtoken no arquivo
                
            req_id = requests.get(f"https://aplicativovendashash-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={id_token}")
            id_vendedor = req_id.json()
            
            meu_aplicativo.carregar_infos_usuario() #recarrega com as informações do usuario criado
            meu_aplicativo.mudar_tela('homepage') #redireciona para homepage
            
        else:
            mensagem_erro = requisicao_dic['error']['message'] #mensagem de erro caso haja
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids['loginpage']
            pagina_login.ids['mensagem_login'].text = mensagem_erro
            pagina_login.ids['mensagem_login'].color = (1, 0, 0, 1)
    
    def trocar_token(self, refresh_token):
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"
        info = {
            "grant_type":  "refresh_token",
            "refresh_token": refresh_token
        }
        requisicao = requests.post(link, data=info) #infos a serem enviadas para logar automaticamente o usuario
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic['user_id']
        id_token = requisicao_dic['id_token']
        return local_id, id_token
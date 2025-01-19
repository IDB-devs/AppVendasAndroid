# AppVendasAndroid

### Objective:

- Creation of an application for sales management in a company.

### Method:

- Using the firebase database and the Kivy library in Python.

### Functions:

- The App has a login page, add a sale page, list total sales of the seller page, total company sales page, monitor sales of other sellers page using each seller's unique ID, change profile photo page and settings page.

### Arquivos Explicação:

- pasta icones -> Where the images necessary for the application to function are stored.
- pasta kv -> Folder where the application window files (frontend) are stored.
- main.kv -> File that connects the application with the kv files through ids (frontend connection to app).
- telas.py -> File that creates application windows based on the ids of the main.kv file (frontend connection to app).
- myfirebase.py -> File to connect and use the personal Firebase database, created to store confidential data such as the API Key of the chosen database (modified to maintain confidentiality, but code indicated for the purpose of understanding the project).
- botoes.py -> File created to create the buttons necessary for the application.
- bannervendedor.py -> File aimed at creating the seller banner on the listavendedorespage.kv and the necessary data to be shown on this banner.
- bannervenda.py -> File aimed at creating the homepage sales banner and the necessary data to be shown on this banner.
- refreshtoken.txt -> Text file that stores the user token for quick login.
- main.py -> Main file with all necessary functions and parameters connected to run the application.
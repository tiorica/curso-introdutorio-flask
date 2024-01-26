# Projeto do Curso Introdutório de Flask (Rocketseat)

## Config inicial
`pip install -r requirements.txt`

### Pode ser necessário adicionar a pasta onde o flask foi instalado à PATH var
`PATH=~/.local/bin:$PATH`

## Run the application
`python3 app.py`

## Create DB using flask shell
`flask shell`
```
>>> db.create_all()
>>> db.session.commit()
>>> exit()
``` 

## Instalar extensão SqliteViewer no VSCode
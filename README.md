# Sobre SM-ORCL

É uma alternativa simples de executar comandos simples dentro de um banco database Oracle ```<= 12.2.0```.

# Dependências

- Esse pacote só funciona em ambiente ```Linux e MacOS``` com o [SQLClient instalado](https://docs.oracle.com/cd/B19306_01/server.102/b14357/ape.htm).

- É necessário que tenha instalado o cliente SQLPlus correspondente ao seu banco de dados.  [How to install SQLPlus client](https://docs.oracle.com/cd/B19306_01/server.102/b14357/ape.htm)

- Este pacote foi desenvolvido na versão ```v3.7.*``` do Python, recomendamos o uso dessa versão a ser utilizada para melhor experiência.

# Instalação

- Execute o comando para obter o pacote. ``` pip install smorcl ```

# Usando

- Em seu arquivo realize o import do modulo.

```python
  from smorcl import Oracle
  orcl = Oracle(
    ip_address= '0.0.0.0',
    username= 'username',
    passowrd= 'password',
    service_name= 'servicename',
    port= 'port'
  )
```
# Comandos

- keepAliveDb verifica disponibilidade do seu banco de dados.

```python
...
  orcl = Oracle(dbora.auth)
  response = orcl.keepAliveDb()
...
```

------------


- Exemplo de insert

```python
...
  orcl = Oracle(dbora.auth)
  
  payload = {
    "name": 'Fulano Sauro',
    "idade": 23,
    "sexo": 'masculino'
  }
  
 response = orcl.insert(table='ex_user',  data=payload)
...
```

------------


- Exemplo de insert com select

```python
...
  orcl = Oracle(dbora.auth)
  
  payloadData = {
    "idade": 23
  }
  
  payload = {
    "idade": 23,
    "sexo": 'masculino'
  }
  
  response = orcl.insertSelect(
      tablePrimary= 'ex_user',
      columnsPrimary= ["name", "email_address"], 
      tableSource= 'ex_client', 
      columnsSource= ["name", "email_address"],
      where= { "idade": 23 }  
    )
...
```
Obs: Caso queira fazer um **where** mais especifico use **handsFreeWhere** ao inves do **where**.
Ex: 
``` 
 handsFreeWhere='idade >= 18 and uf = "RJ"'
``` 

------------

- Exemplo de delete com/sem where
- Se informar que ```{ deleteAll: false }```  vai respeitar a regra do **where** e se estiver como ```{ deleteAll: true }``` ele irá ignorar o **where**.

```python
  ...
    orcl = Oracle(dbora.auth)
    
    payload = { "id": 1, "email_address": "fulano@ciclano.me" } 
    response = orcl.delete( table='ex_user', deleteAll=False, where=payload )
  ...
```

Obs: Caso queira fazer um **where** mais especifico use **handsFreeWhere** ao inves do **where**.
Ex: 
``` 
 handsFreeWhere='idade >= 18 and uf = "RJ"'
``` 

------------


- Exemplo de Update com/sem where
- Se informar que ```{ updateAll: false }``` vai respeitar a regra do **where** e se estiver como ```{ updateAll: true }``` ele irá ignorar o **where**.

```python
  ...
    orcl = Oracle(dbora.auth)
	
    payload = { "email_address": "ciclano@fulano.you" } 
	
    response = orcl.update(table='ex_user', data=payload, updateAll=False, where={ "email_address": "fulano@ciclano.me" })
  ...
```
Obs: Caso queira fazer um **where** mais especifico use **handsFreeWhere** ao inves do **where**.
Ex: 
``` 
 handsFreeWhere='idade >= 18 and uf = "RJ"'
``` 

------------

- Exemplo de Select

```python
  ...
    orcl = Oracle(dbora.auth)
	
    columns=["id", "name", "email_address", "modified_date", "created_by"]
    response = orcl.select(table="EX_USER", columns=columns, where={"name": "Fulano", "email_address": "fulano@ciclano.me"})
  ...
```

Obs: Caso queira fazer um **where** mais especifico use **handsFreeWhere** ao inves do **where**.
Ex: 
``` 
 handsFreeWhere='idade >= 18 and uf = "RJ"'
``` 

------------

Exemplo de Select retornando todas as colunas, como se fosse: **select * from table_name**
- **ATENÇÃO**: Se colocar columns ```[ " * ", "outra_coluna"]``` vai retornar error, use sempre ``[ " * " ]`` sozinho!

```python
  ...
    orcl = Oracle(dbora.auth)
    response = orcl.select(table="EX_USER", columns=["*"], where={"name": "Fulano", "email_address": "fulano@ciclano.me"})
  ...
```
Obs1: Caso não seja informado  a **columns** ``[ " * " ]`` mantendo somente **table** com ou sem **where** ele retornar todas as colunas.
Ex:
```python
...
    payload = {
      "table": "EX_USER",
      "where": {
        "name": "Fulano",
        "email_address": "fulano@ciclano.me"
      }
    }
...
```
Obs2: Caso queira fazer um **where** mais especifico use **handsFreeWhere** ao inves do **where**.
Ex: 
``` 
 handsFreeWhere='idade >= 18 and uf = "RJ"'
``` 

------------

- Exemplo de execute Procedure

```python
  ...
    orcl = Oracle(dbora.auth)
	
    data = {
     "name": 'Fulano Sauro',
     "idade": 23,
     "sexo": 'masculino'
     }

   response = orcl.exec_procedure(procedure_name="CREATE_USER", data=data)
  ...
```

------------


- Exemplo de execute Function

```python
  ...
    orcl = Oracle(dbora.auth)
    data = {
     "name": 'Fulano Sauro',
     "idade": 23,
     "sexo": 'masculino'
     } 
    response = orcl.exec_function(function_name="CREATE_USER", data=data)
  ...
```

------------

- Exemplo de uma drop table
- **ATENÇÃO**: Por default as informações de **cascade** são **false**.

```python
  ...
    orcl = Oracle(dbora.auth)
    response = orcl.drop_table(table="EX_USER", casc=True)
  ...
```

------------

- Exemplo de uma truncate table

```python
  ...
    orcl = Oracle(dbora.auth)
    response = orcl.truncate(table="EX_USER")
  ...
```

# Pague um :coffee:

- Use o PIX, escaneia o QRCode abaixo

<img src="https://i.ibb.co/VVxsZ1f/Whats-App-Image-2020-12-04-at-21-09-50.jpg" height="200" />
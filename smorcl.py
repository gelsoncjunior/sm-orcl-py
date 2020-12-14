import os

class Oracle:
    def __init__(self, username, password, ip_address, port, service_name):
        self.__username = username
        self.__password = password
        self.__ip_address = ip_address
        self.__port = port
        self.__service_name = service_name
        self.__erro = ""

    def exec(self, command):
        stdout = os.popen(command).read()
        stdout = str(stdout).replace("\t", " ").split("\n")
        output = []
        for i in stdout:
            if i != '':
                output.append(i)
        return output

    def fetchSeparetedKeyAndValue(self, data):
        sKey = []
        sValues = []

        idx = 0
        for kv in data.items():
            sKey.append(kv[idx])
            sValues.append((kv[idx + 1]))

        return sKey, sValues

    def objToArrayWithComparisionOfAny(self, data, arrow = None):
        caracter = "="
        if arrow: caracter = arrow
        obj = []

        idx = 0
        for ky in data.items():
            obj.append(f"{ky[0]} {caracter} '{ky[0+1]}'")
            idx += 1
        return obj

    def checkIrregularity(self, output):
        if not output:
            return {"status": 404, "data": [], "error": "Not data found"}
        else:
            for i in output:
                if 'ORA-' in i:
                    return {"status": 404, "data": [], "error": i}
                if '0 rows deleted' in i:
                    return {"status": 404, "data": [], "error": i}
                if 'no rows selected' in i:
                    return {"status": 404, "data": [], "error": i}

    def sqlplus(self, sql):
        tns_connect = f'{self.__username}/{self.__password}@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST={self.__ip_address})(PORT={self.__port})))(CONNECT_DATA=(SERVICE_NAME={self.__service_name})))'
        sqlplus = f'export NLS_LANG=AMERICAN_AMERICA.UTF8 \n sqlplus -s "{tns_connect}" <<EOF \n set long 30000 \n set longchunksize 30000 \n set pages 0 \n set lines 2000 \n {sql} \nEOF'
        response = self.exec(sqlplus)
        existIrregularity = self.checkIrregularity(response)
        if existIrregularity is None or existIrregularity["error"] is None:
            return {"status": 200, "data": response, "error": self.__erro}
        else:
            return existIrregularity


    def query(self, query):
        return self.sqlplus(sql=query)

    def keepAliveDb(self):
        response = self.sqlplus('select 1 from dual;')
        if response["error"]:
            return {"status": 0, "output": "Failed to connect"}
        else:
            return {"status": 1, "output": "Successfully connected"}

    def insert(self, table, data):
        sKey, sValues = self.fetchSeparetedKeyAndValue(data)
        key = str(sKey).strip('[]').replace("'", '')
        vlr = str(sValues).strip('[]')

        query = f"insert into {table} ( {key} ) values ( {vlr} );"
        res = self.sqlplus(query)
        return res

    def insertSelect(self, tablePrimary, columnsPrimary, tableSource, columnsSource, where = None, handsFreeWhere = None):
        isExistWhere = ";"
        objWhere = []

        if where:
            objWhere = self.objToArrayWithComparisionOfAny(where)
            recort = str(objWhere).strip("[]").replace('"', "").replace(',', ' and ')
            isExistWhere = f" where {recort} ;"
        elif handsFreeWhere:
            isExistWhere = f" where {handsFreeWhere} ;"

        keyColumnsPrimary = str(columnsPrimary).strip('[]').replace("'", '')
        keyColumnsSource = str(columnsSource).strip('[]').replace("'", '')
        query = f"insert into {tablePrimary} ( {keyColumnsPrimary} ) select {keyColumnsSource} from {tableSource} {isExistWhere}"
        print(query)

    def select(self, table, columns, where = None, handsFreeWhere = None):
        isExistWhere = ";"
        objWhere = []
        col = []
        idx = 0
        for column in columns:
            if idx != len(columns) -1:
                col.append(column + "||'|'||")
            else:
                col.append(column + "'")
            idx += 1

        col = str(col).strip("[]").strip("'\"").replace('"', '').replace(",", "")

        if where:
            objWhere = self.objToArrayWithComparisionOfAny(where)
            recort = str(objWhere).strip("[]").replace('"', "").replace(',', ' and ')
            isExistWhere = f" where {recort} ;"
        elif handsFreeWhere:
            isExistWhere = f" where {handsFreeWhere} ;"

        query = f'select {col} from {table} {isExistWhere}'
        res = self.sqlplus(query)

        objList = []
        if res["data"] and res["error"] == '':
            for v in res["data"]:
                obj = {}
                data = v.split("|")
                idx = 0
                for i in data:
                    if 'rows selected' in i:
                        pass
                    else:
                        obj[columns[idx]] = i
                    idx += 1
                if len(obj.values()) != 0: objList.append(obj)
            res["data"] = objList
        return res

    def exec_procedure(self, procedure_name, data):
        vlr = str(self.objToArrayWithComparisionOfAny(data, '=>')).strip("[]").replace('"', "")
        query = f"begin \n {procedure_name}({vlr}); \n end; \n/"
        res = self.sqlplus(query)
        return res

    def exec_function(self, function_name, data):
        vlr = str(self.objToArrayWithComparisionOfAny(data, '=>')).strip("[]").replace('"', "")
        query = f"select {function_name}({vlr}) as response from dual;"
        res = self.sqlplus(query)
        return res

    def truncate(self, table):
        query = f'TRUNCATE TABLE {table};'
        res = self.sqlplus(query)
        return res
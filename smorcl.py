import os
from random import randint

class Oracle:
    def __init__(self, username, password, ip_address, port, service_name):
        self.__username = username
        self.__password = password
        self.__ip_address = ip_address
        self.__port = port
        self.__service_name = service_name
        self.__erro = ""

    def __str__(self):
        res = self.keepAliveDb()
        return '{}: {}'.format(res["output"],self.__service_name)

    def __exec(self, command):
        stdout = os.popen(command).read()
        stdout = str(stdout).replace("\t", " ").split("\n")
        output = []
        for i in stdout:
            if i != '':
                output.append(i)
        return output

    def __fetchSeparetedKeyAndValue(self, data):
        sKey = []
        sValues = []

        idx = 0
        for kv in data.items():
            sKey.append(kv[idx])
            sValues.append((kv[idx + 1]))

        return sKey, sValues

    def __objToArrayWithComparisionOfAny(self, data, arrow=None):
        caracter = "="
        if arrow:
            caracter = arrow
        obj = []
        idx = 0
        for ky in data.items():
            obj.append("{} {} '{}'".format(ky[0], caracter, ky[0 + 1]))
            idx += 1
        return obj

    def __checkIrregularity(self, output):
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

    def __sqlplus(self, sql):
        tns_connect = '{}/{}@(DESCRIPTION=(CONNECT_TIMEOUT=1800)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST={})(PORT={})))(CONNECT_DATA=(SERVICE_NAME={})))'.format(
            self.__username, self.__password, self.__ip_address, self.__port, self.__service_name
        )
        sqlplus = 'export NLS_LANG=AMERICAN_AMERICA.UTF8 \n sqlplus -s "{}" <<EOF \n set long 30000 \n set longchunksize 30000 \n set pages 0 \n set lines 2000 \n {} \nEOF'.format(
            tns_connect, sql
        )
        response = self.__exec(sqlplus)
        existIrregularity = self.__checkIrregularity(response)
        if existIrregularity is None or existIrregularity["error"] is None:
            return {"status": 200, "data": response, "error": self.__erro}
        else:
            return existIrregularity

    def keepAliveDb(self):
        response = self.__sqlplus('select 1 from dual;')
        if response["error"]:
            return {"status": 0, "output": "Failed to connect"}
        else:
            return {"status": 1, "output": "Successfully connected"}

    def insert_batch(self, table, data):
        columns, _ = self.__fetchSeparetedKeyAndValue(data[0])
        rows=[]
        idx = 0
        for row in data:
            _, sValues = self.__fetchSeparetedKeyAndValue(row)
            values_strip = ""
            cidx = 0
            for vlr in sValues:
                if vlr is None:
                    vlr = "null"
                else:
                    vlr = "'{}'".format(vlr.replace("\n", "").replace("'", "").replace("/", "").replace("&", " E "))
                if cidx == len(sValues) -1:
                    values_strip = values_strip + " {} as {} ".format(vlr, columns[cidx])
                else:
                    values_strip = values_strip + " {} as {}, ".format(vlr, columns[cidx])
                cidx += 1
            if idx == len(data) -1:
                rows.append("select {} from dual".format(values_strip))
            else:
                rows.append("select {} from dual union all".format(values_strip))
            idx += 1

        select = ""
        for rw in rows:
            if 'union all' in rw:
                select = select + "{} \n".format(rw)
            else:
                select = select + "{} ".format(rw)

        sql= """
ALTER SESSION FORCE PARALLEL DML PARALLEL 5;
commit;
insert /*+ NOAPPEND PARALLEL */
into {}({})
select * from (
    {}
);
commit;
ALTER SESSION DISABLE PARALLEL DML;
        """.format(table, str(columns).strip("[]").replace("'", ""), select)

        #print(sql)
        file_name = 'insert_batch_{}.sql'.format(randint(1,99999))
        file = open(file_name, 'a')
        file.write(sql)
        file.close()

        res = self.__sqlplus("@{}".format(file_name))
        os.remove(file_name)
        return res

    def insert(self, table, data):
        sKey, sValues = self.__fetchSeparetedKeyAndValue(data)
        key = str(sKey).strip('[]').replace("'", '')
        vlr = str(sValues).strip('[]')

        query = "insert into {} ( {} ) values ( {} );".format(
            table, key, vlr
        )
        res = self.__sqlplus(query)
        return res

    def insertSelect(self, tablePrimary, columnsPrimary, tableSource, columnsSource, where=None, handsFreeWhere=None):
        isExistWhere = ";"

        if where:
            if handsFreeWhere:
                raise LookupError("If use where then remove handsFreeWhere")
            objWhere = self.__objToArrayWithComparisionOfAny(where)
            recort = str(objWhere).strip("[]").replace(
                '"', "").replace(',', ' and ')
            isExistWhere = " where {} ;".format(recort)
        elif handsFreeWhere:
            if where:
                raise LookupError("If use handsFreeWhere then remove where")
            isExistWhere = " where {} ;".format(handsFreeWhere)

        keyColumnsPrimary = str(columnsPrimary).strip('[]').replace("'", '')
        keyColumnsSource = str(columnsSource).strip('[]').replace("'", '')
        query = "insert into {} ( {} ) select {} from {} {}".format(
            tablePrimary, keyColumnsPrimary, keyColumnsSource, tableSource, isExistWhere
        )
        res = self.__sqlplus(query)
        return res

    def update(self, table, data, updateAll=True, where=None, handsFreeWhere=None):
        isExistWhere = ";"

        objUpdate = self.__objToArrayWithComparisionOfAny(data)

        if updateAll:
            if where or handsFreeWhere:
                raise LookupError(
                    "Remove where and handsFreeWhere where exist updateAll = True")
            isExistWhere = isExistWhere
        elif where:
            if handsFreeWhere:
                raise LookupError("If use where then remove handsFreeWhere")
            objWhere = self.__objToArrayWithComparisionOfAny(where)
            recort = str(objWhere).strip("[]").replace(
                '"', "").replace(',', ' and ')
            isExistWhere = " where {} ;".format(recort)
        elif handsFreeWhere:
            if where:
                raise LookupError("If use handsFreeWhere then remove where")
            isExistWhere = " where {} ;".format(handsFreeWhere)

        objUpdate = str(objUpdate).strip("[]").replace('"', '')
        query = 'update {} set {} {}'.format(table, objUpdate, isExistWhere)
        res = self.__sqlplus(query)
        print(res)
        return res

    def delete(self, table, deleteAll=True, where=None, handsFreeWhere=None):
        isExistWhere = ";"

        if deleteAll:
            if where or handsFreeWhere:
                raise LookupError(
                    "Remove where and handsFreeWhere where exist deleteAll = True")
            isExistWhere = isExistWhere
        elif where:
            if handsFreeWhere:
                raise LookupError("If use where then remove handsFreeWhere")
            objWhere = self.__objToArrayWithComparisionOfAny(where)
            recort = str(objWhere).strip("[]").replace(
                '"', "").replace(',', ' and ')
            isExistWhere = " where {} ;".format(recort)
        elif handsFreeWhere:
            if where:
                raise LookupError("If use handsFreeWhere then remove where")
            isExistWhere = " where {} ;".format(handsFreeWhere)

        query = "delete {} {}".format(table, isExistWhere)
        res = self.__sqlplus(query)
        return res

    def select(self, table, columns=None, where=None, handsFreeWhere=None):
        isExistWhere = ";"
        col = []
        idx = 0

        if columns is None or len(columns) == 1 and columns[0] == '*':
            columns = self.fetchColumnsTable(table=table)

        for column in columns:
            if idx != len(columns) - 1:
                col.append(column + "||'|'||")
            else:
                col.append(column + "'")
            idx += 1

        col = str(col).strip("[]").strip(
            "'\"").replace('"', '').replace(",", "")

        if where:
            if handsFreeWhere:
                raise LookupError("If use where then remove handsFreeWhere")
            objWhere = self.__objToArrayWithComparisionOfAny(where)
            recort = str(objWhere).strip("[]").replace(
                '"', "").replace(',', ' and ')
            isExistWhere = " where {} ;".format(recort)
        elif handsFreeWhere:
            if where:
                raise LookupError("If use handsFreeWhere then remove where")
            isExistWhere = " where {} ;".format(handsFreeWhere)

        query = 'select {} from {} {}'.format(col, table, isExistWhere)
        res = self.__sqlplus(query)

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
                if len(obj.values()) != 0:
                    objList.append(obj)
            res["data"] = objList
        return res

    def fetchColumnsTable(self, table):
        query = "select lower(COLUMN_NAME) as COLUMN_NAME from user_tab_columns where table_name = upper('{}');".format(table)
        res = self.__sqlplus(query)
        arry = []
        for col in res["data"]:
            if 'rows selected' in col:
                pass
            arry.append(col)
        return arry

    def exec_procedure(self, procedure_name, data = None):
        vlr = ""
        if data is not None:
            vlr = str(self.__objToArrayWithComparisionOfAny(
                data, '=>')).strip("[]").replace('"', "")
        query = "begin \n {}({}); \n end; \n/".format(procedure_name, vlr)
        res = self.__sqlplus(query)
        return res

    def exec_function(self, function_name, data):
        vlr = str(self.__objToArrayWithComparisionOfAny(
            data, '=>')).strip("[]").replace('"', "")
        query = "select {}({}) as response from dual;".format(function_name, vlr)
        res = self.__sqlplus(query)
        return res

    def truncate(self, table):
        query = 'TRUNCATE TABLE {};'.format(table)
        res = self.__sqlplus(query)
        return res

    def drop_table(self, table, casc=None):
        cascConst = ";"
        if casc:
            cascConst = "CASCADE CONSTRAINTS"
        query = "DROP TABLE {} {}".format(table, cascConst)
        res = self.__sqlplus(query)
        return res
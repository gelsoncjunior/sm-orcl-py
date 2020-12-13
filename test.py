from smorcl import Oracle

if __name__ == '__main__':
    orcl = Oracle(
        ip_address="192.168.85.5",
        service_name="TSTDBPRD01",
        username="icotei",
        password="Icotei2020",
        port=1521
    )

    res = orcl.select(table="ic_user", columns=["name", "id", "tax_id"])

from decimal import Decimal
from django.db import connection
from django.db import transaction
from data.contract.models import Contract
from data.contract.models import ContractBalance


def contract_settlements(contract_id: int, last_one: bool = False):
    query = """
        WITH balance_cte_f AS (
            SELECT 
                id,
                contract_id,
                created_at,
                change,
                SUM(change) OVER (PARTITION BY contract_id ORDER BY created_at) AS final_balance
            FROM contract_contractbalance
            WHERE contract_id = %s
        ),
        balance_cte_s AS (
            SELECT 
                id,
                contract_id,
                COALESCE(LAG(final_balance) OVER (PARTITION BY contract_id ORDER BY created_at), 0) AS start_balance,
                change,
                final_balance,
                created_at
            FROM balance_cte_f
        )
        SELECT * FROM balance_cte_s
        ORDER BY created_at;
    """

    params = [contract_id]

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in results]

    if not data:
        return None if last_one else []

    if last_one:
        return data[-1]

    return data


def add_contract_balance(contract: Contract, change: Decimal):
    """
    Yangi ContractBalance yozuvini qo'shish va final_balance ni hisoblash
    """
    with transaction.atomic():
        # Oxirgi balansni olish
        last_balance = contract_settlements(contract.id, last_one=True)
        start_balance = Decimal(last_balance["final_balance"]) if last_balance else Decimal(0)

        # Yangi yakuniy balansni hisoblash
        final_balance = start_balance + change

        # Yozuv yaratish
        cb = ContractBalance.objects.create(
            contract=contract,
            change=change,
            final_balance=final_balance
        )
        return cb

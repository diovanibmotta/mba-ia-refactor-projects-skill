from src.models import order_model
from src.config.settings import (
    DISCOUNT_TIER_HIGH_THRESHOLD, DISCOUNT_TIER_HIGH_RATE,
    DISCOUNT_TIER_MID_THRESHOLD, DISCOUNT_TIER_MID_RATE,
    DISCOUNT_TIER_LOW_THRESHOLD, DISCOUNT_TIER_LOW_RATE,
)


def sales_report():
    data = order_model.get_sales_summary()
    faturamento = data["faturamento"]
    total_pedidos = data["total_pedidos"]

    desconto = 0
    if faturamento > DISCOUNT_TIER_HIGH_THRESHOLD:
        desconto = faturamento * DISCOUNT_TIER_HIGH_RATE
    elif faturamento > DISCOUNT_TIER_MID_THRESHOLD:
        desconto = faturamento * DISCOUNT_TIER_MID_RATE
    elif faturamento > DISCOUNT_TIER_LOW_THRESHOLD:
        desconto = faturamento * DISCOUNT_TIER_LOW_RATE

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": data["pendentes"],
        "pedidos_aprovados": data["aprovados"],
        "pedidos_cancelados": data["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }

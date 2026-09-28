// กติกาต้นทุนและกำไรสำหรับสินค้า ใช้ร่วมกันทั้งคลังและการขาย
export const MIN_MARGIN_RATE = 0.2;

export function getWeightedAverageCost(product) {
  const lots = Array.isArray(product?.costLots) ? product.costLots : [];
  const validLots = lots.filter(
    (lot) => Number(lot.quantity) > 0 && Number(lot.unitCost) >= 0,
  );
  if (!validLots.length)
    return Number(product?.costPrice ?? product?.price ?? 0);
  const quantity = validLots.reduce(
    (sum, lot) => sum + Number(lot.quantity),
    0,
  );
  return (
    validLots.reduce(
      (sum, lot) => sum + Number(lot.quantity) * Number(lot.unitCost),
      0,
    ) / quantity
  );
}

export function previewWeightedAverageCost(product, quantity, unitCost) {
  const currentQuantity = Number(product?.stock ?? 0);
  const incomingQuantity = Math.max(Number(quantity) || 0, 0);
  if (!incomingQuantity) return getWeightedAverageCost(product);
  return (
    (getWeightedAverageCost(product) * currentQuantity +
      Number(unitCost) * incomingQuantity) /
    (currentQuantity + incomingQuantity)
  );
}

export function pricingDecision(
  salePrice,
  product,
  minimumMarginRate = MIN_MARGIN_RATE,
) {
  const cost = getWeightedAverageCost(product);
  const price = Number(salePrice) || 0;
  const marginRate = price ? (price - cost) / price : -1;
  return {
    cost,
    marginRate,
    isLoss: price < cost,
    belowMinimumMargin: marginRate < minimumMarginRate,
    // margin = (ราคาขาย - ต้นทุน) / ราคาขาย จึงต้องหารด้วย (1 - margin)
    recommendedPrice:
      minimumMarginRate < 1
        ? Math.ceil(cost / (1 - minimumMarginRate) / 10) * 10
        : cost,
  };
}

export function appendCostLot(product, quantity, unitCost) {
  const lots = Array.isArray(product.costLots) ? [...product.costLots] : [];
  lots.push({
    receivedAt: new Date().toISOString(),
    quantity: Number(quantity),
    unitCost: Number(unitCost),
  });
  return {
    ...product,
    costLots: lots,
    costPrice: getWeightedAverageCost({ ...product, costLots: lots }),
  };
}

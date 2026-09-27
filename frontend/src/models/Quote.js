/** A draft quote owns line merging and totals independently of Vue. */
export class Quote {
  constructor() {
    this.items = [];
  }

  get total() {
    return this.items.reduce((sum, item) => sum + Math.round(item.price * 100) * item.qty, 0) / 100;
  }

  add(product) {
    const price = Number(product.price);
    if (!Number.isFinite(price) || price < 0 ||
        !Number.isInteger(product.qty) || product.qty <= 0) {
      throw new RangeError('Quote lines require a non-negative price and positive integer quantity.');
    }
    const existing = this.items.find((item) => (product.sku ? item.sku === product.sku : item.name === product.name));
    if (existing) existing.qty += product.qty;
    else this.items.push({ ...product, price });
  }

  remove(index) {
    if (Number.isInteger(index) && index >= 0 && index < this.items.length) {
      this.items.splice(index, 1);
    }
  }
}

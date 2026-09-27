const formatter = new Intl.NumberFormat('th-TH');
export const formatCurrency = (value) => formatter.format(value);

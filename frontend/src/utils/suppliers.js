export function normalizeSupplierName(name) {
  return String(name || "")
    .normalize("NFKC")
    .trim()
    .replace(/\s+/gu, " ")
    .toLocaleLowerCase("th-TH");
}

export function createSupplierCanonicalizer(suppliers = []) {
  const canonicalByName = new Map();

  for (const supplier of suppliers) {
    const normalizedName = normalizeSupplierName(supplier.name);
    if (!normalizedName) continue;

    const current = canonicalByName.get(normalizedName);
    const currentUsage = Number(current?.sku_count ?? current?.sku ?? 0);
    const supplierUsage = Number(supplier.sku_count ?? supplier.sku ?? 0);
    const hasMoreLinks = supplierUsage > currentUsage;
    const winsTie =
      supplierUsage === currentUsage &&
      String(supplier.id).localeCompare(String(current?.id)) < 0;

    if (!current || hasMoreLinks || winsTie) {
      canonicalByName.set(normalizedName, supplier);
    }
  }

  const canonicalSuppliers = suppliers.filter(
    (supplier) =>
      canonicalByName.get(normalizeSupplierName(supplier.name))?.id ===
      supplier.id,
  );
  const canonicalIdBySupplierId = new Map();
  const aliasesByCanonicalId = new Map();

  for (const supplier of suppliers) {
    const canonical = canonicalByName.get(
      normalizeSupplierName(supplier.name),
    );
    if (!canonical) continue;
    canonicalIdBySupplierId.set(String(supplier.id), canonical.id);
    const aliases = aliasesByCanonicalId.get(String(canonical.id)) || [];
    aliases.push(supplier.id);
    aliasesByCanonicalId.set(String(canonical.id), aliases);
  }

  return {
    suppliers: canonicalSuppliers,
    idFor(supplierId) {
      if (!supplierId) return "";
      return canonicalIdBySupplierId.get(String(supplierId)) || supplierId;
    },
    aliasesFor(canonicalId) {
      return aliasesByCanonicalId.get(String(canonicalId)) || [];
    },
  };
}

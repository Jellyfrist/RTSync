/** Synchronous demo adapter. Each read returns an independent copy. */
export class InMemoryRepository {
  constructor(records = []) {
    this.records = structuredClone(records);
  }

  list() {
    return structuredClone(this.records);
  }
}

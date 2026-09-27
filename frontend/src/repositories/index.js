// Composition root: controllers accept an injected repository for testing or reuse.
import { InMemoryRepository } from './InMemoryRepository.js';
import customers from '../data/customers.js';
import employees from '../data/employees.js';
import suppliers from '../data/suppliers.js';

export const repositories = Object.fromEntries(
  Object.entries({ customers, employees, suppliers })
    .map(([name, records]) => [name, new InMemoryRepository(records)]),
);

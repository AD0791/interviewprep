// Use Case: Advanced Type Mapping & Generic Containers (TypeScript)
// Purpose: Configures generic API response models, conditional filters, and mapped type transforms.
// Key features: Generics extends constraints, Omit/Readonly utilities, conditional types, and mapped properties.

// 1. Generic API Response Wrapper
export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  timestamp: string;
}

// 2. Base Data Model
interface Metric {
  id: string;
  name: string;
  value: number;
  recordedBy: string;
}

// 3. Mapped & Conditional Types
// Extract only keys of T whose values are of type string
type StringKeysOnly<T> = {
  [K in keyof T]: T[K] extends string ? K : never;
}[keyof T];

export type MetricStringKeys = StringKeysOnly<Metric>;
// Resulting type is: "id" | "name" | "recordedBy"

// 4. Utility Mappers
// Omit: Creates a type by removing specific keys from Metric
export type MetricSubmission = Omit<Metric, 'id'>;

// 5. Generic Data Store Class
export class DataStore<T extends { id: string }> {
  private cache = new Map<string, T>();

  public save(item: T): void {
    this.cache.set(item.id, item);
  }

  public get(id: string): T | undefined {
    return this.cache.get(id);
  }
}

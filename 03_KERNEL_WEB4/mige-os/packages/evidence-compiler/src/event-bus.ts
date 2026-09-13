import { DomainEvent } from './domain-event';
import { DomainEventType } from './domain-event-type';

export type EventHandler<T = unknown> = (event: DomainEvent<T>) => Promise<void> | void;

export interface EventBus {
  publish<T>(event: DomainEvent<T>): Promise<void>;
  subscribe<T>(
    eventType: DomainEventType,
    handler: EventHandler<T>
  ): () => void;
  unsubscribe(eventType: DomainEventType, handler: EventHandler): void;
  clear(): void;
}

export interface EventBusConfig {
  readonly maxQueueSize?: number;
  readonly enablePersistence?: boolean;
}
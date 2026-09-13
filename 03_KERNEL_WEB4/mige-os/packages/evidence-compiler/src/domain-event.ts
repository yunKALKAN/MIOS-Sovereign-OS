import { Provenance } from '@mucizework/core-contracts';
import { DomainEventType } from './domain-event-type';

export interface DomainEvent<T> {
  readonly id: string;
  readonly type: DomainEventType;
  readonly payload: T;
  readonly provenance: Provenance;
  readonly timestamp: number;
  readonly correlationId: string;
  readonly causationId?: string;
}
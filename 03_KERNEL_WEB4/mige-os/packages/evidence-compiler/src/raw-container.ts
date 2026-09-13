import { Provenance } from '@mucizework/core-contracts';

export enum ContainerType {
  WALLET_PAYLOAD = 'WALLET_PAYLOAD',
  TRANSACTION = 'TRANSACTION',
  CONTRACT_STATE = 'CONTRACT_STATE',
  BLOCK_HEADER = 'BLOCK_HEADER',
  EVENT_LOG = 'EVENT_LOG',
  UNKNOWN = 'UNKNOWN'
}

export interface RawContainer<T> {
  readonly payload: T;
  readonly provenance: Provenance;
  readonly containerType: ContainerType;
  readonly receivedAt: number;
}
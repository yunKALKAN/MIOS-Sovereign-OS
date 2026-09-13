import { Blockchain } from '@mucizework/normalizer';

export interface Provenance {
  readonly blockchain: Blockchain;
  readonly source: string;
  readonly collectedAt: number;
  readonly adapterVersion: string;
  readonly rawHash: string;
  readonly schemaVersion: string;
}
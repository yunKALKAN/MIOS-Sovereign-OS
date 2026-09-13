import { Blockchain } from '@mucizework/normalizer';
import { Evidence } from './evidence';

export interface DiscoveryAdapter {
  readonly blockchain: Blockchain;
  readonly adapterVersion: string;
  
  discover(address: string): Promise<Evidence[]>;
  getAdapterType(): string;
}
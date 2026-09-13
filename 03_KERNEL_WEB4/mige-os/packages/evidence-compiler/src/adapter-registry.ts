import { Blockchain } from '@mucizework/normalizer';
import { DiscoveryAdapter } from './discovery-adapter';

export interface AdapterRegistry {
  register(blockchain: Blockchain, adapter: DiscoveryAdapter): void;
  resolve(blockchain: Blockchain): DiscoveryAdapter;
  unregister(blockchain: Blockchain): void;
  hasAdapter(blockchain: Blockchain): boolean;
  getRegisteredBlockchains(): Blockchain[];
}

export class DefaultAdapterRegistry implements AdapterRegistry {
  private readonly adapters = new Map<Blockchain, DiscoveryAdapter>();
  
  register(blockchain: Blockchain, adapter: DiscoveryAdapter): void {
    if (this.adapters.has(blockchain)) {
      throw new Error(`Adapter zaten kayıtlı: ${blockchain}`);
    }
    this.adapters.set(blockchain, adapter);
  }
  
  resolve(blockchain: Blockchain): DiscoveryAdapter {
    const adapter = this.adapters.get(blockchain);
    if (!adapter) {
      throw new Error(`Adapter bulunamadı: ${blockchain}`);
    }
    return adapter;
  }
  
  unregister(blockchain: Blockchain): void {
    if (!this.adapters.delete(blockchain)) {
      throw new Error(`Adapter kayıtlı değil: ${blockchain}`);
    }
  }
  
  hasAdapter(blockchain: Blockchain): boolean {
    return this.adapters.has(blockchain);
  }
  
  getRegisteredBlockchains(): Blockchain[] {
    return Array.from(this.adapters.keys());
  }
}
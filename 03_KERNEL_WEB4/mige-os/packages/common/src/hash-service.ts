import { createHash } from 'crypto';

export interface HashService {
  sha256(data: string): string;
  sha256Buffer(data: Buffer): string;
  generateEvidenceId(components: HashComponents): string;
  generateNodeId(components: HashComponents): string;
  generateEdgeId(components: HashComponents): string;
  generateSnapshotId(components: HashComponents): string;
}

export interface HashComponents {
  readonly blockchain: string;
  readonly address: string;
  readonly timestamp: number;
  readonly additionalData?: Record<string, unknown>;
}

export class CanonicalHashService implements HashService {
  private readonly algorithm = 'sha256';
  private readonly encoding = 'hex' as const;
  
  sha256(data: string): string {
    return createHash(this.algorithm).update(data).digest(this.encoding);
  }
  
  sha256Buffer(data: Buffer): string {
    return createHash(this.algorithm).update(data).digest(this.encoding);
  }
  
  generateEvidenceId(components: HashComponents): string {
    const normalized = this.normalizeComponents(components);
    const data = `evidence:${normalized.blockchain}:${normalized.address}:${normalized.timestamp}`;
    return this.sha256(data);
  }
  
  generateNodeId(components: HashComponents): string {
    const normalized = this.normalizeComponents(components);
    const data = `node:${normalized.blockchain}:${normalized.address}:${normalized.timestamp}`;
    return this.sha256(data);
  }
  
  generateEdgeId(components: HashComponents): string {
    const normalized = this.normalizeComponents(components);
    const additional = normalized.additionalData 
      ? JSON.stringify(normalized.additionalData) 
      : '';
    const data = `edge:${normalized.blockchain}:${normalized.address}:${normalized.timestamp}:${additional}`;
    return this.sha256(data);
  }
  
  generateSnapshotId(components: HashComponents): string {
    const normalized = this.normalizeComponents(components);
    const additional = normalized.additionalData 
      ? JSON.stringify(normalized.additionalData) 
      : '';
    const data = `snapshot:${normalized.blockchain}:${normalized.address}:${normalized.timestamp}:${additional}`;
    return this.sha256(data);
  }
  
  private normalizeComponents(components: HashComponents): HashComponents {
    return {
      blockchain: components.blockchain.toLowerCase().trim(),
      address: components.address.toLowerCase().trim(),
      timestamp: components.timestamp,
      additionalData: components.additionalData
    };
  }
}

// Singleton instance
export const canonicalHashService = new CanonicalHashService();
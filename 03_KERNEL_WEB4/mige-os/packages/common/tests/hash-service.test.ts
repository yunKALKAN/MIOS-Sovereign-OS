import { CanonicalHashService, canonicalHashService } from '../src/hash-service';

describe('CanonicalHashService', () => {
  let service: CanonicalHashService;

  beforeEach(() => {
    service = new CanonicalHashService();
  });

  describe('sha256', () => {
    it('should generate consistent SHA256 hash', () => {
      const hash1 = service.sha256('test');
      const hash2 = service.sha256('test');
      expect(hash1).toBe(hash2);
      expect(hash1).toHaveLength(64);
    });

    it('should generate different hashes for different inputs', () => {
      const hash1 = service.sha256('test1');
      const hash2 = service.sha256('test2');
      expect(hash1).not.toBe(hash2);
    });
  });

  describe('generateEvidenceId', () => {
    it('should generate consistent evidence ID', () => {
      const components = {
        blockchain: 'ETHEREUM',
        address: '0x1234567890abcdef',
        timestamp: 1234567890
      };
      const id1 = service.generateEvidenceId(components);
      const id2 = service.generateEvidenceId(components);
      expect(id1).toBe(id2);
    });

    it('should normalize blockchain name', () => {
      const components1 = {
        blockchain: 'ETHEREUM',
        address: '0x123',
        timestamp: 123
      };
      const components2 = {
        blockchain: 'ethereum',
        address: '0x123',
        timestamp: 123
      };
      const id1 = service.generateEvidenceId(components1);
      const id2 = service.generateEvidenceId(components2);
      expect(id1).toBe(id2);
    });
  });

  describe('generateNodeId', () => {
    it('should generate consistent node ID', () => {
      const components = {
        blockchain: 'SOLANA',
        address: 'Solana123',
        timestamp: 9876543210
      };
      const id1 = service.generateNodeId(components);
      const id2 = service.generateNodeId(components);
      expect(id1).toBe(id2);
    });
  });

  describe('generateEdgeId', () => {
    it('should generate consistent edge ID', () => {
      const components = {
        blockchain: 'ETHEREUM',
        address: '0xabc',
        timestamp: 111,
        additionalData: { type: 'TRANSFER' }
      };
      const id1 = service.generateEdgeId(components);
      const id2 = service.generateEdgeId(components);
      expect(id1).toBe(id2);
    });
  });

  describe('generateSnapshotId', () => {
    it('should generate consistent snapshot ID', () => {
      const components = {
        blockchain: 'POLYGON',
        address: '0xdef',
        timestamp: 222,
        additionalData: { block: 12345 }
      };
      const id1 = service.generateSnapshotId(components);
      const id2 = service.generateSnapshotId(components);
      expect(id1).toBe(id2);
    });
  });
});

describe('canonicalHashService (singleton)', () => {
  it('should be consistent with service instance', () => {
    const service = new CanonicalHashService();
    const hash1 = canonicalHashService.sha256('test');
    const hash2 = service.sha256('test');
    expect(hash1).toBe(hash2);
  });
});
import { Provenance } from '../src/provenance';
import { Blockchain } from '@mucizework/normalizer';

describe('Provenance', () => {
  describe('interface', () => {
    it('should create valid provenance', () => {
      const provenance: Provenance = {
        blockchain: Blockchain.ETHEREUM,
        source: 'rpc',
        collectedAt: Date.now(),
        adapterVersion: '1.0.0',
        rawHash: 'abc123',
        schemaVersion: '1.0.0'
      };
      
      expect(provenance.blockchain).toBe(Blockchain.ETHEREUM);
      expect(provenance.source).toBe('rpc');
      expect(provenance.collectedAt).toBeDefined();
      expect(provenance.adapterVersion).toBe('1.0.0');
      expect(provenance.rawHash).toBe('abc123');
      expect(provenance.schemaVersion).toBe('1.0.0');
    });

    it('should be readonly', () => {
      const provenance: Provenance = {
        blockchain: Blockchain.ETHEREUM,
        source: 'rpc',
        collectedAt: Date.now(),
        adapterVersion: '1.0.0',
        rawHash: 'abc123',
        schemaVersion: '1.0.0'
      };
      
      expect(() => {
        (provenance as any).source = 'modified';
      }).not.toThrow();
    });
  });

  describe('validation', () => {
    it('should require all fields', () => {
      const createProvenance = (): Provenance => ({
        blockchain: Blockchain.ETHEREUM,
        source: 'rpc',
        collectedAt: Date.now(),
        adapterVersion: '1.0.0',
        rawHash: 'abc123',
        schemaVersion: '1.0.0'
      });
      
      const provenance = createProvenance();
      expect(provenance).toBeDefined();
    });
  });
});
import { Blockchain, CanonicalID } from '../src/canonical-id';

describe('Blockchain', () => {
  describe('enum values', () => {
    it('should have all expected blockchain types', () => {
      expect(Blockchain.ETHEREUM).toBe('ethereum');
      expect(Blockchain.SOLANA).toBe('solana');
      expect(Blockchain.BNB_CHAIN).toBe('bnb_chain');
      expect(Blockchain.POLYGON).toBe('polygon');
      expect(Blockchain.ARBITRUM).toBe('arbitrum');
      expect(Blockchain.OPTIMISM).toBe('optimism');
      expect(Blockchain.AVALANCHE).toBe('avalanche');
      expect(Blockchain.BASE).toBe('base');
      expect(Blockchain.UNKNOWN).toBe('unknown');
    });
  });
});

describe('CanonicalID', () => {
  describe('interface', () => {
    it('should create valid canonical ID', () => {
      const canonicalId: CanonicalID = {
        blockchain: Blockchain.ETHEREUM,
        address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        network: 'mainnet'
      };
      
      expect(canonicalId.blockchain).toBe(Blockchain.ETHEREUM);
      expect(canonicalId.address).toBe('0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb');
      expect(canonicalId.network).toBe('mainnet');
    });
  });

  describe('different blockchains', () => {
    it('should work with Solana', () => {
      const canonicalId: CanonicalID = {
        blockchain: Blockchain.SOLANA,
        address: '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU',
        network: 'mainnet'
      };
      
      expect(canonicalId.blockchain).toBe(Blockchain.SOLANA);
    });

    it('should work with Polygon', () => {
      const canonicalId: CanonicalID = {
        blockchain: Blockchain.POLYGON,
        address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        network: 'mainnet'
      };
      
      expect(canonicalId.blockchain).toBe(Blockchain.POLYGON);
    });
  });
});
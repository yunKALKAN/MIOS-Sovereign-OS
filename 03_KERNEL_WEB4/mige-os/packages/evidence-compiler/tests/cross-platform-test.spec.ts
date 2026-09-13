import { Evidence } from '../src/evidence';

export interface PlatformInfo {
  readonly platform: string;
  readonly arch: string;
  readonly nodeVersion: string;
}

export interface CrossPlatformTestConfig {
  readonly payload: unknown;
  readonly handlerType: string;
  readonly iterations: number;
}

export interface CrossPlatformTestResult {
  readonly passed: boolean;
  readonly platformInfo: PlatformInfo;
  readonly iterations: number;
  readonly uniqueHashes: number;
  readonly hashConsistency: number; // 0-1 arası
  readonly sampleHashes: string[];
  readonly error?: string;
}

export class CrossPlatformTester {
  constructor(
    private readonly dispatcher: any, // CompilerDispatcher
    private readonly hashFunction: (evidence: Evidence) => string
  ) {}
  
  getPlatformInfo(): PlatformInfo {
    return {
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.version
    };
  }
  
  async runTest(config: CrossPlatformTestConfig): Promise<CrossPlatformTestResult> {
    const hashes = new Set<string>();
    const sampleHashes: string[] = [];
    const platformInfo = this.getPlatformInfo();
    
    try {
      for (let i = 0; i < config.iterations; i++) {
        const result = await this.dispatcher.dispatch(
          config.payload,
          config.handlerType
        );
        
        if (!result.success || !result.evidence) {
          return {
            passed: false,
            platformInfo,
            iterations: i,
            uniqueHashes: hashes.size,
            hashConsistency: 0,
            sampleHashes,
            error: result.error || 'Derleme başarısız'
          };
        }
        
        const hash = this.hashFunction(result.evidence);
        hashes.add(hash);
        
        if (sampleHashes.length < 10) {
          sampleHashes.push(hash);
        }
      }
      
      const uniqueHashCount = hashes.size;
      const consistency = uniqueHashCount === 1 ? 1 : 0;
      
      return {
        passed: consistency === 1,
        platformInfo,
        iterations: config.iterations,
        uniqueHashes: uniqueHashCount,
        hashConsistency: consistency,
        sampleHashes
      };
    } catch (error) {
      return {
        passed: false,
        platformInfo,
        iterations: 0,
        uniqueHashes: 0,
        hashConsistency: 0,
        sampleHashes,
        error: error instanceof Error ? error.message : 'Bilinmeyen hata'
      };
    }
  }
  
  async runComparativeTest(
    config: CrossPlatformTestConfig,
    expectedHash: string
  ): Promise<CrossPlatformTestResult> {
    const result = await this.runTest(config);
    
    if (!result.passed) {
      return result;
    }
    
    const matchesExpected = result.sampleHashes[0] === expectedHash;
    
    return {
      ...result,
      passed: matchesExpected,
      error: matchesExpected ? undefined : `Hash beklenen ile eşleşmiyor: beklenen ${expectedHash}, alınan ${result.sampleHashes[0]}`
    };
  }
}

describe('CrossPlatformTest', () => {
  describe('PlatformInfo interface', () => {
    it('should create valid platform info', () => {
      const info: PlatformInfo = {
        platform: 'win32',
        arch: 'x64',
        nodeVersion: 'v20.0.0'
      };
      expect(info.platform).toBeDefined();
      expect(info.arch).toBeDefined();
      expect(info.nodeVersion).toBeDefined();
    });
  });
  
  describe('CrossPlatformTestResult interface', () => {
    it('should create valid result', () => {
      const result: CrossPlatformTestResult = {
        passed: true,
        platformInfo: {
          platform: 'win32',
          arch: 'x64',
          nodeVersion: 'v20.0.0'
        },
        iterations: 10,
        uniqueHashes: 1,
        hashConsistency: 1,
        sampleHashes: ['abc123']
      };
      expect(result.passed).toBe(true);
      expect(result.hashConsistency).toBe(1);
    });
  });
});
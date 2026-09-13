import { Evidence } from '../src/evidence';

export interface SerializationService {
  serialize<T>(data: T): Promise<string>;
  deserialize<T>(data: string): Promise<T>;
}

export interface ReplayTestConfig {
  readonly payload: unknown;
  readonly handlerType: string;
  readonly serializationService: SerializationService;
}

export interface ReplayTestResult {
  readonly passed: boolean;
  readonly originalEvidenceHash: string;
  readonly deserializedEvidenceHash: string;
  readonly hashesMatch: boolean;
  readonly error?: string;
  readonly originalEvidence?: Evidence;
  readonly deserializedEvidence?: Evidence;
}

export class ReplayTester {
  constructor(
    private readonly dispatcher: any, // CompilerDispatcher
    private readonly hashFunction: (data: string) => string
  ) {}
  
  async runTest(config: ReplayTestConfig): Promise<ReplayTestResult> {
    try {
      // İlk derleme
      const firstResult = await this.dispatcher.dispatch(
        config.payload,
        config.handlerType
      );
      
      if (!firstResult.success || !firstResult.evidence) {
        return {
          passed: false,
          originalEvidenceHash: '',
          deserializedEvidenceHash: '',
          hashesMatch: false,
          error: firstResult.error || 'İlk derleme başarısız'
        };
      }
      
      const originalEvidence = firstResult.evidence;
      const originalSerialized = await config.serializationService.serialize(originalEvidence);
      const originalHash = this.hashFunction(originalSerialized);
      
      // Serialize/Deserialize cycle
      const deserialized = await config.serializationService.deserialize<Evidence>(originalSerialized);
      const reSerialized = await config.serializationService.serialize(deserialized);
      const deserializedHash = this.hashFunction(reSerialized);
      
      const hashesMatch = originalHash === deserializedHash;
      
      return {
        passed: hashesMatch,
        originalEvidenceHash: originalHash,
        deserializedEvidenceHash: deserializedHash,
        hashesMatch,
        originalEvidence,
        deserializedEvidence: deserialized
      };
    } catch (error) {
      return {
        passed: false,
        originalEvidenceHash: '',
        deserializedEvidenceHash: '',
        hashesMatch: false,
        error: error instanceof Error ? error.message : 'Bilinmeyen hata'
      };
    }
  }
  
  async runBatchTest(
    configs: ReplayTestConfig[]
  ): Promise<ReplayTestResult[]> {
    const results: ReplayTestResult[] = [];
    
    for (const config of configs) {
      const result = await this.runTest(config);
      results.push(result);
    }
    
    return results;
  }
}

describe('ReplayTest', () => {
  describe('ReplayTestResult interface', () => {
    it('should create valid result', () => {
      const result: ReplayTestResult = {
        passed: true,
        originalEvidenceHash: 'abc123',
        deserializedEvidenceHash: 'abc123',
        hashesMatch: true
      };
      expect(result.passed).toBe(true);
      expect(result.hashesMatch).toBe(true);
    });
  });
});
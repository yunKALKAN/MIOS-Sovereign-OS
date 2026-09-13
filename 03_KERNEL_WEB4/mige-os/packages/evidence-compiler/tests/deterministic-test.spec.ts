import { Evidence } from '../src/evidence';
import { CompilerDispatcher } from '../src/compiler-dispatcher';
import { ResultType } from '@mucizework/common';

export interface DeterministicTestConfig {
  readonly iterations: number;
  readonly payload: unknown;
  readonly handlerType: string;
}

export interface DeterministicTestResult {
  readonly passed: boolean;
  readonly iterations: number;
  readonly uniqueEvidenceIds: number;
  readonly failedIterations: number;
  readonly firstFailedIteration?: number;
  readonly error?: string;
  readonly sampleEvidence?: Evidence;
}

export class DeterministicTester {
  constructor(
    private readonly dispatcher: CompilerDispatcher
  ) {}
  
  async runTest(config: DeterministicTestConfig): Promise<DeterministicTestResult> {
    const evidenceIds = new Set<string>();
    let failedIterations = 0;
    let firstFailedIteration: number | undefined;
    let lastError: string | undefined;
    let sampleEvidence: Evidence | undefined;
    
    for (let i = 0; i < config.iterations; i++) {
      try {
        const result = await this.dispatcher.dispatch(
          config.payload,
          config.handlerType
        );
        
        if (ResultType.isFailure(result)) {
          failedIterations++;
          if (firstFailedIteration === undefined) {
            firstFailedIteration = i + 1;
          }
          lastError = result.error.message;
          continue;
        }
        
        if (ResultType.isSuccess(result)) {
          evidenceIds.add(result.value.id);
          
          if (!sampleEvidence) {
            sampleEvidence = result.value;
          }
        }
      } catch (error) {
        failedIterations++;
        if (firstFailedIteration === undefined) {
          firstFailedIteration = i + 1;
        }
        lastError = error instanceof Error ? error.message : 'Bilinmeyen hata';
      }
    }
    
    const passed = evidenceIds.size === 1 && failedIterations === 0;
    
    return {
      passed,
      iterations: config.iterations,
      uniqueEvidenceIds: evidenceIds.size,
      failedIterations,
      firstFailedIteration,
      error: lastError,
      sampleEvidence
    };
  }
  
  async runBatchTest(
    configs: DeterministicTestConfig[]
  ): Promise<DeterministicTestResult[]> {
    const results: DeterministicTestResult[] = [];
    
    for (const config of configs) {
      const result = await this.runTest(config);
      results.push(result);
    }
    
    return results;
  }
}

describe('DeterministicTest', () => {
  describe('DeterministicTestResult interface', () => {
    it('should create valid result', () => {
      const result: DeterministicTestResult = {
        passed: true,
        iterations: 10,
        uniqueEvidenceIds: 1,
        failedIterations: 0
      };
      expect(result.passed).toBe(true);
      expect(result.uniqueEvidenceIds).toBe(1);
    });
  });
});
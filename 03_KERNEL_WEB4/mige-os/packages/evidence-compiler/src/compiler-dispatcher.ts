import { Evidence } from './evidence';
import { CompilerHandler } from './compiler-handler';
import { CompilerValidator } from './compiler-validator';
import { HandlerRegistry } from './handler-registry';
import { CompileResult, CompileErrorFactory } from '@mucizework/common';

export interface CompilerDispatcherConfig {
  readonly maxConcurrentCompilations: number;
  readonly timeout: number;
  readonly retryAttempts: number;
}

export interface CompilationResult {
  readonly success: boolean;
  readonly evidence?: Evidence;
  readonly error?: string;
  readonly compilationTime: number;
}

export interface CompilerDispatcher {
  registerHandler(handlerType: string, handler: CompilerHandler): void;
  unregisterHandler(handlerType: string): void;
  
  dispatch(
    rawData: unknown,
    handlerType: string,
    validator?: CompilerValidator
  ): Promise<CompileResult<Evidence>>;
  
  dispatchBatch(
    dataBatch: unknown[],
    handlerType: string,
    validator?: CompilerValidator
  ): Promise<CompileResult<Evidence>[]>;
  
  getStatus(): {
    readonly activeCompilations: number;
    readonly queuedCompilations: number;
    readonly completedCompilations: number;
  };
}

export class DefaultCompilerDispatcher implements CompilerDispatcher {
  private activeCompilations = 0;
  private queuedCompilations = 0;
  private completedCompilations = 0;
  
  constructor(
    private readonly config: CompilerDispatcherConfig,
    private readonly handlerRegistry: HandlerRegistry
  ) {}
  
  registerHandler(handlerType: string, handler: CompilerHandler): void {
    this.handlerRegistry.register(handlerType, handler);
  }
  
  unregisterHandler(handlerType: string): void {
    this.handlerRegistry.unregister(handlerType);
  }
  
  async dispatch(
    rawData: unknown,
    handlerType: string,
    validator?: CompilerValidator
  ): Promise<CompileResult<Evidence>> {
    try {
      this.activeCompilations++;
      
      const handler = this.handlerRegistry.resolve(handlerType);
      const processedData = await handler.process(rawData);
      const evidence = await handler.compile(processedData);
      
      if (validator) {
        const validationResult = await validator.validateEvidence(evidence);
        if (!validationResult.isValid) {
          return {
            type: 'failure',
            error: CompileErrorFactory.validation(
              validationResult.error || 'Doğrulama başarısız'
            )
          };
        }
      }
      
      this.completedCompilations++;
      
      return {
        type: 'success',
        value: evidence
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Bilinmeyen hata';
      return {
        type: 'failure',
        error: CompileErrorFactory.unknown(errorMessage)
      };
    } finally {
      this.activeCompilations--;
    }
  }
  
  async dispatchBatch(
    dataBatch: unknown[],
    handlerType: string,
    validator?: CompilerValidator
  ): Promise<CompileResult<Evidence>[]> {
    const results: CompileResult<Evidence>[] = [];
    
    for (let i = 0; i < dataBatch.length; i += this.config.maxConcurrentCompilations) {
      const batch = dataBatch.slice(i, i + this.config.maxConcurrentCompilations);
      const batchResults = await Promise.all(
        batch.map(data => this.dispatch(data, handlerType, validator))
      );
      results.push(...batchResults);
    }
    
    return results;
  }
  
  getStatus(): {
    activeCompilations: number;
    queuedCompilations: number;
    completedCompilations: number;
  } {
    return {
      activeCompilations: this.activeCompilations,
      queuedCompilations: this.queuedCompilations,
      completedCompilations: this.completedCompilations
    };
  }
}
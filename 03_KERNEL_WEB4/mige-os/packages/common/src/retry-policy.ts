export interface RetryPolicy {
  readonly maxAttempts: number;
  readonly initialDelay: number;
  readonly maxDelay: number;
  readonly backoffMultiplier: number;
  readonly shouldRetry: (error: Error) => boolean;
  getDelay(attempt: number): number;
}

export interface RetryOptions {
  readonly maxAttempts?: number;
  readonly initialDelay?: number;
  readonly maxDelay?: number;
  readonly backoffMultiplier?: number;
  readonly shouldRetry?: (error: Error) => boolean;
}

export class DefaultRetryPolicy implements RetryPolicy {
  readonly maxAttempts: number;
  readonly initialDelay: number;
  readonly maxDelay: number;
  readonly backoffMultiplier: number;
  readonly shouldRetry: (error: Error) => boolean;
  
  constructor(options: RetryOptions = {}) {
    this.maxAttempts = options.maxAttempts ?? 3;
    this.initialDelay = options.initialDelay ?? 1000;
    this.maxDelay = options.maxDelay ?? 30000;
    this.backoffMultiplier = options.backoffMultiplier ?? 2;
    this.shouldRetry = options.shouldRetry ?? (() => true); // eslint-disable-line @typescript-eslint/explicit-function-return-type
  }
  
  getDelay(attempt: number): number {
    const delay = this.initialDelay * Math.pow(this.backoffMultiplier, attempt - 1);
    return Math.min(delay, this.maxDelay);
  }
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  policy: RetryPolicy = new DefaultRetryPolicy()
): Promise<T> {
  let lastError: Error | undefined;
  
  for (let attempt = 1; attempt <= policy.maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      if (attempt === policy.maxAttempts || !policy.shouldRetry(lastError)) {
        throw lastError;
      }
      
      const delay = policy.getDelay(attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
}
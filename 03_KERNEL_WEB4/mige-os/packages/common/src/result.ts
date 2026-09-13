export type Result<T, E = Error> =
  | Success<T>
  | Failure<E>;

export interface Success<T> {
  readonly type: 'success';
  readonly value: T;
}

export interface Failure<E> {
  readonly type: 'failure';
  readonly error: E;
}

export class ResultType {
  static success<T>(value: T): Success<T> {
    return { type: 'success', value };
  }
  
  static failure<E>(error: E): Failure<E> {
    return { type: 'failure', error };
  }
  
  static isSuccess<T, E>(result: Result<T, E>): result is Success<T> {
    return result.type === 'success';
  }
  
  static isFailure<T, E>(result: Result<T, E>): result is Failure<E> {
    return result.type === 'failure';
  }
  
  static map<T, U, E>(
    result: Result<T, E>,
    fn: (value: T) => U
  ): Result<U, E> {
    if (ResultType.isSuccess(result)) {
      return ResultType.success(fn(result.value));
    }
    return result;
  }
  
  static flatMap<T, U, E>(
    result: Result<T, E>,
    fn: (value: T) => Result<U, E>
  ): Result<U, E> {
    if (ResultType.isSuccess(result)) {
      return fn(result.value);
    }
    return result;
  }
  
  static getOrElse<T, E>(result: Result<T, E>, defaultValue: T): T {
    if (ResultType.isSuccess(result)) {
      return result.value;
    }
    return defaultValue;
  }
  
  static getOrThrow<T, E>(result: Result<T, E>): T {
    if (ResultType.isSuccess(result)) {
      return result.value;
    }
    throw result.error;
  }
}

// Compile-specific result types
export type CompileResult<T> = Result<T, CompileError>;

export enum CompileErrorType {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  UNSUPPORTED_CONTAINER = 'UNSUPPORTED_CONTAINER',
  SERIALIZATION_ERROR = 'SERIALIZATION_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

export interface CompileError {
  readonly type: CompileErrorType;
  readonly message: string;
  readonly details?: Record<string, unknown>;
  readonly timestamp: number;
}

export class CompileErrorFactory {
  static validation(message: string, details?: Record<string, unknown>): CompileError {
    return {
      type: CompileErrorType.VALIDATION_ERROR,
      message,
      details,
      timestamp: Date.now()
    };
  }
  
  static unsupportedContainer(containerType: string): CompileError {
    return {
      type: CompileErrorType.UNSUPPORTED_CONTAINER,
      message: `Desteklenmeyen container tipi: ${containerType}`,
      timestamp: Date.now()
    };
  }
  
  static serialization(message: string): CompileError {
    return {
      type: CompileErrorType.SERIALIZATION_ERROR,
      message,
      timestamp: Date.now()
    };
  }
  
  static network(message: string): CompileError {
    return {
      type: CompileErrorType.NETWORK_ERROR,
      message,
      timestamp: Date.now()
    };
  }
  
  static unknown(message: string): CompileError {
    return {
      type: CompileErrorType.UNKNOWN_ERROR,
      message,
      timestamp: Date.now()
    };
  }
}
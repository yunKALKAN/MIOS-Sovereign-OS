export enum ErrorType {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NOT_FOUND_ERROR = 'NOT_FOUND_ERROR',
  CONFLICT_ERROR = 'CONFLICT_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

export interface AppError {
  readonly type: ErrorType;
  readonly message: string;
  readonly code?: string;
  readonly details?: Record<string, unknown>;
  readonly cause?: Error;
  readonly timestamp: number;
}

export class AppErrorFactory {
  static validation(
    message: string,
    code?: string,
    details?: Record<string, unknown>
  ): AppError {
    return {
      type: ErrorType.VALIDATION_ERROR,
      message,
      code,
      details,
      timestamp: Date.now()
    };
  }
  
  static notFound(
    message: string,
    code?: string,
    details?: Record<string, unknown>
  ): AppError {
    return {
      type: ErrorType.NOT_FOUND_ERROR,
      message,
      code,
      details,
      timestamp: Date.now()
    };
  }
  
  static conflict(
    message: string,
    code?: string,
    details?: Record<string, unknown>
  ): AppError {
    return {
      type: ErrorType.CONFLICT_ERROR,
      message,
      code,
      details,
      timestamp: Date.now()
    };
  }
  
  static authentication(
    message: string,
    code?: string,
    details?: Record<string, unknown>
  ): AppError {
    return {
      type: ErrorType.AUTHENTICATION_ERROR,
      message,
      code,
      details,
      timestamp: Date.now()
    };
  }
  
  static authorization(
    message: string,
    code?: string,
    details?: Record<string, unknown>
  ): AppError {
    return {
      type: ErrorType.AUTHORIZATION_ERROR,
      message,
      code,
      details,
      timestamp: Date.now()
    };
  }
  
  static rateLimit(
    message: string,
    code?: string,
    details?: Record<string, unknown>
  ): AppError {
    return {
      type: ErrorType.RATE_LIMIT_ERROR,
      message,
      code,
      details,
      timestamp: Date.now()
    };
  }
  
  static network(
    message: string,
    code?: string,
    details?: Record<string, unknown>,
    cause?: Error
  ): AppError {
    return {
      type: ErrorType.NETWORK_ERROR,
      message,
      code,
      details,
      cause,
      timestamp: Date.now()
    };
  }
  
  static internal(
    message: string,
    code?: string,
    details?: Record<string, unknown>,
    cause?: Error
  ): AppError {
    return {
      type: ErrorType.INTERNAL_ERROR,
      message,
      code,
      details,
      cause,
      timestamp: Date.now()
    };
  }
  
  static unknown(
    message: string,
    code?: string,
    details?: Record<string, unknown>,
    cause?: Error
  ): AppError {
    return {
      type: ErrorType.UNKNOWN_ERROR,
      message,
      code,
      details,
      cause,
      timestamp: Date.now()
    };
  }
}

export function isAppError(error: unknown): error is AppError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'type' in error &&
    'message' in error &&
    'timestamp' in error
  );
}
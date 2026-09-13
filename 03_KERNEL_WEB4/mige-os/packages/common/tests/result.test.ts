import { ResultType, CompileErrorFactory, CompileErrorType } from '../src/result';

describe('ResultType', () => {
  describe('success', () => {
    it('should create a success result', () => {
      const result = ResultType.success({ value: 42 });
      expect(result.type).toBe('success');
      if (ResultType.isSuccess(result)) {
        expect(result.value).toEqual({ value: 42 });
      }
    });
  });

  describe('failure', () => {
    it('should create a failure result', () => {
      const error = CompileErrorFactory.validation('Test error');
      const result = ResultType.failure(error);
      expect(result.type).toBe('failure');
      if (ResultType.isFailure(result)) {
        expect(result.error).toEqual(error);
      }
    });
  });

  describe('isSuccess', () => {
    it('should return true for success result', () => {
      const result = ResultType.success(42);
      expect(ResultType.isSuccess(result)).toBe(true);
    });

    it('should return false for failure result', () => {
      const error = CompileErrorFactory.validation('Test error');
      const result = ResultType.failure(error);
      expect(ResultType.isSuccess(result)).toBe(false);
    });
  });

  describe('isFailure', () => {
    it('should return true for failure result', () => {
      const error = CompileErrorFactory.validation('Test error');
      const result = ResultType.failure(error);
      expect(ResultType.isFailure(result)).toBe(true);
    });

    it('should return false for success result', () => {
      const result = ResultType.success(42);
      expect(ResultType.isFailure(result)).toBe(false);
    });
  });

  describe('map', () => {
    it('should map success result', () => {
      const result = ResultType.success(42);
      const mapped = ResultType.map(result, (x) => (x as number) * 2);
      expect(ResultType.isSuccess(mapped)).toBe(true);
      if (ResultType.isSuccess(mapped)) {
        expect(mapped.value).toBe(84);
      }
    });

    it('should pass through failure result', () => {
      const error = CompileErrorFactory.validation('Test error');
      const result = ResultType.failure(error);
      const mapped = ResultType.map(result, (x) => (x as number) * 2);
      expect(ResultType.isFailure(mapped)).toBe(true);
    });
  });

  describe('getOrElse', () => {
    it('should return value for success result', () => {
      const result = ResultType.success(42);
      expect(ResultType.getOrElse(result, 0)).toBe(42);
    });

    it('should return default for failure result', () => {
      const error = CompileErrorFactory.validation('Test error');
      const result = ResultType.failure(error);
      expect(ResultType.getOrElse(result, 0)).toBe(0);
    });
  });
});

describe('CompileErrorFactory', () => {
  describe('validation', () => {
    it('should create validation error', () => {
      const error = CompileErrorFactory.validation('Invalid input');
      expect(error.type).toBe(CompileErrorType.VALIDATION_ERROR);
      expect(error.message).toBe('Invalid input');
      expect(error.timestamp).toBeDefined();
    });
  });

  describe('unsupportedContainer', () => {
    it('should create unsupported container error', () => {
      const error = CompileErrorFactory.unsupportedContainer('UNKNOWN');
      expect(error.type).toBe(CompileErrorType.UNSUPPORTED_CONTAINER);
      expect(error.message).toContain('UNKNOWN');
    });
  });
});
import { DefaultRetryPolicy, withRetry } from '../src/retry-policy';

describe('DefaultRetryPolicy', () => {
  describe('constructor', () => {
    it('should use default values when no options provided', () => {
      const policy = new DefaultRetryPolicy();
      expect(policy.maxAttempts).toBe(3);
      expect(policy.initialDelay).toBe(1000);
      expect(policy.maxDelay).toBe(30000);
    });

    it('should use provided values', () => {
      const policy = new DefaultRetryPolicy({
        maxAttempts: 5,
        initialDelay: 500,
        maxDelay: 10000
      });
      expect(policy.maxAttempts).toBe(5);
      expect(policy.initialDelay).toBe(500);
      expect(policy.maxDelay).toBe(10000);
    });
  });

  describe('getDelay', () => {
    it('should increase delay with attempts', () => {
      const policy = new DefaultRetryPolicy({
        initialDelay: 1000,
        backoffMultiplier: 2
      });
      expect(policy.getDelay(1)).toBe(1000);
      expect(policy.getDelay(2)).toBe(2000);
      expect(policy.getDelay(3)).toBe(4000);
    });

    it('should cap at max delay', () => {
      const policy = new DefaultRetryPolicy({
        initialDelay: 1000,
        maxDelay: 2000,
        backoffMultiplier: 10
      });
      expect(policy.getDelay(1)).toBe(1000);
      expect(policy.getDelay(2)).toBe(2000);
      expect(policy.getDelay(3)).toBe(2000);
    });
  });
});

describe('withRetry', () => {
  describe('success on first attempt', () => {
    it('should return result immediately', async () => {
      const fn = jest.fn().mockResolvedValue('success');
      const result = await withRetry(fn);
      expect(result).toBe('success');
      expect(fn).toHaveBeenCalledTimes(1);
    });
  });

  describe('success after retry', () => {
    it('should retry on failure', async () => {
      const fn = jest.fn()
        .mockRejectedValueOnce(new Error('fail'))
        .mockResolvedValue('success');
      
      const policy = new DefaultRetryPolicy({ maxAttempts: 3 });
      const result = await withRetry(fn, policy);
      expect(result).toBe('success');
      expect(fn).toHaveBeenCalledTimes(2);
    });
  });

  describe('max attempts exceeded', () => {
    it('should throw after max attempts', async () => {
      const fn = jest.fn().mockRejectedValue(new Error('fail'));
      const policy = new DefaultRetryPolicy({ maxAttempts: 2 });
      
      await expect(withRetry(fn, policy)).rejects.toThrow('fail');
      expect(fn).toHaveBeenCalledTimes(2);
    });
  });

  describe('shouldRetry callback', () => {
    it('should respect shouldRetry callback', async () => {
      const fn = jest.fn().mockRejectedValue(new Error('fail'));
      const policy = new DefaultRetryPolicy({
        maxAttempts: 5,
        shouldRetry: () => false
      });
      
      await expect(withRetry(fn, policy)).rejects.toThrow('fail');
      expect(fn).toHaveBeenCalledTimes(1);
    });
  });
});
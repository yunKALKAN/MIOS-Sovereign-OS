import { SystemClock, TestClock } from '../src/clock';

describe('SystemClock', () => {
  let clock: SystemClock;

  beforeEach(() => {
    clock = new SystemClock();
  });

  describe('now', () => {
    it('should return current timestamp', () => {
      const now = clock.now();
      expect(now).toBeGreaterThan(0);
      expect(typeof now).toBe('number');
    });
  });

  describe('nowDate', () => {
    it('should return current Date object', () => {
      const date = clock.nowDate();
      expect(date).toBeInstanceOf(Date);
    });
  });

  describe('sleep', () => {
    it('should sleep for specified duration', async () => {
      const start = Date.now();
      await clock.sleep(100);
      const end = Date.now();
      expect(end - start).toBeGreaterThanOrEqual(100);
    }, 200);
  });
});

describe('TestClock', () => {
  let clock: TestClock;

  beforeEach(() => {
    clock = new TestClock(1000);
  });

  describe('now', () => {
    it('should return configured time', () => {
      expect(clock.now()).toBe(1000);
    });
  });

  describe('setTime', () => {
    it('should update time', () => {
      clock.setTime(2000);
      expect(clock.now()).toBe(2000);
    });
  });

  describe('advance', () => {
    it('should advance time', () => {
      clock.advance(500);
      expect(clock.now()).toBe(1500);
    });
  });

  describe('sleep', () => {
    it('should advance time instead of sleeping', async () => {
      const start = clock.now();
      await clock.sleep(100);
      const end = clock.now();
      expect(end - start).toBe(100);
    });
  });
});
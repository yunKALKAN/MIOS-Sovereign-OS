export interface Clock {
  now(): number;
  nowDate(): Date;
  sleep(ms: number): Promise<void>;
}

export class SystemClock implements Clock {
  now(): number {
    return Date.now();
  }
  
  nowDate(): Date {
    return new Date();
  }
  
  async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export class TestClock implements Clock {
  private currentTime: number;
  
  constructor(initialTime: number = Date.now()) {
    this.currentTime = initialTime;
  }
  
  now(): number {
    return this.currentTime;
  }
  
  nowDate(): Date {
    return new Date(this.currentTime);
  }
  
  async sleep(ms: number): Promise<void> {
    this.currentTime += ms;
  }
  
  setTime(time: number): void {
    this.currentTime = time;
  }
  
  advance(ms: number): void {
    this.currentTime += ms;
  }
}

// Singleton instance
export const systemClock = new SystemClock();
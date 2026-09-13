import { CompilerHandler } from './compiler-handler';

export interface HandlerRegistry {
  register(handlerType: string, handler: CompilerHandler): void;
  resolve(handlerType: string): CompilerHandler;
  unregister(handlerType: string): void;
  hasHandler(handlerType: string): boolean;
  getRegisteredHandlers(): string[];
}

export class DefaultHandlerRegistry implements HandlerRegistry {
  private readonly handlers = new Map<string, CompilerHandler>();
  
  register(handlerType: string, handler: CompilerHandler): void {
    if (this.handlers.has(handlerType)) {
      throw new Error(`Handler zaten kayıtlı: ${handlerType}`);
    }
    this.handlers.set(handlerType, handler);
  }
  
  resolve(handlerType: string): CompilerHandler {
    const handler = this.handlers.get(handlerType);
    if (!handler) {
      throw new Error(`Handler bulunamadı: ${handlerType}`);
    }
    return handler;
  }
  
  unregister(handlerType: string): void {
    if (!this.handlers.delete(handlerType)) {
      throw new Error(`Handler kayıtlı değil: ${handlerType}`);
    }
  }
  
  hasHandler(handlerType: string): boolean {
    return this.handlers.has(handlerType);
  }
  
  getRegisteredHandlers(): string[] {
    return Array.from(this.handlers.keys());
  }
}
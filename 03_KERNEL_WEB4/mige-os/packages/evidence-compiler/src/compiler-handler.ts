import { Evidence } from './evidence';

export interface ProcessedData {
  readonly normalized: unknown;
  readonly metadata: Readonly<Record<string, unknown>>;
  readonly source: string;
}

export interface CompilerHandler {
  process(rawData: unknown): Promise<ProcessedData>;
  compile(processedData: ProcessedData): Promise<Evidence>;
  getHandlerType(): string;
  getSupportedFormats(): string[];
}

export abstract class BaseCompilerHandler implements CompilerHandler {
  abstract getHandlerType(): string;
  abstract getSupportedFormats(): string[];
  
  abstract process(rawData: unknown): Promise<ProcessedData>;
  abstract compile(processedData: ProcessedData): Promise<Evidence>;
  
  protected validateRawData(rawData: unknown): void {
    if (rawData === null || rawData === undefined) {
      throw new Error('Ham veri null veya undefined olamaz');
    }
  }
  
  protected validateProcessedData(processedData: ProcessedData): void {
    if (!processedData.source) {
      throw new Error('İşlenmiş veri kaynağı eksik');
    }
  }
}
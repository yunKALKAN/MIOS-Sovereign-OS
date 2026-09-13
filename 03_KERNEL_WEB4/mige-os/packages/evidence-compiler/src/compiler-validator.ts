import { Evidence } from './evidence';
import { CURRENT_SCHEMA_VERSION } from './evidence';

export interface ValidationResult {
  readonly isValid: boolean;
  readonly error?: string;
  readonly warnings?: string[];
}

export interface CompilerValidator {
  validateEvidence(evidence: Evidence): Promise<ValidationResult>;
  getValidatorType(): string;
}

export abstract class BaseCompilerValidator implements CompilerValidator {
  abstract getValidatorType(): string;
  
  async validateEvidence(evidence: Evidence): Promise<ValidationResult> {
    const warnings: string[] = [];
    
    // Schema version kontrolü
    if (evidence.schemaVersion !== CURRENT_SCHEMA_VERSION) {
      return this.createError(`Schema versiyonu uyumsuz: beklenen ${CURRENT_SCHEMA_VERSION}, alınan ${evidence.schemaVersion}`);
    }
    
    // Required fields kontrolü
    if (!evidence.id || typeof evidence.id !== 'string') {
      return this.createError('Evidence ID gerekli ve string olmalı');
    }
    
    if (!evidence.type) {
      return this.createError('Evidence type gerekli');
    }
    
    if (!evidence.evidenceClass) {
      return this.createError('Evidence class gerekli');
    }
    
    if (!evidence.proofLevel) {
      return this.createError('Proof level gerekli');
    }
    
    if (!evidence.sourceNode || typeof evidence.sourceNode !== 'string') {
      return this.createError('Source node gerekli ve string olmalı');
    }
    
    if (!evidence.provenance) {
      return this.createError('Provenance gerekli');
    }
    
    // Provenance kontrolü
    if (!evidence.provenance.blockchain) {
      return this.createError('Provenance blockchain gerekli');
    }
    
    if (!evidence.provenance.source) {
      return this.createError('Provenance source gerekli');
    }
    
    if (!evidence.provenance.collectedAt || typeof evidence.provenance.collectedAt !== 'number') {
      return this.createError('Provenance collectedAt gerekli ve number olmalı');
    }
    
    if (!evidence.provenance.rawHash || typeof evidence.provenance.rawHash !== 'string') {
      return this.createError('Provenance rawHash gerekli ve string olmalı');
    }
    
    // Attributes kontrolü
    if (!evidence.attributes || typeof evidence.attributes !== 'object') {
      return this.createError('Attributes gerekli ve object olmalı');
    }
    
    return this.createSuccess(warnings);
  }
  
  protected addWarning(warnings: string[], warning: string): void {
    warnings.push(warning);
  }
  
  protected createError(message: string): ValidationResult {
    return {
      isValid: false,
      error: message,
      warnings: []
    };
  }
  
  protected createSuccess(warnings: string[] = []): ValidationResult {
    return {
      isValid: true,
      warnings
    };
  }
}
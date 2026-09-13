import { EvidenceType } from './evidence-type';
import { EvidenceClass } from './evidence-class';
import { ProofLevel } from './proof-level';
import { Provenance } from '@mucizework/core-contracts';

export interface Evidence {
  readonly id: string;
  readonly type: EvidenceType;
  readonly evidenceClass: EvidenceClass;
  readonly proofLevel: ProofLevel;
  
  readonly sourceNode: string;
  readonly targetNode?: string;
  
  readonly attributes: Readonly<Record<string, unknown>>;
  readonly provenance: Provenance;
  readonly schemaVersion: string;
}

export const CURRENT_SCHEMA_VERSION = '1.0.0';
// Sözleşmeler
export { Evidence, CURRENT_SCHEMA_VERSION } from './src/evidence';
export { EvidenceType } from './src/evidence-type';
export { EvidenceClass } from './src/evidence-class';
export { ProofLevel } from './src/proof-level';

// Core Contracts
export { Provenance } from '@mucizework/core-contracts';

// Adapter Registry
export { 
  AdapterRegistry, 
  DefaultAdapterRegistry 
} from './src/adapter-registry';
export { 
  DiscoveryAdapter 
} from './src/discovery-adapter';

// Raw Container
export { 
  RawContainer, 
  ContainerType 
} from './src/raw-container';

// Domain Events
export { 
  DomainEvent 
} from './src/domain-event';
export { 
  DomainEventType 
} from './src/domain-event-type';

// Event Bus
export { 
  EventBus, 
  EventHandler, 
  EventBusConfig 
} from './src/event-bus';

// Compiler Altyapısı
export {
  CompilerDispatcher,
  DefaultCompilerDispatcher,
  CompilerDispatcherConfig,
  CompilationResult
} from './src/compiler-dispatcher';

export {
  CompilerHandler,
  BaseCompilerHandler,
  ProcessedData
} from './src/compiler-handler';

export {
  CompilerValidator,
  BaseCompilerValidator,
  ValidationResult
} from './src/compiler-validator';

export {
  HandlerRegistry,
  DefaultHandlerRegistry
} from './src/handler-registry';

// Test Altyapısı
export {
  DeterministicTester,
  DeterministicTestConfig,
  DeterministicTestResult
} from './tests/deterministic-test.spec';

export {
  ReplayTester,
  ReplayTestConfig,
  ReplayTestResult,
  SerializationService
} from './tests/replay-test.spec';

export {
  CrossPlatformTester,
  CrossPlatformTestConfig,
  CrossPlatformTestResult,
  PlatformInfo
} from './tests/cross-platform-test.spec';

// Common exports (re-export for convenience)
export {
  Result,
  Success,
  Failure,
  ResultType,
  CompileResult,
  CompileError,
  CompileErrorType,
  CompileErrorFactory
} from '@mucizework/common';

export {
  HashService,
  CanonicalHashService,
  HashComponents,
  canonicalHashService
} from '@mucizework/common';

export {
  UUID
} from '@mucizework/common';

export {
  Clock,
  SystemClock,
  TestClock,
  systemClock
} from '@mucizework/common';